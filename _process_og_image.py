"""Gera public/assets/og-image.jpg (1200x630) — imagem de compartilhamento social.

Uso: python3 _process_og_image.py
Requer: Pillow. Usa as fontes Poppins self-hosted do projeto.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1200, 630
ROOT = 'liderseg/public'
OUT = f'{ROOT}/assets/og-image.jpg'

NAVY_TOP = (22, 36, 79)      # #16244F
NAVY_BOTTOM = (13, 22, 52)   # #0D1634
GLOW = (43, 62, 125)         # brilho radial atrás do logo
WHITE = (255, 255, 255)
SOFT = (199, 208, 232)       # texto secundário
GOLD = (227, 182, 75)        # #E3B64B


def vertical_gradient(w, h, top, bottom):
    base = Image.new('RGB', (1, h))
    for y in range(h):
        t = y / (h - 1)
        base.putpixel((0, y), tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)))
    return base.resize((w, h))


def radial_glow(w, h, color, alpha, center, radius):
    glow = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(glow)
    d.ellipse(
        [center[0] - radius, center[1] - radius * 0.62,
         center[0] + radius, center[1] + radius * 0.62],
        fill=alpha,
    )
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    layer = Image.new('RGB', (w, h), color)
    return layer, glow


def fit_font(path, text, max_width, start):
    size = start
    while size > 20:
        f = ImageFont.truetype(path, size)
        if d.textlength(text, font=f) <= max_width:
            return f
        size -= 2
    return f


img = vertical_gradient(W, H, NAVY_TOP, NAVY_BOTTOM)

# Brilho radial sutil atrás do logo
layer, mask = radial_glow(W, H, GLOW, 110, (W // 2, 190), 430)
img.paste(layer, (0, 0), mask)

d = ImageDraw.Draw(img)

# --- Logo (versão branca, fundo transparente) ---
logo = Image.open(f'{ROOT}/assets/logo-liderseg.png').convert('RGBA')
logo_w = 440
logo_h = round(logo.height * logo_w / logo.width)
logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
logo_y = 84
img.paste(logo, ((W - logo_w) // 2, logo_y), logo)

# --- Headline: "Receba sua Indenização" + "em caso de Acidente" ---
font800 = 'liderseg/public/fonts/poppins-800.woff2'
font500 = 'liderseg/public/fonts/poppins-500.woff2'

h1a, h1b = 'Receba sua ', 'Indenização'
h2 = 'em caso de Acidente'
f_h1 = fit_font(font800, h1a + h1b, 1040, 68)
f_h2 = fit_font(font800, h2, 1040, 68)

y1 = 300
w1 = d.textlength(h1a, font=f_h1) + d.textlength(h1b, font=f_h1)
x = (W - w1) / 2
d.text((x, y1), h1a, font=f_h1, fill=WHITE)
d.text((x + d.textlength(h1a, font=f_h1), y1), h1b, font=f_h1, fill=GOLD)

y2 = y1 + f_h1.size + 12
d.text(((W - d.textlength(h2, font=f_h2)) / 2, y2), h2, font=f_h2, fill=WHITE)

# --- Subtítulo ---
sub = 'Você só paga se receber'
f_sub = ImageFont.truetype(font500, 30)
d.text(((W - d.textlength(sub, font=f_sub)) / 2, y2 + f_h2.size + 34), sub, font=f_sub, fill=SOFT)

# --- Domínio ---
dom = 'lidersegindenizacoes.com.br'
f_dom = ImageFont.truetype(font500, 24)
d.text(((W - d.textlength(dom, font=f_dom)) / 2, H - 74), dom, font=f_dom, fill=GOLD)

img.save(OUT, 'JPEG', quality=92, optimize=True)
print('OK', OUT, img.size)
