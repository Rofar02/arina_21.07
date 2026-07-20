"""
Генерация QR-кодов для квеста + страницы qr-print.html для печати.

Как пользоваться:
1. Когда узнаешь реальные ссылки на quest1.html / quest3.html / quest4.html
   (например, после публикации на хостинге), впиши их вместо плейсхолдеров
   в словаре PAGES ниже.
2. Запусти: python generate_qr.py
3. В папке появятся qr_quest1.png, qr_quest3.png, qr_quest4.png и
   qr-print.html (уже с обновлёнными кодами внутри) — открой его и распечатай.

Сам QR всегда классический чёрно-белый (для надёжного сканирования),
вокруг него — декоративная рамка в цвете соответствующей страницы.
"""

import base64
import io

import qrcode
from PIL import Image, ImageDraw

# ---- страницы квеста: подпись, ссылка (плейсхолдер) и цвета рамки ----
# quest1 (пазл) не получает свой QR — на него ведёт кнопка «Я готова» со start.html
PAGES = {
    "start": {
        "label": "Начало — Поздравление",
        "url": "http://5.129.202.42/start.html",
        "bg": "#fff5f7",     # светло-розовый
        "ring": "#a84568",   # тёмно-розовый
    },
    "quest2": {
        "label": "Шаг 2 — Массаж",
        "url": "http://5.129.202.42/quest2.html",
        "bg": "#fff1e6",     # тёплый персик
        "ring": "#a4506d",   # тёплая марсала
    },
    "quest3": {
        "label": "Шаг 3 — Кафе",
        "url": "http://5.129.202.42/quest3.html",
        "bg": "#f3e4cf",     # тёплый крем
        "ring": "#6f4423",   # эспрессо
    },
    "quest4": {
        "label": "Шаг 4 — Термоленд",
        "url": "http://5.129.202.42/quest4.html",
        "bg": "#dff2f3",     # ледяная бирюза
        "ring": "#1c6e77",   # глубокая бирюза
    },
}

CANVAS_SIZE = 900
RING_WIDTH = 22
INNER_PAD = 40
CORNER_RADIUS = 48


def make_qr_image(url: str) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


def compose(page_key: str, cfg: dict) -> Image.Image:
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), cfg["bg"])
    draw = ImageDraw.Draw(canvas)

    # декоративная рамка (кольцо) в цвете страницы
    draw.rounded_rectangle(
        [(RING_WIDTH // 2, RING_WIDTH // 2),
         (CANVAS_SIZE - RING_WIDTH // 2, CANVAS_SIZE - RING_WIDTH // 2)],
        radius=CORNER_RADIUS,
        outline=cfg["ring"],
        width=RING_WIDTH,
    )

    # белая подложка под сам QR — гарантирует контраст с рамкой/фоном
    white_box = [
        (RING_WIDTH + INNER_PAD, RING_WIDTH + INNER_PAD),
        (CANVAS_SIZE - RING_WIDTH - INNER_PAD, CANVAS_SIZE - RING_WIDTH - INNER_PAD),
    ]
    draw.rounded_rectangle(white_box, radius=CORNER_RADIUS // 2, fill="white")

    qr_img = make_qr_image(cfg["url"])
    inner_size = white_box[1][0] - white_box[0][0] - 2 * INNER_PAD
    qr_img = qr_img.resize((inner_size, inner_size), Image.NEAREST)
    paste_x = (CANVAS_SIZE - inner_size) // 2
    paste_y = (CANVAS_SIZE - inner_size) // 2
    canvas.paste(qr_img, (paste_x, paste_y))

    return canvas


def build_print_page(images_b64: dict) -> str:
    cards = []
    for key, cfg in PAGES.items():
        is_placeholder = cfg["url"].startswith("ССЫЛКА_НА")
        warning = (
            '<div class="warn">⚠ Ссылка ещё не заменена на настоящую</div>'
            if is_placeholder else ""
        )
        cards.append(f"""
      <div class="card" style="--ring:{cfg['ring']};--bg:{cfg['bg']}">
        <div class="label">{cfg['label']}</div>
        <img src="data:image/png;base64,{images_b64[key]}" alt="QR — {cfg['label']}">
        <div class="zoom-hint">🔍 нажми, чтобы увеличить</div>
        <div class="url">{cfg['url']}</div>
        {warning}
      </div>""")

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>QR-коды квеста — для печати</title>
<style>
  *{{box-sizing:border-box;}}
  body{{
    margin:0;
    padding:32px 24px;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;
    background:#fdfdfb;
    color:#333;
    text-align:center;
  }}
  h1{{
    font-size:22px;
    margin:0 0 6px;
  }}
  .subtitle{{
    font-size:14px;
    color:#777;
    margin:0 0 28px;
  }}
  .grid{{
    display:flex;
    flex-wrap:wrap;
    gap:24px;
    justify-content:center;
  }}
  .card{{
    width:280px;
    border:3px solid var(--ring);
    background:var(--bg);
    border-radius:20px;
    padding:18px;
    break-inside:avoid;
  }}
  .label{{
    font-size:16px;
    font-weight:700;
    color:var(--ring);
    margin-bottom:12px;
  }}
  .card img{{
    width:100%;
    height:auto;
    display:block;
    border-radius:12px;
    background:#fff;
    cursor:zoom-in;
    transition:transform .15s ease;
  }}
  .card img:hover{{
    transform:scale(1.03);
  }}
  .zoom-hint{{
    margin-top:8px;
    font-size:11px;
    color:#999;
  }}
  .url{{
    margin-top:6px;
    font-size:11px;
    color:#666;
    word-break:break-all;
  }}
  .warn{{
    margin-top:8px;
    font-size:12px;
    font-weight:700;
    color:#b23b3b;
  }}
  #lightbox{{
    position:fixed;
    inset:0;
    background:rgba(20,20,20,0.85);
    display:none;
    align-items:center;
    justify-content:center;
    z-index:100;
    padding:24px;
    cursor:zoom-out;
  }}
  #lightbox.show{{
    display:flex;
  }}
  #lightbox img{{
    max-width:min(90vw,560px);
    max-height:90vh;
    border-radius:16px;
    box-shadow:0 20px 60px rgba(0,0,0,0.45);
  }}
  @media print{{
    body{{padding:12px;}}
    .subtitle{{display:none;}}
    .zoom-hint{{display:none;}}
    #lightbox{{display:none !important;}}
  }}
</style>
</head>
<body>
  <h1>QR-коды квеста</h1>
  <p class="subtitle">Распечатать и наклеить у зеркала / передать администратору салона и кафе. Нажми на QR, чтобы увеличить его на экране.</p>
  <div class="grid">{"".join(cards)}
  </div>

  <div id="lightbox">
    <img id="lightboxImg" src="" alt="">
  </div>

<script>
  var lightbox = document.getElementById('lightbox');
  var lightboxImg = document.getElementById('lightboxImg');
  document.querySelectorAll('.card img').forEach(function (img) {{
    img.addEventListener('click', function () {{
      lightboxImg.src = img.src;
      lightboxImg.alt = img.alt;
      lightbox.classList.add('show');
    }});
  }});
  lightbox.addEventListener('click', function () {{
    lightbox.classList.remove('show');
  }});
</script>
</body>
</html>
"""


if __name__ == "__main__":
    images_b64 = {}
    for key, cfg in PAGES.items():
        out_path = f"qr_{key}.png"
        img = compose(key, cfg)
        img.save(out_path)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        images_b64[key] = base64.b64encode(buf.getvalue()).decode("ascii")
        print(f"{out_path} -> {cfg['url']}")

    with open("qr-print.html", "w", encoding="utf-8") as f:
        f.write(build_print_page(images_b64))
    print("qr-print.html обновлён")
