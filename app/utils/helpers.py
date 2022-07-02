import csv
from datetime import datetime

from app.core.config import Config

from app.utils.globals import CONTACT_ROLE, DISENROLLMENT_REASON

cfg = Config()
env = "P" if cfg.environment.lower() == 'production' else "T"


def get_type(file):
    with open(file, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        if not headers[0]:
            headers.pop(0)
        if headers[0] == 'Enrollment ID':
            return 'HOUSINGAUTH24STCSS_KHS_CSS_ENROLLMENT'
        if headers[0] == 'General ID':
            return 'KERNHOUSINGAUTH_KHS_NONPROGRAM_DEMOGRAPHIC'
        if headers[0] == 'Assessment ID':
            return 'HOUSINGAUTH24STCSS_KHS_CSS_OUTREACH'
    return None


def format_date_time(v) -> str:
    try:
        formatted = (datetime.strptime(v.replace('/', '-'),
                                       '%Y-%m-%d %H:%M:%S')).strftime('%m-%d-%Y %H:%M:%S')
    except ValueError:
        formatted = (datetime.strptime(v.replace('/', '-'),
                                       '%Y-%m-%d %H:%M')).strftime('%m-%d-%Y %H:%M:%S')
    return formatted


def format_date(v):
    if v:
        return datetime.strptime(v, '%Y-%m-%d').strftime('%m-%d-%Y')
    return None


def get_gender(v):
    v = v.upper()
    if v[0] == 'M' or v[0] == 'F':
        return v[0]
    return None


def yes_no(v):
    return 1 if v.lower() == 'yes' or v == 1 else 0


def get_index(v, lst):
    if v.lower() in lst.lower():
        return lst.index(v.lower())
    return None


def get_key(v, dct):
    for key, val in dct.items():
        if v.lower() == val.lower():
            return key
    return None


def build_udfs(row, pre):
    count = 1
    udfs = []
    for i in range((len(row) - pre) // 2):
        code = row[pre + (1 * i)]
        desc = row[pre + (2 * i)]
        if code and desc:
            udfs.append({f'udf_{count}': {'code': code, 'desc': desc}})
    return udfs


class GetCSV:
    def __init__(self, file):
        self.file = file
        self.headers = []
        self.rows = []
        self.csv_type = get_type(file)
        self.filename = ''
        self.model = ''
        self.process()

    def process(self):
        if self.csv_type:
            self.filename = self.csv_type + '_' + env + '_' + datetime.strftime(datetime.now(), '%Y%m%d%H%M%S') + '.txt'
            with open(self.file, 'r') as f:
                reader = csv.reader(f, delimiter=',')
                self.headers = next(reader)
                for i in self.headers:
                    j = self.headers.index(i)
                    self.headers[j] = j
                self.rows = [row for row in reader]
            self.model = self.csv_type.split('_')[-1]

    def build_txt_row(self, row, count):
        data = {}
        if self.model == 'demographics':
            data = {'id': "%04d" % count, 'date': format_date_time(row[3]), 'mem_id': row[4], 'cin': row[5], 'dob': row[7], 'gender': get_gender(row[8]), 'last_name': row[9].title(), 'first_name': row[10].title(), 'middle_name': row[11].title(), 'email': row[12], 'opt_txt': row[14], 'opt_call': row[15], 'phone': {'home': row[16], 'work': row[17], 'cell': row[13]}, 'address': {'street': row[18], 'street2': row[19], 'city': row[20], 'state': row[21], 'zip': row[22]}}
            return data


