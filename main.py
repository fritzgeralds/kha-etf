#!/usr/bin/env python3
from datetime import datetime
import sys
from time import sleep
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import argparse
import os
import shutil
from app.models import GetCSV
from app.config import Config
# from mailer import sendmail ## for future failure alert email

cfg = Config()
env = "T" if cfg.environment.lower() == 'testing' else "P"

parser = argparse.ArgumentParser(description='ETF Watchdog')
parser.add_argument('-i', help='Directory to watch for new files. Default is current directory.',
                    required=False, type=str, default=os.getcwd(), dest='input', action='store', nargs='?',
                    const=os.getcwd(), metavar='WATCH_DIR')
parser.add_argument('-o', help='Directory to save converted files to. Default is current directory.',
                    required=False, type=str, default=os.getcwd(), dest='output', action='store', nargs='?',
                    const=os.getcwd(), metavar='SAVE_DIR')
parser.add_argument('-p', help='Pattern to match. Default is "*.CSV".', required=False, type=str,
                    dest='pattern', default='*.csv')
parser.add_argument('-t', help='Timeout between checks in seconds. Default is 5 seconds.',
                    required=False, type=int, default=5, dest='timeout', action='store', nargs='?', const=5,
                    metavar='<timeout>')
parser.add_argument('-r', help='Search recursively for files matching pattern. Default is False.',
                    required=False, dest='recursive', action='store_true', default=False)
args = parser.parse_args()

if args.input:
    indir = args.input

if args.output:
    outdir = args.output

if args.pattern:
    pattern = args.pattern

if args.timeout:
    timeout = args.timeout

if args.recursive:
    recursive = True
else:
    recursive = False

if not os.path.exists(outdir):
    os.makedirs(outdir)
    if not os.path.exists(indir + '\\processed'):
        os.makedirs(indir + '\\processed')


def process(event, file):
    if file.endswith('.csv'):
        sys.stdout.write('\r' + 'Converting {} to TXT format.'.format(file))
        copy = 1
        try:
            conversion = GetCSV(file)
            if 'Enrollment ID' in conversion.headers[1]:
                filename = 'HOUSINGAUTH24STCSS_KHS_CSS_ENROLLMENT_' + env + '_' + \
                           datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
                while True:
                    if os.path.exists(outdir + '\\' + filename + '.txt'):
                        filename = filename + '_' + str(copy)
                        copy += 1
                    else:
                        break
                with open(outdir + '\\' + filename + '.txt', 'w') as f:
                    rows = conversion.get_row_enrollment()
                    for row in rows:
                        f.write(row + '\n')
            elif 'General ID' in conversion.headers[1]:
                filename = 'HOUSINGAUTH24STCSS_KHS_CSS_DEMOGRAPHICS_' + env + '_' + \
                           datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
                while True:
                    if os.path.exists(outdir + '\\' + filename + '.txt'):
                        filename = filename + '_' + str(copy)
                        copy += 1
                    else:
                        break
                with open(outdir + '\\' + filename + '.txt', 'w') as f:
                    rows = conversion.get_row_demographics()
                    for row in rows:
                        f.write(row + '\n')
            elif 'Outreach' in conversion.headers[1]:
                filename = 'HOUSINGAUTH24STCSS_KHS_CSS_OUTREACH_' + env + '_' + \
                           datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
                while True:
                    if os.path.exists(outdir + '\\' + filename + '.txt'):
                        filename = filename + '_' + str(copy)
                        copy += 1
                    else:
                        break
                with open(outdir + '\\' + filename + '.txt', 'w') as f:
                    rows = conversion.get_row_outreach()
                    for row in rows:
                        f.write(row + '\n')
            else:
                print('\n' + 'Error: File {} does not contain a valid header.'.format(file.split('\\')[-1]))
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
