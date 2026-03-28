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
    c.drawString(50, y, "Evidentia Report")
    y -= 30

    for i, r in enumerate(records, 1):

        if y < 100:
            c.showPage()
            y = h - 50

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Incident {i}")
        y -= 20

        c.setFont("Helvetica", 10)

        primary_text = r.get("english_text") or ""

        for line in wrap(primary_text):
            c.drawString(60, y, line)
            y -= 15

        c.drawString(50, y, "Events: " + ", ".join([e["label"] for e in r["events"]]))
        y -= 15

        c.drawString(50, y, "Laws: " + ", ".join(r["laws"]))
        y -= 15

        for s in r["statements"]:
            for line in wrap(s):
                c.drawString(60, y, "- " + line)
                y -= 15

        y -= 20

    c.save()
    return path
