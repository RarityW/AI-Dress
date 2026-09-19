#!/bin/bash
read -p "Are you sure you want to start production services? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Starting production services..."
    docker compose -f docker-compose.prod.yml up -d --build
    if [ $? -eq 0 ]; then
        echo "Services started successfully."
    else
        echo "Failed to start services."
    fi
else
    echo "Aborted."
fi
