#!/bin/bash

# Function to display step message
display_step() {
    local term_width=$(tput cols)
    local msg="[Step $1] $2"
    local msg_len=${#msg}
    local bar_len=$(( (term_width - msg_len - 2) / 2 ))
    local left_bar=$(printf '%*s' "$bar_len" | tr ' ' '=')
    local right_bar=$(printf '%*s' "$bar_len" | tr ' ' '=')
    echo -e "$left_bar \e[35m[Step $1]\e[0m \e[37m$2\e[0m $right_bar"
}

# Function to display message without step number
display_message() {
    echo -e "---> \e[33m$1\e[0m"
}

# Initialize log file
display_step 1 "Starting installation script"

# Determine the distribution (Debian or Ubuntu)
DISTRIB=$(lsb_release -i | grep 'Distributor ID:' | awk -F ":" '{print $2}' | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')
display_step 2 "Detect distribution"
display_message "Dectected distribution: $DISTRIB"

# Load variables defined in .env
if [ ! -f .env ]; then
    echo "Please edit .env.tpl and save it as .env"
    exit 1
fi
source .env
display_step 3 "Loaded environment variables from .env file"

# Function to check and install a package
check_install() {
    if ! command -v $1 &> /dev/null; then
        display_message "Installing $1..."
        sudo apt update && sudo apt install -y $1
        display_message "$1 installation completed"
    else
        display_message "$1 is already installed."
    fi
}

display_step 4 "Checking and installing prerequisites"
check_install curl
check_install python3
check_install python3-venv

display_step 5 "Installing uv"
if ! command -v uv &> /dev/null; then
    display_message "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    display_message "uv installation completed"
else
    display_message "uv is already installed."
fi

display_step 6 "Checking and installing Docker"
if ! command -v docker &> /dev/null; then
    display_message "Installing Docker..."
    # Add Docker GPG key and repository
    curl -fsSL https://download.docker.com/linux/$DISTRIB/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$DISTRIB $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    sudo apt update
    sudo apt install -y docker.io docker docker-compose-plugin
    # Initialize Docker service
    sudo systemctl start docker
    sudo systemctl enable docker
    display_message "Docker installation completed"
    # Reload user groups
    CURRENTPATH=$(pwd); newgrp docker; cd $CURRENTPATH;
else
    display_message "Docker is already installed."
fi

# Check if the current user is in the docker group
USERNAME=$(whoami)
GROUP="docker"
CURRENTPATH=$(pwd)

if [ "$USERNAME" != "root" ]; then
    if ! groups $USERNAME | grep &>/dev/null "\b$GROUP\b"; then
        display_message "Adding current user to the $GROUP group."
        sudo usermod -aG $GROUP $USERNAME

        display_message "Re-running the script with necessary permissions"
        exec sg $GROUP "$CURRENTPATH/install.sh"
        exit 0
    fi
fi

display_step 7 "Verification and installation completed"

display_step 8 "Installing containers"
docker build . --no-cache --force-rm -t chainsaw -f ./backend/dockers/chainsaw_dockerfile
display_message "Chainsaw container built"

docker pull clamav/clamav:latest
display_message "ClamAV container pulled"

docker build . --no-cache --force-rm -t hayabusa -f ./backend/dockers/hayabusa_dockerfile
display_message "Hayabusa container built"

docker pull wagga40/zircolite
display_message "Zircolite container pulled"

docker build . --no-cache --force-rm -t plaso -f ./backend/dockers/plaso_dockerfile
display_message "Plaso container built"

display_step 9 "Installing Timesketch"
wget https://raw.githubusercontent.com/google/timesketch/master/contrib/deploy_timesketch.sh
chmod +x deploy_timesketch.sh
yes N | sudo ./deploy_timesketch.sh
sudo chown -R $(id -u):$(id -g) timesketch/
display_message "Timesketch installation completed"

display_step 10 "Configuring Timesketch"
# Download the latest tags file from blueteam0ps repo
wget -Nq https://raw.githubusercontent.com/blueteam0ps/AllthingsTimesketch/master/tags.yaml -O ./timesketch/etc/timesketch/tags.yaml

# Increase the CSRF token time limit
echo -e '\nWTF_CSRF_TIME_LIMIT = 3600' >> ./timesketch/etc/timesketch/timesketch.conf

# Set auto analyzer in /opt/timesketch/etc/timesketch/timesketch.conf
echo -e 'AUTO_SKETCH_ANALYZERS = ["Tagger"]' >> ./timesketch/etc/timesketch/timesketch.conf

cd timesketch
docker compose up -d
# Wait for all Timesketch containers to be running before proceeding
while ! (docker compose ps --format "{{.Name}} {{.Status}}" 2>/dev/null | grep -q "timesketch-web.*Up" && \
         docker compose ps --format "{{.Name}} {{.Status}}" 2>/dev/null | grep -q "timesketch-worker.*Up" && \
         docker compose ps --format "{{.Name}} {{.Status}}" 2>/dev/null | grep -q "timesketch-web-legacy.*Up" && \
         docker compose ps --format "{{.Name}} {{.Status}}" 2>/dev/null | grep -q "opensearch.*Up" && \
         docker compose ps --format "{{.Name}} {{.Status}}" 2>/dev/null | grep -q "postgres.*Up" && \
         docker compose ps --format "{{.Name}} {{.Status}}" 2>/dev/null | grep -q "nginx.*Up" && \
         docker compose ps --format "{{.Name}} {{.Status}}" 2>/dev/null | grep -q "redis.*Up"); do
    display_message "Waiting for Timesketch containers to be running..."
    sleep 10
done

display_message "Timesketch configuration completed"

display_step 11 "Creating Timesketch user and installing import client"
docker compose exec timesketch-web tsctl create-user $TIMESKETCH_USER --password $TIMESKETCH_PASSWORD
docker exec timesketch-worker bash -c "pip3 install timesketch-import-client"
display_message "Timesketch user created and import client installed"

cd ..
display_step 12 "Setting up Python virtual environment and installing packages"
source ~/.bashrc
source ~/.profile
uv venv --python 3.12
uv pip install -r ./backend/requirements.txt
display_message "Python virtual environment set up and packages installed"

display_step 13 "Installation complete"

# Uncomment and modify the following lines when ready to import data:
# cp plaso_log2timeline.plaso ${TIMESKETCH_UPLOAD_PATH}/
# docker exec timesketch-worker /bin/bash -c "timesketch_importer -u $TIMESKETCH_USER -p $TIMESKETCH_PASSWORD --host http://timesketch-web:5000 --timeline_name test --sketch_name test /usr/share/timesketch/upload/plaso_log2timeline.plaso"
# rm -f ${TIMESKETCH_UPLOAD_PATH}/plaso_log2timeline.plaso

display_step 14 "Script execution finished"
