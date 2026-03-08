import random
from pathlib import Path
from datetime import date
import pandas as pd
from faker import Faker

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = BASE_DIR / "data" / "input_pdfs"
OUTPUT_DIR = BASE_DIR / "data" / "output"
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

fake = Faker("ro_RO")

LOCALITATI = [
    ("Bucuresti", "Municipiu"),
    ("Cluj-Napoca", "Municipiu"),
    ("Iasi", "Municipiu"),
    ("Timisoara", "Municipiu"),
    ("Constanta", "Municipiu"),
    ("Brasov", "Municipiu"),
    ("Galati", "Municipiu"),
    ("Ploiesti", "Municipiu"),
    ("Suceava", "Municipiu"),
    ("Buzau", "Municipiu"),
    ("Floresti", "Comuna"),
    ("Berceni", "Comuna"),
    ("Mioveni", "Oras"),
    ("Otopeni", "Oras"),
    ("Popesti-Leordeni", "Oras"),
]
JUDETE = ["Bucuresti", "Cluj", "Iasi", "Timis", "Constanta", "Brasov", "Galati", "Prahova", "Suceava", "Buzau"]

def gen_birthdate(year_min=1950, year_max=2006):
    y = random.randint(year_min, year_max)
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    return date(y, m, d)

def cnp_from_birthdate_and_sex(bd: date, sex: str) -> str:
    if bd.year >= 2000:
        s = 5 if sex == "M" else 6
    else:
        s = 1 if sex == "M" else 2

    yy = bd.year % 100
    mm = bd.month
    dd = bd.day
    jj = random.randint(1, 52)
    nnn = random.randint(1, 999)
    c = random.randint(0, 9)
    return f"{s}{yy:02d}{mm:02d}{dd:02d}{jj:02d}{nnn:03d}{c}"

def pick_macos_font():
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/System/Library/Fonts/Supplemental/Verdana.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    return None

def make_text_pdf(path: Path, name: str, cnp: str, locality: str, judet: str):
    c = canvas.Canvas(str(path), pagesize=A4)
    y = A4[1] - 60
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "DECLARATIE PRIVIND PRELUCRAREA DATELOR (DEMO)")
    y -= 30
    c.setFont("Helvetica", 11)
    lines = [
        f"Subsemnatul(a): {name}",
        f"CNP: {cnp}",
        f"Localitatea: {locality}",
        f"Judet: {judet}",
        "",
        "Declar pe propria raspundere ca sunt de acord cu prelucrarea datelor mele",
        "cu caracter personal, in scopuri administrative, conform cerintelor aplicabile.",
        "",
        f"Data: {date.today().isoformat()}",
        "Semnatura: ____________________",
    ]
    for line in lines:
        c.drawString(50, y, line)
        y -= 16
    c.showPage()
    c.save()

def make_scanned_pdf(path: Path, name: str, cnp: str, locality: str, judet: str):
    w, h = 1654, 2339  # ~A4 la ~200dpi
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)

    font_path = pick_macos_font()
    try:
        if font_path:
            font_title = ImageFont.truetype(font_path, 42)
            font_body = ImageFont.truetype(font_path, 30)
        else:
            raise RuntimeError("No mac font found")
    except:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()

    y = 120
    draw.text((120, y), "DECLARATIE PRIVIND PRELUCRAREA DATELOR (SCAN DEMO)", fill="black", font=font_title)
    y += 120

    lines = [
        f"Subsemnatul(a): {name}",
        f"CNP: {cnp}",
        f"Localitatea: {locality}",
        f"Judet: {judet}",
        "",
        "Declar pe propria raspundere ca sunt de acord cu prelucrarea datelor mele",
        "cu caracter personal, in scopuri administrative, conform cerintelor aplicabile.",
        "",
        f"Data: {date.today().isoformat()}",
        "Semnatura: ____________________",
    ]
    for line in lines:
        draw.text((120, y), line, fill="black", font=font_body)
        y += 48

    tmp_img = path.with_suffix(".png")
    img.save(tmp_img)

    c = canvas.Canvas(str(path), pagesize=A4)
    c.drawImage(str(tmp_img), 0, 0, width=A4[0], height=A4[1])
    c.showPage()
    c.save()

    tmp_img.unlink(missing_ok=True)

def generate_dataset(n=50, scanned_ratio=0.5, seed=7):
    random.seed(seed)
    Faker.seed(seed)

    rows = []
    for i in range(1, n + 1):
        name = fake.name()
        sex = random.choice(["M", "F"])
        bd = gen_birthdate()
        cnp = cnp_from_birthdate_and_sex(bd, sex)
        locality, tip = random.choice(LOCALITATI)
        judet = random.choice(JUDETE)

        is_scanned = random.random() < scanned_ratio
        pdf_name = f"{i:03d}_{name.replace(' ', '_')}.pdf"
        pdf_path = INPUT_DIR / pdf_name

        if is_scanned:
            make_scanned_pdf(pdf_path, name, cnp, locality, judet)
            kind = "scanned"
        else:
            make_text_pdf(pdf_path, name, cnp, locality, judet)
            kind = "text"

        rows.append({
            "file": pdf_name,
            "name": name,
            "cnp": cnp,
            "sex_true": sex,
            "birthdate_true": bd.isoformat(),
            "locality": locality,
            "locality_type": tip,
            "judet": judet,
            "pdf_kind": kind
        })

    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "ground_truth.csv", index=False, encoding="utf-8-sig")
    print(f"✅ Am generat {n} PDF-uri în: {INPUT_DIR}")
    print(f"✅ ground_truth.csv: {OUTPUT_DIR / 'ground_truth.csv'}")

if __name__ == "__main__":
    generate_dataset(n=50, scanned_ratio=0.5, seed=7)
