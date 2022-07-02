import csv
import os
import re
import datetime as dt


def yes_no(value):
    if value.lower() == 'yes' or value == '1':
        return '1'
    return '0'


def get_index(value, list):
    for i in list:
        if i.lower() == value.lower():
            return int(list.index(i)) + 1


def get_key(val, reason):
    for key, value in reason.items():
        if val.lower() == value.lower():
            return key
    return 'OTH'


def lower_headers(headers):
    for i in range(len(headers)):
        headers[i] = headers[i].lower()
    return headers


DATE_RE = r"^([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])($| .+$)"
CIN_RE = r"^9(\d{7})[a-zA-Z]$"
CIN_BAD = r"^9(\d)\1+[a-zA-Z]$"
MEM_BAD = r"^MEM(\d)\1+$"
EMAIL_RE = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

CONTACT_ROLE = [
    'CASE MANAGER',
    'PHARM D',
    'SOCIAL WORKER',
    'PROVIDER',
    'OTHER'
]

DISENROLLMENT_REASON = {
    'WM': 'Member is well-managed and not in need of services',
    'DP': 'Member declined to participate',
    'UE': 'unable to engage the Member',
    'UBE': 'unsafe behavior or environment',
    'EXP': 'Member is deceased',
    'NE': 'Member is not enrolled in Medi-Cal at MCP',
    'OH': 'Member’s Medi-Cal eligibility is on hold or termed',
    'CAP': 'Provider does not have capacity for new Members',
    'ERR': 'Member information is incorrect',
    'OTH': 'other reason  as further specified',
    'SC': 'Successfully Completed'
}

ATTEMPT_RESULT = [
    'CONTACTED - CALL WAS COMPLETED',
    'UTC(UNABLE TO CONTACT) - ATTEMPTS HAVE BEEN MADE TO CONTACT CLIENT WITHOUT SUCCESS'
]

ATTEMPT_UNSUCCESFUL_DISPOSITION = [
    'NO ANSWER',
    'VOICEMAIL',
    'LEFT MESSAGE WITH 3RD PARTY',
    'WRONG PHONE NUMBER',
    'DISCONNECTED NUMBER',
    'BUSY SIGNAL'
]

ATTEMPT_SUCCESFUL_DISPOSITION = [
    'DECLINED SERVICES',
    'WELL MANAGED',
    'DUPLICATIVE PROGRAM',
    'UNSAFE BEHAVIOR/ENVIRONMENT',
    'KHS DISENROLLED',
    'Program Enrolled',
    'Program Ineligible'
]

SITE_TIN = "956001629"
SITE_NPI = "1437825213"
PROGRAM_NAME = "CSS"


class GetType(object):
    def __init__(self, filename):
        self.name = filename.split('.')[0]
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            self.rows = [row for row in reader]
            self.headers = self.rows[0]


class GetCSV(object):
    def __init__(self, filename, outdir):
        self.name = filename.split('.')[0]
        self.outdir = outdir
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            self.rows = [row for row in reader]
            self.headers = lower_headers(self.rows[0])
            for i in self.headers:
                j = self.headers.index(i)
                self.headers[j] = j
            self.rows = self.rows[1:]

    def get_row_demographics(self):
        counter = 1
        rows = []
        bad_count = 1
        bad_rows = []
        print(self.recheck_demographics())
        for i in self.rows:
            row = {}
            reason = []
            for j in range(len(self.headers)):
                row[self.headers[j]] = i[j]
            if row[0]:
                try:
                    row[3] = (dt.datetime.strptime(row[3].replace('/', '-'), '%Y-%m-%d %H:%M:%S')).strftime(
                        '%m-%d-%Y %H:%M:%S')
                except:
                    row[3] = (dt.datetime.strptime(row[3].replace('/', '-'), '%Y-%m-%d %H:%M')).strftime(
                        '%m-%d-%Y %H:%M:%S')
                if row[7] != '':
                    row[7] = (dt.datetime.strptime(row[7],
                                                   '%Y-%m-%d')).strftime('%m-%d-%Y')
                else:
                    row[7] = 'MISSING DOB'
                if row[8][0] == 'M' or row[8][0] == 'F':
                    gender = row[8][0]
                else:
                    gender = 'U'
                row[13] = re.sub('\D', '', row[13]) if row[13] else ''
                row[14] = yes_no(row[14]) if row[14] else '0'
                row[15] = yes_no(row[15]) if row[15] else '0'
                row[16] = re.sub('\D', '', row[16]) if row[16] else ''
                row[17] = re.sub('\D', '', row[17]) if row[17] else ''
                address = [row[18], row[19], row[20], row[21], row[22]]
                if all(x == '' for x in address):
                    address = ['601 24th St', '', 'Bakersfield', 'CA', '93301']
                else:
                    address = [row[18], row[19], row[20], row[21], row[22]]
                if len(row[4]) != 10 or \
                        re.match(MEM_BAD, row[4], re.IGNORECASE):
                    reason.append("BAD KHS ID")
                if not re.match(CIN_RE, row[5], re.IGNORECASE) or \
                        re.match(CIN_BAD, row[5], re.IGNORECASE):
                    reason.append("BAD CIN")
                if len(row[7]) != 10:
                    reason.append("BAD DOB")
                if row[12] and not re.match(EMAIL_RE, row[12], re.IGNORECASE):
                    reason.append("BAD EMAIL")
                if any(x == '' for x in [address[0], address[2], address[3], address[4]]):
                    reason.append("BAD ADDRESS")
                reason = ', '.join(reason)
                if reason:
                    bad_rows.append(
                        '{0:04}'.format(bad_count) +
                        f"|{row[3]}|0|{row[4].upper()}|{row[5].upper()}|"
                        f"{row[7]}|{gender}|{row[9]}|{row[10]}|"
                        f"{row[11]}|{row[12]}|{row[13]}|"
                        f"{row[14]}|{row[15]}|"
                        f"{row[16]}|{row[17]}|"
                        f"{address[0]}|{address[1]}|{address[2]}|{address[3]}|{address[4]}|"
                        f"{SITE_TIN}|{SITE_NPI}{f'|{reason}' if reason else ''}")

                    bad_count += 1
                else:
                    rows.append(
                        '{0:04}'.format(counter) +
                        f"|{row[3]}|0|{row[4].upper()}|{row[5].upper()}|"
                        f"{row[7]}|{gender}|{row[9]}|{row[10]}|"
                        f"{row[11]}|{row[12]}|{row[13]}|"
                        f"{row[14]}|{row[15]}|"
                        f"{row[16]}|{row[17]}|"
                        f"{address[0]}|{address[1]}|{address[2]}|{address[3]}|{address[4]}|"
                        f"{SITE_TIN}|{SITE_NPI}")
                    counter += 1
        lists = [rows, bad_rows]
        return lists

    def get_row_enrollment(self):
        counter = 1
        bad_count = 1
        rows = []
        bad_rows = []
        print(self.recheck_enrollment())
        for i in self.rows:
            row = {}
            reason = []
            for j in range(len(self.headers)):
                row[self.headers[j]] = i[j]
            if row[0]:
                try:
                    row[3] = (dt.datetime.strptime(row[3].replace('/', '-'), '%Y-%m-%d %H:%M:%S')).strftime(
                        '%m-%d-%Y %H:%M:%S')
                except:
                    row[3] = (dt.datetime.strptime(row[3].replace('/', '-'), '%Y-%m-%d %H:%M')).strftime(
                        '%m-%d-%Y %H:%M:%S')
                if row[8] != '':
                    row[8] = (dt.datetime.strptime(row[8],
                                                   '%Y-%m-%d')).strftime('%m-%d-%Y')
                if row[11] != '':
                    row[11] = (dt.datetime.strptime(row[11], '%Y-%m-%d')).strftime(
                                                  '%m-%d-%Y')
                if row[12] != '':
                    row[12] = (dt.datetime.strptime(row[12],
                                                   '%Y-%m-%d')).strftime('%m-%d-%Y')
                row[9] = get_index(row[9], CONTACT_ROLE)
                if row[14] != '1':
                    row[13] = get_key(row[13], DISENROLLMENT_REASON)
                row[15] = row[15] if (len(self.headers) >= 16) else ''
                row[16] = row[16] if (len(self.headers) >= 17) else ''
                row[17] = row[17] if (len(self.headers) >= 18) else ''
                row[18] = row[18] if (len(self.headers) >= 19) else ''
                row[19] = row[19] if (len(self.headers) >= 20) else ''
                row[20] = row[20] if (len(self.headers) >= 21) else ''
                row[21] = row[21] if (len(self.headers) >= 22) else ''
                row[22] = row[22] if (len(self.headers) >= 23) else ''
                udfs = [row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21]]
                if len(row[4]) != 10 or \
                        re.match(MEM_BAD, row[4], re.IGNORECASE):
                    reason.append("BAD KHS ID")
                if not re.match(CIN_RE, row[5], re.IGNORECASE) or \
                        re.match(CIN_BAD, row[5], re.IGNORECASE):
                    reason.append("BAD CIN")
                if (len(row[15]) <= 0 and len(row[16]) > 0) or \
                        (len(row[15]) > 0 and len(row[16]) <= 0) or \
                        (len(row[17]) <= 0 and len(row[18]) > 0) or \
                        (len(row[17]) > 0 and len(row[18]) <= 0) or \
                        (len(row[19]) <= 0 and len(row[20]) > 0) or \
                        (len(row[19]) > 0 and len(row[20]) <= 0) or \
                        (len(row[21]) <= 0 and len(row[22]) > 0) or \
                        (len(row[21]) > 0 and len(row[22]) <= 0) or \
                        (all(len(udf) <= 0 for udf in udfs)):
                    reason.append("BAD UDF")
                reason = ', '.join(reason)
                if reason:
                    bad_rows.append(
                        '{0:04}'.format(bad_count) +
                        f"|{row[3]}|0|{row[4].upper()}|{row[5].upper()}|"
                        f"{yes_no(row[7])}|{row[8]}|{row[9]}|"
                        f"{row[10]}|{row[11]}|{row[11]}|"
                        f"{row[12]}|{yes_no(row[14])}|{row[13]}|"
                        f"{SITE_TIN}|{SITE_NPI}|{PROGRAM_NAME}|"
                        f"{row[15]}|{row[16]}|"
                        f"{row[17]}|{row[18]}|"
                        f"{row[19]}|{row[20]}|"
                        f"{row[21]}|{row[22]}{f'|{reason}' if reason else ''}")
                    bad_count += 1
                else:
                    rows.append(
                        '{0:04}'.format(counter) +
                        f"|{row[3]}|0|{row[4].upper()}|{row[5].upper()}|"
                        f"{yes_no(row[7])}|{row[8]}|{row[9]}|"
                        f"{row[10]}|{row[11]}|{row[11]}|"
                        f"{row[12]}|{yes_no(row[14])}|{row[13]}|"
                        f"{SITE_TIN}|{SITE_NPI}|{PROGRAM_NAME}|"
                        f"{row[15]}|{row[16]}|"
                        f"{row[17]}|{row[18]}|"
                        f"{row[19]}|{row[20]}|"
                        f"{row[21]}|{row[22]}")
                    counter += 1
        lists = [rows, bad_rows]
        return lists

    def get_row_outreach(self):
        counter = 1
        rows = []
        bad_count = 1
        bad_rows = []
        recheck = self.recheck_outreach()
        print(recheck)
        for i in self.rows:
            row = {}
            reason = []
            for j in range(len(self.headers)):
                row[self.headers[j]] = i[j]
            if row[0]:
                for i in recheck['outreach']:
                    if row[2].lower() == i['mem'] and row[3].lower() == i['cin']:
                        print(row)
                        break
                try:
                    row[1] = (dt.datetime.strptime(row[1].replace('/', '-'), '%Y-%m-%d %H:%M:%S')).strftime(
                        '%m-%d-%Y %H:%M:%S')
                except:
                    row[1] = (dt.datetime.strptime(row[1].replace('/', '-'), '%Y-%m-%d %H:%M')).strftime(
                        '%m-%d-%Y %H:%M:%S')
                if row[7] != '':
                    row[7] = (dt.datetime.strptime(row[7].replace('/', '-'),
                                               '%Y-%m-%d')).strftime('%m-%d-%Y') + ' '
                else:
                    row[7] = ''
                if row[8] != '':
                    row[8] = (dt.datetime.strptime(row[8],
                                               '%H:%M:%S')).strftime('%H:%M:%S')
                else:
                    row[8] = '12:00:00'
                if row[7] != '' and row[8] != '':
                    appointment = row[7] + row[8]
                else:
                    appointment = ''
                if row[9] != '':
                   row[9] = (dt.datetime.strptime(row[9].replace('/', '-'),
                                               '%Y-%m-%d')).strftime('%m-%d-%Y') + ' '
                else:
                    row[9] = ''
                if row[10] != '':
                   row[10] = (dt.datetime.strptime(row[10],
                                                '%H:%M:%S')).strftime('%H:%M:%S')
                else:
                    row[10] = '12:00:00'
                if row[9] != '' and row[10] != '':
                    contact_client = row[9] + row[10]
                else:
                    contact_client = ''
                if row[11] != '':
                    row[11] = get_index(row[11].upper(), ATTEMPT_RESULT)
                else:
                    row[11] = ''
                if row[12] != '':
                    row[12] = get_index(
                        row[12], ATTEMPT_UNSUCCESFUL_DISPOSITION)
                else:
                    row[12] = ''
                if row[13] != '':
                    row[13] = get_index(
                        row[13], ATTEMPT_SUCCESFUL_DISPOSITION)
                else:
                    row[13] = ''
                row[14] = row[14] if (len(self.headers) >= 15) else ''
                row[15] = row[15] if (len(self.headers) >= 16) else ''
                row[16] = row[16] if (len(self.headers) >= 17) else ''
                row[17] = row[17] if (len(self.headers) >= 18) else ''
                row[18] = row[18] if (len(self.headers) >= 19) else ''
                row[19] = row[19] if (len(self.headers) >= 20) else ''
                row[20] = row[20] if (len(self.headers) >= 21) else ''
                row[21] = row[21] if (len(self.headers) >= 22) else ''
                udfs = [row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21]]
                if len(row[2]) != 10 or \
                        re.match(MEM_BAD, row[2], re.IGNORECASE):
                    reason.append("BAD KHS ID")
                if not re.match(CIN_RE, row[3], re.IGNORECASE) or \
                        re.match(CIN_BAD, row[3], re.IGNORECASE):
                    reason.append("BAD CIN")
                if (len(row[14]) <= 0 and len(row[15]) > 0) or \
                        (len(row[14]) > 0 and len(row[15]) <= 0) or \
                        (len(row[16]) <= 0 and len(row[17]) > 0) or \
                        (len(row[16]) > 0 and len(row[17]) <= 0) or \
                        (len(row[18]) <= 0 and len(row[19]) > 0) or \
                        (len(row[18]) > 0 and len(row[19]) <= 0) or \
                        (len(row[20]) <= 0 and len(row[21]) > 0) or \
                        (len(row[20]) > 0 and len(row[21]) <= 0) or \
                        (all(len(udf) <= 0 for udf in udfs)):
                    reason.append("BAD UDF")
                reason = ', '.join(reason)
                if reason:
                    bad_rows.append(
                        '{0:04}'.format(bad_count) +
                        f"|{row[1]}|0|{row[2].upper()}|{row[3].upper()}|"
                        f"{yes_no(row[5])}|{yes_no(row[6])}|{appointment}|{contact_client}|"
                        f"{row[11]}|{row[12]}|{row[13]}|"
                        f"{SITE_TIN}|{SITE_NPI}|{PROGRAM_NAME}|"
                        f"{row[14]}|{row[15]}|"
                        f"{row[16]}|{row[17]}|"
                        f"{row[18]}|{row[19]}|"
                        f"{row[20]}|{row[21]}{f'|{reason}' if reason else ''}")
                    bad_count += 1
                else:
                    rows.append(
                        '{0:04}'.format(counter) +
                        f"|{row[1]}|0|{row[2].upper()}|{row[3].upper()}|"
                        f"{yes_no(row[5])}|{yes_no(row[6])}|{appointment}|{contact_client}|"
                        f"{row[11]}|{row[12]}|{row[13]}|"
                        f"{SITE_TIN}|{SITE_NPI}|{PROGRAM_NAME}|"
                        f"{row[14]}|{row[15]}|"
                        f"{row[16]}|{row[17]}|"
                        f"{row[18]}|{row[19]}|"
                        f"{row[20]}|{row[21]}")
                    counter += 1
        lists = [rows, bad_rows]
        return lists

    def recheck_demographics(self):
        bad = {
            'demographics': [],
        }
        bad_row_files = []
        for file in os.listdir(self.outdir):
            if file.startswith("BAD_ROWS_KERNHOUSINGAUTH_KHS_NONPROGRAM_DEMOGRAPHIC"):
                bad_row_files.append(file)

        for file in bad_row_files:
            with open(self.outdir + "\\" + file, 'r') as f:
                rows = f.readlines()
                for row in rows:
                    first = row.split('|')[8]
                    last = row.split('|')[7]
                    mem = row.split('|')[3]
                    cin = row.split('|')[4]
                    bad['demographics'].append({
                        'first': first.lower(),
                        'last': last.lower(),
                        'mem': mem.lower(),
                        'cin': cin.lower(),
                    })
        return bad

    def recheck_enrollment(self):
        bad = {
            'enrollment': [],
        }
        bad_row_files = [file for file in os.listdir(self.outdir) if file.startswith("BAD_ROWS_HOUSINGAUTH24STCSS_KHS_CSS_ENROLLMENT")]

        for file in bad_row_files:
            with open(self.outdir + "\\" + file, 'r') as f:
                rows = f.readlines()
                for row in rows:
                    mem = row.split('|')[3]
                    cin = row.split('|')[4]
                    bad['enrollment'].append({
                        'mem': mem.lower(),
                        'cin': cin.lower(),
                    })
        return bad

    def recheck_outreach(self):
        bad = {
            'outreach': [],
        }
        bad_row_files = [file for file in os.listdir(self.outdir) if file.startswith("BAD_ROWS_HOUSINGAUTH24STCSS_KHS_CSS_OUTREACH")]

        for file in bad_row_files:
            with open(self.outdir + "\\" + file, 'r') as f:
                rows = f.readlines()
                for row in rows:
                    mem = row.split('|')[3]
                    cin = row.split('|')[4]
                    bad['outreach'].append({
                        'mem': mem.lower(),
                        'cin': cin.lower(),
                    })
        return bad
