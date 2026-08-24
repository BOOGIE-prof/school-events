#!/usr/bin/env python3
"""Перекраска PNG с прозрачностью в сплошной цвет (альфа сохраняется).

Работает на стандартной библиотеке — ни Pillow, ни других пакетов не нужно.
Поддерживает 8-битные RGBA-файлы без чересстрочности (colorType=6, interlace=0).

    python3 tools/recolor_png.py вход.png выход.png [--color 000000] [--emblem иконка.png]

--emblem дополнительно вырезает левый графический блок (эмблему) в квадрат:
из широкого логотипа получается иконка, читаемая в 32 пикселя.
"""

import argparse
import struct
import sys
import zlib


def read_png_rgba(path):
    raw = open(path, "rb").read()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"{path}: это не PNG")

    header, idat = None, bytearray()
    pos = 8
    while pos < len(raw):
        length = struct.unpack(">I", raw[pos:pos + 4])[0]
        ctype = raw[pos + 4:pos + 8]
        body = raw[pos + 8:pos + 8 + length]
        if ctype == b"IHDR":
            header = struct.unpack(">IIBBBBB", body)
        elif ctype == b"IDAT":
            idat += body
        elif ctype == b"IEND":
            break
        pos += 12 + length

    width, height, depth, color_type, _, _, interlace = header
    if (depth, color_type, interlace) != (8, 6, 0):
        raise SystemExit(f"{path}: поддерживается только 8-битный RGBA без чересстрочности "
                         f"(получено depth={depth}, colorType={color_type}, interlace={interlace})")

    data = zlib.decompress(bytes(idat))
    stride, bpp = width * 4, 4
    pixels = bytearray(height * stride)

    for y in range(height):
        ftype = data[y * (stride + 1)]
        line = data[y * (stride + 1) + 1:(y + 1) * (stride + 1)]
        out = pixels[y * stride:(y + 1) * stride]
        prev = pixels[(y - 1) * stride:y * stride] if y else bytearray(stride)
        for x in range(stride):
            a = out[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            v = line[x]
            if ftype == 1:
                v += a
            elif ftype == 2:
                v += b
            elif ftype == 3:
                v += (a + b) >> 1
            elif ftype == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                v += a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
            out[x] = v & 0xFF
        pixels[y * stride:(y + 1) * stride] = out

    return width, height, pixels


def write_png_rgba(path, width, height, pixels):
    stride = width * 4
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # фильтр None — простое кодирование, zlib добирает сжатие
        raw += pixels[y * stride:(y + 1) * stride]

    def chunk(tag, body):
        return (struct.pack(">I", len(body)) + tag + body
                + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF))

    out = bytearray(b"\x89PNG\r\n\x1a\n")
    out += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    out += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += chunk(b"IEND", b"")
    open(path, "wb").write(out)
    return len(out)


def recolor(width, height, pixels, rgb):
    r, g, b = rgb
    for i in range(0, len(pixels), 4):
        if pixels[i + 3]:
            pixels[i], pixels[i + 1], pixels[i + 2] = r, g, b
    return pixels


def crop_emblem(width, height, pixels, padding=0.12):
    """Возвращает квадратную обрезку первого слева графического блока."""
    stride = width * 4
    filled = [any(pixels[y * stride + x * 4 + 3] > 8 for y in range(height)) for x in range(width)]

    start = next((x for x, f in enumerate(filled) if f), 0)
    gap, end = 0, width - 1
    for x in range(start, width):
        if filled[x]:
            gap = 0
        else:
            gap += 1
            if gap > width * 0.02:  # пауза перед разделителем и текстом
                end = x - gap
                break

    rows = [y for y in range(height)
            if any(pixels[y * stride + x * 4 + 3] > 8 for x in range(start, end + 1))]
    top, bottom = (rows[0], rows[-1]) if rows else (0, height - 1)

    side = max(end - start + 1, bottom - top + 1)
    pad = int(side * padding)
    side += pad * 2
    cx, cy = (start + end) // 2, (top + bottom) // 2
    ox, oy = cx - side // 2, cy - side // 2

    out = bytearray(side * side * 4)
    for y in range(side):
        sy = oy + y
        if 0 <= sy < height:
            for x in range(side):
                sx = ox + x
                if 0 <= sx < width:
                    s, d = (sy * width + sx) * 4, (y * side + x) * 4
                    out[d:d + 4] = pixels[s:s + 4]
    return side, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--color", default="000000", help="цвет в HEX, по умолчанию чёрный")
    ap.add_argument("--emblem", help="дополнительно сохранить квадратную иконку-эмблему")
    args = ap.parse_args()

    hexcolor = args.color.lstrip("#")
    rgb = tuple(int(hexcolor[i:i + 2], 16) for i in (0, 2, 4))

    width, height, pixels = read_png_rgba(args.src)
    pixels = recolor(width, height, pixels, rgb)
    size = write_png_rgba(args.dst, width, height, pixels)
    print(f"{args.dst}: {width}×{height}, {size // 1024} КБ, цвет #{hexcolor}")

    if args.emblem:
        side, cropped = crop_emblem(width, height, pixels)
        size = write_png_rgba(args.emblem, side, side, cropped)
        print(f"{args.emblem}: {side}×{side}, {size // 1024} КБ")


if __name__ == "__main__":
    sys.exit(main())
