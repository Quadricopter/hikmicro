import struct
import hexdump
from locale import atof


class HikmicroJpeg:

    HEADER_READ_BUFFER_SIZE = 1024
    HDRI_HEADER_SIZE = 44

    def __init__(self, filename:str):

        self.jpegfile = open(filename, mode='rb')

        # Search 'HDRI' header
        header_addr = self.__get_header_address(self.jpegfile, b'HDRI')
        if header_addr < 0:
            print("'HDRI' header not found")
            return 1
        print(f'HDRI addr: 0x{header_addr:08x}')

        # Read 'HDRI' header
        self.jpegfile.seek(header_addr, 0)
        header = self.jpegfile.read(self.HDRI_HEADER_SIZE)
        hexdump.hexdump(header)

        self.width = struct.unpack('<I', header[12:16])[0]
        self.height = struct.unpack('<I', header[16:20])[0]
        print(f'[Header] width: {self.width}px, height: {self.height}px')

        unk1a = struct.unpack('<H', header[4:6])[0]
        unk1b = struct.unpack('<H', header[6:8])[0]
        unk1c = struct.unpack('<I', header[4:8])[0]
        unk1d = struct.unpack('<f', header[4:8])[0]
        print(f'         unk1: {unk1a} {unk1b} {unk1c} {unk1d}')

        # Find min/max value
        print('Compute range', end='')
        self.min = 65535
        self.max = 0
        self.jpegfile.seek(header_addr + self.HDRI_HEADER_SIZE, 0)
        for y in range(self.height):
            for x in range(self.width):
                data = self.jpegfile.read(2)
                data = int.from_bytes(data, "little")
                if data < self.min:
                    self.min = data
                if data > self.max:
                    self.max = data
        print(f' -> min: {self.min}, max: {self.max}')

        self.jpegfile.seek(header_addr + self.HDRI_HEADER_SIZE, 0)
#        for y in range(height):
#            for x in range(width):
#                data = self.jpegfile.read(2)
#                data = int.from_bytes(data, "little")
#                color = hm.get_rgb_from_temperature(data)
#                im.putpixel(xy=(x, y), value=color)

    def __get_header_address(self, jpeg_file, header):

        pos = -1
        jpeg_file.seek(0, 0)  # Go back to the begining of the file
        while True:
            buff = jpeg_file.read(self.HEADER_READ_BUFFER_SIZE)
            found = buff.find(header)
            if found >= 0:
                pos = jpeg_file.seek(0, 1) - len(buff) + found
                break

            if len(buff) != self.HEADER_READ_BUFFER_SIZE:
                break

            # Rewind in case of header split between buffer
            jpeg_file.seek(-len(header), 1)

        jpeg_file.seek(0, 0)  # Go back to the begining of the file

        return pos

    def get_size(self):
        return (self.width, self.height)

    def get_range(self):
        return (self.min, self.max)

    def get_next_temperature_list(self) -> list:
        temp_list = []
        for _ in range(self.width):
            data = self.jpegfile.read(2)
            data = int.from_bytes(data, "little")
            temp_list.append(data)
        return temp_list


class HikmicroExportedCsv:

    def __init__(self, filename: str):
        self.file = None
        self.__open(filename)

    def __open(self, filename: str):
        self.min = 0
        self.max = 0
        self.emissivity = 0

        self.file = open(filename, 'rb')
        for line in range(1,17):
            csv_list = self.__read_line()
            if line == 7:  # Read emissivity
                self.emissivity = self.quote_str_to_float(csv_list[3])
            if line == 14:  # Read min temp
                self.min = self.quote_str_to_float(csv_list[3])
            if line == 14:  # Read min temp
                self.min = self.quote_str_to_float(csv_list[3])
        print(f'CSV range     -> min: {self.min}°C, max: {self.max}°C')

    def __read_line(self):
        formated_line = ''
        escape = False
        raw_line = self.file.readline().decode(encoding='latin-1').rstrip()
        for n in range(len(raw_line)):
            if raw_line[n] == '"':
                escape = not escape

            if (raw_line[n] == ',') and not escape:
                formated_line += ';'
            else:
                formated_line += raw_line[n]
        csv_list = formated_line.split(';')
        return csv_list

    def quote_str_to_float(self, quote_str:str):
        isolated = quote_str[1:-1]
        isolated = isolated.replace(',', '.')
        return atof(isolated)

    def get_temperature_range(self):
        return self.min, self.max

    def get_next_temperature_list(self) -> list:
        temperature_list = []

        csv_raw = self.__read_line()
        for raw_temp in csv_raw:
            temperature_list.append(self.quote_str_to_float(raw_temp))

        return temperature_list
