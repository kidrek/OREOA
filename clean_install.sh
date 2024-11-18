#!/bin/bash

echo "Starting cleanup process..."

# Check if docker is installed and running
if command -v docker &> /dev/null; then
    echo "Docker found - cleaning up containers..."
    # Stop any running containers, ignoring errors if none exist
    echo "Stopping running containers..."
    docker container stop $(docker container ls -aq) 2>/dev/null || true
    # Remove stopped containers, ignoring errors if none exist  
    echo "Removing stopped containers..."
    docker container rm $(docker container ls -aq) 2>/dev/null || true
else
    echo "Docker is not installed or not in PATH - skipping container cleanup"
fi

# Remove timesketch directory if it exists
if [ -d "timesketch" ]; then
    echo "Removing timesketch directory..."
    rm -Rf timesketch
fi

# Remove any deploy* files if they exist
if ls deploy* 1> /dev/null 2>&1; then
    echo "Removing deploy files..."
    rm -f deploy*
fi

echo "Cleanup complete!"
