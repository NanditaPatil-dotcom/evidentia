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
    hash_payload = {
        "id": record.get("id"),
        "record": record,
    }
    record_string = json.dumps(hash_payload, sort_keys=True, default=str)
    return hashlib.sha256(record_string.encode()).hexdigest()


def _draw_page_header(c, y):
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "REPORT SUMMARY")
    return y - 25


def _draw_verification_footer(c, page_width):
    footer_text = (
        "This document is a computer-generated evidence report. "
        "The integrity of the data is protected by the digital hash "
        "provided for each entry. For verification, visit Evidentia"
    )
    footer_lines = _wrap_text(footer_text, 100)
    y = 38

    c.line(50, 58, page_width - 50, 58)
    for line in footer_lines:
        c.setFont("Helvetica", 8)
        c.drawString(50, y, line)
        y -= 10


def _wrap_text(value, width=62):
    return [line.strip() for line in wrap(str(value or ""), width) if line.strip()] or [""]


def _build_record_ops(index, record):
    ops = []
    hash_value = generate_hash(record)
    report_id = f"EV-2026-{index:03d}"

    ops.append(("meta", "ID:", report_id))
    ops.append(("meta", "Timestamp:", record["logged_at"]))

    if record.get("coordinates"):
        ops.append(("meta", "Location:", record["coordinates"]))

    statement_value = record.get("statements")
    if isinstance(statement_value, list):
        statement_text = " ".join(statement_value)
    elif isinstance(statement_value, str) and statement_value.strip():
        statement_text = statement_value
    else:
        statement_text = record.get("english_text", "")
    ops.append(("section", "Statement:", _wrap_text(statement_text, 70)))

    for law_line in format_law_lines(record.get("laws")):
        label, value = law_line.split(": ", 1)
        ops.append(("meta", f"{label}:", value))

    accused = record.get("accused_details")
    if accused and accused.get("name"):
        ops.append(("meta", "Accused:", f"{accused['name']} ({accused.get('relation', '')})"))
    else:
        ops.append(("meta", "Accused:", "Not specified"))

    ops.append(("meta", "Attachments:", "Audio_Ref"))
    ops.append(("divider",))
    ops.append(("meta", "Digital Hash:", f"{hash_value[:20]}..."))

    return ops


def _estimate_height(ops, line_height, section_gap):
    height = 0

    for op in ops:
        kind = op[0]
        if kind == "meta":
            value_lines = _wrap_text(op[2], 55)
            height += len(value_lines) * line_height
        elif kind == "section":
            height += line_height
            height += len(op[2]) * line_height
        elif kind == "divider":
            height += line_height

    return height + section_gap


def _draw_meta_row(c, y, label, value, line_height):
    label_x = 50
    value_x = 170
    value_lines = _wrap_text(value, 55)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(label_x, y, label)

    for index, line in enumerate(value_lines):
        c.setFont("Helvetica", 10)
        c.drawString(value_x, y - (index * line_height), line)

    return y - (len(value_lines) * line_height)


def _draw_section(c, y, label, lines, line_height):
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, label)
    y -= line_height

    for line in lines:
        c.setFont("Helvetica", 10)
        c.drawString(60, y, line)
        y -= line_height

    return y


def generate_pdf(records, path):
    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4
    top_y = h - 50
    bottom_margin = 95
    line_height = 15
    section_gap = 20
    y = _draw_page_header(c, top_y)

    for i, r in enumerate(records, 1):
        record_ops = _build_record_ops(i, r)
        required_height = _estimate_height(record_ops, line_height, section_gap)

        if y - required_height < bottom_margin:
            _draw_verification_footer(c, w)
            c.showPage()
            y = _draw_page_header(c, top_y)

        for op in record_ops:
            kind = op[0]
            if kind == "meta":
                y = _draw_meta_row(c, y, op[1], op[2], line_height)
            elif kind == "section":
                y = _draw_section(c, y, op[1], op[2], line_height)
            elif kind == "divider":
                c.line(50, y, 250, y)
                y -= line_height

        c.line(50, y, 550, y)
        y -= 10
        y -= section_gap

    _draw_verification_footer(c, w)
    c.save()
    return path
