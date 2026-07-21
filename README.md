# RO Job Searcher

Sistema semiautomático de busca e triagem de vagas, configurado para:

1. terceiro setor, carbono florestal, AFOLU, MRV, conservação, restauração, biodiversidade, geoprocessamento, GIS e sensoriamento remoto;
2. docência em universidades particulares da cidade de São Paulo;
3. professor de Biologia no ensino médio em colégios particulares de São Paulo.

## Arquitetura

- **Busca:** DDGS, usando consultas configuráveis em `config/searches.yml`.
- **Banco:** SQLite em `data/jobs.sqlite`.
- **Triagem:** pontuação por palavras-chave e filtros mínimos.
- **Dashboard:** página HTML estática em `docs/index.html`, compatível com GitHub Pages.
- **Alertas:** e-mail por SMTP, configurado com GitHub Secrets.
- **Agendamento:** GitHub Actions às segundas, quartas e sextas, às 08h de São Paulo.

## Instalação local

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python src/search_jobs.py
python src/build_dashboard.py
```

Abra `docs/index.html` no navegador.

## GitHub Pages

No repositório, acesse **Settings → Pages** e selecione:

- Source: `Deploy from a branch`
- Branch: `main`
- Folder: `/docs`

O painel ficará disponível em `https://jomilc.github.io/science/`.

## Alertas por e-mail

Em **Settings → Secrets and variables → Actions**, crie:

- `SMTP_HOST` — por exemplo, `smtp.gmail.com`
- `SMTP_PORT` — normalmente `587`
- `SMTP_USER` — endereço remetente
- `SMTP_PASSWORD` — senha de aplicativo, nunca a senha comum da conta
- `ALERT_EMAIL` — endereço que receberá o relatório

Sem esses segredos, o robô continua funcionando e apenas ignora o envio de e-mail.

## Limitações

A coleta depende de mecanismos de busca públicos. Algumas plataformas bloqueiam indexação ou exigem login. O sistema não envia candidaturas automaticamente e sempre mantém a decisão final com o usuário.
