#!/usr/bin/env python3
import argparse
import logging
import os
import sys
from time import sleep

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from app.core.config import Config
from app.utils.helpers import GetCSV
from app.utils.logger import get_logger

cfg = Config()
env = "P" if cfg.environment.lower() == 'production' else "T"

INPUT_DIR = ''
OUTPUT_DIR = ''
PATTERN = ''
DEBUG = False
TIMEOUT = 0
RECURSIVE = False

parser = argparse.ArgumentParser(description='ETF Watchdog')
parser.add_argument('-i', '--input', help='Directory to watch for new files. Default is current directory.',
                    required=False, type=str, default=os.getcwd(), dest='INPUT_DIR', action='store', nargs='?',
                    const=os.getcwd(), metavar='WATCH_DIR')
parser.add_argument('-o', '--output', help='Directory to save converted files to. Default is current directory.',
                    required=False, type=str, default=os.getcwd(), dest='OUTPUT_DIR', action='store', nargs='?',
                    const=os.getcwd(), metavar='SAVE_DIR')
parser.add_argument('-p', '--pattern', help='Pattern to match. Default is "*.CSV".', required=False, type=str,
                    dest='PATTERN', default='*.csv')
parser.add_argument('-t', '--timeout', help='Timeout between checks in seconds. Default is 5 seconds.',
                    required=False, type=int, default=5, dest='TIMEOUT', action='store', nargs='?', const=5,
                    metavar='<timeout>')
parser.add_argument('-r', '--recursive', help='Search recursively for files matching pattern. Default is False.',
                    required=False, dest='RECURSIVE', action='store_true', default=False)
parser.add_argument('-d', '--debug', help='Set logging level to DEBUG.', required=False,
                    dest='DEBUG', action='store_true', default=False)
parser.add_argument('-v', '--version', help='Print version.', action='version', version='1.0')
args = parser.parse_args()

for arg in args.__dict__.keys():
    globals()[arg] = args.__dict__[arg]

PROCESSED_DIR = INPUT_DIR + '/processed'
BAD_DIR = INPUT_DIR + '/bad'

directories = [INPUT_DIR, OUTPUT_DIR, PROCESSED_DIR, BAD_DIR]
for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)


def process(event, file):
    process_logger = logging.getLogger()
    process_logger.info("--------------------------------------------------------------------------------------------")
    process_logger.info(f'Found new file: {file}. Starting TXT conversion.')
    sys.stdout.write('\n')
    file_name = file.split('/')[-1]
    try:
        csv = GetCSV(file)
        if len(csv.good) > 0:
            with open(OUTPUT_DIR + '/' + csv.filename, 'w') as f:
                for row in csv.good:
                    f.write(row.write_row() + '\n')
        if len(csv.bad) > 0:
            with open(INPUT_DIR + '/bad/BAD_ROWS_' + csv.filename.replace('.txt', '.csv'), 'w') as f:
                f.write(','.join(csv.error_headers) + '\n')
                for row in csv.bad:
                    f.write(','.join(row) + '\n')
            process_logger = logging.getLogger(csv.model.title())
            sys.stdout.write('\n')
            process_logger.warning(
                f'Failed to convert {len(csv.bad)} rows. '
                f'Saving bad rows to {"BAD_ROWS_" + csv.filename.replace(".txt", ".csv")}'
            )
        process_logger = logging.getLogger()
        process_logger.info(f'Successfully converted {len(csv.good)} rows.')
        sys.stdout.write('\n')
        process_logger.info(f'Moving {file} to {INPUT_DIR}/processed.')
        rename = INPUT_DIR + '/processed/' + file_name
        copy = 1
        while os.path.exists(rename):
            rename = INPUT_DIR + '/processed/' + \
                     file_name.split('.')[0] + '_' + str(copy) + '.' + file_name.split('.')[1]
            copy += 1
        os.replace(file, rename)
    except Exception as e:
        process_logger.error(f'Error converting {file} to TXT format. Error: {e}')


class MyHandler(PatternMatchingEventHandler):
    patterns = [PATTERN]

    def on_created(self, event):
        sleep(1)
        process(event, event.src_path)


if __name__ == '__main__':
    level = os.getenv('LOG_LEVEL').upper() or DEBUG
    logger = get_logger(level=level)

    logger.info("Starting Watchdog Server...")
    logger.info(" - Watching directory: " + INPUT_DIR)
    logger.info(" - Saving TXT files to: " + OUTPUT_DIR)
    logger.info(" - Pattern: " + PATTERN)
    logger.info(" - Timeout: " + str(TIMEOUT))
    logger.info(" - Recursive: " + str(RECURSIVE))

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, INPUT_DIR, recursive=RECURSIVE)
    observer.start()
    try:
        while True:
            if os.listdir(BAD_DIR):
                os.renames(BAD_DIR, BAD_DIR + ' (' + str(len(os.listdir(INPUT_DIR + '/bad'))) + ')')
                BAD_DIR = BAD_DIR + ' (' + str(len(os.listdir(INPUT_DIR + '/bad'))) + ')'
            sleep(TIMEOUT)
    except KeyboardInterrupt:
        logger.info("Stopping Watchdog Server...")
        observer.stop()
        logger.info("Watchdog Server stopped.")
    observer.join()
