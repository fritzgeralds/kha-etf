#!/usr/bin/env python3
from datetime import datetime
import sys
from time import sleep
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import argparse
import os
import re

from app.utils.helpers import get_type
from app.utils.helpers import *
from app.models.demographics import Demographics
from app.models.enrollment import Enrollment
from app.models.outreach import Outreach
from app.utils.helpers import GetCSV
from app.core.config import Config
# from mailer import sendmail ## for future failure alert email


cfg = Config()
env = "P" if cfg.environment.lower() == 'production' else "T"

parser = argparse.ArgumentParser(description='ETF Watchdog')
parser.add_argument('-i', '--input', help='Directory to watch for new files. Default is current directory.',
                    required=False, type=str, default=os.getcwd(), dest='indir', action='store', nargs='?',
                    const=os.getcwd(), metavar='WATCH_DIR')
parser.add_argument('-o', '--output', help='Directory to save converted files to. Default is current directory.',
                    required=False, type=str, default=os.getcwd(), dest='outdir', action='store', nargs='?',
                    const=os.getcwd(), metavar='SAVE_DIR')
parser.add_argument('-p', '--pattern', help='Pattern to match. Default is "*.CSV".', required=False, type=str,
                    dest='pattern', default='*.csv')
parser.add_argument('-t', '--timeout', help='Timeout between checks in seconds. Default is 5 seconds.',
                    required=False, type=int, default=5, dest='timeout', action='store', nargs='?', const=5,
                    metavar='<timeout>')
parser.add_argument('-r', '--recursive', help='Search recursively for files matching pattern. Default is False.',
                    required=False, dest='recursive', action='store_true', default=False)
args = parser.parse_args()

for arg in args.__dict__.keys():
    globals()[arg] = args.__dict__[arg]

if not os.path.exists(outdir):
    os.makedirs(outdir)
if not os.path.exists(indir + '\\processed'):
    os.makedirs(indir + '\\processed')


def process(event, file):
    file_name = file.split('\\')[-1]
    if file.endswith('.csv') and not file_name.startswith('BAD_'):
        sys.stdout.write('\r' + 'Converting {} to TXT format.'.format(file) + '\n')
        try:
            csv = GetCSV(file)
            if len(csv.good) > 0:
                sys.stdout.write('\r' + 'Found {} good rows.'.format(len(csv.good)) + '\n')
                with open(csv.filename, 'w') as f:
                    for row in csv.good:
                        f.write(row.write_row() + '\n')
                sys.stdout.write('\r' + 'Saved good rows to {}.'.format(csv.filename) + '\n')
            if len(csv.bad) > 0:
                sys.stdout.write('\r' + 'Found {} bad rows.'.format(len(csv.bad)) + '\n')
                with open('BAD_ROWS_' + csv.filename.replace('.txt', '.csv'), 'w') as f:
                    f.write(','.join(csv.error_headers) + '\n')
                    for row in csv.bad:
                        f.write(','.join(row) + '\n')
                sys.stdout.write('\r' + 'Saved bad rows to {}.'.format('BAD_ROWS_' + csv.filename.replace('.txt', '.csv')) + '\n')
        except Exception as e:
            print(e)
            sys.stdout.write('\r' + 'Error converting {} to TXT format.'.format(file) + '\n')
            return
        #     good_rows = []
        #     bad_rows = []
        #     row_count = 1
        #     id_index = 1
        #     # for row in csv.rows:
        #     #     if csv.model == 'demographic':
        #     #         pass
        #     #     if csv.model == 'emrollment':
        #     #         data = {
        #     #                 'id': "%04d" % id_index,
        #     #                 'date': format_date_time(row[3]),
        #     #                 'mem_id': row[4],
        #     #                 'cin': row[5],
        #     #                 'next_visit': yes_no(row[7]),
        #     #                 'next_visit_date': format_date(row[8]),
        #     #                 'role': get_index(row[9], CONTACT_ROLE),
        #     #                 'role_other': row[10],
        #     #                 'contact_date': format_date_time(row[11]),
        #     #                 'effective_date': format_date_time(row[11]),
        #     #                 'term_date': format_date_time(row[11]),
        #     #                 'enrollment_flag': yes_no(row[12]),
        #     #                 'disenrollment_reason': get_key(row[13], DISENROLLMENT_REASON),
        #     #             }
        #     if csv.model == 'demographic':
        #         for row in csv.rows:
        #             try:
        #                 good_rows.append(Demographics(**{
        #                     'id': "%04d" % id_index,
        #                     'date': format_date_time(row[3]),
        #                     'mem_id': row[4].upper(),
        #                     'cin': row[5].upper(),
        #                     'dob': format_date(row[7]),
        #                     'gender': get_gender(row[8]),
        #                     'last_name': row[9].title(),
        #                     'first_name': row[10].title(),
        #                     'middle_name': row[11].title(),
        #                     'email': row[12],
        #                     'opt_txt': yes_no(row[14]),
        #                     'opt_call': yes_no(row[15]),
        #                     'phone': {
        #                         'home': re.sub('\D', '', row[16]),
        #                         'work': re.sub('\D', '', row[17]),
        #                         'cell': re.sub('\D', '', row[13])
        #                     },
        #                     'address': {
        #                         'street': row[18],
        #                         'street2': row[19],
        #                         'city': row[20],
        #                         'state': row[21],
        #                         'zip': row[22]
        #                     }
        #
        #                 }).write_good_row())
        #                 id_index += 1
        #             except Exception as e:
        #                 sys.stdout.write('\r' + 'Error converting row {}: {}'.format(row_count, e) + '\n')
        #                 # sendmail(subject='Error converting row {}'.format(row_count),
        #                 #          body='Error converting row {}: {}'.format(row_count, e))
        #                 row.append(str(e).split('\n')[-1].split(' (')[0])
        #                 bad_rows.append(row)
        #             row_count += 1
        #     elif csv.model == 'enrollment':
        #         pass
        #     elif csv.model == 'outreach':
        #         pass
        #     else:
        #         sys.stdout.write('\r' + 'Error: Unknown model {}'.format(csv.model) + '\n')
        #         # sendmail(subject='Error: Unknown model {}'.format(csv.model),
        #         #          body='Error: Unknown model {}'.format(csv.model))
        #         bad_rows.append(row)
        #     if len(bad_rows) > 0:
        #         sys.stdout.write('\r' + 'Saving bad rows to {}'.format('BAD_' + csv.filename.replace('.txt', '.csv')) + '\n')
        #         with open('BAD_' + csv.filename.replace('.txt', '.csv'), 'w') as f:
        #             f.write(','.join(csv.error_headers) + '\n')
        #             for row in bad_rows:
        #                 f.write(','.join(row) + '\n')
        #     if len(good_rows) > 0:
        #         sys.stdout.write('\r' + 'Saving good rows to {}'.format(csv.filename) + '\n')
        #         with open(csv.filename, 'w') as f:
        #             for row in good_rows:
        #                 f.write(str(row) + '\n')
        #     sys.stdout.write('\r' + 'Moving {} to processed directory.'.format(file_name) + '\n')
        # except Exception as e:
        #     sys.stdout.write('\r' + 'Error processing {}: {}'.format(file_name, e) + '\n')
        #     # sendmail(subject='Error processing {}'.format(file),
        #     #          body='Error processing {}: {}'.format(file, e))
        # rename = indir + '\\processed\\' + file_name
        # copy = 1
        # while os.path.exists(rename):
        #     rename = indir + '\\processed\\' + file_name.split('.')[0] + '_' + str(copy) + '.' + file_name.split('.')[1]
        #     copy += 1
        # os.rename(file, rename)


class MyHandler(PatternMatchingEventHandler):
    patterns = [pattern]

    def on_created(self, event):
        if not event.src_path.split('\\')[-1].startswith('BAD_'):
            sleep(1)
            process(event, event.src_path)
        # print("New file \"{}\" has been created.".format(event.src_path.split('\\')[-1]))
        # sleep(1)
        # process(event, event.src_path)


if __name__ == '__main__':
    print("Starting Watchdog Server...")
    print(" - Watching directory: " + indir)
    print(" - Saving TXT files to: " + outdir)
    print(" - Pattern: " + pattern)
    print(" - Timeout: " + str(timeout))
    print(" - Recursive: " + str(recursive))

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, indir, recursive=recursive)
    observer.start()
    try:
        while True:
            sleep(timeout)
    except KeyboardInterrupt:
        print("\nStopping Watchdog Server...")
        observer.stop()
        print("Watchdog Server stopped.")
    observer.join()
