from dateutil import parser


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
        line = self.find_first_line(file)
        if line is not None:
            sections = line.split()
            data_count = len(sections) - 2

            if data_count != 0:
                data_sets = []
                dates = [parser.parse(' '.join(line.split()[0:2])).timestamp()]
                datas = []

                for i in range(data_count):
                    try:
                        datas.append([float(sections[2+i])])
                    except Exception:
                        print("Invalid Data Line Found! " + line)

                while True:
                    line = file.readline()
                    if line == '':
                        break

                    sections = line.split()

                    try:
                        dates.append(parser.parse(' '.join(line.split()[0:2])).timestamp())
                    except Exception:
                        print("Invalid Data Line Found! " + line)
                        continue

                    for i in range(len(datas)):
                        try:
                            datas[i].append(float(sections[2 + i]))
                        except Exception:
                            datas[i].append(datas[i][-1])

                for i in range(len(datas)):
                    data_sets.append(DataSet(dates, datas[i]))

                return data_sets

        return None

    def find_first_line(self, file):
        while True:
            line = file.readline()

            if not line:
                print("Invalid File Format. Did not find row with valid date time.")
                return None

            try:
                parser.parse(' '.join(line.split()[0:2]))
                return line
            except Exception:
                continue
