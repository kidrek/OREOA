
# OREOA



## Requirements 

Some python modules are required.

```
pip3 install -r requirements.txt
```


### Process data tools

Docker images : 

- chainsaw

```
docker build . --no-cache --force-rm -t chainsaw -f ./dockers/chainsaw_dockerfile
```

- clamav

```
docker pull clamav/clamav:latest
```

- Hayabusa

```
docker build . --no-cache --force-rm -t hayabusa -f ./dockers/hayabusa_dockerfile
```


- Zircolite 

```
docker pull wagga40/zircolite
```

- Plaso

```
docker build . --no-cache --force-rm -t plaso -f ./dockers/plaso_dockerfile
```


### Analyse tools

#### Timesketch

- Docker deployement
```
wget https://raw.githubusercontent.com/google/timesketch/master/contrib/deploy_timesketch.sh
chmod +x deploy_timesketch.sh
yes N | ./deploy_timesketch.sh
```

- Customisation 

```
# Download the latest tags file from blueteam0ps repo
wget -Nq https://raw.githubusercontent.com/blueteam0ps/AllthingsTimesketch/master/tags.yaml -O /opt/timesketch/etc/timesketch/tags.yaml
----
NOTE SEB:    le chemin /opt/timesketch/etc/timesketch/ n'existe pas, plutot "./timesketch/etc/timesketch/tags.yaml"  ??
----

#Increase the CSRF token time limit
echo -e '\nWTF_CSRF_TIME_LIMIT = 3600' >> /opt/timesketch/etc/timesketch/timesketch.conf


# Set auto analyzer in /opt/timesketch/etc/timesketch/timesketch.conf
AUTO_SKETCH_ANALYZERS = ["Tagger"]
-----
NOTE SEB:   echo -e '\nAUTO_SKETCH_ANALYZERS = ["Tagger"]' >> ./timesketch/etc/timesketch/timesketch.conf
----

```

- Start docker

```
docker-compose up
```

- Create user

```
docker-compose exec timesketch-web tsctl create-user $USER1_NAME --password $USER1_PASSWORD
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

