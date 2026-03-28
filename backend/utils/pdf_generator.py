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
    elif ipc_laws:
        lines.append("Relevant Sections: " + ", ".join(ipc_laws))

    if other_laws:
        lines.append("Relevant Sections: " + ", ".join(other_laws))

    if not lines:
        lines.append("Relevant Sections: Not specified")

    return lines


def generate_hash(record):
    record_string = json.dumps(record, sort_keys=True, default=str)
    return hashlib.sha256(record_string.encode()).hexdigest()


def _draw_page_header(c, y):
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "REPORT SUMMARY")
    return y - 25


def _build_record_lines(index, record):
    lines = []
    hash_value = generate_hash(record)
    report_id = f"EV-2026-{index:03d}"

    lines.append(("Helvetica-Bold", 12, f"ID: {report_id}"))
    lines.append(("Helvetica", 10, f"Timestamp: {record['logged_at']}"))

    if record.get("coordinates"):
        lines.append(("Helvetica", 10, f"Location: {record['coordinates']}"))

    lines.append(("Helvetica", 10, "Statement:"))

    statement_lines = record.get("statements") or []
    if statement_lines:
        for statement in statement_lines:
            for line in wrap(statement):
                lines.append(("Helvetica", 10, f"  {line.strip()}"))
    else:
        for line in wrap(record["english_text"]):
            lines.append(("Helvetica", 10, f"  {line.strip()}"))

    for law_line in format_law_lines(record.get("laws")):
        lines.append(("Helvetica", 10, law_line))

    accused = record.get("accused_details")
    if accused and accused.get("name"):
        lines.append(("Helvetica", 10, f"Accused: {accused['name']} ({accused.get('relation', '')})"))
    else:
        lines.append(("Helvetica", 10, "Accused: Not specified"))

    lines.append(("Helvetica", 10, "Attachments: Audio_Ref"))
    lines.append(("Helvetica", 10, "-" * 34))
    lines.append(("Helvetica", 10, f"Digital Hash: {hash_value[:20]}..."))

    return lines


def generate_pdf(records, path):
    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4
    top_y = h - 50
    bottom_margin = 70
    line_height = 15
    section_gap = 20
    y = _draw_page_header(c, top_y)

    for i, r in enumerate(records, 1):
        record_lines = _build_record_lines(i, r)
        required_height = (len(record_lines) * line_height) + section_gap

        if y - required_height < bottom_margin:
            c.showPage()
            y = _draw_page_header(c, top_y)

        for font_name, font_size, text in record_lines:
            c.setFont(font_name, font_size)
            c.drawString(50, y, text)
            y -= line_height

        y -= section_gap

    c.save()
    return path
