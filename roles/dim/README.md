# coastal-image-archive dim role
Deployment of Archive server for coastal images

## Required variables

```
dim_source_directory: # path of source data at remote site
dim_work_directory: # temporary storage directory for dim
dim_data_directory: # path at dim server to store retrieved data
images_database: # database name to store the image details in
dim_sites:
  - id: # name of remote site
    hostname: # hostname of remote site server
    username: # username for access of remote site server
    password: # password for access of remote site server
    datasets:
      - id: images # name of dataset to retrieve from remote site
```

Put these variables in host_vars
