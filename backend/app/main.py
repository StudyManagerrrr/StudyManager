from fastapi import FastAPI,HTTPException,Depends,Header,Request,Response,Cookie,UploadFile,File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse,FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel,Field,field_validator
from sqlalchemy import select,insert,update,func,or_
from sqlalchemy.exc import SQLAlchemyError
from jwt.exceptions import InvalidTokenError
from argon2 import PasswordHasher
import bcrypt
import jwt,uuid,datetime,logging,json,hashlib,hmac,re,ipaddress,csv,io,mimetypes
from pathlib import Path
from collections import defaultdict,deque
from threading import Lock
from app.core.config import settings
from app.database.schema import engine,metadata,reflect_schema
from app.errors import code_for_http,message_for,preferred_language,ERROR_MESSAGES
logging.basicConfig(level=settings.log_level)
app=FastAPI(title='AI Learning Guardian API',version='1.0.0',docs_url='/api/docs')
allowed_origins={settings.frontend_origin}
if settings.app_env.lower() in {'development','dev','test'}:allowed_origins.update({'http://localhost:5173','http://127.0.0.1:5173'})
app.add_middleware(CORSMiddleware,allow_origins=sorted(allowed_origins),allow_credentials=True,allow_methods=['GET','POST','PATCH','DELETE'],allow_headers=['Authorization','Content-Type','Idempotency-Key','Accept-Language','X-Request-ID'],expose_headers=['X-Request-ID'])

def error_response(request,status,code,details=None,headers=None):
 request_id=getattr(request.state,'request_id',str(uuid.uuid4()));language=preferred_language(request);message=message_for(code,language)
 logging.info('api_error request_id=%s status=%s code=%s',request_id,status,code)
 body={'success':False,'error':{'code':code,'message':message,'details':details,'request_id':request_id},'detail':message}
 response_headers=dict(headers or {});response_headers['X-Request-ID']=request_id
 return JSONResponse(status_code=status,content=body,headers=response_headers)

@app.middleware('http')
async def assign_request_id(request:Request,call_next):
 request.state.request_id=str(uuid.uuid4())
 response=await call_next(request)
 response.headers['X-Request-ID']=request.state.request_id
 content_type=response.headers.get('content-type','')
 if content_type.startswith('application/json') and 'charset=' not in content_type.lower():
  response.headers['content-type']='application/json; charset=utf-8'
 return response

@app.exception_handler(StarletteHTTPException)
async def handle_http_exception(request:Request,exc:HTTPException):
 detail=exc.detail
 if isinstance(detail,dict) and detail.get('code') in ERROR_MESSAGES:
  code=detail['code'];safe_details=detail.get('details')
 else:
  code=code_for_http(exc.status_code,detail);safe_details=None
 return error_response(request,exc.status_code,code,safe_details,exc.headers)

@app.exception_handler(RequestValidationError)
async def handle_request_validation(request:Request,exc:RequestValidationError):
 details=[]
 for item in exc.errors():
  kind=str(item.get('type',''));code='required' if kind=='missing' else 'format' if 'parsing' in kind or 'type' in kind else 'value'
  loc=item.get('loc',());field='.'.join(str(part) for part in loc if part not in {'body','query','path','header'})
  details.append({'field':field,'code':code})
 error_code='VALIDATION_REQUIRED' if details and all(item['code']=='required' for item in details) else 'VALIDATION_INVALID_FORMAT' if any(item['code']=='format' for item in details) else 'VALIDATION_INVALID_VALUE'
 return error_response(request,422,error_code,details)

@app.exception_handler(SQLAlchemyError)
async def handle_database_exception(request:Request,exc:SQLAlchemyError):
 request_id=getattr(request.state,'request_id','unknown')
 logging.error('Database request failure request_id=%s exception_type=%s',request_id,type(exc).__name__)
 return error_response(request,503,'DATABASE_UNAVAILABLE')

@app.exception_handler(Exception)
async def handle_unexpected_exception(request:Request,exc:Exception):
 request_id=getattr(request.state,'request_id','unknown')
 logging.error('Unhandled request failure request_id=%s exception_type=%s',request_id,type(exc).__name__)
 return error_response(request,500,'INTERNAL_SERVER_ERROR')
ph=PasswordHasher()
def tbl(n):
 if n not in metadata.tables:raise HTTPException(503,'Required database table unavailable')
 return metadata.tables[n]
def now():return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
def utc_datetime(value):
 if value is None:return None
 parsed=value if isinstance(value,datetime.datetime) else datetime.datetime.fromisoformat(str(value).replace('Z','+00:00'))
 if parsed.tzinfo is not None:parsed=parsed.astimezone(datetime.timezone.utc).replace(tzinfo=None)
 return parsed

VIETNAMESE_WEEKDAYS={
 't2':0,'thu2':0,'thứ hai':0,'thứ2':0,'mon':0,'monday':0,
 't3':1,'thu3':1,'thứ ba':1,'thứ3':1,'tue':1,'tuesday':1,
 't4':2,'thu4':2,'thứ tư':2,'thứ4':2,'wed':2,'wednesday':2,
 't5':3,'thu5':3,'thứ năm':3,'thứ5':3,'thu':3,'thursday':3,
 't6':4,'thu6':4,'thứ sáu':4,'thứ6':4,'fri':4,'friday':4,
 't7':5,'thu7':5,'thứ bảy':5,'thứ7':5,'sat':5,'saturday':5,
 'cn':6,'chu nhat':6,'chủ nhật':6,'sun':6,'sunday':6,
}
TIME_PATTERN=re.compile(r'(\d{1,2})[:hH]?(\d{0,2})')
def parse_clock(value):
 text=str(value).strip().lower().replace('h',':')
 match=re.search(r'(\d{1,2})(?:[:\.](\d{1,2}))?',text)
 if not match:return None
 hour=int(match.group(1));minute=int(match.group(2) or 0)
 if hour>23 or minute>59:return None
 return hour,minute
def parse_natural_timetable(text):
 text=text.replace('\\n','\n')
 rows=[];errors=[]
 for number,line in enumerate(text.splitlines(),1):
  line=' '.join(line.strip().split())
  if not line:continue
  normalized=re.sub(r'[,.]',' ',line.lower())
  normalized=normalized.replace('thứ','thu').replace('chủ nhật','cn').replace('chữ','chu')
  weekday=None
  compact=re.sub(r'\s+','',normalized)
  for label,idx in sorted(VIETNAMESE_WEEKDAYS.items(),key=lambda pair:-len(pair[0])):
   compact_label=re.sub(r'\s+','',label)
   if compact_label in compact:
    weekday=idx;break
  clock_matches=re.findall(r'(\d{1,2}(?:[:.]\d{1,2}|h\d{1,2}|h)?)\s*(?:-|đến|den|to)\s*(\d{1,2}(?:[:.]\d{1,2}|h\d{1,2}|h)?)',normalized)
  if weekday is None or not clock_matches:
   errors.append({'line':number,'message':'Could not detect weekday and time range','source':line})
   continue
  start=parse_clock(clock_matches[0][0]);end=parse_clock(clock_matches[0][1])
  if not start or not end:
   errors.append({'line':number,'message':'Invalid time','source':line})
   continue
  if end[0]*60+end[1]<=start[0]*60+start[1]:
   errors.append({'line':number,'message':'End time must be later than start time','source':line})
   continue
  remainder=line
  remainder=re.sub(r'(?i)^(?:thứ\s*[2-7]|thứ hai|thứ ba|thứ tư|thứ năm|thứ sáu|thứ bảy|chủ nhật|cn|t[2-7])\s*[,:-]*\s*','',remainder)
  remainder=re.sub(r'\s+\d{1,2}(?:[:h\.]\d{1,2})?\s*(?:-|đến|to)\s*\d{1,2}(?:[:h\.]\d{1,2})?\s*',' ',remainder,flags=re.I)
  title=re.sub(r'(?i)\s+(?:tại|phòng|room)\s+.*$','',remainder).strip()
  location_match=re.search(r'(?i)(?:tại|phòng|room)\s+(.+)$',line)
  location=location_match.group(1).strip().rstrip('.').strip() if location_match else None
  title=re.split(r'(?i)\s+(?:từ|from)\s+',title,maxsplit=1)[0].strip()
  title=re.sub(r'(?i)^(?:học|learn|study)\s+','',title).strip()
  title=title or 'Learning session'
  rows.append({'weekday':weekday,'date':None,'title':title,'start_at':f'{start[0]:02d}:{start[1]:02d}','end_at':f'{end[0]:02d}:{end[1]:02d}','location':location,'subject_id':None})
 return rows,errors
def request_ip(request):
 peer=request.client.host if request.client else 'unknown'
 if peer in {'127.0.0.1','::1'}:
  candidate=request.headers.get('cf-connecting-ip')
  if candidate:
   try:return str(ipaddress.ip_address(candidate.strip()))
   except ValueError:pass
 return peer
ACCESS_MINUTES=15
REFRESH_DAYS=30
REFRESH_COOKIE='guardian_refresh'
LOGIN_WINDOW_SECONDS=600
LOGIN_MAX_FAILURES=5
LOGIN_BLOCK_SECONDS=900
_login_failures=defaultdict(deque)
_login_blocks={}
_login_lock=Lock()
_registration_attempts=defaultdict(deque)
REGISTRATION_WINDOW_SECONDS=3600
REGISTRATION_MAX_ATTEMPTS=5
def token(u,session_id,kind='access'):
 lifetime=datetime.timedelta(minutes=ACCESS_MINUTES) if kind=='access' else datetime.timedelta(days=REFRESH_DAYS)
 return jwt.encode({'sub':u['id'],'role':u.get('role'),'sid':session_id,'typ':kind,'jti':str(uuid.uuid4()),'exp':datetime.datetime.now(datetime.timezone.utc)+lifetime},settings.jwt_secret,algorithm='HS256')
def refresh_hash(value):return hashlib.sha256(value.encode('utf-8')).hexdigest()
def set_refresh_cookie(response,value):
 response.set_cookie(REFRESH_COOKIE,value,max_age=REFRESH_DAYS*24*60*60,httponly=True,secure=settings.app_env.lower() not in {'development','dev','test'},samesite='strict',path='/api/v1/auth')
def revoke_cookie(response):response.delete_cookie(REFRESH_COOKIE,path='/api/v1/auth',secure=settings.app_env.lower() not in {'development','dev','test'},httponly=True,samesite='strict')
def check_login_rate_limit(request):
 key=request_ip(request);current=datetime.datetime.now(datetime.timezone.utc).timestamp()
 with _login_lock:
  until=_login_blocks.get(key,0)
  if until>current:raise HTTPException(429,'Too many failed sign-in attempts; try again later')
  _login_blocks.pop(key,None);attempts=_login_failures[key]
  while attempts and current-attempts[0]>LOGIN_WINDOW_SECONDS:attempts.popleft()
def record_login_failure(request):
 key=request_ip(request);current=datetime.datetime.now(datetime.timezone.utc).timestamp()
 with _login_lock:
  attempts=_login_failures[key]
  while attempts and current-attempts[0]>LOGIN_WINDOW_SECONDS:attempts.popleft()
  attempts.append(current)
  if len(attempts)>=LOGIN_MAX_FAILURES:_login_blocks[key]=current+LOGIN_BLOCK_SECONDS
def clear_login_failures(request):
 key=request_ip(request)
 with _login_lock:_login_failures.pop(key,None);_login_blocks.pop(key,None)
def check_registration_rate_limit(request):
 key=request_ip(request);current=datetime.datetime.now(datetime.timezone.utc).timestamp()
 with _login_lock:
  attempts=_registration_attempts[key]
  while attempts and current-attempts[0]>REGISTRATION_WINDOW_SECONDS:attempts.popleft()
  if len(attempts)>=REGISTRATION_MAX_ATTEMPTS:raise HTTPException(429,'Registration limit reached; try again later')
  attempts.append(current)
def audit_auth_event(connection,user_id,action,entity_id,request):
 audit=tbl('audit_logs')
 connection.execute(insert(audit).values(id=str(uuid.uuid4()),user_id=user_id,action=action,entity_type='AUTH_SESSION',entity_id=entity_id,old_values=None,new_values=None,ip_address=request_ip(request),user_agent=request.headers.get('user-agent','')[:500] or None,created_at=now()))
def issue_session(user,request,response):
 sid=str(uuid.uuid4());refresh=token(user,sid,'refresh');session=tbl('user_sessions')
 expiry=datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(days=REFRESH_DAYS)
 peer=request_ip(request)
 agent=request.headers.get('user-agent','')[:500] or None
 with engine.begin() as c:
  c.execute(insert(session).values(id=sid,user_id=user['id'],token_hash=refresh_hash(refresh),ip_address=peer,user_agent=agent,expires_at=expiry.replace(tzinfo=None),revoked_at=None,created_at=now()))
  audit_auth_event(c,user['id'],'LOGIN_SUCCEEDED',sid,request)
 set_refresh_cookie(response,refresh)
 return {'access_token':token(user,sid),'token_type':'bearer','expires_in':ACCESS_MINUTES*60,'user':{k:user[k] for k in ('id','username','email','full_name','role')}}
def current_user(authorization:str|None=Header(default=None)):
 if not authorization or not authorization.startswith('Bearer '):raise HTTPException(401,'Authentication required')
 try:
  p=jwt.decode(authorization[7:],settings.jwt_secret,algorithms=['HS256'])
  if p.get('typ')!='access' or not p.get('sid'):raise HTTPException(401,'Invalid or expired session')
 except InvalidTokenError:raise HTTPException(401,'Invalid or expired session')
 try:
  with engine.connect() as c:
   sessions=tbl('user_sessions')
   active_session=c.execute(select(sessions.c.id).where(sessions.c.id==p['sid'],sessions.c.user_id==p['sub'],sessions.c.revoked_at.is_(None),sessions.c.expires_at>now())).first()
   u=c.execute(select(tbl('users')).where(tbl('users').c.id==p['sub'],tbl('users').c.is_active==1)).mappings().first() if active_session else None
 except SQLAlchemyError:
  logging.exception('Database error while resolving authenticated user')
  raise HTTPException(503,'Authentication service temporarily unavailable')
 if not u:raise HTTPException(401,'Invalid or expired session')
 return {**dict(u),'_session_id':p['sid']}
def student_ids(u):
 with engine.connect() as c:
  if u['role']=='STUDENT':return [u['id']]
  return list(c.execute(select(tbl('guardian_student_links').c.student_id).where(tbl('guardian_student_links').c.guardian_id==u['id'],tbl('guardian_student_links').c.is_active==1)).scalars())
def student_scope(u,sid=None):
 if u['role']=='STUDENT':return u['id']
 ids=student_ids(u)
 if sid in ids:return sid
 if len(ids)==1:return ids[0]
 raise HTTPException(403,'Student relationship required')
def require_owned_record(table_name,record_id,student_id):
 """Reject related IDs that do not belong to the selected Student."""
 if not record_id:return
 t=tbl(table_name)
 with engine.connect() as c:
  if 'student_id' in t.c:
   predicates=[t.c.id==record_id,t.c.student_id==student_id]
   if 'is_active' in t.c:predicates.append(t.c.is_active==1)
   exists=c.execute(select(t.c.id).where(*predicates)).first()
  elif table_name=='topics':
   subjects=tbl('subjects')
   predicates=[t.c.id==record_id,subjects.c.student_id==student_id]
   if 'is_active' in subjects.c:predicates.append(subjects.c.is_active==1)
   exists=c.execute(select(t.c.id).select_from(t.join(subjects,t.c.subject_id==subjects.c.id)).where(*predicates)).first()
  else:
   raise HTTPException(422,f'{table_name} ownership cannot be verified')
 if not exists:raise HTTPException(404,f'{table_name[:-1] if table_name.endswith("s") else table_name} not found for this Student')
def quiz_is_accessible(user,quiz,connection):
 """A quiz is visible to its Guardian or to a linked Student it targets."""
 allowed_students=student_ids(user)
 owners=[]
 if quiz['task_id']:
  tasks=tbl('learning_tasks')
  owner=connection.execute(select(tasks.c.student_id).where(tasks.c.id==quiz['task_id'])).scalar()
  if owner is None:return False
  owners.append(owner)
 if quiz['subject_id']:
  subjects=tbl('subjects')
  owner=connection.execute(select(subjects.c.student_id).where(subjects.c.id==quiz['subject_id'])).scalar()
  if owner is None:return False
  owners.append(owner)
 if owners:
  return bool(allowed_students) and len(set(owners))==1 and owners[0] in allowed_students
 if user['role']=='GUARDIAN':return quiz['created_by']==user['id']
 if not allowed_students:return False
 if user['role']=='STUDENT':
  links=tbl('guardian_student_links')
  if connection.execute(select(links.c.id).where(links.c.student_id==user['id'],links.c.guardian_id==quiz['created_by'],links.c.is_active==1)).first():return True
 return False
def records(name,u,student_col='student_id'):
 t=tbl(name);ids=student_ids(u)
 if student_col not in t.c or not ids:return []
 predicates=[t.c[student_col].in_(ids)]
 if 'is_active' in t.c:predicates.append(t.c.is_active==1)
 with engine.connect() as c:return [dict(r) for r in c.execute(select(t).where(*predicates).limit(100)).mappings()]
@app.on_event('startup')
def startup():
 if engine:
  try:reflect_schema()
  except Exception:logging.exception('TiDB schema reflection failed')
@app.get('/health')
def health():
 if not engine:raise HTTPException(503,'DATABASE_URL is not configured')
 try:
  with engine.connect() as c:c.execute(select(1))
  if not metadata.tables:reflect_schema()
  return {'status':'ok','database':'connected','schema_tables':len(metadata.tables),'writes_on_startup':False}
 except Exception as e:raise HTTPException(503,'Database unavailable: '+type(e).__name__)
class Login(BaseModel):
 username:str
 password:str
 @field_validator('username')
 @classmethod
 def normalize_login_identity(cls,value):
  value=value.strip().lower()
  if not value:raise ValueError('Login identity is required')
  return value
class GuardianRegistration(BaseModel):
 username:str=Field(min_length=3,max_length=32)
 email:str=Field(min_length=3,max_length=255)
 full_name:str=Field(min_length=1,max_length=150)
 password:str
 @field_validator('username')
 @classmethod
 def validate_username(cls,value):
  value=value.strip().lower()
  if not re.fullmatch(r'[a-z0-9][a-z0-9_.-]{2,31}',value):raise ValueError('Use 3–32 letters, numbers, dots, underscores or hyphens')
  return value
 @field_validator('email')
 @classmethod
 def validate_email(cls,value):
  value=value.strip().lower()
  if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]{2,}',value):raise ValueError('Enter a valid email address')
  return value
 @field_validator('full_name')
 @classmethod
 def validate_full_name(cls,value):
  value=' '.join(value.split())
  if not value:raise ValueError('Full name is required')
  return value
class Item(BaseModel):data:dict
class Note(BaseModel):title:str;content:str='';subject_id:str|None=None;topic_id:str|None=None;schedule_id:str|None=None
class SessionStart(BaseModel):schedule_id:str|None=None;session_type:str='STUDY'
class SessionFinish(BaseModel):notes:str|None=None
class TaskStatusUpdate(BaseModel):status:str
class TimetableParse(BaseModel):
 text:str=Field(min_length=1,max_length=10000)
 student_id:str|None=None
class TimetableRow(BaseModel):
 weekday:int|None=None
 date:str|None=None
 title:str=Field(min_length=1,max_length=200)
 start_at:str
 end_at:str
 location:str|None=None
 subject_id:str|None=None
class TimetableImport(BaseModel):
 student_id:str|None=None
 rows:list[TimetableRow]=Field(min_length=1,max_length=500)
class ScheduleViewRequest(BaseModel):
 student_id:str|None=None
 date:str
class DevicePairRequest(BaseModel):
 device_name:str=Field(min_length=1,max_length=150)
 device_identifier:str=Field(min_length=1,max_length=255)
 operating_system:str|None=None
 os_version:str|None=None
 student_id:str|None=None
class AgentEvent(BaseModel):
 event_id:str
 event_type:str
 occurred_at:str
 agent_version:str|None=None
 payload:dict={}
class AgentBatch(BaseModel):
 events:list[AgentEvent]
class StudentRegistration(BaseModel):
 username:str=Field(min_length=3,max_length=32)
 email:str=Field(min_length=3,max_length=255)
 full_name:str=Field(min_length=1,max_length=150)
 password:str
 @field_validator('username')
 @classmethod
 def validate_username(cls,value):
  value=value.strip().lower()
  if not re.fullmatch(r'[a-z0-9][a-z0-9_.-]{2,31}',value):raise ValueError('Use 3–32 letters, numbers, dots, underscores or hyphens')
  return value
 @field_validator('email')
 @classmethod
 def validate_email(cls,value):
  value=value.strip().lower()
  if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]{2,}',value):raise ValueError('Enter a valid email address')
  return value
 @field_validator('full_name')
 @classmethod
 def validate_full_name(cls,value):
  value=' '.join(value.split())
  if not value:raise ValueError('Full name is required')
  return value
@app.post('/api/v1/auth/login')
def login(b:Login,request:Request,response:Response):
 check_login_rate_limit(request)
 t=tbl('users')
 with engine.connect() as c:u=c.execute(select(t).where((t.c.username==b.username)|(t.c.email==b.username),t.c.is_active==1)).mappings().first()
 if not u:
  record_login_failure(request);raise HTTPException(401,'Invalid username or password')
 try:
  stored=u['password_hash']
  if str(stored).startswith(('$2a$','$2b$','$2y$')):
   if not bcrypt.checkpw(b.password.encode(),str(stored).encode()):raise ValueError()
  else:ph.verify(stored,b.password)
 except Exception:
  record_login_failure(request);raise HTTPException(401,'Invalid username or password')
 clear_login_failures(request)
 try:
  with engine.begin() as c:
   if 'last_login_at' in tbl('users').c:
    c.execute(update(tbl('users')).where(tbl('users').c.id==u['id']).values(last_login_at=now()))
 except SQLAlchemyError:
  logging.warning('Could not update last_login_at for authenticated user')
 return issue_session(dict(u),request,response)
@app.post('/api/v1/auth/register',status_code=201)
def register_guardian(b:GuardianRegistration,request:Request):
 check_registration_rate_limit(request)
 if len(b.password)<12 or len(b.password)>128:raise HTTPException(422,'Password must be between 12 and 128 characters')
 users=tbl('users')
 if 'role' not in users.c or 'password_hash' not in users.c or 'is_active' not in users.c:
  raise HTTPException(503,'Account registration is unavailable with the current database schema')
 try:
  with engine.connect() as c:
   duplicate=c.execute(select(users.c.id).where(or_(users.c.username==b.username,users.c.email==b.email))).first()
  if duplicate:raise HTTPException(409,'An account with this username or email already exists')
  values={'id':str(uuid.uuid4()),'username':b.username,'email':b.email,'full_name':b.full_name,
          'password_hash':ph.hash(b.password),'role':'GUARDIAN','is_active':1,'created_at':now(),'updated_at':now()}
  values={k:v for k,v in values.items() if k in users.c}
  with engine.begin() as c:c.execute(insert(users).values(**values))
 except HTTPException:raise
 except SQLAlchemyError as exc:
  if exc.__class__.__name__=='IntegrityError':raise HTTPException(409,'An account with this username or email already exists')
  logging.error('Guardian registration database failure: %s',type(exc).__name__)
  raise HTTPException(503,'Account registration is temporarily unavailable')
 return {'status':'created','role':'GUARDIAN','message':'Guardian account created. Sign in to continue.'}

@app.post('/api/v1/auth/students',status_code=201)
def register_student(b:StudentRegistration,request:Request,u=Depends(current_user)):
 if u['role']!='GUARDIAN':raise HTTPException(403,'Guardian only')
 if len(b.password)<12 or len(b.password)>128:raise HTTPException(422,'Password must be between 12 and 128 characters')
 users=tbl('users');links=tbl('guardian_student_links')
 with engine.connect() as c:
  duplicate=c.execute(select(users.c.id).where(or_(users.c.username==b.username,users.c.email==b.email))).first()
 if duplicate:raise HTTPException(409,'An account with this username or email already exists')
 student_id=str(uuid.uuid4());link_id=str(uuid.uuid4())
 student_values={'id':student_id,'username':b.username,'email':b.email,'full_name':b.full_name,
                 'password_hash':ph.hash(b.password),'role':'STUDENT','is_active':1,'created_at':now(),'updated_at':now()}
 student_values={k:v for k,v in student_values.items() if k in users.c}
 link_values={'id':link_id,'guardian_id':u['id'],'student_id':student_id,'relationship':'GUARDIAN','is_active':1,'created_at':now()}
 link_values={k:v for k,v in link_values.items() if k in links.c}
 try:
  with engine.begin() as c:
   c.execute(insert(users).values(**student_values))
   c.execute(insert(links).values(**link_values))
   audit_auth_event(c,u['id'],'STUDENT_ACCOUNT_CREATED',student_id,request)
 except SQLAlchemyError as exc:
  if exc.__class__.__name__=='IntegrityError':raise HTTPException(409,'An account with this username or email already exists')
  logging.error('Student account creation database failure: %s',type(exc).__name__)
  raise HTTPException(503,'Student account creation is temporarily unavailable')
 return {'status':'created','role':'STUDENT','student':{'id':student_id,'username':b.username,'email':b.email,'full_name':b.full_name}}
@app.post('/api/v1/auth/refresh')
def refresh_session(request:Request,response:Response,refresh_token:str|None=Cookie(default=None,alias=REFRESH_COOKIE)):
 if not refresh_token:raise HTTPException(401,'Refresh session is required')
 origin=request.headers.get('origin')
 allowed={settings.frontend_origin}
 if settings.app_env.lower() in {'development','dev','test'}:allowed.update({'http://localhost:5173','http://127.0.0.1:5173'})
 if origin and origin not in allowed:raise HTTPException(403,'Origin not allowed')
 try:
  claims=jwt.decode(refresh_token,settings.jwt_secret,algorithms=['HS256'])
  if claims.get('typ')!='refresh' or not claims.get('sid'):raise InvalidTokenError('Invalid refresh token')
 except InvalidTokenError:
  revoke_cookie(response);raise HTTPException(401,'Invalid or expired session')
 sessions=tbl('user_sessions');sid=claims['sid'];reason=None
 next_id=str(uuid.uuid4());next_refresh=token({'id':claims['sub']},next_id,'refresh')
 try:
  with engine.begin() as c:
   row=c.execute(select(sessions).where(sessions.c.id==sid,sessions.c.user_id==claims['sub']).with_for_update()).mappings().first()
   if not row:reason='invalid'
   elif row['revoked_at'] is not None:
    c.execute(update(sessions).where(sessions.c.user_id==claims['sub'],sessions.c.revoked_at.is_(None)).values(revoked_at=now()))
    audit_auth_event(c,claims['sub'],'REFRESH_REUSE_DETECTED',sid,request)
    reason='reuse'
   elif not hmac.compare_digest(str(row['token_hash']),refresh_hash(refresh_token)):reason='invalid'
   elif row['expires_at']<=now():
    c.execute(update(sessions).where(sessions.c.id==sid).values(revoked_at=now()));reason='expired'
   else:
    c.execute(update(sessions).where(sessions.c.id==sid).values(revoked_at=now()))
    c.execute(insert(sessions).values(id=next_id,user_id=claims['sub'],token_hash=refresh_hash(next_refresh),ip_address=request.client.host if request.client else None,user_agent=request.headers.get('user-agent','')[:500] or None,expires_at=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(days=REFRESH_DAYS)).replace(tzinfo=None),revoked_at=None,created_at=now()))
    audit_auth_event(c,claims['sub'],'REFRESH_ROTATED',sid,request)
 except SQLAlchemyError:
  logging.exception('Database error while rotating refresh session')
  revoke_cookie(response);raise HTTPException(503,'Authentication service temporarily unavailable')
 if reason:
  revoke_cookie(response)
  raise HTTPException(401,'Refresh token reuse detected; sign in again' if reason=='reuse' else 'Invalid or expired session')
 with engine.connect() as c:
  user=c.execute(select(tbl('users')).where(tbl('users').c.id==claims['sub'],tbl('users').c.is_active==1)).mappings().first()
 if not user:
  with engine.begin() as c:c.execute(update(sessions).where(sessions.c.id==next_id).values(revoked_at=now()))
  revoke_cookie(response);raise HTTPException(401,'Invalid or expired session')
 set_refresh_cookie(response,next_refresh)
 return {'access_token':token(dict(user),next_id),'token_type':'bearer','expires_in':ACCESS_MINUTES*60}
@app.post('/api/v1/auth/logout')
def logout(request:Request,response:Response,u=Depends(current_user)):
 sessions=tbl('user_sessions')
 with engine.begin() as c:
  c.execute(update(sessions).where(sessions.c.id==u['_session_id'],sessions.c.user_id==u['id'],sessions.c.revoked_at.is_(None)).values(revoked_at=now()))
  audit_auth_event(c,u['id'],'LOGOUT',u['_session_id'],request)
 revoke_cookie(response);return {'status':'logged_out'}
@app.post('/api/v1/auth/logout-all')
def logout_all(request:Request,response:Response,u=Depends(current_user)):
 sessions=tbl('user_sessions')
 with engine.begin() as c:
  c.execute(update(sessions).where(sessions.c.user_id==u['id'],sessions.c.revoked_at.is_(None)).values(revoked_at=now()))
  audit_auth_event(c,u['id'],'LOGOUT_ALL',None,request)
 revoke_cookie(response);return {'status':'all_sessions_logged_out'}
@app.get('/api/v1/auth/me')
def me(u=Depends(current_user)):return {k:u.get(k) for k in ('id','username','email','full_name','role')}
@app.get('/api/v1/relationships')
def relationships(u=Depends(current_user)):
 ids=student_ids(u);t=tbl('users')
 with engine.connect() as c:return [dict(x) for x in c.execute(select(t.c.id,t.c.full_name,t.c.username).where(t.c.id.in_(ids))).mappings()] if ids else []

@app.patch('/api/v1/notifications/{notification_id}/read')
def mark_notification_read(notification_id:str,u=Depends(current_user)):
 t=tbl('notifications')
 with engine.begin() as c:
  row=c.execute(select(t).where(t.c.id==notification_id,t.c.user_id==u['id'])).mappings().first()
  if not row:raise HTTPException(404,'Notification not found')
  c.execute(update(t).where(t.c.id==notification_id,t.c.user_id==u['id']).values(is_read=1,read_at=now()))
 return {'id':notification_id,'is_read':True,'read_at':now()}

@app.post('/api/v1/notifications/read-all')
def mark_notifications_read_all(u=Depends(current_user)):
 t=tbl('notifications')
 timestamp=now()
 with engine.begin() as c:
  c.execute(update(t).where(t.c.user_id==u['id'],t.c.is_read==0).values(is_read=1,read_at=timestamp))
 return {'status':'read','read_at':timestamp}
@app.get('/api/v1/{resource}')
def collection(resource:str,u=Depends(current_user)):
 m={'subjects':'subjects','topics':'topics','schedules':'study_schedules','assignments':'learning_tasks','notes':'learning_notes','sessions':'study_sessions','materials':'learning_materials','quizzes':'quizzes','devices':'devices','policies':'application_policies','website-policies':'website_policies','monitoring-events':'monitoring_events','analytics':'daily_reports'}
 if resource=='notifications':
  t=tbl('notifications')
  with engine.connect() as c:return [dict(x) for x in c.execute(select(t).where(t.c.user_id==u['id']).order_by(t.c.created_at.desc()).limit(100)).mappings()]
 if resource=='topics':
  t=tbl('topics');subjects=tbl('subjects');ids=student_ids(u)
  if not ids:return []
  predicates=[subjects.c.student_id.in_(ids)]
  if 'is_active' in subjects.c:predicates.append(subjects.c.is_active==1)
  with engine.connect() as c:return [dict(x) for x in c.execute(select(t).select_from(t.join(subjects,t.c.subject_id==subjects.c.id)).where(*predicates).limit(100)).mappings()]
 if resource=='materials':
  t=tbl('learning_materials');subjects=tbl('subjects');topics=tbl('topics');ids=student_ids(u)
  if not ids:return []
  subject_ids=select(subjects.c.id).where(subjects.c.student_id.in_(ids))
  if 'is_active' in subjects.c:subject_ids=subject_ids.where(subjects.c.is_active==1)
  conditions=[t.c.subject_id.in_(subject_ids),t.c.topic_id.in_(select(topics.c.id).where(topics.c.subject_id.in_(subject_ids)))]
  if u['role']=='GUARDIAN':conditions.append(t.c.uploaded_by==u['id'])
  with engine.connect() as c:return [dict(x) for x in c.execute(select(t).where(or_(*conditions)).limit(100)).mappings()]
 if resource in {'policies','website-policies'}:
  name='application_policies' if resource=='policies' else 'website_policies';t=tbl(name);devices=tbl('devices');ids=student_ids(u)
  if not ids:return []
  device_ids=select(devices.c.id).where(devices.c.owner_user_id.in_(ids),devices.c.is_active==1)
  conditions=[t.c.device_id.in_(device_ids)]
  if u['role']=='GUARDIAN':conditions.append(t.c.created_by==u['id'])
  with engine.connect() as c:return [dict(x) for x in c.execute(select(t).where(or_(*conditions)).limit(100)).mappings()]
 if resource not in m:raise HTTPException(404,'Unknown resource')
 if resource=='quizzes':
  q=tbl('quizzes');tasks=tbl('learning_tasks');subjects=tbl('subjects');ids=student_ids(u)
  conditions=[q.c.created_by==u['id']] if u['role']=='GUARDIAN' else []
  if ids:
   task_ids=select(tasks.c.id).where(tasks.c.student_id.in_(ids))
   subject_ids=select(subjects.c.id).where(subjects.c.student_id.in_(ids))
   conditions.extend([q.c.task_id.in_(task_ids),q.c.subject_id.in_(subject_ids)])
  if u['role']=='STUDENT':
   links=tbl('guardian_student_links')
   guardian_ids=select(links.c.guardian_id).where(links.c.student_id==u['id'],links.c.is_active==1)
   conditions.append(q.c.created_by.in_(guardian_ids))
  if not conditions:return []
  with engine.connect() as c:
   rows=c.execute(select(q).where(q.c.is_active==1,or_(*conditions)).limit(100)).mappings().all()
   return [dict(r) for r in rows if quiz_is_accessible(u,r,c)]
 return records(m[resource],u,'owner_user_id' if resource=='devices' and u['role']=='GUARDIAN' else 'student_id')
@app.post('/api/v1/subjects')
def create_subject(b:Item,u=Depends(current_user)):
 if u['role']!='GUARDIAN':raise HTTPException(403,'Guardian only')
 sid=student_scope(u,b.data.get('student_id'));t=tbl('subjects');d={k:v for k,v in b.data.items() if k in t.c};d.update(id=str(uuid.uuid4()),student_id=sid,is_active=1,created_at=now(),updated_at=now())
 with engine.begin() as c:c.execute(insert(t).values(**d))
 return d
@app.post('/api/v1/schedules')
def create_schedule(b:Item,u=Depends(current_user)):
 if u['role']!='GUARDIAN':raise HTTPException(403,'Guardian only')
 sid=student_scope(u,b.data.get('student_id'));t=tbl('study_schedules');d={k:v for k,v in b.data.items() if k in t.c}
 require_owned_record('subjects',d.get('subject_id'),sid)
 for field in ('start_at','end_at'):
  if d.get(field):d[field]=utc_datetime(d[field])
 if d.get('start_at') and d.get('end_at') and d['end_at']<=d['start_at']:raise HTTPException(422,'end_at must be later than start_at')
 d.update(id=str(uuid.uuid4()),student_id=sid,created_by=u['id'],created_at=now(),updated_at=now(),is_active=1)
 with engine.begin() as c:c.execute(insert(t).values(**d))
 return d
@app.post('/api/v1/assignments')
def create_assignment(b:Item,u=Depends(current_user)):
 if u['role']!='GUARDIAN':raise HTTPException(403,'Guardian only')
 sid=student_scope(u,b.data.get('student_id'));t=tbl('learning_tasks');d={k:v for k,v in b.data.items() if k in t.c}
 require_owned_record('subjects',d.get('subject_id'),sid);require_owned_record('study_schedules',d.get('schedule_id'),sid)
 d.update(id=str(uuid.uuid4()),student_id=sid,created_by=u['id'],status='TODO',priority=d.get('priority','MEDIUM'),created_at=now(),updated_at=now())
 with engine.begin() as c:c.execute(insert(t).values(**d))
 return d
@app.post('/api/v1/notes')
def create_note(b:Note,u=Depends(current_user)):
 if u['role']!='STUDENT':raise HTTPException(403,'Student only')
 d=b.model_dump();require_owned_record('subjects',d.get('subject_id'),u['id']);require_owned_record('topics',d.get('topic_id'),u['id']);require_owned_record('study_schedules',d.get('schedule_id'),u['id'])
 if d.get('topic_id') and d.get('subject_id'):
  topic=tbl('topics')
  with engine.connect() as c:
   if not c.execute(select(topic.c.id).where(topic.c.id==d['topic_id'],topic.c.subject_id==d['subject_id'])).first():raise HTTPException(422,'topic_id must belong to subject_id')
 d.update(id=str(uuid.uuid4()),student_id=u['id'],analysis_status='PENDING',created_at=now(),updated_at=now())
 with engine.begin() as c:c.execute(insert(tbl('learning_notes')).values(**d))
 return d

@app.get('/api/v1/notes/{note_id}')
def get_note(note_id:str,u=Depends(current_user)):
 if u['role']!='STUDENT':raise HTTPException(403,'Student only')
 return owned_record('learning_notes',note_id,u)

@app.patch('/api/v1/notes/{note_id}')
def patch_note(note_id:str,b:Item,u=Depends(current_user)):
 if u['role']!='STUDENT':raise HTTPException(403,'Student only')
 row=owned_record('learning_notes',note_id,u)
 if row.get('submitted_at'):raise HTTPException(409,'Submitted notes cannot be edited')
 values=validate_patch_fields(b.data,{'title','content','subject_id','topic_id','schedule_id'})
 if 'title' in values and not str(values['title']).strip():raise HTTPException(422,'title is required')
 require_owned_record('subjects',values.get('subject_id',row.get('subject_id')),u['id'])
 require_owned_record('topics',values.get('topic_id',row.get('topic_id')),u['id'])
 require_owned_record('study_schedules',values.get('schedule_id',row.get('schedule_id')),u['id'])
 values['updated_at']=now()
 t=tbl('learning_notes')
 with engine.begin() as c:c.execute(update(t).where(t.c.id==note_id,t.c.student_id==u['id']).values(**values))
 return owned_record('learning_notes',note_id,u)

@app.delete('/api/v1/notes/{note_id}')
def delete_note(note_id:str,u=Depends(current_user)):
 if u['role']!='STUDENT':raise HTTPException(403,'Student only')
 row=owned_record('learning_notes',note_id,u)
 if row.get('submitted_at'):raise HTTPException(409,'Submitted notes cannot be deleted')
 t=tbl('learning_notes')
 with engine.begin() as c:c.execute(t.delete().where(t.c.id==note_id,t.c.student_id==u['id']))
 return {'id':note_id,'status':'DELETED'}

@app.post('/api/v1/materials/upload')
async def upload_material(file:UploadFile=File(...),subject_id:str|None=None,topic_id:str|None=None,student_id:str|None=None,u=Depends(current_user)):
 content=await file.read()
 if len(content)>20*1024*1024:raise HTTPException(413,'FILE_TOO_LARGE')
 name=(file.filename or 'upload').strip()
 suffix=Path(name).suffix.lower()
 allowed={'.pdf','.docx','.doc','.xlsx','.xls','.csv','.txt','.png','.jpg','.jpeg','.webp'}
 if suffix not in allowed:raise HTTPException(415,'FILE_TYPE_NOT_ALLOWED')
 if u['role']=='GUARDIAN':
  sid=student_scope(u,student_id)
 else:
  sid=u['id']
 if subject_id:require_owned_record('subjects',subject_id,sid)
 if topic_id:require_owned_record('topics',topic_id,sid)
 material_id=str(uuid.uuid4())
 storage_root=Path(__file__).resolve().parents[2]/'storage'/'documents'
 storage_root.mkdir(parents=True,exist_ok=True)
 safe_name=f"{material_id}{suffix}"
 stored_path=storage_root/safe_name
 stored_path.write_bytes(content)
 extracted=''
 processing_status='COMPLETED'
 try:
  if suffix=='.txt' or suffix=='.csv':
   extracted=content.decode('utf-8-sig',errors='replace')
  elif suffix=='.pdf':
   from pypdf import PdfReader
   extracted='\n'.join(page.extract_text() or '' for page in PdfReader(io.BytesIO(content)).pages)
  elif suffix=='.docx':
   from docx import Document
   extracted='\n'.join(p.text for p in Document(io.BytesIO(content)).paragraphs)
  elif suffix in {'.png','.jpg','.jpeg','.webp'}:
   extracted=''
   processing_status='BLOCKED_OCR_NOT_CONFIGURED'
  elif suffix in {'.xlsx','.xls'}:
   import openpyxl
   workbook=openpyxl.load_workbook(io.BytesIO(content),read_only=True,data_only=True)
   parts=[]
   for sheet in workbook.worksheets:
    for row in sheet.iter_rows(min_row=1,max_row=min(sheet.max_row,200),values_only=True):
     parts.append('\t'.join('' if value is None else str(value) for value in row))
   extracted='\n'.join(parts)
 except Exception as exc:
  extracted=''
  processing_status='FAILED'
  logging.warning('Material extraction failed: %s',type(exc).__name__)
 material=tbl('learning_materials')
 values={'id':material_id,'subject_id':subject_id,'topic_id':topic_id,'uploaded_by':u['id'],
         'title':Path(name).stem,'description':None,'file_name':name,'file_path':str(stored_path),
         'mime_type':mimetypes.guess_type(name)[0] or 'application/octet-stream','file_size_bytes':len(content),
         'material_type':suffix.lstrip('.').upper(),'extracted_text':extracted or None,
         'processing_status':processing_status,'created_at':now()}
 values={k:v for k,v in values.items() if k in material.c}
 with engine.begin() as c:c.execute(insert(material).values(**values))
 return dict(values)

@app.get('/api/v1/materials/{material_id}/download')
def download_material(material_id:str,u=Depends(current_user)):
 material=owned_record('learning_materials',material_id,u)
 path=Path(str(material.get('file_path') or ''))
 if not path.is_file():raise HTTPException(404,'FILE_NOT_FOUND')
 return FileResponse(path,filename=material.get('file_name') or path.name)

@app.post('/api/v1/timetable/parse-text')
def parse_timetable_text(b:TimetableParse,u=Depends(current_user)):
 sid=student_scope(u,b.student_id) if u['role']=='GUARDIAN' else u['id']
 rows,errors=parse_natural_timetable(b.text)
 today=datetime.date.today()
 preview=[]
 existing_schedules=tbl('study_schedules')
 with engine.connect() as c:
  existing=[dict(r) for r in c.execute(select(existing_schedules).where(existing_schedules.c.student_id==sid,existing_schedules.c.is_active==1)).mappings()]
 for row in rows:
  if row['weekday'] is not None:
   delta=(row['weekday']-today.weekday())%7
   date=today+datetime.timedelta(days=delta)
   row['date']=date.isoformat()
  duplicate=False
  for old in existing:
   old_start=utc_datetime(old.get('start_at'))
   old_end=utc_datetime(old.get('end_at'))
   if row['date'] and old_start and old_end:
    if old_start.date().isoformat()==row['date'] and old_start.strftime('%H:%M')==row['start_at'] and old_end.strftime('%H:%M')==row['end_at']:
     duplicate=True
  row['status']='duplicate' if duplicate else 'ready'
 return {'student_id':sid,'rows':rows,'errors':errors,'duplicate_count':sum(r['status']=='duplicate' for r in rows),'ready_count':sum(r['status']=='ready' for r in rows)}

@app.post('/api/v1/timetable/parse-file')
async def parse_timetable_file(file:UploadFile=File(...),u=Depends(current_user)):
 if u['role']!='GUARDIAN':raise HTTPException(403,'Only Guardian can import a timetable; Student preview is available by text')
 content=await file.read()
 if len(content)>10*1024*1024:raise HTTPException(413,'FILE_TOO_LARGE')
 name=(file.filename or 'upload').lower()
 rows=[];errors=[]
 if name.endswith('.csv'):
  text=content.decode('utf-8-sig')
  reader=csv.DictReader(io.StringIO(text))
  for number,row in enumerate(reader,2):
   title=row.get('title') or row.get('subject') or row.get('Môn') or row.get('subject_name')
   start=row.get('start') or row.get('start_at') or row.get('Bắt đầu') or row.get('Giờ bắt đầu')
   end=row.get('end') or row.get('end_at') or row.get('Kết thúc') or row.get('Giờ kết thúc')
   location=row.get('location') or row.get('room') or row.get('Phòng')
   if not title or not start or not end:
    errors.append({'line':number,'message':'Missing title, start time or end time','source':''})
    continue
   s=parse_clock(start);e=parse_clock(end)
   if not s or not e:
    errors.append({'line':number,'message':'Invalid time','source':''});continue
   weekday_value=row.get('weekday') or row.get('day') or row.get('Thứ') or row.get('Ngày')
   weekday=None
   if weekday_value:
    key=str(weekday_value).strip().lower().replace(' ','')
    weekday=VIETNAMESE_WEEKDAYS.get(key)
   date=row.get('date') or row.get('Ngày học')
   rows.append({'weekday':weekday,'date':date,'title':str(title).strip(),'start_at':f'{s[0]:02d}:{s[1]:02d}','end_at':f'{e[0]:02d}:{e[1]:02d}','location':location,'subject_id':None,'status':'ready'})
 elif name.endswith('.xlsx'):
  try:
   import openpyxl
   workbook=openpyxl.load_workbook(io.BytesIO(content),read_only=True,data_only=True)
   sheet=workbook.active
   headers=[str(c.value).strip().lower() if c.value is not None else '' for c in next(sheet.iter_rows(min_row=sheet.max_row if False else 1,max_row=1))]
   for number,values in enumerate(sheet.iter_rows(min_row=2,values_only=True),2):
    record={headers[i]:str(v).strip() if v is not None else '' for i,v in enumerate(values[:len(headers)])}
    title=record.get('title') or record.get('subject') or record.get('môn') or record.get('subject_name')
    start=record.get('start') or record.get('start_at') or record.get('bắt đầu') or record.get('giờ bắt đầu')
    end=record.get('end') or record.get('end_at') or record.get('kết thúc') or record.get('giờ kết thúc')
    location=record.get('location') or record.get('room') or record.get('phòng')
    if not title or not start or not end:
     errors.append({'line':number,'message':'Missing title, start time or end time','source':''});continue
    s=parse_clock(start);e=parse_clock(end)
    if not s or not e:
     errors.append({'line':number,'message':'Invalid time','source':''});continue
    weekday_value=record.get('weekday') or record.get('day') or record.get('thứ') or record.get('ngày')
    weekday=VIETNAMESE_WEEKDAYS.get(str(weekday_value).strip().lower().replace(' ',''))
    rows.append({'weekday':weekday,'date':record.get('date') or record.get('ngày học'),'title':title,'start_at':f'{s[0]:02d}:{s[1]:02d}','end_at':f'{e[0]:02d}:{e[1]:02d}','location':location,'subject_id':None,'status':'ready'})
  except ImportError:
   raise HTTPException(503,'XLSX parser is not installed')
 elif name.endswith('.txt'):
  text=content.decode('utf-8-sig')
  rows,errors=parse_natural_timetable(text)
 elif name.endswith('.pdf'):
  try:
   from pypdf import PdfReader
   text='\n'.join(page.extract_text() or '' for page in PdfReader(io.BytesIO(content)).pages)
   rows,errors=parse_natural_timetable(text)
  except ImportError:
   raise HTTPException(503,'PDF parser is not installed')
 elif name.endswith('.docx'):
  try:
   from docx import Document
   document=Document(io.BytesIO(content))
   text='\n'.join(p.text for p in document.paragraphs)
   rows,errors=parse_natural_timetable(text)
  except ImportError:
   raise HTTPException(503,'DOCX parser is not installed')
 else:
  raise HTTPException(415,'Unsupported timetable file type')
 return {'rows':rows,'errors':errors,'ready_count':sum(r.get('status')=='ready' for r in rows),'file_name':file.filename}

@app.get('/api/v1/schedules/view')
def schedule_view(date:str,u=Depends(current_user),student_id:str|None=None,view:str='week'):
 if u['role']=='GUARDIAN':
  sid=student_scope(u,student_id)
 else:
  sid=u['id']
 try:
  anchor=datetime.datetime.strptime(date,'%Y-%m-%d').date()
 except ValueError:
  raise HTTPException(422,'Invalid date')
 if view=='day':
  start=anchor;end=anchor
 elif view=='month':
  start=anchor.replace(day=1)
  if start.month==12:end=start.replace(year=start.year+1,month=1)-datetime.timedelta(days=1)
  else:end=start.replace(month=start.month+1)-datetime.timedelta(days=1)
 else:
  start=anchor-datetime.timedelta(days=anchor.weekday());end=start+datetime.timedelta(days=6)
 start_at=datetime.datetime.combine(start,datetime.time.min)
 end_at=datetime.datetime.combine(end+datetime.timedelta(days=1),datetime.time.min)
 schedules=tbl('study_schedules')
 with engine.connect() as c:
  rows=c.execute(select(schedules).where(schedules.c.student_id==sid,schedules.c.is_active==1,schedules.c.start_at>=start_at,schedules.c.start_at<end_at).order_by(schedules.c.start_at.asc())).mappings().all()
 result=[dict(row) for row in rows]
 return {'student_id':sid,'view':view,'start':start.isoformat(),'end':end.isoformat(),'rows':result,'count':len(result)}

@app.post('/api/v1/timetable/import')
def import_timetable(b:TimetableImport,u=Depends(current_user)):
 if u['role']!='GUARDIAN':raise HTTPException(403,'Only Guardian can import timetables')
 sid=student_scope(u,b.student_id)
 schedules=tbl('study_schedules')
 created=0;skipped=0;errors=[]
 with engine.begin() as c:
  for number,row in enumerate(b.rows,1):
   try:
    start_clock=parse_clock(row.start_at);end_clock=parse_clock(row.end_at)
    if not start_clock or not end_clock:raise ValueError('Invalid time')
    if end_clock[0]*60+end_clock[1]<=start_clock[0]*60+start_clock[1]:raise ValueError('End time must be later')
    if row.date:
     day=datetime.date.fromisoformat(row.date)
    elif row.weekday is not None:
     today=datetime.date.today();day=today+datetime.timedelta(days=(row.weekday-today.weekday())%7)
    else:
     raise ValueError('Missing date or weekday')
    start=datetime.datetime.combine(day,datetime.time(start_clock[0],start_clock[1]))
    end=datetime.datetime.combine(day,datetime.time(end_clock[0],end_clock[1]))
    duplicate=c.execute(select(schedules.c.id).where(schedules.c.student_id==sid,schedules.c.start_at==start,schedules.c.end_at==end,schedules.c.is_active==1)).first()
    if duplicate:
     skipped+=1;continue
    if row.subject_id:require_owned_record('subjects',row.subject_id,sid)
    d={'id':str(uuid.uuid4()),'student_id':sid,'subject_id':row.subject_id,'created_by':u['id'],
       'title':row.title.strip(),'study_type':'STUDY','description':None,'location':row.location,
       'start_at':start,'end_at':end,'is_active':1,'created_at':now(),'updated_at':now()}
    d={k:v for k,v in d.items() if k in schedules.c}
    c.execute(insert(schedules).values(**d));created+=1
   except Exception as exc:
    errors.append({'line':number,'message':str(exc)})
 return {'created':created,'skipped':skipped,'errors':errors}
@app.post('/api/v1/study-sessions/start')
def start_session(b:SessionStart,u=Depends(current_user)):
 if u['role']!='STUDENT':raise HTTPException(403,'Student only')
 require_owned_record('study_schedules',b.schedule_id,u['id'])
 t=tbl('study_sessions')
 with engine.connect() as c:
  if c.execute(select(t.c.id).where(t.c.student_id==u['id'],t.c.ended_at.is_(None))).first():raise HTTPException(409,'Study session already active')
 d={'id':str(uuid.uuid4()),'student_id':u['id'],'schedule_id':b.schedule_id,'started_at':now(),'total_duration_seconds':0,'valid_duration_seconds':0,'break_duration_seconds':0,'status':'ACTIVE','session_type':b.session_type,'created_at':now()}
 with engine.begin() as c:c.execute(insert(t).values(**d))
 return d
@app.post('/api/v1/study-sessions/{sid}/finish')
def finish_session(sid:str,b:SessionFinish,u=Depends(current_user)):
 t=tbl('study_sessions')
 with engine.begin() as c:
  r=c.execute(select(t).where(t.c.id==sid,t.c.student_id==u['id'],t.c.ended_at.is_(None))).mappings().first()
  if not r:raise HTTPException(404,'Active session not found')
  sec=max(0,int((now()-r['started_at']).total_seconds()));c.execute(update(t).where(t.c.id==sid).values(ended_at=now(),total_duration_seconds=sec,status='COMPLETED',notes=b.notes))
 return {'id':sid,'elapsed_seconds':sec,'verified_study_seconds':0,'verification':'Requires monitoring evidence'}

@app.get('/api/v1/study-sessions/active')
def active_session(u=Depends(current_user)):
 if u['role']!='STUDENT':raise HTTPException(403,'Student only')
 t=tbl('study_sessions')
 with engine.connect() as c:
  row=c.execute(select(t).where(t.c.student_id==u['id'],t.c.ended_at.is_(None)).order_by(t.c.started_at.desc()).limit(1)).mappings().first()
 return dict(row) if row else None
@app.get('/api/v1/dashboard/{role}')
def dashboard(role:str,u=Depends(current_user)):
 requested_role=role.upper()
 if requested_role not in {'GUARDIAN','STUDENT','PARENT','ADMIN'}:
  raise HTTPException(404,'Unknown dashboard role')
 if requested_role=='ADMIN':
  raise HTTPException(403,'Admin workspace is not implemented')
 if requested_role=='PARENT':requested_role='GUARDIAN'
 if requested_role in {'GUARDIAN','STUDENT'} and u['role']!=requested_role:
  raise HTTPException(403,'Dashboard role does not match authenticated account role')
 ids=student_ids(u)
 if not ids:
  return {'role':u['role'],'student_id':None,'metrics':None,'tasks':[],'schedules':[],'sessions':[],'state':'unverified'}
 sid=student_scope(u)
 with engine.connect() as c:
  t=tbl('learning_tasks');s=tbl('study_sessions'); sch=tbl('study_schedules'); today=datetime.date.today();a=datetime.datetime.combine(today,datetime.time.min);z=a+datetime.timedelta(days=1)
  metrics={'tasks':c.execute(select(func.count()).select_from(t).where(t.c.student_id==sid)).scalar(),'completed_tasks':c.execute(select(func.count()).select_from(t).where(t.c.student_id==sid,t.c.status=='COMPLETED')).scalar(),'sessions_today':c.execute(select(func.count()).select_from(s).where(s.c.student_id==sid,s.c.started_at>=a,s.c.started_at<z)).scalar(),'scheduled_today':c.execute(select(func.count()).select_from(sch).where(sch.c.student_id==sid,sch.c.start_at>=a,sch.c.start_at<z)).scalar()}
 return {'role':u['role'],'student_id':sid,'metrics':metrics,'tasks':records('learning_tasks',u),'schedules':records('study_schedules',u),'sessions':records('study_sessions',u)}
@app.post('/api/v1/quizzes/{qid}/attempts')
def attempt(qid:str,u=Depends(current_user)):
 if u['role']!='STUDENT':raise HTTPException(403,'Student only')
 q=tbl('quizzes')
 with engine.connect() as c:quiz=c.execute(select(q).where(q.c.id==qid,q.c.is_active==1)).mappings().first()
 if not quiz:raise HTTPException(404,'Quiz not found')
 with engine.connect() as c:
  if not quiz_is_accessible(u,quiz,c):raise HTTPException(404,'Quiz not found')
 t=tbl('quiz_attempts')
 with engine.begin() as c:
  n=c.execute(select(func.count()).select_from(t).where(t.c.quiz_id==qid,t.c.student_id==u['id'])).scalar()+1
  if quiz['max_attempts'] and n>quiz['max_attempts']:raise HTTPException(409,'Attempt limit reached')
  d={'id':str(uuid.uuid4()),'quiz_id':qid,'student_id':u['id'],'attempt_number':n,'score':0,'correct_count':0,'total_count':0,'status':'IN_PROGRESS','started_at':now()};c.execute(insert(t).values(**d))
 return d
@app.get('/api/v1/monitoring/status')
def monitoring(u=Depends(current_user)):
 ids=student_ids(u);t=tbl('devices')
 with engine.connect() as c:ds=[dict(x) for x in c.execute(select(t).where(t.c.owner_user_id.in_(ids),t.c.is_active==1)).mappings()] if ids else []
 return {'devices':ds,'state':'connected' if any(d['agent_status']=='CONNECTED' for d in ds) else 'offline_or_unknown'}

@app.post('/api/v1/devices/pair')
def pair_device(b:DevicePairRequest,u=Depends(current_user)):
 if u['role']!='GUARDIAN':raise HTTPException(403,'Guardian only')
 sid=student_scope(u,b.student_id)
 devices=tbl('devices')
 if not {'id','owner_user_id','device_name','device_identifier','is_active','registered_at','updated_at'} <= set(devices.c.keys()):
  raise HTTPException(503,'Device pairing is unavailable with the current database schema')
 with engine.begin() as c:
  existing=c.execute(select(devices).where(devices.c.device_identifier==b.device_identifier,devices.c.is_active==1)).mappings().first()
  if existing:
   if existing['owner_user_id']!=sid:raise HTTPException(409,'Device identifier is already registered to another Student')
   device=dict(existing)
  else:
   device={'id':str(uuid.uuid4()),'owner_user_id':sid,'device_name':b.device_name.strip(),
           'device_identifier':b.device_identifier.strip(),'operating_system':b.operating_system,
           'os_version':b.os_version,'agent_version':'0.1.0','agent_status':'DISCONNECTED',
           'last_heartbeat_at':None,'is_active':1,'registered_at':now(),'updated_at':now()}
   device={k:v for k,v in device.items() if k in devices.c}
   c.execute(insert(devices).values(**device))
 device_token=jwt.encode({'sub':sid,'did':device['id'],'typ':'device','exp':datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(days=365)},settings.jwt_secret,algorithm='HS256')
 return {'device':device,'device_token':device_token}

def decode_device_token(authorization:str|None):
 if not authorization or not authorization.startswith('Bearer '):raise HTTPException(401,'Device authentication required')
 try:
  claims=jwt.decode(authorization[7:],settings.jwt_secret,algorithms=['HS256'])
  if claims.get('typ')!='device' or not claims.get('did') or not claims.get('sub'):raise InvalidTokenError('Invalid device token')
  return claims
 except InvalidTokenError:raise HTTPException(401,'Invalid or expired device token')

@app.post('/api/v1/agent/events/batch')
def agent_event_batch(b:AgentBatch,authorization:str|None=Header(default=None)):
 claims=decode_device_token(authorization)
 devices=tbl('devices');events=tbl('monitoring_events')
 with engine.begin() as c:
  device=c.execute(select(devices).where(devices.c.id==claims['did'],devices.c.owner_user_id==claims['sub'],devices.c.is_active==1)).mappings().first()
  if not device:raise HTTPException(401,'Device is revoked or unregistered')
  now_value=now();heartbeat_seen=False;accepted=0
  for event in b.events:
   if event.event_type not in {'HEARTBEAT','AGENT_STARTED','AGENT_STOPPED','SESSION_STARTED','SESSION_FINISHED','ACTIVITY_SUMMARY'}:
    raise HTTPException(422,'Unsupported agent event type')
   if len(event.event_id)>128 or len(event.event_type)>100:raise HTTPException(422,'Invalid agent event')
   try:
    occurred=utc_datetime(event.occurred_at)
   except (TypeError,ValueError):
    raise HTTPException(422,'Invalid occurred_at')
   if not occurred:occurred=now_value
   session_id=event.payload.get('session_id')
   if session_id:
    study_sessions=tbl('study_sessions')
    session_row=c.execute(select(study_sessions.c.id).where(study_sessions.c.id==session_id,study_sessions.c.student_id==claims['sub'])).first()
    if not session_row:raise HTTPException(422,'session_id is outside the device Student scope')
   values={'id':str(uuid.uuid4()),'student_id':claims['sub'],'device_id':claims['did'],
           'session_id':session_id,
           'event_type':event.event_type,'severity':'INFO',
           'description':event.payload.get('description') if event.payload.get('description') else None,
           'metadata':{'event_id':event.event_id,'agent_version':event.agent_version,**event.payload},
           'occurred_at':occurred}
   values={k:v for k,v in values.items() if k in events.c}
   c.execute(insert(events).values(**values))
   if event.event_type=='HEARTBEAT':heartbeat_seen=True
   accepted+=1
  updates={'last_heartbeat_at':now_value,'agent_status':'CONNECTED','updated_at':now_value}
  if heartbeat_seen:c.execute(update(devices).where(devices.c.id==claims['did']).values(**{k:v for k,v in updates.items() if k in devices.c}))
 return {'status':'accepted','accepted':accepted,'heartbeat':heartbeat_seen,'server_time':now_value.isoformat()}

class QuizSubmission(BaseModel): answers:list[dict]
@app.get('/api/v1/quizzes/{quiz_id}')
def get_quiz(quiz_id:str,u=Depends(current_user)):
 q=tbl('quizzes');questions=tbl('questions');options=tbl('question_options')
 with engine.connect() as c:
  quiz=c.execute(select(q).where(q.c.id==quiz_id,q.c.is_active==1)).mappings().first()
  if not quiz:raise HTTPException(404,'Quiz not found')
  if not quiz_is_accessible(u,quiz,c):raise HTTPException(404,'Quiz not found')
  qs=c.execute(select(questions).where(questions.c.quiz_id==quiz_id).order_by(questions.c.sort_order)).mappings().all();result=[]
  for qrow in qs:
   opts=c.execute(select(options.c.id,options.c.option_text,options.c.option_label,options.c.sort_order).where(options.c.question_id==qrow['id']).order_by(options.c.sort_order)).mappings().all()
   result.append({'id':qrow['id'],'question_text':qrow['question_text'],'question_type':qrow['question_type'],'difficulty':qrow['difficulty'],'points':float(qrow['points']),'options':[dict(o) for o in opts]})
 return {'id':quiz['id'],'title':quiz['title'],'description':quiz['description'],'passing_score':float(quiz['passing_score']),'time_limit_seconds':quiz['time_limit_seconds'],'questions':result}
@app.post('/api/v1/quiz-attempts/{attempt_id}/submit')
def submit_quiz(attempt_id:str,b:QuizSubmission,u=Depends(current_user)):
 if u['role']!='STUDENT':raise HTTPException(403,'Student only')
 attempts=tbl('quiz_attempts');answers_t=tbl('quiz_answers');questions=tbl('questions');options=tbl('question_options')
 with engine.begin() as c:
  a=c.execute(select(attempts).where(attempts.c.id==attempt_id,attempts.c.student_id==u['id']).with_for_update()).mappings().first()
  if not a:raise HTTPException(404,'Quiz attempt not found')
  if a['status']!='IN_PROGRESS':raise HTTPException(409,'Quiz attempt has already been submitted')
  quiz=tbl('quizzes');quiz_row=c.execute(select(quiz).where(quiz.c.id==a['quiz_id'],quiz.c.is_active==1)).mappings().first()
  if not quiz_row or not quiz_is_accessible(u,quiz_row,c):raise HTTPException(404,'Quiz attempt not found')
  qrows=c.execute(select(questions).where(questions.c.quiz_id==a['quiz_id'])).mappings().all();qmap={str(x['id']):x for x in qrows};provided={str(x.get('question_id')):x for x in b.answers}
  if len(provided)!=len(b.answers) or any(qid not in qmap for qid in provided):raise HTTPException(422,'Answers contain duplicate or unknown question IDs')
  points_total=sum(float(x['points']) for x in qrows);awarded=0.0;correct=0
  for qid,q in qmap.items():
   response=provided.get(qid,{});option_id=response.get('selected_option_id');answer_text=response.get('answer_text');is_correct=None;pts=0.0
   if q['question_type'] in ('MULTIPLE_CHOICE','SINGLE_CHOICE','TRUE_FALSE'):
    if option_id:
     opt=c.execute(select(options).where(options.c.id==option_id,options.c.question_id==qid)).mappings().first()
     if not opt:raise HTTPException(422,'Selected option does not belong to its question')
     is_correct=bool(opt['is_correct']);pts=float(q['points']) if is_correct else 0.0
   # Free-response answers are recorded for human review and never auto-scored.
   awarded+=pts;correct+=1 if is_correct else 0
   c.execute(insert(answers_t).values(id=str(uuid.uuid4()),attempt_id=attempt_id,question_id=qid,selected_option_id=option_id,answer_text=answer_text,answer_data=response.get('answer_data'),is_correct=is_correct,awarded_points=pts,answered_at=now()))
  score=round(awarded/points_total*100,2) if points_total else 0
  c.execute(update(attempts).where(attempts.c.id==attempt_id).values(score=score,correct_count=correct,total_count=len(qrows),status='COMPLETED',completed_at=now()))
 passing=float(quiz_row['passing_score'])
 manual_review=any(q['question_type'] not in ('MULTIPLE_CHOICE','SINGLE_CHOICE','TRUE_FALSE') for q in qrows)
 return {'attempt_id':attempt_id,'score':score,'correct_count':correct,'total_count':len(qrows),'passed':None if manual_review else score>=passing,'pending_review':manual_review,'passing_score':passing,'note':'Free-response answers require Guardian review.' if manual_review else None}

@app.post('/api/v1/ai/analyze-note/{note_id}')
async def analyze_note(note_id:str,u=Depends(current_user)):
 from app.services.ai import AIProvider,AIUnavailable
 if u['role']!='STUDENT':raise HTTPException(403,'Student only')
 notes=tbl('learning_notes');analyses=tbl('ai_analyses')
 with engine.connect() as c:note=c.execute(select(notes).where(notes.c.id==note_id,notes.c.student_id==u['id'])).mappings().first()
 if not note:raise HTTPException(404,'Learning note not found')
 if not note['content'] or not note['content'].strip():raise HTTPException(422,'Add note content before requesting analysis')
 provider=AIProvider()
 try:
  raw=await provider.complete_json('You are a careful learning coach. Analyze only the student content supplied. Return JSON with summary, key_concepts, missing_topics, weak_topics, recommendations, formulas. Use cautious language; a missing mention is not proof of missing knowledge.',note['content'])
  parsed=json.loads(raw)
  required=('summary','key_concepts','missing_topics','weak_topics','recommendations','formulas')
  if not isinstance(parsed,dict) or any(k not in parsed for k in required) or not isinstance(parsed['summary'],str) or any(not isinstance(parsed[k],list) for k in required[1:]):raise ValueError('Provider response did not match the analysis schema')
 except AIUnavailable as e:raise HTTPException(503,str(e))
 except Exception as e:raise HTTPException(502,'AI analysis failed validation: '+type(e).__name__)
 d={'id':str(uuid.uuid4()),'note_id':note_id,'summary':str(parsed['summary']),'key_concepts':json.dumps(parsed['key_concepts'],ensure_ascii=False),'missing_topics':json.dumps(parsed['missing_topics'],ensure_ascii=False),'weak_topics':json.dumps(parsed['weak_topics'],ensure_ascii=False),'recommendations':json.dumps(parsed['recommendations'],ensure_ascii=False),'formulas':json.dumps(parsed['formulas'],ensure_ascii=False),'model_name':provider.model,'provider_name':settings.ai_provider or 'configured-compatible-provider','status':'SUCCEEDED','created_at':now()}
 with engine.begin() as c:c.execute(insert(analyses).values(**d));c.execute(update(notes).where(notes.c.id==note_id).values(analysis_status='COMPLETED',submitted_at=now(),updated_at=now()))
 return {'status':'SUCCEEDED','analysis':{k:parsed[k] for k in required}}

def owned_record(table_name,record_id,user):
 t=tbl(table_name);ids=student_ids(user)
 if not ids:raise HTTPException(404,'Record not found')
 with engine.connect() as c:
  if 'student_id' in t.c:
   predicates=[t.c.id==record_id,t.c.student_id.in_(ids)]
   if 'is_active' in t.c:predicates.append(t.c.is_active==1)
   row=c.execute(select(t).where(*predicates)).mappings().first()
  elif table_name=='topics':
   subjects=tbl('subjects')
   predicates=[t.c.id==record_id,subjects.c.student_id.in_(ids)]
   if 'is_active' in subjects.c:predicates.append(subjects.c.is_active==1)
   row=c.execute(select(t).select_from(t.join(subjects,t.c.subject_id==subjects.c.id)).where(*predicates)).mappings().first()
  else:raise HTTPException(422,'Record ownership cannot be verified')
 if not row:raise HTTPException(404,'Record not found')
 return dict(row)

def guardian_required(user):
 if user['role']!='GUARDIAN':raise HTTPException(403,'Guardian only')

def validate_patch_fields(data,allowed):
 unexpected=set(data)-set(allowed)
 if unexpected:raise HTTPException(422,'Unexpected editable fields: '+', '.join(sorted(unexpected)))
 values={k:v for k,v in data.items() if k in allowed}
 if not values:raise HTTPException(422,'No editable fields supplied')
 return values

@app.get('/api/v1/subjects/{subject_id}')
def get_subject(subject_id:str,u=Depends(current_user)):return owned_record('subjects',subject_id,u)

@app.patch('/api/v1/subjects/{subject_id}')
def patch_subject(subject_id:str,b:Item,u=Depends(current_user)):
 guardian_required(u);row=owned_record('subjects',subject_id,u);t=tbl('subjects')
 values=validate_patch_fields(b.data,{'name','description','color','icon'})
 with engine.begin() as c:c.execute(update(t).where(t.c.id==subject_id,t.c.student_id==row['student_id']).values(**values,updated_at=now()))
 return owned_record('subjects',subject_id,u)

@app.delete('/api/v1/subjects/{subject_id}')
def archive_subject(subject_id:str,u=Depends(current_user)):
 guardian_required(u);row=owned_record('subjects',subject_id,u);t=tbl('subjects')
 with engine.begin() as c:c.execute(update(t).where(t.c.id==subject_id,t.c.student_id==row['student_id']).values(is_active=0,updated_at=now()))
 return {'id':subject_id,'status':'ARCHIVED'}

@app.post('/api/v1/topics')
def create_topic(b:Item,u=Depends(current_user)):
 guardian_required(u);t=tbl('topics');subject_id=b.data.get('subject_id')
 subject=owned_record('subjects',subject_id,u)
 editable={k:v for k,v in b.data.items() if k!='subject_id'}
 values=validate_patch_fields(editable,{'name','description','difficulty','parent_topic_id'})
 if not values.get('name'):raise HTTPException(422,'name is required')
 values['subject_id']=subject['id']
 if values.get('parent_topic_id'):
  parent=owned_record('topics',values['parent_topic_id'],u)
  if parent['subject_id']!=subject_id:raise HTTPException(422,'Parent topic must belong to the selected subject')
 values.update(id=str(uuid.uuid4()),created_at=now())
 with engine.begin() as c:c.execute(insert(t).values(**values))
 return values

@app.get('/api/v1/topics/{topic_id}')
def get_topic(topic_id:str,u=Depends(current_user)):return owned_record('topics',topic_id,u)

@app.patch('/api/v1/topics/{topic_id}')
def patch_topic(topic_id:str,b:Item,u=Depends(current_user)):
 guardian_required(u);row=owned_record('topics',topic_id,u);t=tbl('topics')
 values=validate_patch_fields(b.data,{'name','description','difficulty','parent_topic_id'})
 if values.get('parent_topic_id'):
  cursor=values['parent_topic_id'];seen=set()
  while cursor:
   if cursor==topic_id or cursor in seen:raise HTTPException(422,'Topic parent would create a cycle')
   seen.add(cursor);parent=owned_record('topics',cursor,u)
   if parent['subject_id']!=row['subject_id']:raise HTTPException(422,'Parent topic must belong to the same subject')
   cursor=parent.get('parent_topic_id')
 with engine.begin() as c:c.execute(update(t).where(t.c.id==topic_id).values(**values))
 return owned_record('topics',topic_id,u)

@app.get('/api/v1/schedules/{schedule_id}')
def get_schedule(schedule_id:str,u=Depends(current_user)):return owned_record('study_schedules',schedule_id,u)

@app.get('/api/v1/assignments/{task_id}')
def get_assignment(task_id:str,u=Depends(current_user)):
 return owned_record('learning_tasks',task_id,u)

@app.patch('/api/v1/assignments/{task_id}/status')
def update_assignment_status(task_id:str,b:TaskStatusUpdate,u=Depends(current_user)):
 if u['role']!='STUDENT':raise HTTPException(403,'Only students can update assignment progress')
 row=owned_record('learning_tasks',task_id,u)
 status=b.status
 if status not in {'IN_PROGRESS','COMPLETED'}:
  raise HTTPException(422,'Only IN_PROGRESS or COMPLETED is allowed')
 current=row.get('status')
 if current=='COMPLETED':
  raise HTTPException(409,'Task already completed')
 if status=='IN_PROGRESS' and current not in {'TODO','IN_PROGRESS','ASSIGNED'}:
  raise HTTPException(409,'Task cannot be started from its current status')
 if status=='COMPLETED' and current not in {'TODO','IN_PROGRESS','ASSIGNED'}:
  raise HTTPException(409,'Task cannot be completed from its current status')
 values={'status':status,'updated_at':now()}
 if status=='COMPLETED':values['completed_at']=now()
 with engine.begin() as c:
  c.execute(update(tbl('learning_tasks')).where(tbl('learning_tasks').c.id==task_id,tbl('learning_tasks').c.student_id==u['id']).values(**values))
  if status=='COMPLETED' and 'notifications' in metadata.tables:
   notifications=tbl('notifications')
   if 'title' in notifications.c and 'message' in notifications.c and 'notification_type' in notifications.c:
    c.execute(insert(notifications).values(
      id=str(uuid.uuid4()),user_id=row['created_by'],title='Student completed a task',
      message=f"{u['full_name']} completed: {row['title']}",
      notification_type='TASK_COMPLETED',priority='NORMAL',
      related_entity_type='learning_task',related_entity_id=task_id,
      is_read=0,read_at=None,created_at=now()))
 return owned_record('learning_tasks',task_id,u)

@app.patch('/api/v1/schedules/{schedule_id}')
def patch_schedule(schedule_id:str,b:Item,u=Depends(current_user)):
 guardian_required(u);row=owned_record('study_schedules',schedule_id,u);t=tbl('study_schedules')
 values=validate_patch_fields(b.data,{'title','subject_id','study_type','description','location','start_at','end_at','recurrence_rule','reminder_minutes'})
 if 'subject_id' in values:require_owned_record('subjects',values['subject_id'],row['student_id'])
 for field in ('start_at','end_at'):
  if field in values:values[field]=utc_datetime(values[field])
 start=values.get('start_at',row['start_at']);end=values.get('end_at',row['end_at'])
 if start and end and end<=start:raise HTTPException(422,'end_at must be later than start_at')
 values['updated_at']=now()
 with engine.begin() as c:c.execute(update(t).where(t.c.id==schedule_id,t.c.student_id==row['student_id']).values(**values))
 return owned_record('study_schedules',schedule_id,u)

@app.delete('/api/v1/schedules/{schedule_id}')
def archive_schedule(schedule_id:str,u=Depends(current_user)):
 guardian_required(u);row=owned_record('study_schedules',schedule_id,u);t=tbl('study_schedules')
 with engine.begin() as c:c.execute(update(t).where(t.c.id==schedule_id,t.c.student_id==row['student_id']).values(is_active=0,updated_at=now()))
 return {'id':schedule_id,'status':'ARCHIVED'}
