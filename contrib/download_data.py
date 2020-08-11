#!/usr/bin/env python

import os
import sys
import subprocess
import re
from image_format import ImageFormat
import MySQLdb
import datetime
import argparse


class Download:
    lock_file = '/opt/dim/download_data.lock'
    site = None
    limit = 20
    destination_dir = '/data/images'
    source_dir = None
    database_default_file = '~/.my.cnf'
    image_dirs = None
    sub_dirs = True
    started = None
    count = 0

    def __init__(self, site, source_dir, sub_dirs=True):
        self.site = site
        self.source_dir = source_dir
        self.sub_dirs = sub_dirs

        self.started = datetime.datetime.utcnow().strftime('%c UTC')
        self.check_lock()
        self.set_image_dirs()

    def check_lock(self):
        lock_path, lock_filename = os.path.split(self.lock_file)
        lock_file = subprocess.check_output(
            ['find', lock_path, '-name', lock_filename, '-mmin', '+60']).strip()
        if lock_file == self.lock_file:
            # kill old processes
            #    os.system("for pid in $(ps -ef | awk '/download_data.py/ {print $2}'); do kill -9 $pid; done")
            # remove lockfile
            os.system('rm %s' % self.lock_file)

        if os.path.exists(self.lock_file):
            sys.exit(0)
        else:
            os.system('touch %s' % self.lock_file)

    def _lock(self):
        os.system('touch %s' % self.lock_file)

    def _unlock(self):
        os.system('rm %s' % self.lock_file)

    def set_image_dirs(self):
        self.image_dirs = subprocess.check_output(['ssh', self.site, 'find', self.source_dir, '-type', 'd'])\
            .strip().split('\n')

    def scp(self, source, destination):
        cmd = 'scp -p  %s:%s %s' % (self.site, source, destination)
        if self.validate(cmd):
            os.system(cmd)
            if os.path.isfile(destination):
                return True
        else:
            print('INCORRECT:', cmd)
            return False

    def run(self):
        db = MySQLdb.connect(read_default_file=self.database_default_file)
        cur = db.cursor()
        select_sql = "select location from Images where site='%s' and inarchive=0 order by epoch desc;" % self.site
        cur.execute(select_sql)
        for item in cur.fetchall():
            if self.count > self.limit:
                break
            I = ImageFormat(item[0])
            destination_file = '%s%s' % (self.destination_dir, item[0])
            if not os.path.isfile(destination_file):
                if self.sub_dirs:
                    image_dir = os.path.join(self.source_dir, I.datetime.strftime('%Y.%j.%m%d'))
                else:
                    image_dir = self.source_dir
                if image_dir not in self.image_dirs:
                    continue
                fname = subprocess.check_output(['ssh', self.site, 'find', image_dir, '-name', I.get_short()]).strip()

                if fname == "":
                    continue
                if os.access(self.destination_dir, os.W_OK):
                    self.mkdir(os.path.dirname(destination_file))
                    status = self.scp(fname, destination_file)
                    if status:
                        self.count += 1

        db.close()

    def validate(self, scp_cmd):
        result = False
        digits = re.findall('\d+', scp_cmd)
        exts = re.findall('\.c\d{1,2}[\.\w]+', scp_cmd)
        check1 = len(digits) == 16
        check2 = len(exts) == 2
        if check1 and check2:
            check3 = digits[3] == digits[9]  # epoch time should be equal
            check4 = exts[0] == exts[1]  # extensions (including camera number) should be equal
            if check3 and check4:
                result = True

        return result

    def report(self):
        print(self.started)
        print('%i images downloaded from %s' % (self.count, self.site))

    @staticmethod
    def mkdir(path):
        if not os.path.isdir(path):
            os.system('mkdir -p %s' % path)


def main():
    parser = argparse.ArgumentParser(description='Coastal Image download manager.')
    parser.add_argument('-i', '--site-id', help='id of site (defaults to name of site)')
    parser.add_argument('-d', '--source-dir', help='source directory')
    parser.add_argument('-l', '--sub-dirs', action='store_true', help='True if source directory has date sub directories')

    args = parser.parse_args()

    D = Download(site=args.site_id, source_dir=args.source_dir, sub_dirs=args.sub_dirs)
    D.run()
    D.report()
    D._unlock()


if __name__ == '__main__':
    main()
