import struct
import zlib
import io
import os

def create_png(width, height, bg_color, text_color, letter='E'):
    def create_rgba_image(w, h, bg, txt, ch):
        pixels = []
        center_x, center_y = w // 2, h // 2
        radius = min(w, h) // 2 - 2

        for y in range(h):
            row = []
            for x in range(w):
                dx = x - center_x
                dy = y - center_y
                dist = (dx * dx + dy * dy) ** 0.5

                if dist <= radius:
                    in_letter = False
                    rel_x = (x - center_x + radius) / (2 * radius)
                    rel_y = (y - center_y + radius) / (2 * radius)

                    bar_thickness = 0.18
                    serif_size = 0.08

                    if 0.2 <= rel_x <= 0.8:
                        if 0.15 <= rel_y <= 0.15 + bar_thickness:
                            in_letter = True
                        elif 0.42 <= rel_y <= 0.42 + bar_thickness * 0.8:
                            in_letter = True
                        elif 0.7 <= rel_y <= 0.7 + bar_thickness:
                            in_letter = True

                    if 0.2 <= rel_x <= 0.2 + bar_thickness:
                        if 0.15 <= rel_y <= 0.85:
                            in_letter = True

                    if in_letter:
                        row.extend(txt)
                    else:
                        row.extend(bg)
                else:
                    row.extend([0, 0, 0, 0])
            pixels.append(bytes(row))
        return pixels

    def make_png(w, h, rows):
        def chunk(chunk_type, data):
            c = chunk_type + data
            return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

        header = b'\x89PNG\r\n\x1a\n'
        ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)

        raw = b''
        for row in rows:
            raw += b'\x00' + row

        return header + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')

    rows = create_rgba_image(width, height, bg_color, text_color, letter)
    return make_png(width, height, rows)


def create_ico(png_data_list, ico_path):
    sizes = [16, 32, 48, 128, 256]
    images = []

    for size in sizes:
        png_data = create_png(size, size, [22, 119, 255, 255], [255, 255, 255, 255])
        images.append(png_data)

    header = struct.pack('<HHH', 0, 1, len(images))

    offset = 6 + 16 * len(images)
    entries = b''
    for i, (size, img) in enumerate(zip(sizes, images)):
        entries += struct.pack('<BBBBHHII', size, size, 0, 0, 1, 32, len(img), offset)
        offset += len(img)

    with open(ico_path, 'wb') as f:
        f.write(header + entries)
        for img in images:
            f.write(img)

    print(f'ICO file created: {ico_path}')

    for size in [16, 32, 48, 128, 256]:
        png_path = ico_path.replace('.ico', f'_{size}x{size}.png')
        png_data = create_png(size, size, [22, 119, 255, 255], [255, 255, 255, 255])
        with open(png_path, 'wb') as f:
            f.write(png_data)
        print(f'PNG file created: {png_path}')


if __name__ == '__main__':
    output_dir = os.path.dirname(os.path.abspath(__file__))
    ico_path = os.path.join(output_dir, 'app_icon.ico')
    create_ico(None, ico_path)
    print('Icon generation completed!')
