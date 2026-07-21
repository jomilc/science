from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import yaml
from ddgs import DDGS

from database import connect, upsert_jobs

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config' / 'searches.yml'
DB = ROOT / 'data' / 'jobs.sqlite'


def clean(text: str | None) -> str:
    return re.sub(r'\s+', ' ', text or '').strip()


def organization_from_url(url: str) -> str:
    host = urlparse(url).netloc.lower().replace('www.', '')
    return host.split('.')[0].replace('-', ' ').title()


def score_job(text: str, scoring: dict) -> int:
    normalized = text.casefold()
    score = 20
    for keyword, weight in scoring.get('positive_keywords', {}).items():
        if keyword.casefold() in normalized:
            score += int(weight)
    for keyword, weight in scoring.get('negative_keywords', {}).items():
        if keyword.casefold() in normalized:
            score += int(weight)
    return max(0, min(score, 100))


def collect() -> list[dict]:
    cfg = yaml.safe_load(CONFIG.read_text(encoding='utf-8'))
    scoring = cfg['scoring']
    threshold = int(scoring.get('minimum_score', 0))
    now = datetime.now(timezone.utc).isoformat()
    results: list[dict] = []

    with DDGS() as ddgs:
        for category, group in cfg['search_groups'].items():
            for query in group['queries']:
                try:
                    hits = ddgs.text(query, region='br-pt', safesearch='moderate', max_results=12)
                except Exception as exc:
                    print(f'Falha na consulta {query!r}: {exc}')
                    continue
                for hit in hits or []:
                    url = clean(hit.get('href') or hit.get('url'))
                    title = clean(hit.get('title'))
                    snippet = clean(hit.get('body') or hit.get('snippet'))
                    if not url or not title:
                        continue
                    combined = f'{title} {snippet} {query}'
                    score = score_job(combined, scoring)
                    if score < threshold:
                        continue
                    fingerprint = hashlib.sha256(url.rstrip('/').encode('utf-8')).hexdigest()
                    results.append({
                        'fingerprint': fingerprint,
                        'title': title,
                        'organization': organization_from_url(url),
                        'url': url,
                        'snippet': snippet,
                        'source': urlparse(url).netloc,
                        'category': category,
                        'score': score,
                        'first_seen': now,
                        'last_seen': now,
                    })
    return results


def main() -> None:
    jobs = collect()
    connection = connect(DB)
    upsert_jobs(connection, jobs)
    print(f'{len(jobs)} resultados processados.')


if __name__ == '__main__':
    main()
