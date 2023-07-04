BACKEND_PATH=./backend/
FRONTEND_PATH=./frontend/
ACTIVATE=. venv/bin/activate
UPDATE_VENV=pip install --upgrade pip && cd $(BACKEND_PATH) && pip3 install . && rm -rf flight_record.egg-info/ build/
REMOVE_CACHE=find $(BACKEND_PATH) -type d | grep __pycache__ | xargs rm -rf

all: install-python venv compile
complete-install: install-deps install-python venv compile

compile:
	cc -O3 -fPIC -shared -o $(BACKEND_PATH)/haversine/distance.so $(BACKEND_PATH)/haversine/distance.c

install-deps:
	bash scripts/install-deps.sh

install-python:
	bash scripts/install-python.sh

venv:
	bash scripts/create-venv.sh
	$(ACTIVATE) && $(UPDATE_VENV)
	rm -rf .mypy_cache/ __pycache__/

update-venv:
	$(ACTIVATE) && $(UPDATE_VENV)

run: compile
	$(ACTIVATE) && cd $(BACKEND_PATH) && python3 run.py

clean-venv:
	rm -rf venv/

clean:
	rm -f flight-record.zip

purge: clean clean-venv
	rm -rf python/
	$(REMOVE_CACHE)
	rm -f $(BACKEND_PATH)/haversine/distance.so

pack: clean
	$(REMOVE_CACHE)
	zip -r flight-record.zip $(BACKEND_PATH) $(FRONTEND_PATH) scripts/ compose.yml deploy.env Dockerfile Makefile \
	--exclude '*__pycache__*' --exclude '*node_modules*' --exclude '*static/data*' --exclude '*static/react*' --exclude '*.so' \
	--exclude '*.vscode*' --exclude '*build*'
