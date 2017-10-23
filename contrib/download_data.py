#!/usr/bin/env python

import os
from image_format import ImageFormat
import MySQLdb

site = 'zandmotor'
limit = 100

db = MySQLdb.connect(read_default_file='~/.my.cnf')
cur = db.cursor()
select_sql = "select * from Images where site='%s' and inarchive=0 order by epoch desc limit %i;" % (site, limit)
cur.execute(select_sql)

for item in cur.fetchall():
    I = ImageFormat(item[0])
    if not os.path.isfile('/data/%s/%s' % (site, I.get_short())):
        find_statement = 'find /argus -name "%s" -mmin +1' % I.get_short()
        os.system("ssh %s %s > /tmp/%s_file.txt" % (site, find_statement, site))
        with open("/tmp/%s_file.txt" % site) as fobj:
            fname = fobj.read().strip()
        os.system('scp %s:%s /data/%s' % (site, fname, site))