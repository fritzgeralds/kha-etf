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
