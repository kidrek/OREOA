#!/bin/bash

# Fonction pour vérifier et installer un paquet
check_install() {
    if ! command -v $1 &> /dev/null; then
        echo "$1 is not installed. Installing..."
        sudo apt update && sudo apt install -y $1
    else
        echo "$1 is installed."
    fi
}

# Vérifier et installer pip3
check_install pip3

# Vérifier et installer Docker
if ! command -v docker &> /dev/null; then
    echo "Docker n'est pas installé. Installation..."
    
    # Ajout de la clé GPG et configuration du dépôt Docker
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Installation de Docker
    sudo apt update
    sudo apt install -y docker.io docker docker-compose-plugin
    sudo systemctl start docker
    sudo systemctl enable docker
else
    echo "Docker est déjà installé."
fi

echo "Vérification et installation terminées."



echo "Installing containers"
docker build . --no-cache --force-rm -t chainsaw -f ./backend/dockers/chainsaw_dockerfile
docker pull clamav/clamav:latest
docker build . --no-cache --force-rm -t hayabusa -f ./backend/dockers/hayabusa_dockerfile
docker pull wagga40/zircolite
docker build . --no-cache --force-rm -t plaso -f .backend//dockers/plaso_dockerfile

wget https://raw.githubusercontent.com/google/timesketch/master/contrib/deploy_timesketch.sh
chmod +x deploy_timesketch.sh
yes N | ./deploy_timesketch.sh


# Download the latest tags file from blueteam0ps repo
wget -Nq https://raw.githubusercontent.com/blueteam0ps/AllthingsTimesketch/master/tags.yaml -O ./timesketch/etc/timesketch/tags.yaml

#Increase the CSRF token time limit
echo -e '\nWTF_CSRF_TIME_LIMIT = 3600' >> ./timesketch/etc/timesketch/timesketch.conf


# Set auto analyzer in /opt/timesketch/etc/timesketch/timesketch.conf
echo -e 'AUTO_SKETCH_ANALYZERS = ["Tagger"]' >> ./timesketch/etc/timesketch/timesketch.conf

cd timesketch
docker compose up -d
