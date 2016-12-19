#!/bin/bash
#
# Script to check the integrity of the database for the records added today 
#
# Changelog
# Version  Date        Author    Remarks
# 1.0      2016-10-24  J. Baten  Initial version
#
# Script is called with 0 arguments:
#
# Example record
# MariaDB [SiteImages]> select * from Images limit 1;
# +------------------------------------------------------------------------------------+------+------------+--------+-------+-----------+
# | location                                                                           | site | epoch      | camera | type  | dayminute |
# +------------------------------------------------------------------------------------+------+------------+--------+-------+-----------+
# | /sete/2011/c1/103_Apr.13/1302694201.Wed.Apr.13_11_30_01.UTC.2011.sete.c1.snap.jpg  | sete | 1302694201 |      1 | snap  |       690 |
# +------------------------------------------------------------------------------------+------+------------+--------+-------+-----------+

DBUSER="root"
DATABASE="SiteImages"
DBTABLE="Images"
DATE="$( date +%Y-%m-%d )"


# Build SQL query string
SQL="select location  from Images where date(from_unixtime(epoch)) = date('${DATE}') order by  epoch;"

#RESULT=$( mysql -h localhost -u "${DBUSER}"  --database="${DATABASE}" -e "${SQL}" 2>&1 )

for IMAGEFILE in $(  mysql -h localhost -u "${DBUSER}"  --database="${DATABASE}" -e "${SQL}" 2>&1 )
do
  # Check if file exists. If yes, okay, if not, log error.
  if [ -f $IMAGEFILE ]
  then
    # if exists, that would be nice. We do nothing
    echo "${IMAGEFILE} does exist. That is good."
  else
    # If not exists, bad file! Bad, bad file!
    echo "${IMAGEFILE} does NOT exist. That is bad."
    logger "check-db-integrity-for-today.sh: ERROR: I did not find the file mentioned in the database. File: ${IMAGEFILE}" 
  fi 

done

# Done







