import hashlib
import json

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def wrap(text, n=80):
    words = text.split()
    lines, cur = [], ""

    for w in words:
        if len(cur + w) < n:
            cur += w + " "
        else:
            lines.append(cur)
            cur = w + " "
    lines.append(cur)
    return lines


def format_law_lines(laws):
    laws = laws or []
    ipc_laws = [law for law in laws if isinstance(law, str) and law.startswith("IPC")]
    bns_laws = [law for law in laws if isinstance(law, str) and law.startswith("BNS")]
    other_laws = [
        law for law in laws
        if isinstance(law, str) and not law.startswith("IPC") and not law.startswith("BNS")
    ]

    lines = []

    if ipc_laws:
        lines.append("Laws: " + ", ".join(ipc_laws))

    if bns_laws and ipc_laws:
        lines.append(
            "Relevant Sections: "
            + ", ".join(
                f"{law} (formerly {ipc_laws[0]})" if index == 0 else law
                for index, law in enumerate(bns_laws)
            )
        )
    elif bns_laws:
        lines.append("Relevant Sections: " + ", ".join(bns_laws))

    if other_laws:
        label = "Relevant Sections" if lines else "Laws"
        lines.append(f"{label}: " + ", ".join(other_laws))

    if not lines:
        lines.append("Laws: Not specified")

    return lines


def generate_hash(record):
    record_string = json.dumps(record, sort_keys=True, default=str)
    return hashlib.sha256(record_string.encode()).hexdigest()


def generate_pdf(records, path):
    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4

    for i, r in enumerate(records, 1):
        y = h - 50

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "REPORT SUMMARY")
        y -= 25

        hash_value = generate_hash(r)

        report_id = f"EV-2026-{i:03d}"
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"ID: {report_id}")
        y -= 20

        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Timestamp: {r['logged_at']}")
        y -= 15

        if r.get("coordinates"):
            c.drawString(50, y, f"Location: {r['coordinates']}")
            y -= 15

        c.drawString(50, y, "Statement:")
        y -= 15

        statement_lines = r.get("statements") or []
        if statement_lines:
            for statement in statement_lines:
                for line in wrap(statement):
                    c.drawString(60, y, line)
                    y -= 15
        else:
            for line in wrap(r["english_text"]):
                c.drawString(60, y, line)
                y -= 15

        for law_line in format_law_lines(r.get("laws")):
            c.drawString(50, y, law_line)
            y -= 15

        accused = r.get("accused_details")
        if accused and accused.get("name"):
            c.drawString(50, y, f"Accused: {accused['name']} ({accused.get('relation', '')})")
        else:
            c.drawString(50, y, "Accused: Not specified")
        y -= 15

        c.drawString(50, y, "Attachments: Audio_Ref")
        y -= 20

        c.line(50, 65, w - 50, 65)
        c.drawString(50, 50, f"Digital Hash: {hash_value[:20]}...")

        if i < len(records):
            c.showPage()

    c.save()
    return path
