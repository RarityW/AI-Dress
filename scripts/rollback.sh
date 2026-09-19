#!/bin/bash
if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

VERSION=$1

read -p "Are you sure you want to rollback to $VERSION? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Rolling back to $VERSION..."
    export IMAGE_TAG=$VERSION
    docker compose -f docker-compose.prod.yml down
    docker compose -f docker-compose.prod.yml up -d
    if [ $? -eq 0 ]; then
        echo "Rollback successful."
    else
        echo "Rollback failed."
    fi
else
    echo "Aborted."
fi
