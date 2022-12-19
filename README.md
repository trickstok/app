<img src="static/assets/banner.png">

# Tricks Tok
The Tiktok of Trick


**This project is available at [trickstok.tk](https://trickstok.tk)**

## Developers

### Self-host:

[//]: # (In production mode we use a load balancer to support multiple users connected...<br>)

[//]: # (On one node we have 3 instances:)

[//]: # ()
[//]: # (Node 1: 192.168.1.20<br>)

[//]: # (    - Instance 1: 192.168.1.20:10000<br>)

[//]: # (    - Instance 2: 192.168.1.20:11000<br>)

[//]: # (    - Instance 3: 192.168.1.20:12000)

[//]: # ()
[//]: # (Node 2: 192.168.1.30<br>)

[//]: # (    - Instance 1: 192.168.1.30:10000<br>)

[//]: # (    - Instance 2: 192.168.1.30:11000<br>)

[//]: # (    - Instance 3: 192.168.1.30:12000)

All basics scripts are in Makefile...

> Warning ! For https support you need `certificate.pem` and `privatekey.pem` at project root directory

**install:**<br>
Install dependencies and configure TricksTok
```shell
make install
```

After `make install` you need to refactor `config.auto.ini` -> `config.ini` and change values ([config reference](#configuration-file-reference)) !'

**run:**<br>
Run TricksTok, in development mode, you can add -https for https support.
```shell
make run[-https]
```

**deploy:**<br>
Build and run TricksTok, in a production mode, you can add -https for https support.
```shell
make deploy[-https]
```

**install-service:**<br>
Install the service file, to make TricksTok start at boot
```shell
make install-service
```

For advanced deployment with multiple instances and a load balancer you can use `script/generate_instances`.

This script will create config file for each instance and load_balancer rules.

options:
```
--number_of_instances=5 # REQUIRED, number of configurations instances wanted

--config=/path/to/sampleconfig.ini # Sample config file, with secret, db logins, mailserver... (default to config.ini)

--ports=20,10,30 # comma separated numbers, they will be used to run instance (default to auto)

--generate_load_balancer_rules=yes/no # Tell script if you want to generate load balancer rules for created instances (default to yes)

--load_balancer_port=8080 # On which port load balancer should run (default to 8080)

```
Execute script:
```shell
python3 scripts/generate_instances [options]
```

### Configuration file reference

Here is the required config.ini file:

config.ini
```dotenv
[App]
DB_USER=user
DB_PASSWORD=userpassword
DB_URL=your.mongo.server/?retryWrites=true&w=majority
SECRET=secretrandomstring
MAILSERVER=192.168.1.141
MAILING_LISTS=test,other
PORT=10000
```

**DB_*:**<br>
DB_* field are required to connect with a mongodb database;<br>
DB_USER: username<br>
DB_PASSWORD: password for username<br>
DB_URL: url to your mongodb server

Mongodb database need a database named `trickstok` and the following collections:
`comments,mailing,reports,users,videos,views`

**SECRET:**<br>
SECRET is a random string used as a salt to encode passwords et enforce security, put whatever you want.

**MAILSERVER:**<br>
MAILSERVER is an ip where a mailserver is running (with no creds needed to send mails), you can use [mailproxy](https://github.com/kz26/mailproxy).

**MAILING_LIST:**<br>
MAILING_LIST is a comma separated lists of mails, not very useful for self-host, it's useful when you make a newsletter on landing page or something like that... You can keep the default configuration nothing will change...

**PORT:**<br>
PORT is on which port TricksTok will run, choose the one you want.
