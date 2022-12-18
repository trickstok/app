run:
	python3 main.py --config config.ini --debug

run-https:
	python3 main.py --config config.ini --secure --debug

deploy:
	python3 main.py --config config.ini

deploy-https:
	python3 main.py --config config.ini --secure