from datetime import datetime

DATE_FORMATS = ['%d/%m/%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S']


class DataSet:
    def __init__(self, x_data, y_data):
        self.x = x_data
        self.y = y_data

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y


class DataProcessor:
    def __int__(self):
        self.x = None

    def read_datetime_file(self, path):
        file = open(path, "r")
        line, date_format = self.find_first_line(file)
        if line is not None:
            sections = line.split()
            data_count = len(sections) - 2

            if data_count != 0:
                data_sets = []
                dates = [datetime.strptime(line[0:19], DATE_FORMATS[date_format]).timestamp()]
                datas = []

                for i in range(data_count):
                    datas.append([float(sections[2+i])])

                while True:
                    line = file.readline()
                    if line == '':
                        break
                    sections = line.split()
                    try:
                        dates.append(datetime.strptime(line[0:19], DATE_FORMATS[date_format]).timestamp())
                    except:
                        date_format = 1 - date_format
                        dates.append(datetime.strptime(line[0:19], DATE_FORMATS[date_format]).timestamp())

                    for i in range(data_count):
                        try:
                            datas[i].append(float(sections[2 + i]))
                        except:
                            datas[i].append(datas[i][-1])

                for i in range(data_count):
                    data_sets.append(DataSet(dates, datas[i]))

                return data_sets

        return None

    def find_first_line(self, file):
        while True:
            line = file.readline()

            if not line:
                print("Wrong File Format!")
                return None

            for i in range(len(DATE_FORMATS)):
                try:
                    datetime.strptime(line[0:19], DATE_FORMATS[i])
                    return line, i
                except ValueError:
                    continue
