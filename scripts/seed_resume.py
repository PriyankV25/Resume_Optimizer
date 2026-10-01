"""Optional manual seed utility. The web app auto-seeds on first authenticated access."""
import os, json
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
ROOT=Path(__file__).resolve().parents[1]
from backend.services.resume_service import load_seed

url=os.environ['SUPABASE_URL']; key=os.environ['SUPABASE_SERVICE_ROLE_KEY']; email=os.environ['ADMIN_EMAILS'].split(',')[0].strip().lower()
client=create_client(url,key)
users = client.auth.admin.list_users()
user=next((u for u in users if (u.email or '').lower()==email),None)
if not user: raise SystemExit(f'No Supabase Auth user found for {email}')
resume=load_seed()
existing=client.table('resume_configs').select('id').eq('user_id',user.id).limit(1).execute().data
if existing: client.table('resume_configs').update({'resume':resume}).eq('user_id',user.id).execute()
else: client.table('resume_configs').insert({'user_id':user.id,'resume':resume}).execute()
print('Seeded canonical resume for',email)
