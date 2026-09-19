#!/bin/bash
read -p "Are you sure you want to deploy? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Deploying..."
    git pull origin main
    docker compose -f docker-compose.prod.yml pull
    docker compose -f docker-compose.prod.yml up -d --build
    if [ $? -eq 0 ]; then
        echo "Deploy successful."
    else
        echo "Deploy failed."
    fi
else
    echo "Aborted."
fi
