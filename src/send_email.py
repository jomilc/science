from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from database import connect

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "jobs.sqlite"


def main() -> None:
    host = (os.getenv("SMTP_HOST") or "").strip()
    user = (os.getenv("SMTP_USER") or "").strip()
    password = os.getenv("SMTP_PASSWORD") or ""
    recipient = (os.getenv("ALERT_EMAIL") or "").strip()

    if not all([host, user, password, recipient]):
        print("SMTP não configurado; alerta por e-mail ignorado.")
        return

    port_text = (os.getenv("SMTP_PORT") or "587").strip()

    try:
        port = int(port_text)
    except ValueError:
        print(
            f"SMTP_PORT inválido: {port_text!r}. "
            "Usando a porta padrão 587."
        )
        port = 587

    connection = connect(DB)

    rows = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE status = 'new'
        ORDER BY score DESC
        LIMIT 10
        """
    ).fetchall()

    if not rows:
        print("Sem vagas novas para alertar.")
        return

    lines = ["Novas oportunidades identificadas:", ""]

    for row in rows:
        lines.extend(
            [
                f"{row['score']}/100 — {row['title']}",
                row["url"],
                "",
            ]
        )

    message = EmailMessage()
    message["Subject"] = (
        f"RO Job Searcher: {len(rows)} novas oportunidades"
    )
    message["From"] = user
    message["To"] = recipient
    message.set_content("\n".join(lines))

    with smtplib.SMTP(host, port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(message)

    connection.execute(
        "UPDATE jobs SET status = 'notified' WHERE status = 'new'"
    )
    connection.commit()

    print("Alerta enviado.")


if __name__ == "__main__":
    main()
