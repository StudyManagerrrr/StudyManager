import httpx
from app.core.config import settings
class AIUnavailable(RuntimeError):pass
class AIProvider:
 def __init__(self):self.key=settings.ai_api_key;self.base=settings.ai_base_url;self.model=settings.ai_model
 async def complete_json(self,system,prompt):
  if not self.key or not self.base or not self.model:raise AIUnavailable('Configure AI_API_KEY, AI_BASE_URL, and AI_MODEL to enable AI analysis.')
  async with httpx.AsyncClient(timeout=90) as c:
   r=await c.post(self.base.rstrip('/')+'/chat/completions',headers={'Authorization':'Bearer '+self.key},json={'model':self.model,'messages':[{'role':'system','content':system},{'role':'user','content':prompt}],'response_format':{'type':'json_object'}})
   r.raise_for_status();return r.json()['choices'][0]['message']['content']
