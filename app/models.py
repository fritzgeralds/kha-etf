import csv
import re
import datetime as dt


def yesNo(value):
    if value == 'Yes':
        return '1'
    else:
        return '0'

def getIndex(value, list):
    for i in list:
        if i.lower() == value.lower():
            return int(list.index(i)) + 1
    return

DATE_RE = r"^([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])($| .+$)"

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

class GetCSV(object):
    def __init__(self, filename):
        self.name = filename.split('.')[0]
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            self.rows = [row for row in reader]
            self.headers = self.rows[0]
            self.rows = self.rows[1:]

    def get_row_demographics(self):
        counter = 1
        rows = []
        for i in self.rows:
            row = {}
            for j in range(len(self.headers)):
                row[self.headers[j]] = i[j]
            row['Date Created Time'] = (dt.datetime.strptime(row['Date Created Time'], '%m/%d/%Y %H:%M')).strftime(
                '%m-%d-%Y %H:%M:%S')
            row['Date of Birth Date'] = (dt.datetime.strptime(row['Date of Birth Date'],
                                                              '%m/%d/%Y')).strftime('%m-%d-%Y')
            rows.append(
                '{0:04}'.format(counter) +
                f"|{row['Date Created Time']}|1|{row['KHS ID']}|{row['CIN']}|"
                f"{row['Date of Birth Date']}|{row['Gender'][0]}|{row['Last Name']}|{row['First Name']}|"
                f"{row['Middle Name']}|{row['Email Address']}|{row['Member Mobile Phone Number?']}|"
                f"{row['Member Opt in for texting?']}|{row['Member Opt in for automated calls?']}|"
                f"{row['Address']}|{row['Address2']}|{row['City']}|{row['State']}|{row['ZIP Code']}|"
                f"{SITE_TIN}|{SITE_NPI}")
            counter += 1
        return rows

    def get_row_enrollment(self):
        counter = 1
        rows = []
        for i in self.rows:
            row = {}
            for j in range(len(self.headers)):
                row[self.headers[j]] = i[j]
            row['Date Created Time'] = (dt.datetime.strptime(row['Date Created Time'], '%m/%d/%Y %H:%M')).strftime(
                                        '%m-%d-%Y %H:%M:%S')
            if row['NEXT VISITSCHEDULED'] != '':
                row['NEXT VISITSCHEDULED'] = (dt.datetime.strptime(row['NEXT VISITSCHEDULED'],
                                               '%m/%d/%Y')).strftime('%m-%d-%Y')
            if row['Project Start Date'] != '':
                row['Project Start Date'] = (dt.datetime.strptime(row['Project Start Date'], '%m/%d/%Y')).strftime(
                                              '%m-%d-%Y')
            if row['Project Exit Date'] != '':
                row['Project Exit Date'] = (dt.datetime.strptime(row['Project Exit Date'],
                                               '%m/%d/%Y')).strftime('%m-%d-%Y')
            rows.append(
                '{0:04}'.format(counter) +
                f"|{row['Date Created Time']}|1|{row['KHS ID']}|{row['CIN']}|"
                f"{yesNo(row['Member Next Visit Scheduled?'])}|{row['NEXT VISITSCHEDULED']}|{row['Contact Role']}|"
                f"{row['Contact Role Other']}|{row['Project Start Date']}|{row['Project Start Date']}|"
                f"{row['Project Exit Date']}|{row['Enrollment Flag']}|"
                f"{SITE_TIN}|{SITE_NPI}|{PROGRAM_NAME}||||")
            counter += 1
        return rows

    def get_row_outreach(self):
        counter = 1
        rows = []
        for i in self.rows:
            row = {}
            for j in range(len(self.headers)):
                row[self.headers[j]] = i[j]
            row['Added Date'] = (dt.datetime.strptime(row['Added Date'], '%Y-%m-%d')).strftime(
                '%m-%d-%Y %H:%M:%S')
            row['Appointment Date'] = (dt.datetime.strptime(row['Appointment Date'],
                                                            '%Y-%m-%d')).strftime('%m-%d-%Y')
            row['Attempt to contact Client Date'] = (dt.datetime.strptime(row['Attempt to contact Client Date'],
                                                                          '%Y-%m-%d')).strftime('%m-%d-%Y')
            if row['Attempt to contact Client Result'] != '':
                row['Attempt to contact Client Result'] = getIndex(row['Attempt to contact Client Result'], ATTEMPT_RESULT)
            else:
                row['Attempt to contact Client Result'] = ''
            if row['Attempt to contact client Unsuccessful Disposition'] != '':
                row['Attempt to contact client Unsuccessful Disposition'] = getIndex(
                    row['Attempt to contact client Unsuccessful Disposition'], ATTEMPT_UNSUCCESFUL_DISPOSITION)
            else:
                row['Attempt to contact client Unsuccessful Disposition'] = ''
            if row['Attempt to contact client Successful Disposition'] != '':
                row['Attempt to contact client Successful Disposition'] = getIndex(
                    row['Attempt to contact client Successful Disposition'], ATTEMPT_SUCCESFUL_DISPOSITION)
            else:
                row['Attempt to contact client Successful Disposition'] = ''
            rows.append(
                '{0:04}'.format(counter) +
                f"|{row['Added Date']}|1|{row['KHS ID']}|{row['CIN']}|"
                f"{yesNo(row['Appointment Rescheduled'])}|{yesNo(row['Appointment Cancelled'])}|{row['Appointment Date']}|{row['Attempt to contact Client Date']}|"
                f"{row['Attempt to contact Client Result']}|{row['Attempt to contact client Unsuccessful Disposition']}|{row['Attempt to contact client Successful Disposition']}|"
                f"|{SITE_TIN}|{SITE_NPI}|{PROGRAM_NAME}||||")
            counter += 1
        return rows
