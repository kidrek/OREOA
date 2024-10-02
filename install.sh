#!/bin/bash

DISTRIB=`lsb_release -i | grep 'Distributor ID:' | awk -F ":" '{print $2}' | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]'`

# Chargement des variables definies dans .env
source .env

# Fonction pour vérifier et installer un paquet
check_install() {
    if ! command -v $1 &> /dev/null; then
        echo "$1 is not installed. Installing..."
        sudo apt update && sudo apt install -y $1
    else
        echo "$1 is installed."
    fi
}

# Vérifier et installerles prerequis
check_install curl
if [ $DISTRIB = "debian" ]; then
  check_install python3
  check_install python3-pip
elif [ $DISTRIB = "ubuntu" ]; then
  check_install pip3
fi 


# Vérifier et installer Docker
if ! command -v docker &> /dev/null; then
    echo "Docker n'est pas installé. Installation..."
    
    # Ajout de la clé GPG et configuration du dépôt Docker
    curl -fsSL https://download.docker.com/linux/$DISTRIB/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$DISTRIB $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Installation de Docker
    sudo apt update
    sudo apt install -y docker.io docker docker-compose-plugin
    # Initialisation du service
    sudo systemctl start docker
    sudo systemctl enable docker
    # Recharge les groupes d appartenance du compte utilisateur
    CURRENTPATH=`pwd`; newgrp docker; cd $CURRENTPATH;
else
    echo "Docker est déjà installé."
fi


# Verifier la presence du compte utilisateur dans le groupe docker
USERNAME=$(whoami)
GROUP="docker"
CURRENTPATH=`pwd`

if [ `cat /etc/group | grep "$GROUP" |  grep "$USERNAME" | wc -c` -eq 0 ]; then
  # Ajout du compte utilisateur courant dans le groupe
  echo "Ajout du compte utilisateur courant dans le groupe $GROUP."
  sudo usermod -aG $GROUP $USERNAME

  # Execution a nouveau du script d installation
  echo "Nouvelle exécution du script avec les permissions nécessaires"
  sg $GROUP -c "$CURRENTPATH/install.sh"
  exit 0
fi



echo "Vérification et installation terminées."



echo "Installing containers"
docker build . --no-cache --force-rm -t chainsaw -f ./backend/dockers/chainsaw_dockerfile
docker pull clamav/clamav:latest
docker build . --no-cache --force-rm -t hayabusa -f ./backend/dockers/hayabusa_dockerfile
docker pull wagga40/zircolite
docker build . --no-cache --force-rm -t plaso -f ./backend//dockers/plaso_dockerfile
echo "==========="
echo "Installing Timesketch"
echo "==========="
wget https://raw.githubusercontent.com/google/timesketch/master/contrib/deploy_timesketch.sh
chmod +x deploy_timesketch.sh
yes N | sudo ./deploy_timesketch.sh
sudo chown -R $(id -u):$(id -g) timesketch/

# Download the latest tags file from blueteam0ps repo
wget -Nq https://raw.githubusercontent.com/blueteam0ps/AllthingsTimesketch/master/tags.yaml -O ./timesketch/etc/timesketch/tags.yaml

#Increase the CSRF token time limit
echo -e '\nWTF_CSRF_TIME_LIMIT = 3600' >> ./timesketch/etc/timesketch/timesketch.conf


# Set auto analyzer in /opt/timesketch/etc/timesketch/timesketch.conf
echo -e 'AUTO_SKETCH_ANALYZERS = ["Tagger"]' >> ./timesketch/etc/timesketch/timesketch.conf

cd timesketch
docker compose up -d

sleep 10

echo "Create timesketch user"
docker compose exec timesketch-web tsctl create-user $TIMESKETCH_USER --password $TIMESKETCH_PASSWORD
echo "Install timesketch import client"
docker exec timesketch-worker bash -c "pip3 install timesketch-import-client"


echo "Install all python3 packages"
if [ $DISTRIB = "debian" ]; then
  pip3 install -r ./backend/requirements.txt --break-system-packages
elif [ $DISTRIB = "ubuntu" ]; then
  pip3 install -r ./backend/requirements.txt
fi

# Place plaso_log2timeline.plaso on upload folder in timesketch docker, then : 
#cp plaso_log2timeline.plaso {TIMESKETCH_DOCKER}/upload/
#docker exec timesketch-worker /bin/bash -c "timesketch_importer -u secubian -p secubian --host http://timesketch-web:5000 --timeline_name test --sketch_name test /usr/share/timesketch/upload/plaso_log2timeline.plaso"
#rm -f {TIMESKETCH_DOCKER}/upload/plaso_log2timeline.plaso
