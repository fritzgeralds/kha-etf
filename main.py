#!/usr/bin/env python3
import argparse
import contextlib
import logging
import os
import shutil
import sys
from time import sleep

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from app.core.config import Config
from app.core.logger import get_logger
from app.utils.helpers import GetCSV

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
parser.add_argument('-d', '--debug', help='Set logging level to DEBUG.', required=False,
                    dest='debug', action='store_true')
args = parser.parse_args()

for arg in args.__dict__.keys():
    globals()[arg] = args.__dict__[arg]

if not os.path.exists(outdir):
    os.makedirs(outdir)
if not os.path.exists(indir + '\\processed'):
    os.makedirs(indir + '\\processed')
if not os.path.exists(os.getcwd() + '\\logs'):
    os.makedirs(os.getcwd() + '\\logs')


def process(event, file):
    logger = logging.getLogger()
    logger.info("-----------------------------------------------------------------------------------------------------")
    logger.info(f'Found new file: {file}. Starting TXT conversion.')
    sys.stdout.write('\n')
    file_name = file.split('\\')[-1]
    try:
        csv = GetCSV(file)
        if len(csv.good) > 0:
            with open(csv.filename, 'w') as f:
                for row in csv.good:
                    f.write(row.write_row() + '\n')
        if len(csv.bad) > 0:
            with open('BAD_ROWS_' + csv.filename.replace('.txt', '.csv'), 'w') as f:
                f.write(','.join(csv.error_headers) + '\n')
                for row in csv.bad:
                    f.write(','.join(row) + '\n')
            logger = logging.getLogger(csv.model.title())
            sys.stdout.write('\n')
            logger.warning(f'Failed to convert {len(csv.bad)} rows. Saving bad rows to'
                           f' {"BAD_ROWS_" + csv.filename.replace(".txt", ".csv")}')
        logger = logging.getLogger()
        logger.info(f'Successfully converted {len(csv.good)} rows.')
        sys.stdout.write('\n')
        logger.info(f'Moving {file} to {indir}\\processed.')
        rename = indir + '\\processed\\' + file_name
        copy = 1
        while os.path.exists(rename):
            rename = indir + '\\processed\\' + file_name.split('.')[0] + '_' + str(copy) + '.' + file_name.split('.')[1]
            copy += 1
        os.replace(file, rename)
    except Exception as e:
        logger.error(f'Error converting {file} to TXT format. Error: {e}')


class MyHandler(PatternMatchingEventHandler):
    patterns = [pattern]

    def on_created(self, event):
        if not event.src_path.split('\\')[-1].startswith('ABAD_'):
            sleep(1)
            process(event, event.src_path)


if __name__ == '__main__':
    level = os.getenv('LOG_LEVEL') or debug
    logger = get_logger(level=level)

    logger.info("Starting Watchdog Server...")
    logger.info(" - Watching directory: " + indir)
    logger.info(" - Saving TXT files to: " + outdir)
    logger.info(" - Pattern: " + pattern)
    logger.info(" - Timeout: " + str(timeout))
    logger.info(" - Recursive: " + str(recursive))

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, indir, recursive=recursive)
    observer.start()
    try:
        while True:
            sleep(timeout)
    except KeyboardInterrupt:
        logger.info("Stopping Watchdog Server...")
        observer.stop()
        logger.info("Watchdog Server stopped.")
    observer.join()
