run:
	python3 main.py --config config.ini --debug

run-https:
	python3 main.py --config config.ini --secure --debug

deploy:
	python3 main.py --config config.ini

deploy-https:
	python3 main.py --config config.ini --secure

install:
	echo "Creating temporary directories"
	mkdir data
	mkdir data/pdp
	mkdir data/thumbnails
	mkdir data/videos
	mv cache/banned.mp4 data/videos/banned.mp4
	echo "Installing requirements"
	pip install -r requirements.txt
	echo "Creating default config file in config.auto.ini, please refactor and change values to yours !"
	echo -e "[App]\nDB_USER=user\nDB_PASSWORD=password\nDB_URL=localhost:27000\nSECRET=mysecretsalt\nMAILSERVER=localhost:25\nMAILING_LISTS=newsletter,test\nPORT=8080" > config.auto.ini

install-service:
	echo "Please execute in sudo"
	echo "Moving service file to systemd"
	mv
	echo "Registering service file"
	echo "Type `sudo systemctl start trickstok.service` to start service"