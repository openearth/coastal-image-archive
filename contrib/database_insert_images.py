#!/usr/bin/env python

import os
import argparse
from image_format import ImageFormat
import MySQLdb
import datetime


class ImageList:
    filename = '/tmp/image_list.txt'
    image_list = None
    site = None
    siteid = None
    mmin = -1440
    cam_min = None
    cam_max = None
    database_default_file = '~/.my.cnf'

    def __init__(self, site, siteid=None, **kwargs):
        self.site = site
        if siteid:
            self.siteid = siteid
        else:
            self.siteid = site
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)
        self.set_mmin()
        self.create_image_list()
        self.read_image_list()
     
        self.database_insert()

    def _check_file_existance(self, filename):
        if not os.path.exists(filename):
            raise IOError('file not found: %s' % filename)

    def set_database_default_file(self, database_default_file):
        self._check_file_existance(database_default_file)
        self.database_default_file = database_default_file

    def create_image_list(self):
        # REMOTE_USER variable is work-around to not hard-code the user
        # just using ~ will try to use the local user
        os.system('REMOTE_USER=$(ssh %s whoami) && ssh %s ~$REMOTE_USER/bin/image_list.sh %+i > %s' % (self.siteid, self.siteid, self.mmin, self.filename))

    def read_image_list(self):
        self._check_file_existance(self.filename)
        with open(self.filename) as fobj:
            txt = fobj.read()
        self.image_list = txt.split()

    def set_mmin(self):
        self._check_file_existance(self.database_default_file)
        db = MySQLdb.connect(read_default_file=self.database_default_file)

        cur = db.cursor()

        where_clause = "site='%s'" % self.site
        if self.cam_min is not None:
            where_clause = '%s AND camera>=%i' % (where_clause, self.cam_min)
        if self.cam_max is not None:
            where_clause = '%s AND camera<=%i' % (where_clause, self.cam_max)

        select_sql = "SELECT epoch FROM Images WHERE %s ORDER BY epoch DESC LIMIT 1" % where_clause

        cur.execute(select_sql)
        if cur.rowcount > 0:
            epoch = cur.fetchone()[0]
            dt = datetime.datetime.utcfromtimestamp(epoch)
            mmin = int((dt - datetime.datetime.utcnow()).total_seconds() / 60)
            self.mmin = mmin
        db.close()

    def database_insert(self):
        self._check_file_existance(self.database_default_file)
        db = MySQLdb.connect(read_default_file=self.database_default_file)

        cur = db.cursor()
        n = 0
        for image in self.image_list:
            I = ImageFormat(filename=image, site=self.site)
            try:
                select_sql = "SELECT location FROM Images WHERE location='%s'" % I.get_long()
            except:
                print 'ERROR: filename: %s' % image
                continue
            cur.execute(select_sql)
            if cur.rowcount == 0:
                insert_sql = "INSERT INTO Images (location,site,epoch,camera,type,dayminute) " + \
                             "VALUES ('%s', '%s', %i, %i, '%s', %i)" % (I.get_long(), self.site, I.epoch, I.camera, I.image_type, I.dayminute)
                cur.execute(insert_sql)
                db.commit()
                n += 1
        db.close()
        print datetime.datetime.utcnow().strftime('%c UTC')
        print "%i new images found on station %s (%s) over the last %i minutes" % (len(self.image_list), self.site, self.siteid, -self.mmin)
        print "details of %i new images added to the database" % n


def main():
    parser = argparse.ArgumentParser(description='Coastal Image filename database inserter.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', '--site', help='name of site')
    group.add_argument('-c', '--config-file', help='yml file containing site information')
    parser.add_argument('-i', '--site-id', help='id of site (defaults to name of site)')
    parser.add_argument('-m', '--mysql-config', help='mysql config file (defaults to ~/.my.cnf)')

    args = parser.parse_args()

    if args.mysql_config:
        if os.path.exists(args.mysql_config):
            kwargs = {'database_default_file': args.mysql_config}
        else:
            raise IOError('file not found: %s' % args.mysql_config)
    else:
        kwargs = {}

    if args.config_file:
        if os.path.exists(args.config_file):
            import yaml
            with open(args.config_file, 'r') as stream:
                sites = yaml.load(stream)
            for site in sites['sites']:
                if 'id' in site:
                    siteid = site['id']
                else:
                    siteid = None
                cam_min, cam_max = None, None
                if 'cam_min' in site:
                    cam_min = site['cam_min']
                if 'cam_max' in site:
                    cam_max = site['cam_max']
                IL = ImageList(site=site['site'], siteid=siteid, cam_min=cam_min, cam_max=cam_max, **kwargs)
        else:
            raise IOError('file not found: %s' % args.config_file)

    if args.site:
        IL = ImageList(site=args.site, siteid=args.site_id, **kwargs)


if __name__ == '__main__':
    main()
