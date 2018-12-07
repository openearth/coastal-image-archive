#!/usr/bin/env python

import os
# import MySQLdb
import argparse

# defaults
DEFAULT_IMAGES_DIR = '/data/images'
DEFAULT_MYSQL_DEFAULT_FILE = '~/.my.cnf'


def update_inarchive(images_dir=DEFAULT_IMAGES_DIR, mysql_default_file=DEFAULT_MYSQL_DEFAULT_FILE):
    """
    Update inarchive column of MySQL database where it is 0 and the related image appears to be available.

    :param images_dir: root directory where images are stored
    :param mysql_default_file: read_default_file defining the database connection
    :return:
    """

    # connect to database
    db = MySQLdb.connect(read_default_file=mysql_default_file)

    cur = db.cursor()

    # execute select query to find all images where inarchive=0
    select_sql = 'SELECT location FROM Images WHERE inarchive=0'
    cur.execute(select_sql)

    print('%i rows selected' % cur.rowcount)

    # initialize counter n
    n = 0
    for record in cur.fetchall():
        # construct full path
        fullpath = os.path.join(images_dir, record[0])

        if os.path.exists(fullpath):
            # execute update statement to set inarchive=1
            update_sql = "UPDATE Images SET inarchive=1 WHERE location='%s'" % record[0]
            cur.execute(update_sql)

            # counter + 1
            n += 1

    # commit and close database connection
    db.commit()
    db.close()

    print('%i new images available in archive' % n)


def main():
    parser = argparse.ArgumentParser(description='Coastal Image MySQL database updater. Update inarchive column of MySQL database where it is 0 and the related image appears to be available')
    parser.add_argument('-d', '--images-dir', default=DEFAULT_IMAGES_DIR, help='root directory where images are stored')
    parser.add_argument('-m', '--mysql-default-file', default=DEFAULT_MYSQL_DEFAULT_FILE, help='read_default_file defining the database connection')

    args = parser.parse_args()

    update_inarchive(images_dir=args.images_dir, mysql_default_file=args.mysql_default_file)


if __name__ == '__main__':
    main()