import csv
import re
import datetime as dt


def yesNo(value):
    if value.lower() == 'yes' or value == '1':
        return '1'
    else:
        return '0'

def getIndex(value, list):
    for i in list:
        if i.lower() == value.lower():
            return int(list.index(i)) + 1
    return

def getKey(val, reason):
    for key, value in reason.items():
         if val.lower() == value.lower():
             return key
    return 'OTH'


def lowerHeaders(headers):
    for i in range(len(headers)):
        headers[i] = headers[i].lower()
    return headers


DATE_RE = r"^([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])($| .+$)"

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
    'UTC (UNABLE TO CONTACT) - ATTEMPTS HAVE BEEN MADE TO CONTACT MEMBER WITHOUT SUCCESS'
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
SITE_NPI = "437825213"
PROGRAM_NAME = "CSS"


class GetType(object):
    def __init__(self, filename):
        self.name = filename.split('.')[0]
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            self.rows = [row for row in reader]
            self.headers = self.rows[0]


class GetCSV(object):
    def __init__(self, filename):
        self.name = filename.split('.')[0]
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            self.rows = [row for row in reader]
            self.headers = lowerHeaders(self.rows[0])
            for i in self.headers:
                j = self.headers.index(i)
                self.headers[j] = j
            self.rows = self.rows[1:]

    def get_row_demographics(self):
        counter = 1
        rows = []
        bad_count = 1
        bad_rows = []
        for i in self.rows:
            row = {}
            for j in range(len(self.headers)):
                row[self.headers[j]] = i[j]
            row[3] = (dt.datetime.strptime(row[3], '%m/%d/%Y %H:%M')).strftime(
                '%m-%d-%Y %H:%M:%S')
            if row[6] != '':
                row[6] = (dt.datetime.strptime(row[6],
                                               '%m/%d/%Y')).strftime('%m-%d-%Y')
            else:
                row[6] = ''
            if row[7][0] == 'M' or row[7][0] == 'F':
                gender = row[7][0]
            else:
                gender = 'U'
            row[12] = re.sub('\D', '', row[12]) if row[12] else ''
            row[13] = yesNo(row[13]) if row[13] else '0'
            row[14] = yesNo(row[14]) if row[14] else '0'
            row[15] = re.sub('\D', '', row[15]) if row[15] else ''
            row[16] = re.sub('\D', '', row[16]) if row[16] else ''
            row[17] = row[17] if row[17] else 'None'
            row[19] = row[19] if row[19] else 'None'
            row[20] = row[20] if row[20] else 'NA'
            row[21] = row[21] if row[21] else '00000'
            if len(row[5]) != 9:
                bad_rows.append(
                    '{0:04}'.format(bad_count) +
                    f"|{row[3]}|0|{row[4].upper()}|{row[5].upper()}|"
                    f"{row[6]}|{gender}|{row[8]}|{row[9]}|"
                    f"{row[10]}|{row[11]}|{row[12]}|"
                    f"{row[13]}|{row[14]}|"
                    f"{row[15]}|{row[16]}|"
                    f"{row[17]}|{row[18]}|{row[19]}|{row[20]}|{row[21]}|"
                    f"{SITE_TIN}|{SITE_NPI}")
                bad_count += 1
            else:
                rows.append(
                    '{0:04}'.format(counter) +
                    f"|{row[3]}|0|{row[4].upper()}|{row[5].upper()}|"
                    f"{row[6]}|{gender}|{row[8]}|{row[9]}|"
                    f"{row[10]}|{row[11]}|{row[12]}|"
                    f"{row[13]}|{row[14]}|"
                    f"{row[15]}|{row[16]}|"
                    f"{row[17]}|{row[18]}|{row[19]}|{row[20]}|{row[21]}|"
                    f"{SITE_TIN}|{SITE_NPI}")
                counter += 1
            lists = [rows, bad_rows]
        return lists

    def get_row_enrollment(self):
        counter = 1
        bad_count = 1
        rows = []
        bad_rows = []
        for i in self.rows:
            row = {}
            for j in range(len(self.headers)):
                row[self.headers[j]] = i[j]
            row[3] = (dt.datetime.strptime(row[3], '%m/%d/%Y %H:%M')).strftime(
                                        '%m-%d-%Y %H:%M:%S')
            if row[7] != '':
                row[7] = (dt.datetime.strptime(row[7],
                                               '%m/%d/%Y')).strftime('%m-%d-%Y')
            if row[10] != '':
                row[10] = (dt.datetime.strptime(row[10], '%m/%d/%Y')).strftime(
                                              '%m-%d-%Y')
            if row[11] != '':
                row[11] = (dt.datetime.strptime(row[11],
                                               '%m/%d/%Y')).strftime('%m-%d-%Y')
            row[8] = getIndex(row[8], CONTACT_ROLE)
            if row[19] != '1':
                row[12] = getKey(row[12], DISENROLLMENT_REASON)
            if len(row[5]) != 9:
                bad_rows.append(
                    '{0:04}'.format(bad_count) +
                    f"|{row[3]}|0|{row[4].upper()}|{row[5].upper()}|"
                    f"{yesNo(row[6])}|{row[7]}|{row[8]}|"
                    f"{row[9]}|{row[10]}|{row[10]}|"
                    f"{row[11]}|{yesNo(row[19])}|{row[12]}|"
                    f"{SITE_TIN}|{SITE_NPI}|{PROGRAM_NAME}|{row[13] if (len(self.headers) >= 14) else ''}"
                    f"|{row[14] if (len(self.headers) >= 15) else ''}|{row[15] if (len(self.headers) >= 16) else ''}"
                    f"|{row[16] if (len(self.headers) >= 17) else ''}|{row[17] if (len(self.headers) >= 18) else ''}"
                    f"|{row[18] if (len(self.headers) >= 19) else ''}||")
                bad_count += 1
            else:
                rows.append(
                    '{0:04}'.format(counter) +
                    f"|{row[3]}|0|{row[4].upper()}|{row[5].upper()}|"
                    f"{yesNo(row[6])}|{row[7]}|{row[8]}|"
                    f"{row[9]}|{row[10]}|{row[10]}|"
                    f"{row[11]}|{yesNo(row[19])}|{row[12]}|"
                    f"{SITE_TIN}|{SITE_NPI}|{PROGRAM_NAME}|{row[13] if (len(self.headers) >= 14) else ''}"
                    f"|{row[14] if (len(self.headers) >= 15) else ''}|{row[15] if (len(self.headers) >= 16) else ''}"
                    f"|{row[16] if (len(self.headers) >= 17) else ''}|{row[17] if (len(self.headers) >= 18) else ''}"
                    f"|{row[18] if (len(self.headers) >= 19) else ''}||")
                counter += 1
            lists = [rows, bad_rows]
        return lists

    def get_row_outreach(self):
        counter = 1
        rows = []
        bad_count = 1
        bad_rows = []
        for i in self.rows:
            row = {}
            for j in range(len(self.headers)):
                row[self.headers[j]] = i[j]
            row[1] = (dt.datetime.strptime(row[1].replace('/', '-'), '%m-%d-%Y %H:%M')).strftime(
                '%m-%d-%Y %H:%M:%S')
            if row[6] != '':
                row[6] = (dt.datetime.strptime(row[6].replace('/', '-'),
                                           '%m-%d-%Y')).strftime('%m-%d-%Y') + ' '
            else:
                row[6] = ''
            if row[7] != '':
                row[7] = (dt.datetime.strptime(row[7],
                                           '%H:%M:%S')).strftime('%H:%M:%S')
            else:
                row[7] = ''
            appointment = row[6] + row[7]
            if row[8] != '':
               row[8] = (dt.datetime.strptime(row[8].replace('/', '-'),
                                           '%m-%d-%Y')).strftime('%m-%d-%Y') + ' '
            else:
                row[8] = ''
            if row[9] != '':
               row[9] = (dt.datetime.strptime(row[9],
                                            '%H:%M:%S')).strftime('%H:%M:%S')
            else:
                row[9] = ''
            contact_client = row[8] + row[9]
            if row[10] != '':
                row[10] = getIndex(row[10], ATTEMPT_RESULT)
            else:
                row[10] = ''
            if row[11] != '':
                row[11] = getIndex(
                    row[11], ATTEMPT_UNSUCCESFUL_DISPOSITION)
            else:
                row[12] = ''
            if row[12] != '':
                row[12] = getIndex(
                    row[12], ATTEMPT_SUCCESFUL_DISPOSITION)
            else:
                row[12] = ''
            if len(row[3]) != 9:
                bad_rows.append(
                    '{0:04}'.format(bad_count) +
                    f"|{row[1]}|0|{row[2].upper()}|{row[3].upper()}|"
                    f"{yesNo(row[4])}|{yesNo(row[5])}|{appointment}|{contact_client}|"
                    f"{row[10]}|{row[11]}|{row[12]}|"
                    f"{SITE_TIN}|{SITE_NPI}|{PROGRAM_NAME}|{row[13] if (len(self.headers) >= 14) else ''}"
                    f"|{row[14] if (len(self.headers) >= 15) else ''}|{row[15] if (len(self.headers) >= 16) else ''}"
                    f"|{row[16] if (len(self.headers) >= 17) else ''}|{row[17] if (len(self.headers) >= 18) else ''}"
                    f"|{row[18] if (len(self.headers) >= 19) else ''}|{row[19] if (len(self.headers) >= 20) else ''}"
                    f"|{row[20] if (len(self.headers) >= 21) else ''}")
                bad_count += 1
            else:
                rows.append(
                    '{0:04}'.format(counter) +
                    f"|{row[1]}|0|{row[2].upper()}|{row[3].upper()}|"
                    f"{yesNo(row[4])}|{yesNo(row[5])}|{appointment}|{contact_client}|"
                    f"{row[10]}|{row[11]}|{row[12]}|"
                    f"{SITE_TIN}|{SITE_NPI}|{PROGRAM_NAME}|{row[13] if (len(self.headers) >= 14) else ''}"
                    f"|{row[14] if (len(self.headers) >= 15) else ''}|{row[15] if (len(self.headers) >= 16) else ''}"
                    f"|{row[16] if (len(self.headers) >= 17) else ''}|{row[17] if (len(self.headers) >= 18) else ''}"
                    f"|{row[18] if (len(self.headers) >= 19) else ''}|{row[19] if (len(self.headers) >= 20) else ''}"
                    f"|{row[20] if (len(self.headers) >= 21) else ''}")
                counter += 1
            lists = [rows, bad_rows]
        return lists
