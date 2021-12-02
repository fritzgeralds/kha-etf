#!/usr/bin/env python3
import sys
from time import sleep
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import argparse
import os
import shutil
from mailer import sendmail
import csv
from models import getCSV

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


def process(event):
    sys.stdout.write('\r' + 'Converting {} to TXT format.'.format(event.src_path.split('\\')[-1]))
    for file in os.listdir(indir):
        if file.endswith('.csv'):
            sys.stdout.write('\r' + 'Converting {} to TXT format.'.format(file))
            filename = file.split('.')[0]
            ext = file.split('.')[1]
            copy = 1
            while True:
                if os.path.exists(outdir + '\\' + filename + '.txt'):
                    filename = filename + '_' + str(copy)
                    copy += 1
                else:
                    break
            getCSV(indir + '\\' + file)

            shutil.copy(indir + '\\' + file, outdir + '\\' + filename + '.txt')

            filename = file.split('.')[0]
            if '{}'.format(file) in os.listdir(outdir):
                print('\nFile already exists. Skipping.')
            else:
                with open(os.path.join(indir, file), 'r') as csvfile:
                    reader = csv.reader(csvfile)
                    with open(os.path.join(outdir, file.split('.')[0] + '.txt'), 'w') as txtfile:
                        for row in reader:
                            txtfile.write('{}\n'.format(row[0]))
    sys.stdout.write('\r' + 'Converting {} to TXT format.'.format(event.src_path.split('\\')[-1]))
    print('\nConversion complete.')





    #         with open(os.path.join(indir, file), 'r', newline='\n') as csvfile:
    #             reader = csv.reader(csvfile, delimiter=',')
    #             line = 0
    #             with open(os.path.join(outdir, file.split('.')[0] + '.txt'), 'w') as f:
    #                 for row in reader:
    #                     if line == 0:
    #                         line += 1
    #                         continue
    #                     else:
    #                         f.write('|'.join(row[1:]) + '\n')
    #                         line += 1
    #         shutil.move(os.path.join(indir, file), os.path.join('./processed', file))
    # sys.stdout.flush()
    # sleep(1)
    # sys.stdout.write('...Done!\n')
    # sys.stdout.flush()
    # sleep(1)
    # # try:
    # #     shutil.copy(event.src_path, outdir + "\\" + ((event.src_path.split('\\')[-1]).split('.')[0]) + '.txt')
    # # except IOError as e:
    # #     print('Unable to copy file. {}'.format(e))
    # #     sendmail(subject='Conversion failure: {}'.format(event.src_path.split('\\')[-1], body=e))
    # # except Exception as e:
    # #     print('Unexpected error:', sys.exc_info()[0])
    # #     sendmail(subject='Unexpected error: {}'.format(event.src_path.split('\\')[-1], body=e))
    # print("Conversion complete. Submitting to KBH.\n")


class MyHandler(PatternMatchingEventHandler):
    patterns = [pattern]

    def on_created(self, event):
        print("New file \"{}\" has been created.".format(event.src_path.split('\\')[-1]))
        process(event)


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
