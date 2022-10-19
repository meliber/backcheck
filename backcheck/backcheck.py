from core import Directory
from core import Result
from core import check
from rich import print as rprint

import argparse
import time

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='the path for check')
    parser.add_argument('--rm', action='store_true', help='remove file which has backup')
    args = parser.parse_args()
    files, has_backup, has_no_backup = check(args.path)
    n_files = len(files)
    n_has_backup = len(has_backup)
    n_has_no_backup = len(has_no_backup)
    if n_has_backup + n_has_no_backup != n_files:
        raise('some files has not been processd')
    print(f'number of files: {n_files}')
    print(f'number of files has backup: {n_has_backup}')
    print(f'number of files has no backup: {n_has_no_backup}')
    if args.rm:
        rprint("[red bold]files has backup will be deleted 5 seconds later, press 'Ctrl + C' to stop")
        time.sleep(5)
        for i in has_backup:
            c.remove()
