#!/bin/bash

PS3="Select the OS: "
select os_type in Fedora Ubuntu; do
    echo "Selected OS: $os_type"
    break
done

if [ $REPLY -eq 2 ]; then
    sudo apt install openssl libssl-dev zlib1g-dev libmysqlclient-dev libffi-dev gcc  # pkg-config
else
    sudo dnf install openssl-devel zlib-devel mysql-devel libffi-devel gcc-c++ # pkgconfig
fi
