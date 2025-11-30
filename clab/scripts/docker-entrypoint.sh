#!/bin/bash

set -e

# This exists when running locally (docker compose volume mount), but not when run in GitLab
if [ -d "/tmp/.ssh" ]
then
    cp -R /tmp/.ssh /root/.ssh
    chown -R root:root /root/.ssh/
    chmod 700 /root/.ssh
    chmod -R 600 /root/.ssh/*
fi

"$@"
