#!/usr/bin/env python

"""
Script to populate and update the table with most recent images
"""

import MySQLdb

database_default_file = '~/.my.cnf'


db = MySQLdb.connect(read_default_file=database_default_file)

cur = db.cursor()

site_select_sql = "SELECT site FROM Sites"

cur.execute(site_select_sql)
sites = []
if cur.rowcount > 0:
    sites = [item[0] for item in cur.fetchall()]

for site in sites:
        
    epoch_select_sql = "SELECT epoch FROM Images WHERE site='%s' and inarchive=1 ORDER BY epoch DESC limit 1" % site
    cur.execute(epoch_select_sql)
    epoch_gte = 0
    if cur.rowcount > 0:
        epoch_gte = int(cur.fetchone()[0])
        epoch_gte = epoch_gte - 86400 - epoch_gte % 60  # floor epoch__gte to minutes and go one day back

    images_type_sql = "SELECT DISTINCT type FROM Images WHERE site='%s' AND inarchive=1 AND epoch>=%i" % (site, epoch_gte)
    cur.execute(images_type_sql)
    images_types = []
    if cur.rowcount > 0:
        images_types = [item[0] for item in cur.fetchall()]

    for image_type in images_types:
        epoch_select_sql = "SELECT epoch FROM Images WHERE site='%s' and inarchive=1 and type='%s' ORDER BY epoch DESC limit 1" % (site, image_type)
        cur.execute(epoch_select_sql)
        epoch_gte = 0
        if cur.rowcount > 0:
            epoch_gte = int(cur.fetchone()[0])
            epoch_gte = epoch_gte - epoch_gte % 60  # floor epoch__gte to minutes

        mostrecent_delete_sql = "DELETE FROM MostRecentImages WHERE epoch<%i" % epoch_gte
        cur.execute(mostrecent_delete_sql)
        db.commit()

        images_select_sql = "SELECT location,type,camera,site,epoch FROM Images WHERE site='%s' AND inarchive=1 AND epoch>=%i AND type='%s'" % (site, epoch_gte, image_type)
        cur.execute(images_select_sql)
        if cur.rowcount > 0:
            mostrecentimages = cur.fetchall()
            for image in mostrecentimages:
                mostrecent_select_sql = "SELECT location FROM MostRecentImages WHERE site='%s' AND camera=%i AND type='%s'" % (image[-2], image[-3], image[1])
                cur.execute(mostrecent_select_sql)
                if cur.rowcount > 0:
                    location = cur.fetchone()[0]
                    if location != image[0]:
                        update_sql = "UPDATE MostRecentImages SET location='%s',epoch=%i WHERE site='%s' AND camera=%i AND type='%s'" % (image[0], image[-1], image[-2], image[-3], image[1])
                        cur.execute(update_sql)
                        db.commit()
                else:
                    insert_sql = "INSERT INTO MostRecentImages (location, type, camera, site, epoch) VALUES ('%s', '%s', %i, '%s', %i)" % image
                    cur.execute(insert_sql)
                    db.commit()

db.close()

