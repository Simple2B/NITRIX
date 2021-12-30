# NITRIX
Sales Tracking App


# Migration from v4 to v5

## Migration must be done with empty db on first run of project or after deleted db volume from docker


## first you need to checkout on branch version_1

``` git co version_1 ```

## activate venv

``` source .venv/bin/activate ```

## to collect data from db to json files run command

``` flask make-data-migration ```


## switch to develop branch

``` git co develop ```

## if containers are running you must run command
```docker-compose down```
## and delete db volume
```docker volume rm <name> ```
## run command
```docker-compose up -d --build```

## you need to initialize db with command 
``` docker-compose exec app flask init-db ``` 
## to get data from json files to db run command

``` docker-compose exec app flask make-data-migration ``` 


## to sync ninja_client_id with new nitrix resellers run command
``` docker-compose exec app flask sync-ninja-ids ```

### after migration finished check logs and look for resellers who don't have ninja_client_id, you need to set them manually whit flask shell inside container
### it may happened when names in nitrix and invoice ninja is different (was changed manually)

<br>