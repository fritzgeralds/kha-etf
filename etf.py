#!/usr/bin/env python3
from datetime import datetime
import sys
from time import sleep
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import argparse
import os
import shutil
from app.utils.helpers import get_type
from app.models import GetCSV, GetType
from app.core.config import Config
# from mailer import sendmail ## for future failure alert email


cfg = Config()
env = "T" if cfg.environment.lower() == 'testing' else "P"

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
    if file.endswith('.csv'):
        sys.stdout.write('\r' + 'Converting {} to TXT format.'.format(file) + '\n')
        try:
            csv_type = get_type(file)
            conversion = GetCSV(file, outdir)
            good_rows = []
            bad_rows = []
            filename = ''
            if csv_type == 'demographics':
                filename = 'KERNHOUSINGAUTH_KHS_NONPROGRAM_DEMOGRAPHIC_' + env + '_' + \
                           datetime.strftime(datetime.now(), '%Y%m%d%H%M%S') + '.txt'

            if 'Enrollment ID' in ftype.headers:
                filename = 'HOUSINGAUTH24STCSS_KHS_CSS_ENROLLMENT_' + env + '_' + \
                           datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
                good_rows, bad_rows = conversion.get_row_enrollment()
            elif 'General ID' in ftype.headers:
                filename = 'KERNHOUSINGAUTH_KHS_NONPROGRAM_DEMOGRAPHIC_' + env + '_' + \
                           datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
                good_rows, bad_rows = conversion.get_row_demographics()
            elif 'Assessment ID' in ftype.headers:
                filename = 'HOUSINGAUTH24STCSS_KHS_CSS_OUTREACH_' + env + '_' + \
                           datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
                good_rows, bad_rows = conversion.get_row_outreach()
            else:
                print('\n' + 'Error: File {} does not contain a valid header.'.format(file.split('\\')[-1]))
            if filename:
                if good_rows:
                    with open(outdir + '\\' + filename + '.txt', 'w') as f:
                        for row in good_rows:
                            f.write(row + '\n')
                if bad_rows:
                    with open(outdir + '\\BAD_ROWS_' + filename + '.txt', 'w') as f:
                        for row in bad_rows:
                            f.write(row + '\n')
            shutil.move(os.path.join(indir, file.split('\\')[-1]), os.path.join(indir + '\\processed', file.split('\\')[-1]))
        except Exception as e:
            print(e)
    print('\nConversion complete.')


class MyHandler(PatternMatchingEventHandler):
    patterns = [pattern]

    def on_created(self, event):
        print("New file \"{}\" has been created.".format(event.src_path.split('\\')[-1]))
        sleep(1)
        process(event, event.src_path)


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
