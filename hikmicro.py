#!/usr/bin/env python3

import argparse
import struct
import hexdump
import PIL
import PIL.Image
from modules.heatmap import Heatmap, Palette

HEADER_READ_BUFFER_SIZE = 1024
HDRI_HEADER_SIZE = 44


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
    parser.add_argument('-p', '--palette', type=int, default=Palette.WHITEHOT)
    parser.add_argument('--show', action="store_true")
    args = parser.parse_args()

    if args.palette < 0 or args.palette >= len(Palette):
        print(f'Unsupported palette, must be in [0:{len(Palette)-1}]')
        return 1

    with open(args.jpeg, mode='rb') as jpegfile:

        # Search 'HDRI' header
        header_addr = get_header_address(jpegfile, b'HDRI')
        if header_addr < 0:
            print("'HDRI' header not found")
            return 1
        print(f'HDRI addr: 0x{header_addr:08x}')

        # Read 'HDRI' header
        jpegfile.seek(header_addr, 0)
        header = jpegfile.read(HDRI_HEADER_SIZE)
        hexdump.hexdump(header)

        width = struct.unpack('<I', header[12:16])[0]
        height = struct.unpack('<I', header[16:20])[0]
        print(f'[Header] width: {width}px, height: {height}px')

        unk1a = struct.unpack('<H', header[4:6])[0]
        unk1b = struct.unpack('<H', header[6:8])[0]
        unk1c = struct.unpack('<I', header[4:8])[0]
        unk1d = struct.unpack('<f', header[4:8])[0]
        print(f'         unk1: {unk1a} {unk1b} {unk1c} {unk1d}')

        # Find min/max value
        print('First pass, compute temperature range', end='')
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
        print('Second pass, compute picture')
        hm = Heatmap(palette=args.palette)
        hm.dump_palette()
        hm.set_temperature_range(min, max)

        im = PIL.Image.new(mode="RGB", size=(width, height))
        jpegfile.seek(header_addr + HDRI_HEADER_SIZE, 0)
        for y in range(height):
            for x in range(width):
                data = jpegfile.read(2)
                data = int.from_bytes(data, "little")
                color = hm.get_rgb_from_temperature(data)
                im.putpixel(xy=(x, y), value=color)

        im = im.resize(size=(480, 640),
                       resample=PIL.Image.LANCZOS)
        if args.show:
            im.show()

    return 0


if __name__ == '__main__':
    main()
