from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Template

from database import connect

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'jobs.sqlite'
DOCS = ROOT / 'docs'

TEMPLATE = Template(r'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>RO Job Searcher</title>
<style>
body{font-family:Arial,sans-serif;margin:0;background:#f4f6f8;color:#1f2937}header{background:#123c2f;color:white;padding:24px}main{max-width:1200px;margin:auto;padding:20px}.controls{display:grid;grid-template-columns:2fr 1fr 1fr;gap:12px;margin-bottom:18px}.card{background:white;border-radius:12px;padding:16px;margin:12px 0;box-shadow:0 2px 8px #0001}.score{font-weight:bold}.high{color:#08783e}.medium{color:#9a6700}.low{color:#a12622}.meta{font-size:.9rem;color:#5b6470}.tag{display:inline-block;background:#e6efeb;border-radius:999px;padding:4px 9px;margin-right:6px;font-size:.8rem}a.button{display:inline-block;background:#123c2f;color:white;text-decoration:none;padding:9px 12px;border-radius:8px;margin-top:10px}@media(max-width:700px){.controls{grid-template-columns:1fr}}
</style>
</head><body><header><h1>RO Job Searcher</h1><p>Radar semiautomático de oportunidades profissionais e de docência</p></header>
<main><div class="controls"><input id="q" placeholder="Buscar cargo, instituição ou palavra-chave"><select id="category"><option value="">Todas as categorias</option><option value="environmental">Meio ambiente e geotecnologias</option><option value="universities">Universidades</option><option value="schools">Colégios</option></select><select id="minscore"><option value="0">Qualquer aderência</option><option value="60">Aderência ≥ 60</option><option value="75">Aderência ≥ 75</option></select></div><div id="summary"></div><div id="jobs"></div></main>
<script>
const jobs={{ jobs_json }};
const esc=s=>(s||'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
function render(){const q=document.querySelector('#q').value.toLowerCase();const cat=document.querySelector('#category').value;const min=+document.querySelector('#minscore').value;const filtered=jobs.filter(j=>(!cat||j.category===cat)&&j.score>=min&&(`${j.title} ${j.organization} ${j.snippet}`).toLowerCase().includes(q)).sort((a,b)=>b.score-a.score);document.querySelector('#summary').innerHTML=`<strong>${filtered.length}</strong> oportunidades exibidas`;document.querySelector('#jobs').innerHTML=filtered.map(j=>`<article class="card"><span class="tag">${esc(j.category)}</span><span class="score ${j.score>=75?'high':j.score>=55?'medium':'low'}">Aderência ${j.score}/100</span><h2>${esc(j.title)}</h2><div class="meta">${esc(j.organization)} · fonte: ${esc(j.source)} · visto em ${esc(j.last_seen.slice(0,10))}</div><p>${esc(j.snippet)}</p><a class="button" href="${esc(j.url)}" target="_blank" rel="noopener">Abrir vaga</a></article>`).join('')||'<p>Nenhuma vaga corresponde aos filtros.</p>'}
['q','category','minscore'].forEach(id=>document.querySelector('#'+id).addEventListener('input',render));render();
</script></body></html>''')


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    connection = connect(DB)
    rows = [dict(row) for row in connection.execute("SELECT * FROM jobs WHERE status != 'discarded' ORDER BY score DESC, last_seen DESC")]
    (DOCS / 'jobs.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    (DOCS / 'index.html').write_text(TEMPLATE.render(jobs_json=json.dumps(rows, ensure_ascii=False)), encoding='utf-8')
    (DOCS / '.nojekyll').write_text('', encoding='utf-8')
    print(f'Dashboard criado com {len(rows)} vagas.')


if __name__ == '__main__':
    main()
