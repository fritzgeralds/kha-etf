import csv
import datetime as dt


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
                '%m-%d-%Y %I:%M:%S %p')
            row['Date of Birth Date'] = (dt.datetime.strptime(row['Date of Birth Date'],
                                                              '%m/%d/%Y')).strftime('%m-%d-%Y')
            rows.append(
                '{0:04}'.format(counter) +
                f"|{row['Date Created Time']}|1|{row['KHS ID']}|{row['CIN']}|"
                f"{row['Date of Birth Date']}|{row['Gender'][0]}|{row['Last Name']}|{row['First Name']}|"
                f"{row['Middle Name']}|{row['Email Address']}|{row['Member Mobile Phone Number?']}|"
                f"{row['Member Opt in for texting?']}|{row['Member Opt in for automated calls?']}|"
                f"{row['Address']}|{row['Address2']}|{row['City']}|{row['State']}|{row['ZIP Code']}|"
                f"SITE_TIN|SITE_NPI")
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
                '%m-%d-%Y %I:%M:%S %p')
            rows.append(
                '{0:04}'.format(counter) +
                f"|{row['Date Created Time']}|1|{row['KHS ID']}|{row['CIN']}|"
                f"{row['Member Next Visit Scheduled?']}|{row['NEXT VISITSCHEDULED']}|{row['Contact Role']}|"
                f"{row['Contact Role Other']}|{row['Project Start Date']}|{row['Project Start Date']}|"
                f"{row['Project Exit Date']}|{row['Enrollment Flag']}|"
                f"SITE_TIN|SITE_NPI|PROGRAM_NAME||||")
            counter += 1
        return rows

    def get_row_outreach(self):
        counter = 1
        rows = []
        for i in self.rows:
            row = {}
            for j in range(len(self.headers)):
                row[self.headers[j]] = i[j]
            row['Date Created Time'] = (dt.datetime.strptime(row['Date Created Time'], '%m/%d/%Y %H:%M')).strftime(
                '%m-%d-%Y %I:%M:%S %p')
            row['Date of Birth Date'] = (dt.datetime.strptime(row['Date of Birth Date'],
                                                              '%m/%d/%Y')).strftime('%m-%d-%Y')
            rows.append(
                '{0:04}'.format(counter) +
                f"|{row['Date Created Time']}|VOID|{row['KHS ID']}|{row['CIN']}|"
                f"{row['Date of Birth Date']}|{row['Gender'][0]}|{row['Last Name']}|{row['First Name']}|"
                f"{row['Middle Name']}|{row['Email Address']}|{row['Member Mobile Phone Number?']}|"
                f"MEM_HOME_PHONE|MEM_WORK_PHONE|{row['Address']}|{row['Address2']}|{row['City']}|"
                f"{row['State']}|{row['ZIP Code']}|SITE_TIN|SITE_NPI")
            counter += 1
        return rows
