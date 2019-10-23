#!/usr/bin/env python

import os
import argparse

from image_format import ImageFormat

from irods.session import iRODSSession

ENV_FILE = os.path.expanduser('~/.irods/irods_environment.json')
DEFAULT_IHOME = "/tempZone/home"


def irods_ingest(image_file, research_group, **kwargs):

    if "iHome" in kwargs:
        iHome = kwargs["iHome"]
    else:
        iHome = DEFAULT_IHOME

    if "env_file" in kwargs:
        env_file = kwargs["env_file"]
    else:
        env_file = ENV_FILE

    with iRODSSession(irods_env_file=env_file) as session:
        # construct main collection path
        collection_path = os.path.join(iHome, research_group)
        # get collection
        coll = session.collections.get(collection_path)

        # parse image_file as ImageFormat object
        img_fmt = ImageFormat(os.path.basename(image_file))

        # construct iRODS image path
        iImage_path = os.path.join(iHome, research_group, img_fmt.get_long()[1:])

        print(os.path.dirname(iImage_path))

        # create or get the containing collection
        if not session.collections.exists(os.path.dirname(iImage_path)):
            iImage_coll = session.collections.create(os.path.dirname(iImage_path))
            print("{} path created".format(os.path.dirname(iImage_path)))
        else:
            iImage_coll = session.collections.get(os.path.dirname(iImage_path))

        # collect paths of file in particular collection
        iRODS_image_list = [f_obj.path for f_obj in iImage_coll.data_objects]

        if iImage_path in iRODS_image_list:
            print("'{}' already available, nothing to do".format(iImage_path))
        else:
            # put file in iRODS
            obj = session.data_objects.put(image_file, iImage_path)
            print("'{}' added".format(iImage_path))

        obj = session.data_objects.get(iImage_path)
        keys = obj.metadata.keys()
        # add metadata to file
        if "epoch" not in keys:
            obj.metadata.add('epoch', str(img_fmt.epoch))
        if "site" not in keys:
            obj.metadata.add('site', img_fmt.site)
        if "camera" not in keys:
            obj.metadata.add('camera', str(img_fmt.camera))
        if "image_type" not in keys:
            obj.metadata.add('image_type', img_fmt.image_type)


def main():
    parser = argparse.ArgumentParser(description='Coastal Image ingest into iRODS')
    parser.add_argument('-i', '--image-file', help='path to image file')
    parser.add_argument('-g', '--research-group', help='iRODS research-group name')

    args = parser.parse_args()

    irods_ingest(image_file=args.image_file, research_group=args.research_group)


if __name__ == '__main__':
    main()