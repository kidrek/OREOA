# OREOA - Initialisation

## Pré-requis

L'exécution de l'outil Ansible nécessite certains prérequis.

```bash
sudo apt update; sudo apt install ansible build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl git libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

Récupération de la dernière version de pyenv :

```bash
curl -fsSL https://pyenv.run | bash
```


Il peut être util d’installer des versions de pythons différentes en fonction des outils utilisés.
Voici les étapes à réaliser pour la création d’un environnement virtuel dans un dossier spécifique.

```bash
pyenv install 3.10
virtualenv -p /$HOME/.pyenv/versions/3.10.x/bin/python3.10 myenv
```

Cette dernière étape permet d’initialiser l’environnement, avant toute exécution du projet python et le téléchargement de module python.

```bash
. ./myenv/bin/activate && python -V
```

## Déploiement

Les variables attendues dans le fichier ```inventory``` sont les suivantes : 
- ansible_user : login du compte utilisateur dont la session sera enrichie par les outils et la documentation
- ansible_ssh_pass : le mot de passe de l'utilisateur permettant l'authentification SSH
- ansible_sudo_pass : le mot de passe de l'utilisateur
- arch : cette variable permet de définir l'architecture cible ex: ```amd64```, ```arm64``` // Elle sera à terme remplacée par la variable globale d'Ansible.

Voici des exemples de fichier inventory :

* pour une machine accessible via SSH. Le paquet ```sshpass``` sera donc un pré-requis

```
127.0.0.1 ansible_user=xx ansible_ssh_pass=xx arch=xx
```

* pour appliquer le playbook sur la machine en local : 

```
127.0.0.1 ansible_connection=local ansible_user=xx arch=xx
```


Une fois les données fournies, voici la commande à exécuter (potentiellement au sein d'une instance tmux/screen): 

```bash
ansible-playbook -i inventory -K oreoa.yml
```

Un redémarrage est conseillé, une fois le système installé.
