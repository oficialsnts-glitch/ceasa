"""Crop and resize the CEASA icon into PWA-ready sizes."""
from PIL import Image
import os

SRC = "/app/icon-source.png"
OUT_DIR = "/app/icons"
os.makedirs(OUT_DIR, exist_ok=True)

img = Image.open(SRC).convert("RGBA")

# 1) Detect the strongly-colored bounding box (green background of the icon)
rgb = img.convert("RGB")
w, h = rgb.size
px = rgb.load()
min_x, min_y, max_x, max_y = w, h, 0, 0
for y in range(h):
    for x in range(w):
        r, g, b = px[x, y]
        # Consider a pixel part of the icon if not near-white and reasonably saturated
        mx = max(r, g, b); mn = min(r, g, b)
        is_whiteish = (r > 235 and g > 235 and b > 235)
        is_colored = (mx - mn) > 20 or mx < 220
        if is_colored and not is_whiteish:
            if x < min_x: min_x = x
            if y < min_y: min_y = y
            if x > max_x: max_x = x
            if y > max_y: max_y = y

# Add small padding
pad = 2
min_x = max(0, min_x - pad); min_y = max(0, min_y - pad)
max_x = min(w - 1, max_x + pad); max_y = min(h - 1, max_y + pad)

# Make it a square by expanding to the larger dimension
side = max(max_x - min_x, max_y - min_y)
cx = (min_x + max_x) // 2
cy = (min_y + max_y) // 2
half = side // 2 + 2
left = max(0, cx - half); top = max(0, cy - half)
right = min(w, cx + half); bottom = min(h, cy + half)
# force square
size = min(right - left, bottom - top)
right = left + size
bottom = top + size

cropped = img.crop((left, top, right, bottom))
print(f"Cropped bbox: {(left, top, right, bottom)}  size={cropped.size}")

# 2) Resize to standard PWA sizes
sizes = {
    "icon-192.png": 192,
    "icon-256.png": 256,
    "icon-384.png": 384,
    "icon-512.png": 512,
    "apple-touch-icon.png": 180,
    "favicon-32.png": 32,
    "favicon-16.png": 16,
}
for name, sz in sizes.items():
    resized = cropped.resize((sz, sz), Image.LANCZOS)
    resized.save(os.path.join(OUT_DIR, name), optimize=True)
    print(f"Wrote {name} ({sz}x{sz})")

# 3) Maskable icon: pad the icon on a solid emerald background for safe zone
maskable = Image.new("RGBA", (512, 512), (5, 122, 85, 255))  # emerald-700
inner = cropped.resize((360, 360), Image.LANCZOS)  # ~70% safe zone
maskable.paste(inner, ((512 - 360) // 2, (512 - 360) // 2), inner)
maskable.save(os.path.join(OUT_DIR, "maskable-512.png"), optimize=True)
print("Wrote maskable-512.png")

# 4) favicon.ico multi-size
ico_img = cropped.resize((64, 64), Image.LANCZOS)
ico_img.save(os.path.join(OUT_DIR, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
print("Wrote favicon.ico")
