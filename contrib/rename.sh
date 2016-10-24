#!/bin/bash
#
# Script to rename the imported images
#
# Version: 1.0
# Date: 2016-10-24
# Author: J. Baten
#
# The renaming of the files is as follows:
# Original short format: 1476099002.c8.snap.jpg meaning: 
# <epoch time>.c<camera #>.<image type: snap|timex|min|max>.jpg
# Should be converted to Long format: <epoch time>.<weekday>.<month>.<day>_<hour>_<min>_<sec>.UTC.<year>.<station>.c<camera #>.< image type: snap|timex|min|max>.jpg
# <epoch time>.<weekday>.<month>.<day>_<hour>_<min>_<sec>.UTC.<year>.<station>.c<camera #>.< image type: snap|timex|min|max>.jpg
# 
# Files are located on the fieldstation in /argus/images/<dir>
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
  echo "Original input format:  <epoch time>.c<camera #>.<image type: snap|timex|min|max>.jpg"
  echo "Output filename format: <epoch time>.<weekday>.<month>.<day>_<hour>_<min>_<sec>.UTC.<year>.<station>.c<camera #>.< image type: snap|timex|min|max>.jpg"
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
  echo "FATAL: input file not found!"
  logger "FATAL: input file not found!"
  usage
  exit
fi
# Check that destination directory exists
if [ ! -d $2 ]
then
  echo "FATAL: No destiniation directory found."
  logger "FATAL: No destiniation directory found."
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

# Split FILENAME into parts to get epoch
IFS='.' read -r -a FILEARRAY <<< "${FILENAME}"

EPOCHTIME=${FILEARRAY[0]}
CAMERA=${FILEARRAY[1]}
IMAGETYPE=${FILEARRAY[2]}

# Split epochtime in components to insert into string
DATESTRINGPART=$(date -d @${EPOCHTIME} "+%a.%m.%d_%H_%M_%S.UTC.%Y")

# <epoch time>.<weekday>.<month>.<day>_<hour>_<min>_<sec>.UTC.<year>.<station>.c<camera #>.< image type: snap|timex|min|max>.jpg
NEWFILENAME="${FILEARRAY[0]}.${DATESTRINGPART}.${STATION}.${CAMERA}.${IMAGETYPE}.jpg"

echo "Moving ${FILENAME} to ${NEWFILENAME}"
logger "Moving ${FILENAME} to ${NEWFILENAME}"

mv  ${SOURCEFILE} ${NEWFILENAME}

# Done







