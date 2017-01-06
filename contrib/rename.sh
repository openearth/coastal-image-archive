#!/bin/bash
#
# Script to rename the imported images
#
# Changelog
# Version  Date        Author    Remarks
# 1.0      2016-10-24  J. Baten  Initial version
# 1.1      2016-11-11  J. Baten  Added SQL insert into database, Added dayminute column calculation, corrected handling of camera number
#
# The renaming of the files is as follows:
# Original short format: 1476099002.c8.snap.jpg meaning: 
# <epoch time>.c<camera #>.<image type: snap|timex|min|max>.jpg
# Should be converted to Long format: <epoch time>.<weekday>.<month>.<day>_<hour>_<min>_<sec>.UTC.<year>.<station>.c<camera #>.< image type: snap|timex|min|max>.jpg
# <epoch time>.<weekday>.<month>.<day>_<hour>_<min>_<sec>.UTC.<year>.<station>.c<camera #>.< image type: snap|timex|min|max>.jpg
# 
# Files are located on the fieldstation in /somedir/images/<dir>
# 
# The format of <dir> is year in 4 digits, <dot> daynumber <dot> month+day concattenated in 4 characters.
#
# Script is called with 2 arguments:
# Argument 1 is the complete path of the imported image file.
# Argument 2 is the path of the work directory.
# Argument 3 is the name/code of the station.

# Example name of imported image:
# /home/dim/data/dim-work/ZANDMOTOR/20161021-094419-GMT/fromSource/zandmotor/images/2016.291.1017/1476690829.c2.snap.jpg


function usage {
  echo "This script renames files."
  echo "Original input format:  <epoch time>.c<camera #>.<image type: snap|timex|min|max|stack><extension .jpg|.ras.gz>"
  echo "Output filename format: <epoch time>.<weekday>.<month>.<day>_<hour>_<min>_<sec>.UTC.<year>.<station>.c<camera #>.< image type: snap|timex|min|max><extension .jpg|.ras.gz>"
  echo 
  echo "To do this 3 arguments are needed:"
  echo "First argument: complete path of the imported image file."
  echo "Second argument: path of the work directory."
  echo "Third argument: name/code of the station."
}

# Check that all 3 arguments are present
if [ $# -ne 3 ]
then
  echo "FATAL: Not enough arguments provided!"
  logger "FATAL: Not enough arguments provided!"
  usage
  exit
fi
# Check that inputfile exists
if [ ! -f $1 ]
then
  echo "FATAL: input file $1 not found!"
  logger "FATAL: input file $1 not found!"
  usage
  exit
fi
# Check that destination directory exists
if [ ! -d $2 ]
then
  echo "FATAL: No destination directory $2 found."
  logger "FATAL: No destination directory $2 found."
  usage
  exit
fi

# save IFS
OLDIFS="${IFS}"
# Split original name on array bases on 
IFS='/' read -r -a NAMEARRAY <<< "${1}"

# Get name of image 
FILENAME=$(basename ${1})
SOURCEFILE=$1
STATION=$3

echo "Filename found : ${FILENAME}"

NEWFILEPATH=$( python ~/bin/image_format.py --site ${STATION} ${FILENAME})
NEWFILENAME=$(basename ${NEWFILEPATH})

DESTINATIONDIR=$(dirname "$2${NEWFILEPATH}")

mkdir -p "${DESTINATIONDIR}"

echo "Moving ${SOURCEFILE} to ${DESTINATIONDIR}/${NEWFILENAME}"
logger "Moving ${SOURCEFILE} to ${DESTINATIONDIR}/${NEWFILENAME}"

mv  "${SOURCEFILE}"   "${DESTINATIONDIR}/${NEWFILENAME}"
ret=$?
if [ "$ret" -ne 0 ]
then
  # move was not successful. Let's tell someone
  logger "Last move of ${SOURCEFILE} to ${DESTINATIONDIR}/${NEWFILENAME} was NOT successful"
fi

# Done







