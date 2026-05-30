"""Generate placeholder app icons for the Tauri build.

Produces the four icons Tauri expects under app/src-tauri/icons/:
    32x32.png, 128x128.png, 128x128@2x.png, icon.ico, icon.png

Run from the repo root:
    python app/scripts/gen_icons.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "src-tauri" / "icons"
OUT.mkdir(parents=True, exist_ok=True)

BG = (13, 17, 23, 255)        # dark backdrop
FG = (255, 122, 89, 255)      # accent (markitdown "M")


def _draw(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), BG)
    draw = ImageDraw.Draw(img)
    # Rounded square
    radius = size // 6
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=BG)

    # Stylised "M" via three vertical bars + two diagonals
    bar_w = max(2, size // 12)
    margin = size // 5
    h = size - 2 * margin
    x_left = margin
    x_mid = size // 2
    x_right = size - margin - bar_w
    y_top = margin
    y_bot = margin + h

    draw.rectangle((x_left, y_top, x_left + bar_w, y_bot), fill=FG)
    draw.rectangle((x_right, y_top, x_right + bar_w, y_bot), fill=FG)
    draw.polygon(
        [
            (x_left + bar_w, y_top),
            (x_left + bar_w + max(2, bar_w // 2), y_top),
            (x_mid + bar_w // 2, y_bot - bar_w),
            (x_mid - bar_w // 2, y_bot - bar_w),
        ],
        fill=FG,
    )
    draw.polygon(
        [
            (x_right, y_top),
            (x_right - max(2, bar_w // 2), y_top),
            (x_mid - bar_w // 2, y_bot - bar_w),
            (x_mid + bar_w // 2, y_bot - bar_w),
        ],
        fill=FG,
    )
    return img


def main() -> None:
    master = _draw(512)
    master.save(OUT / "icon.png")
    _draw(32).save(OUT / "32x32.png")
    _draw(128).save(OUT / "128x128.png")
    _draw(256).save(OUT / "128x128@2x.png")

    # ICO with multiple resolutions for crisp Windows display.
    ico_master = _draw(256)
    ico_master.save(
        OUT / "icon.ico",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print(f"wrote icons to {OUT}")


if __name__ == "__main__":
    main()
