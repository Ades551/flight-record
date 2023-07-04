# FlightRecord
Main goal of this project is to track flights and add communication record  between pilots and towers on their flight path and visualize it.

Back-end part of the application is written in `python` and consists of 3 main parts, each running on its own thread:
* `Flask` which provides an API and also front-end application.
* `OpenSky Network API` from where real-time flight information is received.
* `SpokenData API` which provides information about recordings.

The front-end is written in `react` which uses `leaflet` for the interactive map.

## Installation
```console
# dnf install -y podman python3-pip # RHEL based OS
# apt install -y podman python3-pip # Debian based OS
```
Install `podman-compose` using python `pip`
```console
# pip3 install podman-compose
```

## Deployment
You must enter your credentials for the application to run properly. Those credentials are stored in the [credentials.toml](backend/api/credentials.toml) file.
```toml
[opensky]
username = "username"
password = "password"

[spokendata]
API-key = "api-key"
```

You can specify port on which to listen for incomming connections by using `ENV` variable `FLASK_PORT=8000`. Please note that you need to specify this variable in the [deploy.env](deploy.env) file or directly in the [compose.yml](compose.yml).

To make sure that firewall is not blocking this communication:
```console
# firewall-cmd --add-port=8000/tcp
```

If you want to run application container also after the user logout:
```console
# loginctl enable-linger $UID
```

Build and run the application as container:
```console
$ podman-compose up -d
```

## Development
### Install NodeJS
React part was written using version 18 of `NodeJS`, so it may not work on the other versions.

Using Debian based OS:
```console
$ curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
$ sudo apt install nodejs
```

Using RHEL based OS:
```console
# dnf remove nodejs
# dnf module reset nodejs
# dnf module install nodejs:18
```

### Complete installation with dependencies
To install dependencies, donwload python interpret and create venv
```console
$ make complete-install
```

### Install dependencies
```console
$ make install-deps
```

### Install python and create virtual environment
```console
$ make
```

## Environmental variables
Here is the list of all `ENV` with example values.
```bash
FLASK_PORT=5000
FLASK_USE_PUB_IP=true
FLASK_PUB_IP="150.150.14.5"
DATABASE_URL="mysql://<user>:<password>@<host>/<database>"
API_CREDENTIALS="~/.config/flight-record/credentials.toml"
``` 
`FLASK_PUB_IP` is applied only when `FLASK_USE_PUB_IP` is `true`. In case that `FLASK_PUB_IP` is not specified and `FLASK_USE_PUB_IP` is `true` than public IP is detected automatically.
