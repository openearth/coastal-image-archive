# coastal-image-archive databases role
Deployment of Archive server for coastal images

## Required variables

```
databases:
  - CoastalImages # name of database to be created
database_dumps:
  - name: CoastalImages # database name or "all"
    target: create-images-database.sql # mysqldump file
database_downloads_dir: ~/downloads_dir # path where to find the database dumps
mysql_users:
  - name: ImagesAdmin # username
    passwd: "{{ lookup('password', '/tmp/imagesadmin_mysql_passwd chars=ascii_letters,digits length=8') }}"
    priv: CoastalImages.*:ALL
```