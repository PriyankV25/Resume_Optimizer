from __future__ import annotations

import copy
import json
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = ROOT / 'seed' / 'priyankDetails.json'


def load_seed() -> dict[str, Any]:
    with SEED_PATH.open(encoding='utf-8') as f:
        source = json.load(f)
    return normalize_resume(source)


def normalize_resume(source: dict[str, Any]) -> dict[str, Any]:
    """Normalize the user's existing JSON shape into the app's canonical schema."""
    data = copy.deepcopy(source)
    basics = data.get('basics', {})
    loc = basics.get('location', {}) or {}
    contact = basics.get('contact', {}) or {}
    contact.setdefault('phone', [])
    skills = data.get('skills', {}) or {}

    normalized = {
        'personal_information': {
            'name': basics.get('name', ''),
            'title': basics.get('title', ''),
            'location': {
                'city': loc.get('city', ''),
                'state': loc.get('state', loc.get('State', '')),
                'country': loc.get('country', ''),
            },
            'contact': contact,
        },
        'professional_summary': {'summary': basics.get('summary', '')},
        'skills': {key: skills.get(key, []) for key in [
            'programming', 'automation', 'devops', 'cloud', 'ai_ml',
            'operating_systems', 'databases', 'tools', 'data_analytics',
            'architecture_and_apis'
        ]},
        'experience': [],
        'projects': [],
        'education': data.get('education', []),
        'certifications': data.get('certifications', []),
        'achievements': data.get('achievements', []),
        'languages': data.get('languages', []),
    }

    for item in data.get('experience', []):
        company = item.get('company', '')
        if isinstance(company, dict):
            company_name = company.get('company_name', '')
            brand = company.get('brand', '')
        else:
            company_name = company
            brand = item.get('brand', '')
        normalized['experience'].append({
            'company': company_name,
            'brand': brand,
            'position': item.get('position', ''),
            'location': item.get('location', ''),
            'employment_type': item.get('employment_type', ''),
            'start_date': item.get('start_date', ''),
            'end_date': item.get('end_date', ''),
            'responsibilities': item.get('responsibilities', item.get('description', [])),
            'achievements': item.get('achievements', []),
        })

    for item in data.get('projects', []):
        highlights = item.get('highlights', [])
        if isinstance(highlights, dict):
            key_caps = highlights.get('key_capabilities', [])
            impact = highlights.get('impact', [])
        else:
            key_caps = highlights
            impact = item.get('impact', [])
        normalized['projects'].append({
            'name': item.get('name', ''),
            'project_type': item.get('project_type', ''),
            'description': item.get('description', []),
            'technical_skills': item.get('technical_skills', []),
            'key_capabilities': key_caps,
            'impact': impact,
            'deployment': item.get('deployment', ''),
            'github': item.get('github', ''),
            'live_url': item.get('live_url', item.get('url', '')),
        })

    return normalized


def resume_to_text(resume: dict[str, Any]) -> str:
    return json.dumps(resume, ensure_ascii=False, indent=2)


def company_from_jd(jd: str) -> str:
    # Kept intentionally conservative: analytics can be enriched by the LLM later.
    for marker in (' at ', ' @ ', 'Company:', 'Company -'):
        if marker in jd:
            tail = jd.split(marker, 1)[1].split('\n', 1)[0].strip()
            if tail:
                return tail[:120]
    return ''


def now_iso() -> str:
    return datetime.utcnow().isoformat() + 'Z'
