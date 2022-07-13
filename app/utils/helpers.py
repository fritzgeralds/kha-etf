import csv
import logging
import re
import string
from datetime import datetime

from dateutil.parser import parse

from app.core.config import Config
from app.models.demographics import Demographics
from app.models.enrollment import Enrollment
from app.models.outreach import Outreach
from app.utils.constants import CONTACT_ROLE, DISENROLLMENT_REASON, ATTEMPT_RESULT, ATTEMPT_UNSUCCESFUL_DISPOSITION, \
    ATTEMPT_SUCCESFUL_DISPOSITION

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


def format_date_time(v, t):
    try:
        date = parse(v)
        if t == 'date':
            return date.strftime('%m-%d-%Y')
        elif t == 'time':
            return date.strftime('%H:%M:%S')
        elif t == 'datetime':
            return date.strftime('%m-%d-%Y %H:%M:%S')
    except ValueError:
        return ''


def get_gender(v):
    v = v.upper()
    if v[0] == 'M' or v[0] == 'F':
        return v[0]
    return "U"


def yes_no(v):
    if isinstance(v, str):
        return 1 if v.lower() == 'yes' or v == '1' else 0
    return 1 if v == 1 else 0


def get_index(v, lst) -> int:
    for val in lst:
        if v.lower() == val.lower():
            return lst.index(val) + 1
    return 0


def get_key(v, dct):
    for key, val in dct.items():
        if v.lower() == val.lower():
            return key
    return None


def get_disenrollment_key(v, dct):
    for key, val in dct.items():
        if v.lower().translate({ord(c): None for c in string.whitespace}) == \
                val.lower().translate({ord(c): None for c in string.whitespace}):
            return key
    return None


def build_udfs(row, pre):
    count = 1
    udfs = []
    for i in range(pre, len(row), 2):
        udfs.append({f'udf_{count}': {'code': row[i], 'desc': row[i + 1]}})
        count += 1
    return udfs


class GetCSV:
    def __init__(self, file):
        self.file = file
        self.error_headers = []
        self.headers = []
        self.rows = []
        self.good = []
        self.bad = []
        self.csv_type = get_type(file)
        self.filename = ''
        self.model = ''
        self.has_error = False
        self.process()
        self.build_txt_row()

    def process(self):
        if self.csv_type:
            self.filename = self.csv_type + '_' + env + '_' + datetime.strftime(datetime.now(), '%Y%m%d%H%M%S') + '.txt'
            with open(self.file, 'r') as f:
                reader = csv.reader(f, delimiter=',')
                self.headers = next(reader)
                if self.headers[-1] == 'Error':
                    self.has_error = True
                self.error_headers = [h for h in self.headers]
                if self.error_headers[-1] != 'Error':
                    self.error_headers.append('Error')
                for i in self.headers:
                    j = self.headers.index(i)
                    self.headers[j] = j
                self.rows = [row for row in reader]
            self.model = self.csv_type.split('_')[-1].lower()
            for row in self.rows:
                for i in range(len(row)):
                    row[i] = row[i].strip()

    def build_txt_row(self):
        id_index = 1
        logger = logging.getLogger(self.model.title())
        for row in self.rows:
            if self.has_error:
                row.pop()
            if row[0]:
                try:
                    if self.model == 'demographic':
                        self.good.append(Demographics(**{'filename': self.file.split('/')[-1],'row_id': self.rows.index(row) + 1,'id': "%04d" % id_index,'date': format_date_time(row[3], 'datetime'),'mem_id': row[4].upper(),'cin': row[5].upper(),'dob': format_date_time(row[7], 'date'),'gender': get_gender(row[8]),'last_name': row[9].title(),'first_name': row[10].title(),'middle_name': row[11].title(),'email': row[12],'opt_txt': yes_no(row[14]),'opt_call': yes_no(row[15]),'phone': {'home': re.sub('\D', '', row[16]),'work': re.sub('\D', '', row[17]),'cell': re.sub('\D', '', row[13])},'address': {'street': row[18],'street2': row[19],'city': row[20],'state': row[21],'zip': row[22]}}))
                    elif self.model == 'enrollment':
                        self.good.append(Enrollment(**{'filename': self.file.split('/')[-1],'row_id': self.rows.index(row) + 1,'id': "%04d" % id_index,'date': format_date_time(row[3], 'datetime'),'mem_id': row[4].upper(),'cin': row[5].upper(),'next_visit': yes_no(row[7]),'next_visit_date': format_date_time(row[8], 'date'),'role': get_index(row[9], CONTACT_ROLE),'role_other': row[10],'contact_date': format_date_time(row[11], 'date'),'effective_date': format_date_time(row[11], 'date'),'term_date': format_date_time(row[12], 'date'),'enrollment_flag': yes_no(row[14]),'disenrollment_reason': get_disenrollment_key(row[13], DISENROLLMENT_REASON),'udf': build_udfs(row, 15)}))
                    elif self.model == 'outreach':
                        self.good.append(Outreach(**{'filename': self.file.split('/')[-1],'row_id': self.rows.index(row) + 1,'id': "%04d" % id_index,'date': format_date_time(row[1], 'datetime'),'mem_id': row[2].upper(),'cin': row[3].upper(),'rescheduled': yes_no(row[5]),'cancelled': yes_no(row[6]),'appointment_date': format_date_time(row[7] + ' ' + row[8], 'datetime'),'attempt_time': format_date_time(row[9] + ' ' + row[10], 'datetime'),'attempt_result': get_index(row[11], ATTEMPT_RESULT),'unsuccessful': get_index(row[12], ATTEMPT_UNSUCCESFUL_DISPOSITION),'successful': get_index(row[13], ATTEMPT_SUCCESFUL_DISPOSITION),'udf': build_udfs(row, 14)}))
                    id_index += 1
                except Exception as e:
                    logger.error(e)
                    row.append(str(e).split(' :: ')[-1])
                    self.bad.append(row)
        logger.info(f'Found {len(self.good)} good rows and {len(self.bad)} bad rows.')

