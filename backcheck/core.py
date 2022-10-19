
from pathlib import Path
from rich import print as rprint

import subprocess
import argparse

class Directory():
    "represent a directory."

    def __init__(self, path):
        try:
            p = Path(path)
            self.path = p
        except:
            raise('invalid path')

    @property
    def files(self):
        return [x for x in self.path.iterdir() if not x.is_dir()]

    @property
    def folders(self):
        return [x for x in self.path.iterdir() if x.is_dir()]

class Result():
    """result of backup check"""

    def __init__(self, file):
        try:
            stem = file.stem
            suffix = file.suffix
        except:
            raise("get file name or suffix failed")
        self.file = file
        self.has_backup = False
        self.result_objs = []
        self.matches = []
        self._check()

    def _check(self):
        """check if a file (likely) has a backup.
        file should be a Path object."""

        result = subprocess.run(['plocate', self.file.stem,], stdout=subprocess.PIPE)
        result = result.stdout.decode('utf-8').split('\n')
        result = [i.strip() for i in result if i]
        if result:
            for i in result:
                if i:
                    self.result_objs.append(Path(i))
            self.result_objs = [ i for i in self.result_objs if i.resolve() != self.file.resolve()]
            for i in self.result_objs:
                if i.exists() and i.suffix == self.file.suffix:
                    self.matches.append(i)
        if self.matches:
            self.has_backup = True

    def remove(self):
        """remove a file which likely has backup files."""
        import os
        if self.has_backup and self.file.exists():
            try:
                os.remove(self.file)
                if not self.file.exists():
                    print(self.file.resolve(), 'has been deleted')
            except:
                raise('remove file failed')

def check(directory):
    files = Directory(directory).files
    has_backup = []
    has_no_backup = []
    for f in files:
        c = Result(f)
        rprint(c.file)
        if c.has_backup:
            has_backup.append(c)
            rprint("[italic green]found backup files")
            print("likely backup list:")
            for i in c.matches:
                rprint("[italic blue]{}".format(i))
        else:
            has_no_backup.append(c)
            rprint("[italic red]found no backup files")
        print('------------')
    return files, has_backup, has_no_backup
