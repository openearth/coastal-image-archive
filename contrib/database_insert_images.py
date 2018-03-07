#!/usr/bin/env python

import os
import subprocess
import argparse
from image_format import ImageFormat
import MySQLdb
import datetime


class ImageList:
    image_list = None
    site = None
    siteid = None
    mmin = -1440
    database_default_file = '~/.my.cnf'

    def __init__(self, site, siteid=None, mmin=True):
        self.site = site
        if siteid:
            self.siteid = siteid
        else:
            self.siteid = site
        if mmin:
            self.set_mmin()
        else:
            self.mmin = 0
        self.retrieve_image_list()

        self.database_insert()

    def retrieve_image_list(self):
        # REMOTE_USER variable is work-around to not hard-code the user
        # just using ~ will try to use the local user
        remote_user = subprocess.check_output(['ssh', self.siteid, 'whoami']).strip()
        image_list = subprocess.check_output(['ssh', self.siteid,
                                              '~%s/bin/image_list.sh' % remote_user, '%+i' % self.mmin]
                                             ).strip().split('\n')
        self.image_list = image_list

    def set_mmin(self):
        db = MySQLdb.connect(read_default_file=self.database_default_file)

        cur = db.cursor()

        select_sql = "SELECT epoch FROM Images WHERE site='%s' ORDER BY epoch DESC LIMIT 1" % self.site

        cur.execute(select_sql)
        if cur.rowcount > 0:
            epoch = cur.fetchone()[0]
            dt = datetime.datetime.utcfromtimestamp(epoch)
            mmin = int((dt - datetime.datetime.utcnow()).total_seconds() / 60)
            self.mmin = mmin
        db.close()

    def database_insert(self):
        db = MySQLdb.connect(read_default_file=self.database_default_file)

        cur = db.cursor()
        n = 0
        for image in self.image_list:
            I = ImageFormat(filename=image, site=self.site)
            if I.format is None:
                continue
            select_sql = "SELECT location FROM Images WHERE location='%s'" % I.get_long()
            cur.execute(select_sql)
            if cur.rowcount == 0:
                insert_sql = "INSERT INTO Images (location,site,epoch,camera,type,dayminute) " + \
                             "VALUES ('%s', '%s', %i, %i, '%s', %i)" % (
                                 I.get_long(), self.site, I.epoch, I.camera, I.image_type, I.dayminute)
                cur.execute(insert_sql)
                db.commit()
                n += 1
        db.close()
        print datetime.datetime.utcnow().strftime('%c UTC')
        print "%i new images found on station %s (%s) over the last %i minutes" % (
            len(self.image_list), self.site, self.siteid, -self.mmin)
        print "details of %i new images added to the database" % n


def main():
    parser = argparse.ArgumentParser(description='Coastal Image filename database inserter.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', '--site', help='name of site')
    group.add_argument('-c', '--config-file', help='yml file containing site information')
    parser.add_argument('-i', '--site-id', help='id of site (defaults to name of site)')
    parser.add_argument('-a', '--all', action='store_true',
                        help='retrieve information of all images from remote station (default is incremental since the latest image found in the database)')

    args = parser.parse_args()
    mmin = not args.all

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
                IL = ImageList(site=site['site'], siteid=siteid, mmin=mmin)
        else:
            raise IOError('file not found: %s' % args.config_file)

    if args.site:
        IL = ImageList(site=args.site, siteid=args.site_id, mmin=mmin)


if __name__ == '__main__':
    main()