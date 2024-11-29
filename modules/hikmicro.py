from locale import atof


class HikmicroJpeg:

    def __init__(self):
        pass

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
#        print(f'CSV min: {self.min}°C, max: {self.max}°C')

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
