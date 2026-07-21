from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from database import connect

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'jobs.sqlite'


def main() -> None:
    host = os.getenv('SMTP_HOST')
    user = os.getenv('SMTP_USER')
    password = os.getenv('SMTP_PASSWORD')
    recipient = os.getenv('ALERT_EMAIL')
    port = int(os.getenv('SMTP_PORT', '587'))
    if not all([host, user, password, recipient]):
        print('SMTP não configurado; alerta ignorado.')
        return

    connection = connect(DB)
    rows = connection.execute("SELECT * FROM jobs WHERE status='new' ORDER BY score DESC LIMIT 10").fetchall()
    if not rows:
        print('Sem vagas novas para alertar.')
        return

    lines = ['Novas oportunidades identificadas:', '']
    for row in rows:
        lines += [f"{row['score']}/100 — {row['title']}", row['url'], '']

    msg = EmailMessage()
    msg['Subject'] = f'RO Job Searcher: {len(rows)} novas oportunidades'
    msg['From'] = user
    msg['To'] = recipient
    msg.set_content('\n'.join(lines))

    with smtplib.SMTP(host, port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(msg)
    connection.execute("UPDATE jobs SET status='notified' WHERE status='new'")
    connection.commit()
    print('Alerta enviado.')


if __name__ == '__main__':
    main()
