import uuid
import hashlib
from types import SimpleNamespace
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, JSON, MetaData, Numeric,
    String, Table, Text, create_engine, select, insert, update, func
)

from app import main as api
from app.core.config import Settings


def define_test_schema(metadata):
    users = Table('users', metadata,
        Column('id', String(36), primary_key=True), Column('username', String(100), unique=True),
        Column('email', String(255), unique=True), Column('password_hash', String(255)),
        Column('full_name', String(150)), Column('role', String(20)),
        Column('is_active', Boolean, nullable=False, default=True))
    user_sessions = Table('user_sessions', metadata,
        Column('id', String(36), primary_key=True), Column('user_id', String(36)),
        Column('token_hash', String(255), unique=True), Column('ip_address', String(45)),
        Column('user_agent', String(500)), Column('expires_at', DateTime),
        Column('revoked_at', DateTime), Column('created_at', DateTime))
    audit_logs = Table('audit_logs', metadata,
        Column('id', String(36), primary_key=True), Column('user_id', String(36)),
        Column('action', String(100)), Column('entity_type', String(100)), Column('entity_id', String(36)),
        Column('old_values', JSON), Column('new_values', JSON), Column('ip_address', String(45)),
        Column('user_agent', String(500)), Column('created_at', DateTime))
    links = Table('guardian_student_links', metadata,
        Column('id', String(36), primary_key=True), Column('guardian_id', String(36)),
        Column('student_id', String(36)), Column('is_active', Boolean))
    subjects = Table('subjects', metadata,
        Column('id', String(36), primary_key=True), Column('student_id', String(36)),
        Column('name', String(150)), Column('description', Text), Column('color', String(20)),
        Column('icon', String(100)), Column('is_active', Boolean),
        Column('created_at', DateTime), Column('updated_at', DateTime))
    Table('topics', metadata,
        Column('id', String(36), primary_key=True), Column('subject_id', String(36)),
        Column('parent_topic_id', String(36)), Column('name', String(200)),
        Column('description', Text), Column('difficulty', String(20)), Column('created_at', DateTime))
    schedules = Table('study_schedules', metadata,
        Column('id', String(36), primary_key=True), Column('student_id', String(36)),
        Column('subject_id', String(36)), Column('created_by', String(36)),
        Column('title', String(200)), Column('study_type', String(30)), Column('description', Text),
        Column('location', String(255)), Column('start_at', DateTime), Column('end_at', DateTime),
        Column('recurrence_rule', JSON), Column('reminder_minutes', Integer), Column('is_active', Boolean),
        Column('created_at', DateTime), Column('updated_at', DateTime))
    tasks = Table('learning_tasks', metadata,
        Column('id', String(36), primary_key=True), Column('student_id', String(36)),
        Column('subject_id', String(36)), Column('schedule_id', String(36)),
        Column('created_by', String(36)), Column('title', String(255)), Column('description', Text),
        Column('priority', String(20)), Column('status', String(30)), Column('due_at', DateTime),
        Column('completed_at', DateTime), Column('estimated_minutes', Integer),
        Column('created_at', DateTime), Column('updated_at', DateTime))
    quizzes = Table('quizzes', metadata,
        Column('id', String(36), primary_key=True), Column('task_id', String(36)),
        Column('subject_id', String(36)), Column('created_by', String(36)), Column('title', String(255)),
        Column('description', Text), Column('difficulty', String(30)), Column('question_count', Integer),
        Column('passing_score', Numeric(5, 2)), Column('time_limit_seconds', Integer),
        Column('max_attempts', Integer), Column('is_mandatory', Boolean), Column('is_active', Boolean),
        Column('created_at', DateTime))
    questions = Table('questions', metadata,
        Column('id', String(36), primary_key=True), Column('quiz_id', String(36)),
        Column('topic_id', String(36)), Column('question_text', Text), Column('question_type', String(30)),
        Column('difficulty', String(20)), Column('explanation', Text), Column('correct_answer', JSON),
        Column('points', Numeric(7, 2)), Column('sort_order', Integer), Column('created_at', DateTime))
    options = Table('question_options', metadata,
        Column('id', String(36), primary_key=True), Column('question_id', String(36)),
        Column('option_text', Text), Column('option_label', String(10)), Column('is_correct', Boolean),
        Column('sort_order', Integer))
    attempts = Table('quiz_attempts', metadata,
        Column('id', String(36), primary_key=True), Column('quiz_id', String(36)),
        Column('student_id', String(36)), Column('attempt_number', Integer), Column('score', Numeric(7, 2)),
        Column('correct_count', Integer), Column('total_count', Integer), Column('status', String(30)),
        Column('started_at', DateTime), Column('completed_at', DateTime))
    answers = Table('quiz_answers', metadata,
        Column('id', String(36), primary_key=True), Column('attempt_id', String(36)),
        Column('question_id', String(36)), Column('selected_option_id', String(36)),
        Column('answer_text', Text), Column('answer_data', JSON), Column('is_correct', Boolean),
        Column('awarded_points', Numeric(7, 2)), Column('answered_at', DateTime))
    sessions = Table('study_sessions', metadata,
        Column('id', String(36), primary_key=True), Column('student_id', String(36)),
        Column('schedule_id', String(36)), Column('device_id', String(36)), Column('started_at', DateTime),
        Column('ended_at', DateTime), Column('total_duration_seconds', Integer),
        Column('valid_duration_seconds', Integer), Column('break_duration_seconds', Integer),
        Column('status', String(30)), Column('session_type', String(30)), Column('notes', Text),
        Column('created_at', DateTime))
    learning_notes = Table('learning_notes', metadata,
        Column('id', String(36), primary_key=True), Column('student_id', String(36)),
        Column('subject_id', String(36)), Column('topic_id', String(36)), Column('schedule_id', String(36)),
        Column('title', String(255)), Column('content', Text), Column('analysis_status', String(30)),
        Column('submitted_at', DateTime), Column('created_at', DateTime), Column('updated_at', DateTime))
    notifications = Table('notifications', metadata,
        Column('id', String(36), primary_key=True), Column('user_id', String(36)),
        Column('title', String(255)), Column('message', Text), Column('notification_type', String(50)),
        Column('priority', String(20)), Column('related_entity_type', String(50)),
        Column('related_entity_id', String(36)), Column('is_read', Boolean),
        Column('read_at', DateTime), Column('created_at', DateTime))
    ai_analyses = Table('ai_analyses', metadata,
        Column('id', String(36), primary_key=True), Column('note_id', String(36)),
        Column('summary', Text), Column('key_concepts', JSON), Column('missing_topics', JSON),
        Column('weak_topics', JSON), Column('recommendations', JSON), Column('formulas', JSON),
        Column('model_name', String(150)), Column('provider_name', String(100)),
        Column('status', String(30)), Column('created_at', DateTime))
    devices = Table('devices', metadata,
        Column('id', String(36), primary_key=True), Column('owner_user_id', String(36)),
        Column('device_name', String(150)), Column('device_identifier', String(255), unique=True),
        Column('operating_system', String(100)), Column('os_version', String(100)),
        Column('agent_version', String(50)), Column('agent_status', String(30)),
        Column('last_heartbeat_at', DateTime), Column('is_active', Boolean),
        Column('registered_at', DateTime), Column('updated_at', DateTime))
    monitoring_events = Table('monitoring_events', metadata,
        Column('id', String(36), primary_key=True), Column('student_id', String(36)),
        Column('device_id', String(36)), Column('session_id', String(36)),
        Column('event_type', String(100)), Column('severity', String(20)),
        Column('description', Text), Column('metadata', JSON), Column('occurred_at', DateTime))
    learning_materials = Table('learning_materials', metadata,
        Column('id', String(36), primary_key=True), Column('subject_id', String(36)),
        Column('topic_id', String(36)), Column('uploaded_by', String(36)),
        Column('title', String(255)), Column('description', Text), Column('file_name', String(255)),
        Column('file_path', String(1000)), Column('mime_type', String(150)), Column('file_size_bytes', Integer),
        Column('material_type', String(50)), Column('extracted_text', Text),
        Column('processing_status', String(30)), Column('created_at', DateTime))
    return {'users': users, 'user_sessions': user_sessions, 'audit_logs': audit_logs, 'guardian_student_links': links, 'subjects': subjects,
            'topics': metadata.tables['topics'], 'study_schedules': schedules,
            'learning_tasks': tasks, 'quizzes': quizzes, 'questions': questions,
            'question_options': options, 'quiz_attempts': attempts,
            'quiz_answers': answers, 'study_sessions': sessions,
            'learning_notes': learning_notes, 'notifications': notifications,
            'ai_analyses': ai_analyses, 'devices': devices,
            'monitoring_events': monitoring_events, 'learning_materials': learning_materials}


@pytest.fixture

def isolated_client(monkeypatch, tmp_path):
    api._login_failures.clear()
    api._login_blocks.clear()
    api._registration_attempts.clear()
    engine = create_engine(f"sqlite:///{tmp_path / 'guardian-test.sqlite3'}")
    metadata = MetaData()
    tables = define_test_schema(metadata)
    metadata.create_all(engine)
    ids = {
        'guardian': 'guardian-1', 'other_guardian': 'guardian-2',
        'student': 'student-1', 'other_student': 'student-2',
        'subject': 'subject-1', 'other_subject': 'subject-2', 'topic': 'topic-1', 'other_topic': 'topic-2',
        'schedule': 'schedule-1', 'other_schedule': 'schedule-2',
        'task': 'task-2', 'quiz': 'quiz-2', 'question': 'question-2',
        'correct_option': 'option-correct', 'wrong_option': 'option-wrong',
    }
    with engine.begin() as conn:
        conn.execute(insert(tables['users']), [
            {'id': ids['guardian'], 'username': 'guardian', 'email': 'g@example.test',
             'password_hash': 'unused', 'full_name': 'Guardian', 'role': 'GUARDIAN', 'is_active': True},
            {'id': ids['other_guardian'], 'username': 'other-guardian', 'email': 'g2@example.test',
             'password_hash': 'unused', 'full_name': 'Other Guardian', 'role': 'GUARDIAN', 'is_active': True},
            {'id': ids['student'], 'username': 'student', 'email': 's@example.test',
             'password_hash': 'unused', 'full_name': 'Student', 'role': 'STUDENT', 'is_active': True},
            {'id': ids['other_student'], 'username': 'other-student', 'email': 's2@example.test',
             'password_hash': 'unused', 'full_name': 'Other Student', 'role': 'STUDENT', 'is_active': True},
        ])
        conn.execute(insert(tables['guardian_student_links']), [
            {'id': 'link-1', 'guardian_id': ids['guardian'], 'student_id': ids['student'], 'is_active': True},
            {'id': 'link-2', 'guardian_id': ids['other_guardian'], 'student_id': ids['other_student'], 'is_active': True},
        ])
        conn.execute(insert(tables['subjects']), [
            {'id': ids['subject'], 'student_id': ids['student'], 'name': 'Math', 'is_active': True},
            {'id': ids['other_subject'], 'student_id': ids['other_student'], 'name': 'Science', 'is_active': True},
        ])
        conn.execute(insert(tables['topics']), [
            {'id': ids['topic'], 'subject_id': ids['subject'], 'name': 'Algebra'},
            {'id': ids['other_topic'], 'subject_id': ids['other_subject'], 'name': 'Chemistry'},
        ])
        conn.execute(insert(tables['study_schedules']), [
            {'id': ids['schedule'], 'student_id': ids['student'], 'created_by': ids['guardian'],
             'title': 'Study', 'study_type': 'SELF_STUDY', 'start_at': datetime(2026, 11, 20, 9),
             'end_at': datetime(2026, 11, 20, 10), 'is_active': True},
            {'id': ids['other_schedule'], 'student_id': ids['other_student'], 'created_by': ids['other_guardian'],
             'title': 'Other study', 'study_type': 'SELF_STUDY', 'start_at': datetime(2026, 11, 20, 9),
             'end_at': datetime(2026, 11, 20, 10), 'is_active': True},
        ])
        conn.execute(insert(tables['learning_tasks']).values(
            id=ids['task'], student_id=ids['other_student'], created_by=ids['other_guardian'],
            title='Other family task', priority='MEDIUM', status='TODO', created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()))
        conn.execute(insert(tables['quizzes']).values(
            id=ids['quiz'], task_id=ids['task'], created_by=ids['other_guardian'], title='Other quiz',
            question_count=1, passing_score=70, max_attempts=2, is_mandatory=True, is_active=True,
            created_at=datetime.utcnow()))
        conn.execute(insert(tables['questions']).values(
            id=ids['question'], quiz_id=ids['quiz'], question_text='Two plus two?',
            question_type='MULTIPLE_CHOICE', points=1, sort_order=0, created_at=datetime.utcnow()))
        conn.execute(insert(tables['question_options']), [
            {'id': ids['correct_option'], 'question_id': ids['question'], 'option_text': '4',
             'option_label': 'A', 'is_correct': True, 'sort_order': 0},
            {'id': ids['wrong_option'], 'question_id': ids['question'], 'option_text': '5',
             'option_label': 'B', 'is_correct': False, 'sort_order': 1},
        ])

    monkeypatch.setattr(api, 'engine', engine)
    monkeypatch.setattr(api, 'metadata', metadata)
    monkeypatch.setattr(api, 'reflect_schema', lambda: sorted(metadata.tables))
    client = TestClient(api.app)
    yield client, ids, engine, tables
    client.close()
    engine.dispose()


def test_guardian_registration_creates_hashed_account_and_can_sign_in(isolated_client):
    client, _, engine, tables = isolated_client
    response = client.post('/api/v1/auth/register', json={
        'username': 'New.Guardian', 'email': '  NEW@example.test ',
        'full_name': '  New   Guardian  ', 'password': 'A secure passphrase 2026',
        'role': 'STUDENT',
    })
    assert response.status_code == 201
    assert response.json()['role'] == 'GUARDIAN'
    with engine.connect() as conn:
        user = conn.execute(select(tables['users']).where(
            tables['users'].c.username == 'new.guardian')).mappings().one()
        assert user['email'] == 'new@example.test'
        assert user['full_name'] == 'New Guardian'
        assert user['role'] == 'GUARDIAN'
        assert user['password_hash'].startswith('$argon2id$')
        assert conn.execute(select(func.count()).select_from(tables['user_sessions'])).scalar_one() == 0
    login = client.post('/api/v1/auth/login', json={
        'username': 'new.guardian', 'password': 'A secure passphrase 2026'})
    assert login.status_code == 200
    assert login.json()['user']['role'] == 'GUARDIAN'

    normalized = client.post('/api/v1/auth/login', json={
        'username': '  NEW.GUARDIAN  ',
        'password': 'A secure passphrase 2026',
    })
    assert normalized.status_code == 200


def test_guardian_can_create_and_link_student_account(isolated_client):
    client, ids, engine, tables = isolated_client
    headers = bearer(ids['guardian'], 'GUARDIAN', engine, tables)
    response = client.post('/api/v1/auth/students', headers=headers, json={
        'username': 'student-account',
        'email': 'student-account@example.test',
        'full_name': 'Student Account',
        'password': 'A secure student passphrase',
    })
    assert response.status_code == 201
    body = response.json()
    assert body['role'] == 'STUDENT'
    student_id = body['student']['id']

    login = client.post('/api/v1/auth/login', json={
        'username': 'student-account',
        'password': 'A secure student passphrase',
    })
    assert login.status_code == 200
    assert login.json()['user']['role'] == 'STUDENT'
    assert login.json()['access_token']

    with engine.connect() as conn:
        link = conn.execute(select(tables['guardian_student_links']).where(
            tables['guardian_student_links'].c.student_id == student_id)).mappings().one()
        assert link['guardian_id'] == ids['guardian']
        assert link['is_active'] is True


def test_student_cannot_create_another_student_account(isolated_client):
    client, ids, engine, tables = isolated_client
    response = client.post('/api/v1/auth/students',
                           headers=bearer(ids['student'], 'STUDENT', engine, tables),
                           json={
                               'username': 'other-student',
                               'email': 'other-student@example.test',
                               'full_name': 'Other Student',
                               'password': 'A secure student passphrase',
                           })
    assert response.status_code == 403


def test_guardian_registration_rejects_duplicate_identity_and_weak_password(isolated_client):
    client, _, engine, tables = isolated_client
    duplicate = client.post('/api/v1/auth/register', json={
        'username': 'guardian', 'email': 'another@example.test',
        'full_name': 'Duplicate', 'password': 'A secure passphrase 2026'})
    assert duplicate.status_code == 409
    weak = client.post('/api/v1/auth/register', json={
        'username': 'new.guardian', 'email': 'new@example.test',
        'full_name': 'New Guardian', 'password': 'short'})
    assert weak.status_code == 422
    assert 'short' not in weak.text
    with engine.connect() as conn:
        assert conn.execute(select(func.count()).select_from(tables['users'])).scalar_one() == 4


def test_forwarded_cloudflare_client_ip_is_used_only_for_loopback_proxy():
    proxied = SimpleNamespace(client=SimpleNamespace(host='127.0.0.1'),
        headers={'cf-connecting-ip': '203.0.113.7'})
    direct = SimpleNamespace(client=SimpleNamespace(host='192.0.2.8'),
        headers={'cf-connecting-ip': '203.0.113.9'})
    assert api.request_ip(proxied) == '203.0.113.7'
    assert api.request_ip(direct) == '192.0.2.8'


def test_unified_error_contract_for_authentication_validation_and_not_found(isolated_client):
    client, _, _, _ = isolated_client

    login = client.post('/api/v1/auth/login', json={
        'username': 'missing-user',
        'password': 'Wrong password',
    }, headers={'Accept-Language': 'vi'})
    assert login.status_code == 401
    login_body = login.json()
    assert login_body['success'] is False
    assert login_body['error']['code'] == 'AUTH_INVALID_CREDENTIALS'
    assert login_body['error']['request_id']
    assert login.headers['X-Request-ID'] == login_body['error']['request_id']
    assert 'Wrong password' not in login.text

    validation = client.post('/api/v1/auth/login', json={}, headers={'Accept-Language': 'en'})
    assert validation.status_code == 422
    validation_body = validation.json()
    assert validation_body['success'] is False
    assert validation_body['error']['code'] == 'VALIDATION_REQUIRED'
    assert all(set(detail) == {'field', 'code'} for detail in validation_body['error']['details'])

    unauthorized = client.get('/api/v1/auth/me', headers={'Accept-Language': 'en'})
    assert unauthorized.status_code == 401
    assert unauthorized.json()['error']['code'] == 'AUTH_UNAUTHORIZED'


def test_guardian_without_linked_student_gets_empty_dashboard(isolated_client):
    client, _, engine, tables = isolated_client
    user_id = 'guardian-no-link'
    with engine.begin() as conn:
        conn.execute(insert(tables['users']).values(
            id=user_id, username='guardian-no-link', email='no-link@example.test',
            password_hash='unused', full_name='Unlinked Guardian',
            role='GUARDIAN', is_active=True))
    response = client.get('/api/v1/dashboard/guardian', headers=bearer(user_id, 'GUARDIAN', engine, tables))
    assert response.status_code == 200
    body = response.json()
    assert body['student_id'] is None
    assert body['tasks'] == []
    assert body['schedules'] == []
    assert body['metrics'] is None
    assert body['state'] == 'unverified'


def test_dashboard_rejects_role_mismatch_and_admin_workspace(isolated_client):
    client, ids, engine, tables = isolated_client
    mismatch = client.get('/api/v1/dashboard/student',
                          headers=bearer(ids['guardian'], 'GUARDIAN', engine, tables))
    assert mismatch.status_code == 403

    admin_id = 'admin-1'
    with engine.begin() as conn:
        conn.execute(insert(tables['users']).values(
            id=admin_id, username='admin', email='admin@example.test',
            password_hash='unused', full_name='Admin',
            role='ADMIN', is_active=True))
    admin = client.get('/api/v1/dashboard/admin',
                       headers=bearer(admin_id, 'ADMIN', engine, tables))
    assert admin.status_code == 403


def test_http_errors_use_localized_stable_envelope_and_request_id(isolated_client):
    client, _, _, _ = isolated_client
    response = client.get('/not-a-real-route', headers={'Accept-Language': 'en-US'})
    body = response.json()
    assert response.status_code == 404
    assert body['success'] is False
    assert body['error']['code'] == 'RESOURCE_NOT_FOUND'
    assert body['error']['message'] == 'The requested item was not found.'
    assert body['error']['request_id'] == response.headers['X-Request-ID']
    assert body['detail'] == body['error']['message']


def test_validation_errors_do_not_echo_submitted_secrets(isolated_client):
    client, _, _, _ = isolated_client
    response = client.post('/api/v1/auth/login', json={'username': 'student', 'password': None})
    body = response.json()
    assert response.status_code == 422
    assert body['success'] is False
    assert body['error']['code'] == 'VALIDATION_INVALID_FORMAT'
    assert body['error']['request_id'] == response.headers['X-Request-ID']
    assert 'input' not in str(body).lower()


def test_unexpected_errors_are_sanitized_and_correlatable(isolated_client):
    client, _, _, _ = isolated_client
    async def fail_for_test():
        raise RuntimeError('private secret path')
    api.app.add_api_route('/__test/unexpected-error', fail_for_test, methods=['GET'])
    try:
        safe_client = TestClient(api.app, raise_server_exceptions=False)
        response = safe_client.get('/__test/unexpected-error')
        safe_client.close()
    finally:
        api.app.router.routes[:] = [route for route in api.app.router.routes if getattr(route, 'path', None) != '/__test/unexpected-error']
    body = response.json()
    assert response.status_code == 500
    assert body['error']['code'] == 'INTERNAL_SERVER_ERROR'
    assert body['error']['request_id'] == response.headers['X-Request-ID']
    assert 'private secret path' not in response.text
    assert 'traceback' not in response.text.lower()


def bearer(user_id, role, engine, tables):
    sid = str(uuid.uuid4())
    with engine.begin() as conn:
        conn.execute(insert(tables['user_sessions']).values(
            id=sid, user_id=user_id, token_hash=hashlib.sha256(uuid.uuid4().hex.encode()).hexdigest(),
            expires_at=datetime.utcnow() + timedelta(days=1), revoked_at=None, created_at=datetime.utcnow()))
    return {'Authorization': f'Bearer {api.token({"id": user_id, "role": role}, sid)}'}


def test_schedule_view_reads_day_week_and_month(isolated_client):
    client, ids, engine, tables = isolated_client
    headers=bearer(ids['guardian'],'GUARDIAN',engine,tables)
    with engine.begin() as conn:
        conn.execute(insert(tables['study_schedules']).values(
            id='view-schedule',student_id=ids['student'],created_by=ids['guardian'],
            title='Viewed schedule',study_type='STUDY',
            start_at=datetime(2026,11,20,7),end_at=datetime(2026,11,20,9),is_active=True,
            created_at=datetime.utcnow(),updated_at=datetime.utcnow()))
    day=client.get('/api/v1/schedules/view',headers=headers,params={
        'date':'2026-11-20','view':'day','student_id':ids['student']})
    assert day.status_code==200
    assert day.json()['count']>=1
    assert any(row['id']=='view-schedule' for row in day.json()['rows'])
    week=client.get('/api/v1/schedules/view',headers=headers,params={
        'date':'2026-11-20','view':'week','student_id':ids['student']})
    assert week.status_code==200
    assert week.json()['count']>=1


def test_guardian_natural_timetable_preview_and_import(isolated_client):
    client, ids, engine, tables = isolated_client
    headers=bearer(ids['guardian'],'GUARDIAN',engine,tables)
    preview=client.post('/api/v1/timetable/parse-text',headers=headers,json={
        'student_id':ids['student'],
        'text':'Thứ 2 học Toán từ 7h đến 9h tại phòng A101.\nThứ 5 học Cơ sở dữ liệu từ 13h30 đến 15h30.'})
    assert preview.status_code==200
    body=preview.json()
    assert len(body['rows'])==2
    assert body['rows'][0]['title']=='Toán'

    result=client.post('/api/v1/timetable/import',headers=headers,json={
        'student_id':ids['student'],'rows':body['rows']})
    assert result.status_code==200
    assert result.json()['created']==2

    repeated=client.post('/api/v1/timetable/import',headers=headers,json={
        'student_id':ids['student'],'rows':body['rows']})
    assert repeated.status_code==200
    assert repeated.json()['created']==0
    assert repeated.json()['skipped']==2


def test_guardian_pair_and_agent_batch_heartbeat(isolated_client):
    client, ids, engine, tables = isolated_client
    guardian_headers=bearer(ids['guardian'],'GUARDIAN',engine,tables)
    paired=client.post('/api/v1/devices/pair',headers=guardian_headers,json={
        'device_name':'Study PC','device_identifier':'device-test-1',
        'operating_system':'Windows','os_version':'11','student_id':ids['student']})
    assert paired.status_code==200
    body=paired.json()
    assert body['device']['owner_user_id']==ids['student']
    assert body['device_token']

    batch=client.post('/api/v1/agent/events/batch',
                      headers={'Authorization':'Bearer '+body['device_token']},
                      json={'events':[{
                          'event_id':'event-1','event_type':'HEARTBEAT',
                          'occurred_at':'2026-11-20T03:30:00Z',
                          'agent_version':'0.1.0','payload':{'os':'Windows','mode':'visible_user_process'}
                      }]})
    assert batch.status_code==200
    assert batch.json()['accepted']==1

    with engine.connect() as conn:
        device=conn.execute(select(tables['devices']).where(tables['devices'].c.id==body['device']['id'])).mappings().one()
        assert device['agent_status']=='CONNECTED'
        event=conn.execute(select(tables['monitoring_events']).where(
            tables['monitoring_events'].c.device_id==body['device']['id'])).mappings().one()
        assert event['student_id']==ids['student']
        assert event['event_type']=='HEARTBEAT'

    with engine.begin() as conn:
        conn.execute(update(tables['devices']).where(tables['devices'].c.id==body['device']['id']).values(is_active=0))
    revoked=client.post('/api/v1/agent/events/batch',
                        headers={'Authorization':'Bearer '+body['device_token']},
                        json={'events':[]})
    assert revoked.status_code==401


def test_student_can_only_start_and_complete_owned_task(isolated_client):
    client, ids, engine, tables = isolated_client
    headers = bearer(ids['student'], 'STUDENT', engine, tables)

    task_id = 'student-task'
    with engine.begin() as conn:
        conn.execute(insert(tables['learning_tasks']).values(
            id=task_id, student_id=ids['student'], created_by=ids['guardian'],
            title='Owned task', priority='HIGH', status='TODO',
            created_at=datetime.utcnow(), updated_at=datetime.utcnow()))

    detail = client.get(f'/api/v1/assignments/{task_id}', headers=headers)
    assert detail.status_code == 200

    started = client.patch(f'/api/v1/assignments/{task_id}/status',
                           headers=headers, json={'status': 'IN_PROGRESS'})
    assert started.status_code == 200
    assert started.json()['status'] == 'IN_PROGRESS'

    completed = client.patch(f'/api/v1/assignments/{task_id}/status',
                             headers=headers, json={'status': 'COMPLETED'})
    assert completed.status_code == 200
    assert completed.json()['status'] == 'COMPLETED'
    assert completed.json()['completed_at']
    with engine.connect() as conn:
        notification = conn.execute(select(tables['notifications']).where(
            tables['notifications'].c.user_id == ids['guardian'],
            tables['notifications'].c.notification_type == 'TASK_COMPLETED')).mappings().first()
        assert notification is not None

    foreign = client.patch('/api/v1/assignments/task-2/status',
                           headers=headers, json={'status': 'IN_PROGRESS'})
    assert foreign.status_code == 404


def test_student_active_session_is_scoped_and_not_cross_user(isolated_client):
    client, ids, engine, tables = isolated_client
    with engine.begin() as conn:
        conn.execute(insert(tables['study_sessions']).values(
            id='active-owned-session', student_id=ids['student'], schedule_id=None,
            started_at=datetime.utcnow(), total_duration_seconds=0,
            valid_duration_seconds=0, break_duration_seconds=0,
            status='ACTIVE', session_type='STUDY', created_at=datetime.utcnow()))
    headers = bearer(ids['student'], 'STUDENT', engine, tables)
    active = client.get('/api/v1/study-sessions/active', headers=headers)
    assert active.status_code == 200
    assert active.json()['id'] == 'active-owned-session'

    other_headers = bearer(ids['other_student'], 'STUDENT', engine, tables)
    other = client.get('/api/v1/study-sessions/active', headers=other_headers)
    assert other.status_code == 200
    assert other.json() is None


def test_student_cannot_read_or_start_unassigned_quiz(isolated_client):
    client, ids, engine, tables = isolated_client
    headers = bearer(ids['student'], 'STUDENT', engine, tables)
    assert client.get(f"/api/v1/quizzes/{ids['quiz']}", headers=headers).status_code == 404
    assert client.post(f"/api/v1/quizzes/{ids['quiz']}/attempts", headers=headers).status_code == 404


def test_guardian_cannot_read_quiz_for_unlinked_student(isolated_client):
    client, ids, engine, tables = isolated_client
    assert client.get(f"/api/v1/quizzes/{ids['quiz']}", headers=bearer(ids['guardian'], 'GUARDIAN', engine, tables)).status_code == 404


def test_guardian_cannot_attach_foreign_subject_to_assignment(isolated_client):
    client, ids, engine, tables = isolated_client
    response = client.post('/api/v1/assignments', headers=bearer(ids['guardian'], 'GUARDIAN', engine, tables), json={
        'data': {'student_id': ids['student'], 'subject_id': ids['other_subject'], 'title': 'Invalid link'}
    })
    assert response.status_code == 404
    with engine.connect() as conn:
        assert conn.execute(select(func.count()).select_from(tables['learning_tasks'])).scalar_one() == 1


def test_student_cannot_start_session_on_foreign_schedule(isolated_client):
    client, ids, engine, tables = isolated_client
    response = client.post('/api/v1/study-sessions/start', headers=bearer(ids['student'], 'STUDENT', engine, tables),
                           json={'schedule_id': ids['other_schedule']})
    assert response.status_code == 404
    with engine.connect() as conn:
        assert conn.execute(select(func.count()).select_from(tables['study_sessions'])).scalar_one() == 0


def test_linked_student_can_read_quiz_without_answer_key(isolated_client):
    client, ids, engine, tables = isolated_client
    with engine.begin() as conn:
        conn.execute(insert(tables['learning_tasks']).values(
            id='task-1', student_id=ids['student'], created_by=ids['guardian'], title='My task',
            priority='MEDIUM', status='TODO', created_at=datetime.utcnow(), updated_at=datetime.utcnow()))
        conn.execute(insert(tables['quizzes']).values(
            id='quiz-1', task_id='task-1', created_by=ids['guardian'], title='My quiz', question_count=1,
            passing_score=70, max_attempts=2, is_mandatory=True, is_active=True, created_at=datetime.utcnow()))
        conn.execute(insert(tables['questions']).values(
            id='question-1', quiz_id='quiz-1', question_text='One plus one?', question_type='MULTIPLE_CHOICE',
            points=1, sort_order=0, created_at=datetime.utcnow()))
        conn.execute(insert(tables['question_options']).values(
            id='option-1', question_id='question-1', option_text='2', option_label='A',
            is_correct=True, sort_order=0))
    response = client.get('/api/v1/quizzes/quiz-1', headers=bearer(ids['student'], 'STUDENT', engine, tables))
    assert response.status_code == 200
    option = response.json()['questions'][0]['options'][0]
    assert option['option_text'] == '2'
    assert 'is_correct' not in option


def test_login_with_invalid_token_is_401(isolated_client):
    client, _, _, _ = isolated_client
    assert client.get('/api/v1/auth/me', headers={'Authorization': 'Bearer not-a-jwt'}).status_code == 401


def test_refresh_rotates_and_reuse_revokes_active_session(isolated_client):
    client, ids, engine, tables = isolated_client
    with engine.begin() as conn:
        conn.execute(tables['users'].update().where(tables['users'].c.id == ids['student']).values(
            password_hash=api.ph.hash('correct horse battery')))
    login = client.post('/api/v1/auth/login', json={'username': 'student', 'password': 'correct horse battery'})
    assert login.status_code == 200
    old_refresh = client.cookies.get(api.REFRESH_COOKIE)
    assert old_refresh
    old_access = login.json()['access_token']
    assert client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {old_access}'}).status_code == 200

    rotated = client.post('/api/v1/auth/refresh')
    assert rotated.status_code == 200
    new_refresh = client.cookies.get(api.REFRESH_COOKIE)
    new_access = rotated.json()['access_token']
    assert new_refresh and new_refresh != old_refresh
    assert client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {old_access}'}).status_code == 401
    assert client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {new_access}'}).status_code == 200

    client.cookies.set(api.REFRESH_COOKIE, old_refresh, path='/api/v1/auth')
    reuse = client.post('/api/v1/auth/refresh')
    assert reuse.status_code == 401
    assert client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {new_access}'}).status_code == 401
    with engine.connect() as conn:
        rows = conn.execute(select(tables['user_sessions']).where(
            tables['user_sessions'].c.user_id == ids['student'])).mappings().all()
    assert rows and all(row['revoked_at'] is not None for row in rows)


def test_logout_revokes_current_access_session(isolated_client):
    client, ids, engine, tables = isolated_client
    with engine.begin() as conn:
        conn.execute(tables['users'].update().where(tables['users'].c.id == ids['student']).values(
            password_hash=api.ph.hash('correct horse battery')))
    login = client.post('/api/v1/auth/login', json={'username': 'student', 'password': 'correct horse battery'})
    assert login.status_code == 200
    access = login.json()['access_token']
    assert client.post('/api/v1/auth/logout', headers={'Authorization': f'Bearer {access}'}).status_code == 200
    assert client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {access}'}).status_code == 401


def test_production_requires_non_placeholder_jwt_secret():
    with pytest.raises(ValueError):
        Settings(_env_file=None, app_env='production')
    with pytest.raises(ValueError):
        Settings(_env_file=None, app_env='production', jwt_secret='replace-with-a-unique-random-secret-of-at-least-32-characters')


def test_development_secret_is_ephemeral_not_a_static_default():
    first = Settings(_env_file=None, app_env='development')
    second = Settings(_env_file=None, app_env='development')
    assert first.jwt_secret and len(first.jwt_secret) >= 32
    assert first.jwt_secret != second.jwt_secret


def test_login_rate_limit_blocks_repeated_failures(isolated_client):
    client, _, _, _ = isolated_client
    api._login_failures.clear()
    api._login_blocks.clear()
    for _ in range(api.LOGIN_MAX_FAILURES):
        response = client.post('/api/v1/auth/login', json={'username': 'student', 'password': 'wrong'})
        assert response.status_code == 401
    blocked = client.post('/api/v1/auth/login', json={'username': 'student', 'password': 'wrong'})
    assert blocked.status_code == 429


def test_topic_list_is_scoped_and_guardian_cannot_create_under_foreign_subject(isolated_client):
    client, ids, engine, tables = isolated_client
    student_headers = bearer(ids['student'], 'STUDENT', engine, tables)
    listed = client.get('/api/v1/topics', headers=student_headers)
    assert listed.status_code == 200
    assert [row['id'] for row in listed.json()] == [ids['topic']]
    guardian_headers = bearer(ids['guardian'], 'GUARDIAN', engine, tables)
    denied = client.post('/api/v1/topics', headers=guardian_headers, json={
        'data': {'subject_id': ids['other_subject'], 'name': 'Unrelated topic'}
    })
    assert denied.status_code == 404
    created = client.post('/api/v1/topics', headers=guardian_headers, json={
        'data': {'subject_id': ids['subject'], 'name': 'Geometry', 'difficulty': 'MEDIUM'}
    })
    assert created.status_code == 200
    assert created.json()['subject_id'] == ids['subject']


def test_subject_archive_hides_it_from_student_collection(isolated_client):
    client, ids, engine, tables = isolated_client
    guardian_headers = bearer(ids['guardian'], 'GUARDIAN', engine, tables)
    response = client.delete(f"/api/v1/subjects/{ids['subject']}", headers=guardian_headers)
    assert response.status_code == 200
    listed = client.get('/api/v1/subjects', headers=bearer(ids['student'], 'STUDENT', engine, tables))
    assert all(row['id'] != ids['subject'] for row in listed.json())
    with engine.connect() as conn:
        assert conn.execute(select(tables['subjects'].c.is_active).where(
            tables['subjects'].c.id == ids['subject'])).scalar_one() is False


def test_student_cannot_patch_guardian_subject(isolated_client):
    client, ids, engine, tables = isolated_client
    response = client.patch(f"/api/v1/subjects/{ids['subject']}",
        headers=bearer(ids['student'], 'STUDENT', engine, tables), json={'data': {'name': 'Changed'}})
    assert response.status_code == 403


def test_guardian_schedule_patch_normalizes_timezone_and_rejects_inverted_range(isolated_client):
    client, ids, engine, tables = isolated_client
    headers = bearer(ids['guardian'], 'GUARDIAN', engine, tables)
    response = client.patch(f"/api/v1/schedules/{ids['schedule']}", headers=headers, json={'data': {
        'start_at': '2026-11-20T10:00:00+07:00', 'end_at': '2026-11-20T11:00:00+07:00'
    }})
    assert response.status_code == 200
    assert response.json()['start_at'].startswith('2026-11-20T03:00:00')
    invalid = client.patch(f"/api/v1/schedules/{ids['schedule']}", headers=headers, json={'data': {
        'start_at': '2026-11-20T14:00:00+07:00', 'end_at': '2026-11-20T13:00:00+07:00'
    }})
    assert invalid.status_code == 422


def test_student_cannot_read_unlinked_subject_detail(isolated_client):
    client, ids, engine, tables = isolated_client
    response = client.get(f"/api/v1/subjects/{ids['other_subject']}",
        headers=bearer(ids['student'], 'STUDENT', engine, tables))
    assert response.status_code == 404


def test_topic_parent_update_cannot_create_cycle(isolated_client):
    client, ids, engine, tables = isolated_client
    with engine.begin() as conn:
        conn.execute(insert(tables['topics']).values(
            id='topic-child', subject_id=ids['subject'], parent_topic_id=ids['topic'], name='Child'))
    response = client.patch(f"/api/v1/topics/{ids['topic']}",
        headers=bearer(ids['guardian'], 'GUARDIAN', engine, tables),
        json={'data': {'parent_topic_id': 'topic-child'}})
    assert response.status_code == 422


def test_auth_audit_records_do_not_contain_tokens_or_passwords(isolated_client):
    client, ids, engine, tables = isolated_client
    with engine.begin() as conn:
        conn.execute(tables['users'].update().where(tables['users'].c.id == ids['student']).values(
            password_hash=api.ph.hash('never-log-this-password')))
    login = client.post('/api/v1/auth/login', json={'username': 'student', 'password': 'never-log-this-password'})
    assert login.status_code == 200
    with engine.connect() as conn:
        row = conn.execute(select(tables['audit_logs']).where(
            tables['audit_logs'].c.user_id == ids['student'])).mappings().one()
    assert row['action'] == 'LOGIN_SUCCEEDED'
    assert row['old_values'] is None and row['new_values'] is None
    assert login.json()['access_token'] not in str(dict(row))
    assert 'never-log-this-password' not in str(dict(row))
