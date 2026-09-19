#!/bin/bash
read -p "Are you sure you want to stop production services? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Stopping production services..."
    docker compose -f docker-compose.prod.yml down
    if [ $? -eq 0 ]; then
        echo "Services stopped successfully."
    else
        echo "Failed to stop services."
    fi
else
    echo "Aborted."
fi
