#!/bin/bash
#
# Version: $Id$
# Author: J. Baten
#
# Description
# Script to generate dummy files to test the working of the Archive server for coastal images
#
# Example of input files:
# Source files are located on the fieldstation in /$ROOTIMAGESDIR/images/<dir>
# The format of <dir> is year in 4 digits, <dot> daynumber <dot> month+day concattenated in 4 characters.
# Example: /$ROOTIMAGESDIR/images/2016.277.1003/1475518499.c6.snap.jpg
# Format description:
# Original short format: 1476099002.c8.snap.jpg meaning: <epoch time>.c<camera #>.<image type: snap|timex|min|max>.jpg
# Should be converted when copying to Long format: <epoch time>.<weekday>.<month>.<day>_<hour>_<min>_<sec>.UTC.<year>.<station>.c<camera #>.< image type: snap|timex|min|max>.jpg

# We will use ImageMagick to create dummy files
# as in:$ convert -size 32x32 xc:white empty.jpg

# ENVIRONMENT VARIABLE(S):
# You can use MYIMAGESDIR to relocate the $ROOTIMAGESDIR root directory


# FS means fieldstation
FSDIR="images"
YEARNUMBER="$(date +%Y)"
DAYNUMBER="$(date +%j)"
DAY="$(date +%d)"
MONTH="$(date +%m)"
EPOCHTIME="$(date +%s)"
IMAGETYPE="snap"
CAMERAS="1 2 3"

# pre-flight Check
which convert > /dev/null
CONVERTFOUND=$?
if [ "${CONVERTFOUND}" -eq 1 ]
then
  echo "ERROR: This script needs the 'convert' program from the ImageMagick package but it was not found!"
  exit
fi

if [ -z "$ROOTIMAGESDIR" ]
then
  echo "Environment variable ROOTIMAGESDIR is undefined!"
  exit 1
fi

# Check if necessary dirs exist
declare -i result
if [ ! -d "${ROOTIMAGESDIR}" ] 
then
  echo "There is no ${ROOTIMAGESDIR} directory yet!"
  read -p "Should I create it (y/n)? : " answer
  if [ "${answer}" == "y" ]
  then
    mkdir "${ROOTIMAGESDIR}" 
    result=$?
    if [ "${result}" -ge 1 ]
    then
      echo "Error when trying to create directory ${ROOTIMAGESDIR}"
      exit
    fi
  else
    echo "I need ${ROOTIMAGESDIR} to exist"
    echo "Aborting..."
    exit
  fi
fi

if [ ! -d "${ROOTIMAGESDIR}/${FSDIR}" ]
then
  echo "There is no ${ROOTIMAGESDIR}/${FSDIR} directory yet!"
  read -p "Should I create it (y/n)? : " answer
  if [ "${answer}" == "y" ] 
  then
    mkdir "${ROOTIMAGESDIR}/${FSDIR}" 
    result=$?
    if [ "${result}" -eq 1 ]
    then
      echo "Error when trying to create directory ${ROOTIMAGESDIR}/${FSDIR}"
      exit
    fi

  else
    echo "I need ${ROOTIMAGESDIR}/${FSDIR} to exist"
    echo "Aborting..."
    exit
  fi
  
else
  SUBDIR="${YEARNUMBER}.${DAYNUMBER}.${MONTH}${DAY}"

  if [ ! -d "${ROOTIMAGESDIR}/${FSDIR}/${SUBDIR}" ]
  then
    echo "There is no ${ROOTIMAGESDIR}/${FSDIR}/${SUBDIR} directory yet!"
    read -p "Should I create it (y/n)? : " answer

    if [ "${answer}" == "y" ]
    then
      mkdir "${ROOTIMAGESDIR}/${FSDIR}/${SUBDIR}" 
      result=$?
      if [ "${result}" -eq 1 ]
      then
        echo "Error when trying to create directory ${ROOTIMAGESDIR}/${FSDIR}/${SUBDIR}"
        exit
      fi

    else
      echo "I need ${ROOTIMAGESDIR}/${FSDIR}/${SUBDIR} to store image files in"
      echo "Aborting..."
      exit
    fi

  fi  
  echo "Making files in ${ROOTIMAGESDIR}/${FSDIR}/${SUBDIR}"
  # loop over CAMERAS
  for camera in $CAMERAS
  do 
    FILENAME="${EPOCHTIME}.c${camera}.${IMAGETYPE}.jpg"
    # convert -size 32x32 xc:white empty.jpg
    # convert -background white -fill black -pointsize 72 label:WhateverYouWantToWrite OutputFile
    # convert -size 32x32 xc:white "${ROOTIMAGESDIR}/${FSDIR}/${SUBDIR}/${FILENAME}"
    convert -background white -fill black -pointsize 72 label:dummy_file "${ROOTIMAGESDIR}/${FSDIR}/${SUBDIR}/${FILENAME}"
    result=$?
    if [ "${result}" -eq 1 ]
    then
      echo "Error when trying to create an image file (${ROOTIMAGESDIR}/${FSDIR}/${SUBDIR}/$FILENAME)"
      exit
    fi
  done
  echo "Results:"
  ls -al "${ROOTIMAGESDIR}/${FSDIR}/${SUBDIR}"/*
fi
