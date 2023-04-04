#!/bin/env python3

from backcheck.core import Directory
from backcheck.core import Result
from backcheck.core import check
from rich import print as rprint

import argparse
import time

def backcheck(check_dir, back_dir, rm=False):
    files, has_backup, has_no_backup = check(check_dir, back_dir)
    n_files = len(files)
    n_has_backup = len(has_backup)
    n_has_no_backup = len(has_no_backup)
    if n_has_backup + n_has_no_backup != n_files:
        raise Exception('some files has not been processd')
    print(f'number of files: {n_files}')
    print(f'number of files has backup: {n_has_backup}')
    print(f'number of files has no backup: {n_has_no_backup}')
    if rm:
        rprint("[red bold]files has backup will be deleted 5 seconds later, press 'Ctrl + C' to stop")
        time.sleep(5)
        for i in has_backup:
            i.remove()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('check_dir', help='the directory for check')
    parser.add_argument('back_dir', help='backup directory for check against, where backups reside')
    parser.add_argument('--rm', action='store_true', help='remove files in check_dir which have backup')
    args = parser.parse_args()
    backcheck(args.check_dir, args.back_dir, args.rm)
