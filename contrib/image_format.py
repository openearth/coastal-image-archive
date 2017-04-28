#!/usr/bin/env python

import datetime
import argparse
import re


class ImageFormat:
    filename = None
    site = None
    datetime = None
    format = None
    _re_short = '\d+\.c\d{1,2}\.\D+$'
    # /zandmotor/2017/c12/114_Apr.24/1493031607.Mon.Apr.24_11_00_07.UTC.2017.zandmotor.c12.timex.jpg
    _re_long = '\d+\.[A-Z][a-z]{2}\.[A-Z][a-z]{2}\.\d{2}_\d{2}_\d{2}_\d{2}\.[A-Z]{3}.\d{4}\.[a-z]+\.c\d{1,2}\.\D+$'

    def __init__(self, filename, site=None):
        self.filename = filename
        self.get_format()
        self.site = site
        self.interprete()

    def get_format(self):
        if self.format is None:
            if re.search(self._re_short, self.filename):
                self.format = 'short'
            elif re.search(self._re_long, self.filename):
                self.format = 'long'
            else:
                # format not matching any of the above
                return None
        return self.format

    def interprete_short(self):
        fileparts = self.filename.split('.')
        self.epoch = int(fileparts[0])
        self.camera = int(fileparts[1][1:])
        self.image_type = fileparts[2]
        self.ext = self.filename.split(self.image_type)[-1]

        self.datetime = datetime.datetime.utcfromtimestamp(self.epoch)

    def interprete_long(self):
        pattern = '(?P<epoch>\d+)\.[A-Z][a-z]{2}\.[A-Z][a-z]{2}\.\d{2}_\d{2}_\d{2}_\d{2}\.[A-Z]{3}.\d{4}\.(?P<site>[a-z]+)\.c(?P<camera>\d{1,2})\.(?P<type>[a-z]+)\D+$'
        groupdict = re.search(pattern, self.filename).groupdict()

        self.epoch = int(groupdict['epoch'])
        self.site = groupdict['site']
        self.camera = int(groupdict['camera'])
        self.image_type = groupdict['type']
        self.ext = self.filename.split(self.image_type)[-1]

        self.datetime = datetime.datetime.utcfromtimestamp(self.epoch)


    def interprete(self):
        if self.get_format() == 'short':
            self.interprete_short()
        elif self.get_format() == 'long':
            self.interprete_long()
        elif self.format is not None:
            UserWarning('format %s of %s not implemented yet' % (self.format, self.filename))
        else:
            UserWarning('format of %s not recognized' % self.filename)

    def get_short(self):
        if self.get_format == 'short':
            return self.filename
        else:
            filename = '.'.join(['%s' % self.epoch,
                                 'c%i' % self.camera,
                                 self.image_type,
                                 ]) + self.ext
            return filename

    def get_long(self):
        if self.get_format == 'long':
            return self.filename
        else:
            path = '/' + '/'.join([self.site,
                                   self.datetime.strftime('%Y'),
                                   'c%i' % self.camera,
                                   self.datetime.strftime('%j_%b.%d')])
            filename = '.'.join(['%s' % self.epoch,
                                 self.datetime.strftime('%a.%b.%d_%H_%M_%S.UTC.%Y'),
                                 self.site,
                                 'c%i' % self.camera,
                                 self.image_type,
                                 ]) + self.ext
            return '/'.join([path, filename])

    @property
    def dayminute(self):
        midnight = self.datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        return int((self.datetime - midnight).total_seconds() / 60)

    def get(self, format):
        if format == 'short':
            return self.get_short()
        elif format == 'long':
            return self.get_long()
        else:
            pass


def main():
    parser = argparse.ArgumentParser(description='Coastal Image filename converter.')
    parser.add_argument('filename', help='filename of image')
    parser.add_argument('-f', '--format', help='desired output format', default='long')
    parser.add_argument('-s', '--site', help='name of site', nargs=1)

    args = parser.parse_args()

    I = ImageFormat(args.filename)

    if I.get_format() == 'short':
        I.site = args.site[0]

    if args.format.lower() == 'short':
        print(I.get_short())
    elif args.format.lower() == 'long':
        print(I.get_long())

if __name__ == '__main__':
    main()
