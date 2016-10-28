# coastal-image-archive dim role
Deployment of Archive server for coastal images

## Required variables

```
dim_source_directory: # path of source data at remote site
dim_target_directory: # path at dim server to store retrieved data
dim_sites:
  - id: # name of remote site
    hostname: # hostname of remote site server
    username: # username for access of remote site server
    password: # password for access of remote site server
    datasets:
      - id: images # name of dataset to retrieve from remote site
```
