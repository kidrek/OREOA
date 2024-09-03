


## Requirements 

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