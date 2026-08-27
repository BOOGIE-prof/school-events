#!/usr/bin/env python3
"""Генерация иконок приложения из логотипа школы.

    python3 tools/make_icons.py путь/к/логотипу.png

Логотип берётся белый на прозрачном фоне (как исходный файл школы). Скрипт
вырезает эмблему, вписывает её в квадрат фирменного цвета и сохраняет размеры,
которые нужны домашнему экрану телефона и вкладке браузера.

Работает на стандартной библиотеке — Pillow не требуется.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recolor_png import read_png_rgba, write_png_rgba, recolor, crop_emblem  # noqa: E402

BRAND = (0x80, 0x00, 0x80)  # фирменный пурпурный
STATIC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")

# имя файла, размер, доля эмблемы от стороны, фон
ICONS = [
    ("icon-192.png", 192, 0.62, BRAND),
    ("icon-512.png", 512, 0.62, BRAND),
    # maskable: система может обрезать иконку до круга, поэтому эмблема мельче
    ("icon-maskable-512.png", 512, 0.46, BRAND),
    # iOS не поддерживает прозрачность на домашнем экране — фон обязателен
    ("apple-touch-icon.png", 180, 0.62, BRAND),
]


def resize_rgba(width, height, pixels, new_size):
    """Билинейное масштабирование RGBA-картинки в квадрат new_size."""
    out = bytearray(new_size * new_size * 4)
    for y in range(new_size):
        sy = (y + 0.5) * height / new_size - 0.5
        y0 = max(0, min(height - 1, int(sy)))
        y1 = min(height - 1, y0 + 1)
        wy = max(0.0, min(1.0, sy - y0))
        for x in range(new_size):
            sx = (x + 0.5) * width / new_size - 0.5
            x0 = max(0, min(width - 1, int(sx)))
            x1 = min(width - 1, x0 + 1)
            wx = max(0.0, min(1.0, sx - x0))
            d = (y * new_size + x) * 4
            for c in range(4):
                p00 = pixels[(y0 * width + x0) * 4 + c]
                p01 = pixels[(y0 * width + x1) * 4 + c]
                p10 = pixels[(y1 * width + x0) * 4 + c]
                p11 = pixels[(y1 * width + x1) * 4 + c]
                top = p00 + (p01 - p00) * wx
                bottom = p10 + (p11 - p10) * wx
                out[d + c] = int(round(top + (bottom - top) * wy))
    return out


def compose(emblem_size, emblem, canvas_size, background):
    """Кладёт эмблему по центру квадратного холста нужного цвета."""
    r, g, b = background
    canvas = bytearray()
    for _ in range(canvas_size * canvas_size):
        canvas += bytes((r, g, b, 255))

    offset = (canvas_size - emblem_size) // 2
    for y in range(emblem_size):
        for x in range(emblem_size):
            s = (y * emblem_size + x) * 4
            alpha = emblem[s + 3]
            if not alpha:
                continue
            d = ((y + offset) * canvas_size + (x + offset)) * 4
            for c in range(3):
                # обычное альфа-смешивание поверх фона
                canvas[d + c] = (emblem[s + c] * alpha + canvas[d + c] * (255 - alpha)) // 255
    return canvas


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(STATIC, "logo.png")
    width, height, pixels = read_png_rgba(src)
    pixels = recolor(width, height, pixels, (255, 255, 255))  # эмблема белая на цветном фоне
    side, emblem = crop_emblem(width, height, pixels, padding=0.04)
    print(f"эмблема вырезана: {side}×{side} из {width}×{height}")

    for name, size, scale, background in ICONS:
        target = max(1, int(size * scale))
        scaled = resize_rgba(side, side, emblem, target)
        canvas = compose(target, scaled, size, background)
        path = os.path.join(STATIC, name)
        written = write_png_rgba(path, size, size, canvas)
        print(f"  {name}: {size}×{size}, {written // 1024} КБ")


if __name__ == "__main__":
    main()
