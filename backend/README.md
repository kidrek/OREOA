
# OREOA

## Requirements to process data

Docker images : 

- chainsaw

```
docker build . --no-cache --force-rm -t chainsaw -f ./dockers/chainsaw_dockerfile
```

- clamav

```
docker pull clamav/clamav:latest
```

- Zircolite 

```
docker pull wagga40/zircolite
```

- Plaso

```
docker build . --no-cache --force-rm -t plaso -f ./dockers/plaso_dockerfile
```


## Analyse tool

### Timesketch

- Docker deployement
```
wget https://raw.githubusercontent.com/google/timesketch/master/contrib/deploy_timesketch.sh
yes N | ./deploy_timesketch.sh
```

- Import data

```
# Install timesketch-import-client python module on timesketch-worker
docker exec timesketch-worker bash -c "pip3 install timesketch-import-client" 

# Place plaso_log2timeline.plaso on upload folder in timesketch docker, then : 
cp plaso_log2timeline.plaso {TIMESKETCH_DOCKER}/upload/
docker exec timesketch-worker /bin/bash -c "timesketch_importer -u secubian -p secubian --host http://timesketch-web:5000 --timeline_name test --sketch_name test /usr/share/timesketch/upload/plaso_log2timeline.plaso"
rm -f {TIMESKETCH_DOCKER}/upload/plaso_log2timeline.plaso
```

- Analyse data

