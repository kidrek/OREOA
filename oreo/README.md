# OREO

L'application OREO doit être présente sur le système de fichiers dans un répertoire portant son nom.


## ROADMAP

1. Detecter tout nouveau fichier
Source : https://www.kdnuggets.com/monitor-your-file-system-with-pythons-watchdog

2. Réaliser le HASH SHA256 du fichier

3. Identifier le type de collecte (Velociraptor / Malware / Dump mémoire), via pattern
3.1 Malware -> AssemblyLine, Glimps
3.2 Identifier le type de fichier
3.2.1 Si .zip -> Extraction des fichiers (en recursif, et avec mot de passe) dans un répertoire dédié à l'analyse des données
3.2.2 Sinon ...


## Prerequis
Pour pouvoir interagir avec les différentes tasks définies, il est impératif :
- qu'un serveur redis soit initialisé et fonctionnel ;
- que le worker celery soit également en écoute ;


L'arborescence doit également respecter quelques prérequis : 
```
- Nom de l'application (ici oreo)
    - celery.py
    - settings.py
    - __init__.py
    - tasks    <-- L'ensemble des tâches y seront stockées
        - tasks.py   <-- L'ensemble des tâches devront y être déclarées
```


Certains outils sont également requis 

```
apt install -f fdfind
```

### Serveur REDIS

``` docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:latest
    container_name: oreo_redis
    environment:
      ALLOW_EMPTY_PASSWORD: yes
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - oreo_network

volumes:
  redis_data:

networks:
  oreo_network:
    driver: bridge
```

Une fois le docker démarré, le port 6379 sera exposé : 
```
docker-compose up
```


### Worker Celery
Le worker celery démarre de la manière suivante : 

```
git clone https://github.com/kidrek/OREO.git
cd OREO
celery --app=oreo worker --loglevel=info
```

il est également possible de faire en sorte qu'il redémarre à chaque modification de code.
Pour cela, il est nécessaire d'installer watchdog.

```
pip install watchdog

git clone https://github.com/kidrek/OREO.git
cd OREO
watchmedo auto-restart --directory=./ --pattern="*.py" --recursive -- celery --app=oreo worker --concurrency=1  --loglevel=INFO
```

Source : 
- https://celery.school/watchfiles-reload-celery-worker-code-changes


### Run tasks daemon

```
python3 run_task.py
```

Sources : 
- https://bilalozdemir.me/posts/python/task-queue-celery-redis/
- https://dev.to/akarshan/the-curious-case-of-celery-work-flows-39f7
- https://ask.github.io/celery/userguide/executing.html

## References

https://medium.com/@mika.palmytech.cc/celery-django-best-practices-a9fab2b1c9d1
