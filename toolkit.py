#!/usr/bin/env python3

import argparse
import PIL
import PIL.Image
import json
from modules.heatmap import Heatmap, Palette
from modules.hikmicro import HikmicroJpeg, HikmicroExportedCsv


def main():

    parser = argparse.ArgumentParser(
                    prog='HIKMICRO Toolkit',
                    description='Extract thermal data from HIKMICRO jpg file')
    parser.add_argument('--jpeg', required=True, help='HIKMICRO JPEG radiometric file')
    parser.add_argument('--csv', help="CSV exported from HIKMICRO Analyser")
    parser.add_argument('--palette', help=f'Palette selection [0:{len(Palette)-1}]', type=int, default=Palette.WHITEHOT)
    parser.add_argument('--min', help='Force min temperature', type=int)
    parser.add_argument('--max', help='Force max temperature', type=int)
    parser.add_argument('--output', help='Output file')
    parser.add_argument('--json', help='Export file info as json file')
    parser.add_argument('--show', help='Preview exported picture', action="store_true")
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

    # Export json
    if args.json:
        with open(args.json, "w") as json_file:
            json_dict = {
                'emissivity': jpeg.emissivity,
                'reflection_temperature': jpeg.reflection_temperature,
                'internal': {
                    'temperature': jpeg.environment_temperature,
                    'humidity': jpeg.humidity,
                },
                'size': {
                    'width': jpeg.get_size()[0],
                    'height': jpeg.get_size()[1]
                }
            }
            json_file.write(json.dumps(json_dict, indent=4))

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

    image_size = jpeg.get_size()
    if not csv:
        # Create image
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
        if args.output:
            im.save(args.output)

    else:
        # Create jpeg vs csv diff
        if args.output is not None:
            with open(args.output, "w") as output_file:
                for y in range(image_size[1]):
                    jpeg_temp_list = jpeg.get_next_temperature_list()
                    csv_temp_list = csv.get_next_temperature_list()
                    for x in range(image_size[0]):
                        color_16bit = jpeg_temp_list[x]
                        color_degree = csv_temp_list[x]
                        output_file.write(f'{color_16bit},{color_degree}\n')


if __name__ == '__main__':
    main()
