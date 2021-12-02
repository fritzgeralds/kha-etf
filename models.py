import csv


class getCSV(object):
    def __init__(self, filename):
        self.name = filename.split('.')[0]
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            self.rows = [row for row in reader]
            self.headers = self.rows[0]
            self.rows = self.rows[1:]
        return
    def get_headers(self):
        return self.headers
    def get_rows(self):
        return self.rows
    def get_name(self):
        return self.name
    def get_row(self, index):
        return self.rows[index]


a = getCSV('Demographics.csv').rows

        for i in kwargs:
            setattr(self, i, kwargs[i])
    def __str__(self):
        return self.__dict__.__str__()

    def get_rows(self, **kwargs):


values = []
objects = []

with open('Demographics.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row_values in csv_reader:
        values.append(row_values)

column_names = values[0]
for row_values in values[1:]:
    objects.append({key: value for key, value in zip(column_names[1:], row_values[1:])})

row = 1
for i in [Row(**object) for object in objects]:
    print(f'Row {row}: {"|".join(i.__dict__.values()).replace("/", "-")}')
    row += 1
    for j in i.__dict__:
        print(j)
        print(getattr(i, j))
    print('\n')

    # print('|'.join("%s" % item for item in i.__dict__.values()))
    # row += 1



class Row(object):
    def __init__(self, **kwargs):
        for i in kwargs:
            setattr(self, i, kwargs[i])

    def __str__(self):
        return "<Row: %s>" % self.name