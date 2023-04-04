
from pathlib import Path
from rich import print as rprint
from functools import partial

import subprocess

def hash_file(file, hash_al='sha1'):
    """return hash of given file"""
    import hashlib
    hash_als = {'sha1': hashlib.sha1(),
                'sha256': hashlib.sha256(),
                'sha512': hashlib.sha512()
                }
    try:
        select_hash = hash_als[hash_al]
    except:
        raise Exception('unsupported hash algorithm')
    with open(file, 'rb') as f:
        while True:
            chunk = f.read(2048)
            if not chunk:
                break
            select_hash.update(chunk)
    return hash_al, select_hash.hexdigest()

class Directory():
    "represent a directory."

    def __init__(self, path):
        try:
            p = Path(path)
            self.path = p
        except:
            raise Exception('invalid path')

    @property
    def files(self):
        return [x for x in self.path.iterdir() if not x.is_dir()]

    @property
    def folders(self):
        return [x for x in self.path.iterdir() if x.is_dir()]

class Result():
    """result of backup check"""

    def __init__(self, file, back_dir, hash_compare=True, hash_al=None):
        try:
            stem = file.stem
            suffix = file.suffix
        except:
            raise Exception("get file name or suffix failed")
        self.file = file
        try:
            self.back_dir = Path(back_dir).expanduser().resolve()
        except:
            raise Exception('failed to parse backup directory')
        self.has_backup = False
        self.result_objs = []
        self.matches = []
        self.replicas = []
        self.hash_compare = hash_compare
        if hash_al:
            self.hash_al = hash_al
            self.hash_file = partial(hash_file, hash_al=self.hash_al)
        else:
            self.hash_al = 'sha1'
            self.hash_file = hash_file
        self._check()

    def _check(self):
        """check if a file (likely) has a backup.
        file should be a Path object."""

        result = subprocess.run(['plocate', self.back_dir, self.file.stem,], stdout=subprocess.PIPE)
        result = result.stdout.decode('utf-8').split('\n')
        result = [i.strip() for i in result if i]
        if result:
            for i in result:
                if i:
                    self.result_objs.append(Path(i))
            #self.result_objs = [ i for i in self.result_objs if i.resolve() != self.file.resolve()]
            for i in self.result_objs:
                if i.exists() and i.suffix == self.file.suffix:
                    self.matches.append(i)
        if self.matches:
            for i in self.matches:
                o_hash = self.hash_file(self.file)
                b_hash = self.hash_file(i)
                if o_hash == b_hash:
                    print(f'Original {self.hash_al} hash:', o_hash)
                    print(f'Backup {self.hash_al} hash:', b_hash)
                    self.replicas.append(i)
        if self.replicas:
            self.has_backup = True

    def remove(self):
        """remove a file which likely has backup files."""
        import os
        if self.has_backup:
            try:
                os.remove(self.file)
                if not self.file.exists():
                    print(self.file.resolve(), 'has been deleted')
            except:
                raise Exception('remove file failed')

def check(directory, back_dir, hash=None):
    files = Directory(directory).files
    has_backup = []
    has_no_backup = []
    for f in files:
        c = Result(f, back_dir, hash_al=hash)
        rprint(c.file)
        if c.has_backup:
            has_backup.append(c)
            rprint("[italic green]found backup files")
            print("likely backup list:")
            for i in c.matches:
                rprint(f"[italic blue]{i}")
        else:
            has_no_backup.append(c)
            rprint("[italic red]found no backup files")
        print('------------')
    return files, has_backup, has_no_backup
