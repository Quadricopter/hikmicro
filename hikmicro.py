#!/usr/bin/env python3

import argparse
import struct
import hexdump
import PIL
import PIL.Image
from modules.heatmap import Heatmap, Palette

HEADER_READ_BUFFER_SIZE = 1024
HDRI_HEADER_SIZE = 44


# def color_map(min:float, max:float, cur:float) -> int:
#     cur -= min
#     max -= min
#     col = int((cur * 255) / max)
#     if col < 0:
#         col = 0
#     if col > 255:
#         col = 255
#     return col


def get_header_address(jpeg_file, header):

    pos = -1
    jpeg_file.seek(0, 0)  # Go back to the begining of the file
    while True:
        buff = jpeg_file.read(HEADER_READ_BUFFER_SIZE)
        found = buff.find(header)
        if found >= 0:
            pos = jpeg_file.seek(0, 1) - len(buff) + found
            break

        if len(buff) != HEADER_READ_BUFFER_SIZE:
            break

        # Rewind in case of header split between buffer
        jpeg_file.seek(-len(header), 1)

    jpeg_file.seek(0, 0)  # Go back to the begining of the file

    return pos


def main():

    parser = argparse.ArgumentParser(
                    prog='HIKMICRO Toolkit',
                    description='Extract thermal data from HIKMICRO jpg file')
    parser.add_argument('-j', '--jpeg', required=True)
    args = parser.parse_args()

    with open(args.jpeg, mode='rb') as jpegfile:

        # Search 'HDRI' header
        header_addr = get_header_address(jpegfile, b'HDRI')
        if header_addr < 0:
            print("'HDRI' header not found")
            return 1
        print(f'HDRI addr: 0x{header_addr:08x}')

# # ---------------------------------------------------------------------------
# 
#         for n in range(1024):
#             # Search this address somewhere in the file
#             tmp_addr = header_addr - n
#             byte_addr = tmp_addr.to_bytes(4, 'little')
#             addr = get_header_address(jpegfile, byte_addr)
#             if addr > 0:
#                 print(f'addr: 0x{tmp_addr:08x} -> {addr}')
# 
# # ---------------------------------------------------------------------------

        # Read 'HDRI' header
        jpegfile.seek(header_addr, 0)
        header = jpegfile.read(HDRI_HEADER_SIZE)
        hexdump.hexdump(header)

        unk1a = struct.unpack('<H', header[4:6])[0]
        unk1b = struct.unpack('<H', header[6:8])[0]
        unk1c = struct.unpack('<f', header[4:8])[0]
        unk1d = struct.unpack('<I', header[4:8])[0]
        width = struct.unpack('<I', header[12:16])[0]
        height = struct.unpack('<I', header[16:20])[0]
        print(f'[Header] width: {width}px, height: {height}px')
        print(f'         unk1: {unk1a} {unk1b} {unk1c} {unk1d}')

        # Find min/max value
        print(f'First pass, compute IR temperature range.', end='')
        min = 65535
        max = 0
        jpegfile.seek(header_addr + HDRI_HEADER_SIZE, 0)
        for y in range(height):
            for x in range(width):
                data = jpegfile.read(2)
                data = int.from_bytes(data, "little")
                if data < min:
                    min = data
                if data > max:
                    max = data
        print(f' -> min: {min}, max: {max}')

        # Convert raw to picture
        im = PIL.Image.new(mode="RGB", size=(width, height))
        hm = Heatmap(palette=Palette.RAINBOW)
        hm.set_temperature_range(min, max)
        print(f'Second pass, compute picture')
        jpegfile.seek(header_addr + HDRI_HEADER_SIZE, 0)
        for y in range(height):
            for x in range(width):
                data = jpegfile.read(2)
                data = int.from_bytes(data, "little")
                color = hm.get_rgb_from_temperature(data)
                im.putpixel(xy=(x, y), value=color)

        im.show()

    return 0

if __name__ == '__main__':
    main()
