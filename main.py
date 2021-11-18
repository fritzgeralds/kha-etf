#!/usr/bin/env python3
import sys
from time import sleep
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import argparse
import os
import shutil
from mailer import sendmail

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
    input = args.input

if args.output:
    output = args.output

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
    sys.stdout.flush()
    sleep(1)
    for i in range(0,3):
        sys.stdout.write('.')
        sys.stdout.flush()
        sleep(1)
    try:
        shutil.copy(event.src_path, output + "\\" + ((event.src_path.split('\\')[-1]).split('.')[0]) + '.txt')
        print(output + "\\" + ((event.src_path.split('\\')[-1]).split('.')[0]) + '.txt')
    except IOError as e:
        print('Unable to copy file. {}'.format(e))
    except:
        print('Unexpected error:', sys.exc_info()[0])
    print("Conversion complete. Submitting to KBH.\n")


class MyHandler(PatternMatchingEventHandler):
    patterns = [pattern]

    def on_created(self, event):
        print("New file \"{}\" has been created.".format(event.src_path.split('\\')[-1]))
        process(event)


if __name__ == '__main__':
    print("Starting Watchdog Server...")
    print(" - Watching directory: " + input)
    print(" - Saving TXT files to: " + output)
    print(" - Pattern: " + pattern)
    print(" - Timeout: " + str(timeout))
    print(" - Recursive: " + str(recursive))

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, input, recursive=recursive)
    observer.start()
    try:
        while True:
            sleep(timeout)
    except KeyboardInterrupt:
        print("\nStopping Watchdog Server...")
        observer.stop()
        print("Watchdog Server stopped.")
    observer.join()