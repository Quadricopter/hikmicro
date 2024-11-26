#!/usr/bin/env python3

from enum import IntEnum
import math


class Palette(IntEnum):

    GRAYSCALE = 0   # Grayscale
    RAINBOW = 1     # black-blue-cyan-green-yellow-red
    IRONBOW = 2     # black-blue-magenta-orange-yellow-white / FLIR


class Heatmap():

    DEFAULT_MIN_TEMPERATURE = 20
    DEFAULT_MAX_TEMPERATURE = 40

    def __init__(self, palette=Palette.RAINBOW):

        self.min_temp = self.DEFAULT_MIN_TEMPERATURE
        self.max_temp = self.DEFAULT_MAX_TEMPERATURE
        self.set_palette(palette)

    def set_palette(self, palette=Palette.RAINBOW):

        self.color_map = []

        if palette == Palette.GRAYSCALE:
            # RGB(0, 0, 0) -> RGB(255, 255, 255)
            for value in range(255):
                self.color_map.append((value, value, value))

        if palette == Palette.RAINBOW:
            # Now 100% black
            # Add blue:     RGB(0, 0, 0) -> RGB(0, 0, 255)
            for blue in range(255):
                self.color_map.append((0, 0, blue))

            # Now 100% blue
            # Add green:    RGB(0, 0, 255) -> RGB(0, 255, 255)
            for green in range(255):
                self.color_map.append((0, green, 255))

            # Now 100% cyan
            # Remove blue:  RGB(0, 255, 255) -> RGB(0, 255, 0)
            for blue in range(255):
                self.color_map.append((0, 255, 255 - blue))

            # Now 100% green
            # Add red:      RGB(0, 255, 0) -> RGB(255, 255, 0)
            for red in range(255):
                self.color_map.append((red, 255, 0))

            # Now 100% yellow
            # remove green: RGB(255, 255, 0) -> RGB(255, 0, 0)
            for green in range(255):
                self.color_map.append((255, 255 - green, 0))

            # Now 100% red

        if palette == Palette.IRONBOW:
            # black-blue-magenta-orange-yellow-white / FLIR

            # RGB(0, 0, 0) -> RGB(0, 0, 127)
            for value in range(0, 127, 1):
                self.color_map.append((0, 0, value))

            # RGB(0, 0, 127) -> RGB(255, 0, 255)
            for value in range(0, 127, 1):
                self.color_map.append((2 * value, 0, 128 + value))

            # RGB(255, 0, 255) -> RGB(255, 0, 0)
            for value in range(0, 255, 2):
                self.color_map.append((255, 0, 255 - value))

            # RGB(255, 0, 0) -> RGB(255, 255, 0)
            for value in range(255):
                self.color_map.append((255, value, 0))

            # RGB(255, 255, 0) -> RGB(255, 255, 255)
            for value in range(0, 255, 2):
                self.color_map.append((255, 255, value))

        # print(f'Heatmap color count: {len(self.color_map)} colors')

    def set_temperature_range(self, min, max):

        self.min_temp = min
        self.max_temp = max
        print(f'set_temperature_range: [{min:.1f}:{max:.1f}]')

    def get_rgb_from_temperature(self, temperature, alpha=1) -> tuple:

        # color_map idx:             [0 --------------- len(color_map)]
        # temperature:   [-----------min----------------------max-------------]

        temperature -= self.min_temp

        if alpha > 1.0:
            z = temperature / (self.max_temp - self.min_temp)
            z = min(z, 1.0)
            z = max(z, 0.0)
            z = 1.0 - math.pow((1.0 - math.pow(z, alpha)), 1.0 / alpha)
            temperature = z * (self.max_temp - self.min_temp)

        #   max-min   -> len(color_map)
        # temperature ->   color_idx
        color_idx = int((temperature * len(self.color_map)) // (self.max_temp - self.min_temp))
        color_idx = min(color_idx, (len(self.color_map) - 1))
        color_idx = max(color_idx, 0)

        return self.color_map[color_idx]
