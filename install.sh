#!/bin/bash

# Initialize step counter
STEP=1

# Python version
PYTHON_VERSION=3.12

# Optionally download the latest Timesketch tags file
INSTALL_TAGS=false

# Optionally install auto analyzers
INSTALL_AUTO_ANALYZERS=false

# Function to display step message with automatic step numbering
display_step() {
    local message="$1"
    local term_width
    term_width=$(tput cols)
    local msg="[Step $STEP] $message"
    local bar_len=$(( (term_width - ${#msg} - 2) / 2 ))
    local bar
    bar=$(printf '%*s' "$bar_len" | tr ' ' '=')
    echo -e "${bar} \e[35m$msg\e[0m ${bar}"
    ((STEP++))
}

# Function to display message without step number
display_message() {
    echo -e "---> \e[33m$1\e[0m"
}

# Function to check and install packages
install_packages() {
    local packages=("$@")
    local to_install=()

    for pkg in "${packages[@]}"; do
        if ! command -v "$pkg" &>/dev/null; then
            to_install+=("$pkg")
        else
            display_message "$pkg is already installed."
        fi
    done

    if (( ${#to_install[@]} )); then
        display_message "Installing packages: ${to_install[*]}..."
        sudo apt update && sudo apt install -y "${to_install[@]}"
        display_message "Package installation completed."
    else
        display_message "All prerequisite packages are already installed."
    fi
}

# Function to install uv
install_uv() {
    if ! command -v uv &>/dev/null; then
        display_message "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        display_message "uv installation completed."
    else
        display_message "uv is already installed."
    fi
}

# Function to install Docker
install_docker() {
    if ! command -v docker &>/dev/null; then
        display_message "Installing Docker..."

        # Uninstall old/packaged versions of Docker
        for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove -y "$pkg"; done

        # Add Docker GPG key and repository
        # Add Docker's official GPG key:
        sudo apt-get update
        sudo apt-get install -y ca-certificates curl
        sudo install -m 0755 -d /etc/apt/keyrings
        sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
        sudo chmod a+r /etc/apt/keyrings/docker.asc

        # Add the repository to Apt sources:
        # If you use an Ubuntu derivative distro, such as Linux Mint, you may need to use UBUNTU_CODENAME instead of VERSION_CODENAME.
        echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt-get update

        # Install Docker
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

        # Initialize Docker service
        sudo systemctl enable --now docker

        display_message "Docker installation completed."
    else
        display_message "Docker is already installed."
    fi
}

# Function to build and pull Docker containers
manage_containers() {
    local build_images=(
        "chainsaw:./backend/dockers/chainsaw_dockerfile"
        "hayabusa:./backend/dockers/hayabusa_dockerfile"
        "plaso:./backend/dockers/plaso_dockerfile"
    )
    local pull_images=(
        "clamav/clamav:latest"
        "wagga40/zircolite"
    )

    for image in "${build_images[@]}"; do
        IFS=':' read -r tag dockerfile <<< "$image"
        docker build --no-cache --force-rm -t "$tag" -f "$dockerfile" .
        display_message "Built Docker image: $tag"
    done

    for image in "${pull_images[@]}"; do
        docker pull "$image"
        display_message "Pulled Docker image: $image"
    done
}

# Function to install Timesketch
install_timesketch() {
    display_step "Installing Timesketch"
    wget -q https://raw.githubusercontent.com/google/timesketch/master/contrib/deploy_timesketch.sh
    chmod +x deploy_timesketch.sh
    yes N | sudo ./deploy_timesketch.sh
    sudo chown -R "$(id -u):$(id -g)" timesketch/
    display_message "Timesketch installation completed."
}

# Function to configure Timesketch
configure_timesketch() {
    display_step "Configuring Timesketch"

    # Optionally download the latest tags file
    if [ "${INSTALL_TAGS:-true}" = true ]; then
        display_message "Downloading the latest tags file..."
        wget -Nq https://raw.githubusercontent.com/blueteam0ps/AllthingsTimesketch/master/tags.yaml -O ./timesketch/etc/timesketch/tags.yaml
    else
        display_message "Skipping download of tags file."
    fi

    # Increase the CSRF token time limit
    echo -e '\nWTF_CSRF_TIME_LIMIT = 3600' | sudo tee -a ./timesketch/etc/timesketch/timesketch.conf > /dev/null

    # Set auto analyzer in /opt/timesketch/etc/timesketch/timesketch.conf
    if [ "${INSTALL_AUTO_ANALYZERS:-true}" = true ]; then
        echo -e 'AUTO_SKETCH_ANALYZERS = ["Tagger"]' >> ./timesketch/etc/timesketch/timesketch.conf
    else
        display_message "Skipping setting AUTO_SKETCH_ANALYZERS."
    fi

    cd timesketch
    docker compose up -d

    # Wait for all Timesketch containers to be running
    display_message "Waiting for Timesketch containers to be running..."
    while ! docker compose ps --filter "status=running" | grep -q 'Up'; do
        sleep 10
    done

    display_message "Timesketch configuration completed."

    display_step "Creating Timesketch user and installing import client"
    docker compose exec timesketch-web tsctl create-user "$TIMESKETCH_USER" --password "$TIMESKETCH_PASSWORD"
    docker exec timesketch-worker bash -c "pip3 install timesketch-import-client"
    display_message "Timesketch user created and import client installed."

    cd ..
}


# Function to set up Python virtual environment
setup_python_env() {
    display_step "Setting up Python virtual environment and installing packages"

    uv venv --python "$PYTHON_VERSION"
    uv pip install --upgrade pip
    uv pip install -r ./backend/requirements.txt

    display_message "Python virtual environment set up and packages installed."
}

# Initialize installation
display_step "Starting installation script"

# Detect distribution
display_step "Detecting Linux distribution"
DISTRIB=$(lsb_release -is | tr '[:upper:]' '[:lower:]')
display_message "Detected distribution: $DISTRIB"

# Load environment variables
if [[ ! -f .env ]]; then
    echo "Please copy .env.tpl to .env and configure it before running the script."
    exit 1
fi

# Check if 'timesketch' directory already exists
display_step "Checking if 'timesketch' directory already exists"
if [[ -d "./timesketch" ]]; then
    display_message "Timesketch directory already exists. Skipping installation."
    exit 1
fi

source .env
display_step "Loaded environment variables from .env file"

# Install prerequisites
display_step "Checking and installing prerequisites"
install_packages curl python3 python3-venv

# Install uv
display_step "Installing uv"
install_uv

# Install Docker
display_step "Checking and installing Docker"
install_docker

# Add current user to Docker group if necessary
USERNAME=$(whoami)
GROUP="docker"

if [[ "$USERNAME" != "root" ]] && ! groups "$USERNAME" | grep -qw "$GROUP"; then
    display_message "Adding user '$USERNAME' to the '$GROUP' group."
    sudo usermod -aG "$GROUP" "$USERNAME"
    display_message "Re-running the script with necessary permissions."
    exec sg "$GROUP" "$0"
    exit 0
fi

display_step "Verification and installation completed"

# Manage Docker containers
display_step "Installing Docker containers"
manage_containers

# Install Timesketch
install_timesketch

# Configure Timesketch
configure_timesketch

# Setup Python environment
setup_python_env

display_step "Installation complete"

# Uncomment and modify the following lines when ready to import data:
# cp plaso_log2timeline.plaso "${TIMESKETCH_UPLOAD_PATH}/"
# docker exec timesketch-worker timesketch_importer -u "$TIMESKETCH_USER" -p "$TIMESKETCH_PASSWORD" \
#     --host http://timesketch-web:5000 --timeline_name test --sketch_name test /usr/share/timesketch/upload/plaso_log2timeline.plaso
# rm -f "${TIMESKETCH_UPLOAD_PATH}/plaso_log2timeline.plaso"

display_step "Script execution finished"
