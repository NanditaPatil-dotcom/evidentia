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


def generate_pdf(records, path):
    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4
    y = h - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "REPORT SUMMARY")
    y -= 25

    for i, r in enumerate(records, 1):

        if y < 120:
            c.showPage()
            y = h - 50

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
        for line in wrap(r["english_text"]):
            c.drawString(60, y, line)
            y -= 15

        c.drawString(50, y, "Legal Classification:")
        y -= 15
        c.drawString(60, y, ", ".join(r["laws"]))
        y -= 15

        accused = r.get("accused_details")
        if accused and accused.get("name"):
            c.drawString(50, y, f"Accused: {accused['name']} ({accused.get('relation', '')})")
        else:
            c.drawString(50, y, "Accused: Not specified")
        y -= 15

        c.drawString(50, y, "Attachments: Audio_Ref")
        y -= 20

    c.save()
    return path
