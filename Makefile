run:
	python3 main.py --config config.ini --debug

run-https:
	python3 main.py --config config.ini --secure --debug

deploy:
	python3 main.py --config config.ini

deploy-https:
	python3 main.py --config config.ini --secure

install:
	echo "\n\n\n\nCreating temporary directories"
	mkdir -p data
	mkdir -p data/pdp
	mkdir -p data/thumbnails
	mkdir -p data/videos
	cp cache/banned.mp4 data/videos/banned.mp4
	echo "\n\n\n\nInstalling requirements"
	pip install -r requirements.txt
	echo "\n\n\n\nConfiguring start file"
	echo "cd ${pwd} && make deploy" > scripts/start.sh
	echo "\n\n\n\nCreating default config file in config.auto.ini, please refactor and change values to yours !"
	echo "[App]\nDB_USER=user\nDB_PASSWORD=password\nDB_URL=localhost:27000\nSECRET=mysecretsalt\nMAILSERVER=localhost:25\nMAILING_LISTS=newsletter,test\nPORT=8080" > config.auto.ini

install-service:
	echo "\n\n\n\nPlease execute in sudo"
	echo "\n\n\n\nMoving service file to systemd"
	cp trickstok.service /etc/systemd/system/trickstok.service
	echo "\n\n\n\nRegistering service file"
	systemctl enable trickstok.service
	echo "\n\n\n\nCreating folder at root"
	mkdir -p "/trickstok"
	echo "\n\n\n\nCreating start.sh"
	echo "cd `pwd` && make deploy" > scripts/start.sh
	echo "\n\n\n\nCopying start file (script/start.sh)"
	cp scripts/start.sh /trickstok/start.sh
	echo "\n\n\n\nType sudo systemctl start trickstok.service to start service"