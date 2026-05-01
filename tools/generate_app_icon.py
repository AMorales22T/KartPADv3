from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "static"
ASSETS_DIR = ROOT / "assets"


def rounded_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def create_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (8, 12, 24, 255))
    draw = ImageDraw.Draw(img)

    # Background gradient with playful kart energy.
    for y in range(size):
        t = y / max(size - 1, 1)
        r = int(12 + 16 * t)
        g = int(24 + 70 * t)
        b = int(38 + 110 * t)
        draw.line((0, y, size, y), fill=(r, g, b, 255))

    # Diagonal speed streaks.
    for idx, alpha in enumerate((36, 28, 20)):
        offset = int(size * (0.16 + idx * 0.12))
        width = int(size * 0.055)
        draw.polygon(
            [
                (0, offset),
                (int(size * 0.32), offset - width),
                (size, offset + int(size * 0.18)),
                (size, offset + int(size * 0.18) + width),
            ],
            fill=(255, 255, 255, alpha),
        )

    # Glow plate behind the controller.
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse(
        (
            int(size * 0.17),
            int(size * 0.15),
            int(size * 0.83),
            int(size * 0.81),
        ),
        fill=(64, 255, 234, 86),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(radius=max(8, size // 28)))
    img.alpha_composite(glow)

    # Main Wiimote body.
    body_box = (
        int(size * 0.26),
        int(size * 0.12),
        int(size * 0.74),
        int(size * 0.88),
    )
    body_shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(body_shadow)
    rounded_box(
        shadow_draw,
        (body_box[0] + int(size * 0.015), body_box[1] + int(size * 0.02), body_box[2] + int(size * 0.015), body_box[3] + int(size * 0.02)),
        radius=int(size * 0.11),
        fill=(2, 6, 18, 135),
    )
    body_shadow = body_shadow.filter(ImageFilter.GaussianBlur(radius=max(6, size // 64)))
    img.alpha_composite(body_shadow)

    body = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    body_draw = ImageDraw.Draw(body)
    rounded_box(body_draw, body_box, radius=int(size * 0.11), fill=(248, 250, 255, 255), outline=(191, 202, 255, 255), width=max(2, size // 90))
    body_draw.rounded_rectangle(
        (
            int(size * 0.31),
            int(size * 0.16),
            int(size * 0.69),
            int(size * 0.82),
        ),
        radius=int(size * 0.09),
        outline=(221, 229, 255, 255),
        width=max(2, size // 128),
    )
    img.alpha_composite(body)
    draw = ImageDraw.Draw(img)

    # Top sensor slot and LED panel.
    rounded_box(
        draw,
        (
            int(size * 0.39),
            int(size * 0.17),
            int(size * 0.61),
            int(size * 0.205),
        ),
        radius=int(size * 0.016),
        fill=(193, 204, 255, 255),
    )
    rounded_box(
        draw,
        (
            int(size * 0.42),
            int(size * 0.73),
            int(size * 0.58),
            int(size * 0.775),
        ),
        radius=int(size * 0.016),
        fill=(230, 236, 255, 255),
    )

    # D-pad.
    pad_center = (int(size * 0.41), int(size * 0.39))
    pad_color = (66, 96, 255, 255)
    arm = int(size * 0.064)
    thickness = int(size * 0.038)
    rounded_box(draw, (pad_center[0] - thickness // 2, pad_center[1] - arm, pad_center[0] + thickness // 2, pad_center[1] + arm), radius=thickness // 2, fill=pad_color)
    rounded_box(draw, (pad_center[0] - arm, pad_center[1] - thickness // 2, pad_center[0] + arm, pad_center[1] + thickness // 2), radius=thickness // 2, fill=pad_color)
    draw.ellipse(
        (
            pad_center[0] - thickness // 2,
            pad_center[1] - thickness // 2,
            pad_center[0] + thickness // 2,
            pad_center[1] + thickness // 2,
        ),
        fill=(97, 126, 255, 255),
    )

    # A button.
    a_center = (int(size * 0.58), int(size * 0.41))
    a_radius = int(size * 0.078)
    draw.ellipse(
        (
            a_center[0] - a_radius,
            a_center[1] - a_radius,
            a_center[0] + a_radius,
            a_center[1] + a_radius,
        ),
        fill=(0, 214, 194, 255),
        outline=(231, 255, 251, 255),
        width=max(2, size // 85),
    )
    draw.text(
        (a_center[0] - int(size * 0.025), a_center[1] - int(size * 0.04)),
        "A",
        fill=(8, 22, 36, 255),
    )

    # B trigger marker.
    b_center = (int(size * 0.61), int(size * 0.60))
    b_radius = int(size * 0.042)
    draw.ellipse(
        (
            b_center[0] - b_radius,
            b_center[1] - b_radius,
            b_center[0] + b_radius,
            b_center[1] + b_radius,
        ),
        fill=(255, 120, 74, 255),
    )
    draw.text(
        (b_center[0] - int(size * 0.016), b_center[1] - int(size * 0.025)),
        "B",
        fill=(255, 248, 240, 255),
    )

    # Secondary buttons.
    for x in (0.44, 0.51):
        draw.ellipse(
            (
                int(size * x - size * 0.018),
                int(size * 0.55 - size * 0.018),
                int(size * x + size * 0.018),
                int(size * 0.55 + size * 0.018),
            ),
            fill=(204, 212, 246, 255),
        )

    # Player LEDs.
    led_y = int(size * 0.75)
    for i in range(4):
        fill = (0, 244, 211, 255) if i == 0 else (181, 193, 240, 255)
        draw.rounded_rectangle(
            (
                int(size * (0.44 + i * 0.035)),
                led_y,
                int(size * (0.46 + i * 0.035)),
                int(size * 0.773),
            ),
            radius=int(size * 0.008),
            fill=fill,
        )

    # Motion ring.
    ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ring_draw = ImageDraw.Draw(ring)
    ring_draw.arc(
        (
            int(size * 0.12),
            int(size * 0.1),
            int(size * 0.88),
            int(size * 0.86),
        ),
        start=308,
        end=48,
        fill=(255, 208, 74, 255),
        width=max(8, size // 32),
    )
    ring = ring.filter(ImageFilter.GaussianBlur(radius=max(2, size // 120)))
    img.alpha_composite(ring)

    # Fine highlight.
    draw.arc(
        (
            int(size * 0.30),
            int(size * 0.14),
            int(size * 0.70),
            int(size * 0.44),
        ),
        start=180,
        end=340,
        fill=(255, 255, 255, 148),
        width=max(3, size // 140),
    )

    return img


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

    base = create_icon(1024)
    base.save(ASSETS_DIR / "kartpadv3-icon-1024.png")
    base.resize((512, 512), Image.Resampling.LANCZOS).save(STATIC_DIR / "icon-512.png")
    base.resize((192, 192), Image.Resampling.LANCZOS).save(STATIC_DIR / "icon-192.png")
    base.resize((256, 256), Image.Resampling.LANCZOS).save(ASSETS_DIR / "kartpadv3-icon-256.png")
    base.save(
        ASSETS_DIR / "kartpadv3.ico",
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
    )


if __name__ == "__main__":
    main()
