#!/usr/bin/env python3

import argparse
import PIL
import PIL.Image
from modules.heatmap import Heatmap, Palette
from modules.hikmicro import HikmicroJpeg, HikmicroExportedCsv


def main():

    parser = argparse.ArgumentParser(
                    prog='HIKMICRO Toolkit',
                    description='Extract thermal data from HIKMICRO jpg file')
    parser.add_argument('-j', '--jpeg', required=True)
    parser.add_argument('-c', '--csv')
    parser.add_argument('-p', '--palette', type=int, default=Palette.WHITEHOT)
    parser.add_argument('-m', '--min', type=int)
    parser.add_argument('-M', '--max', type=int)
    parser.add_argument('--show', action="store_true")
    args = parser.parse_args()

    if args.palette < 0 or args.palette >= len(Palette):
        print(f'Unsupported palette, must be in [0:{len(Palette)-1}]')
        return 1

    # Open JPEG file
    jpeg = HikmicroJpeg(args.jpeg)

    # Open CSV file
    csv = None
    if args.csv:
        csv = HikmicroExportedCsv(args.csv)

    # Create palette
    hm = Heatmap(palette=args.palette)
    hm.dump_palette()
    temp_range = jpeg.get_range()
    min_temp = temp_range[0]
    max_temp = temp_range[1]
    if args.min is not None:
        min_temp = args.min
    if args.max:
        max_temp = args.max
    hm.set_temperature_range(min_temp, max_temp)

    # Create image
    image_size = jpeg.get_size()
    im = PIL.Image.new(mode="RGB", size=(image_size[0], image_size[1]))

    for y in range(image_size[1]):
        jpeg_temp_list = jpeg.get_next_temperature_list()
        for x in range(image_size[0]):
            color = hm.get_rgb_from_temperature(jpeg_temp_list[x])
            im.putpixel(xy=(x, y), value=color)

    im = im.resize(size=(480, 640),
                    resample=PIL.Image.LANCZOS)
    if args.show:
        im.show()


if __name__ == '__main__':
    main()
