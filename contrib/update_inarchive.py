#!/usr/bin/env python

import os
import MySQLdb

db = MySQLdb.connect(read_default_file='~/.my.cnf')

cur = db.cursor()

select_sql = 'SELECT location FROM Images WHERE inarchive=0'

cur.execute(select_sql)
n = 0
print '%i rows selected' % cur.rowcount
for location in cur.fetchall():
    fullpath = '/data/images%s' % location[0]
    if os.path.exists(fullpath):
        update_sql = "UPDATE Images SET inarchive=1 WHERE location='%s'" % location[0]
        cur.execute(update_sql)
        n += 1

db.commit()
db.close()

print '%i new images available in archive' % n