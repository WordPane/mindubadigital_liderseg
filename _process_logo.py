#!/usr/bin/env python3
"""Favicon: icone da logo (branco+dourado) sobre quadrado navy arredondado."""
from PIL import Image, ImageDraw, ImageChops

COLOR = "liderseg/public/assets/logo-liderseg-color.png"
NAVY = (20, 34, 80)  # --color-navy-900

logo = Image.open(COLOR).convert("RGBA")
alpha = logo.split()[3].point(lambda v: 0 if v < 30 else v)

# coluna "ativa" = tem pelo menos 5 px opacos (ignora ruído do JPEG)
hist = alpha.histogram()
cols = []
for x in range(logo.width):
    col = alpha.crop((x, 0, x + 1, logo.height)).histogram()
    cols.append(sum(col[128:]) >= 5)
blocks, start = [], None
for x, on in enumerate(cols + [False]):
    if on and start is None:
        start = x
    elif not on and start is not None:
        blocks.append((start, x))
        start = None
print("blocos:", blocks)
cut = (blocks[0][1] + blocks[1][0]) // 2
icon = logo.crop((0, 0, cut, logo.height))
icon = icon.crop(icon.split()[3].getbbox())
print("ícone:", icon.size)

ir, ig, ib, ia = icon.split()
mask = ImageChops.subtract(ib, ir).point(lambda v: 255 if v > 10 else 0)
icon_w = Image.new("RGBA", icon.size, (255, 255, 255, 255))
icon_w.putalpha(ia)
icon_fg = Image.composite(icon_w, icon, mask)

S = 512
pad = int(S * 0.16)
sq = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(sq)
d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=NAVY + (255,))
fit = icon_fg.copy()
fit.thumbnail((S - 2 * pad, S - 2 * pad), Image.LANCZOS)
sq.paste(fit, ((S - fit.width) // 2, (S - fit.height) // 2), fit)

sq.resize((64, 64), Image.LANCZOS).save("liderseg/public/favicon.png")
sq.save("liderseg/public/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

small = sq.resize((128, 128), Image.LANCZOS)
for name, c in (("light", (240, 240, 240)), ("dark", (30, 30, 30))):
    p = Image.new("RGB", (256, 256), c)
    p.paste(small, (64, 64), small)
    p.save(f"_prev-fav-{name}.png")
print("ok")
