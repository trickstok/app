<div style="text-align: center">

<img src="static/assets/banner.png" width="500" style="border-radius: 20px">

<div style="display: flex; flex-direction: row; justify-content: space-evenly">
<span class="badge"><span class="first" style="background: #1c1c1c; padding: .5em; border-radius: 10px 0 0 10px;">State</span><span class="second red" style="padding: .5em; border-radius: 0 10px 10px 0; background: #FF6B6B; color: #F7FFF7">DEV</span></span>
<span class="badge"><span class="first" style="background: #1c1c1c; padding: .5em; border-radius: 10px 0 0 10px;">Licence</span><span class="second blue" style="padding: .5em; border-radius: 0 10px 10px 0; background: #4c7bfe; color: #F7FFF7">CeCILL v2.1</span></span>
<span class="badge"><span class="first" style="background: #1c1c1c; padding: .5em; border-radius: 10px 0 0 10px;">Version</span><span class="second yellow" style="padding: .5em; border-radius: 0 10px 10px 0; background: #FFE66D; color: #1c1c1c">a+0.0</span></span>
<span class="badge"><span class="first" style="background: #1c1c1c; padding: .5em; border-radius: 10px 0 0 10px;">Discord</span><span class="second grey" style="padding: .5em; border-radius: 0 10px 10px 0; background: #9f9f9f; color: #1c1c1c">Closed</span></span>
</div>

# Tricks Tok


The Tiktok of Trick

</div>
 
**This project is available at [trickstok.tk](https://trickstok.tk)**

## Developers

Please note that all scripts need to be executed at project root !

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
Install the service file, to make TricksTok start at boot, <b style="color: red">Execute after `make install`</b>
```shell
make install-service
```

You can configure start script in `script/start.sh`, default it execute `make deploy`

---

For advanced deployment with multiple instances and a load balancer you can use `script/generate_instances`.

This script will create config file for each instance and load_balancer rules.

It will also create instances/start.sh that will start every instance and the loadbalancer at the same time.
You can move this start.sh in scripts/start.sh and execute `make install` to make every instance and load balancer start at boot

options:
```
--number_of_instances=5 # REQUIRED, number of configurations instances wanted

--config=/path/to/sampleconfig.ini # Sample config file, with secret, db logins, mailserver... (default to config.ini)

--ports=20,10,30 # comma separated numbers, they will be used to run instance (default to auto)

--generate_load_balancer_rules=yes/no # Tell script if you want to generate load balancer rules for created instances (default to yes)

--load_balancer_port=8080 # On which port load balancer should run (default to 8080)

--start_cmd=python3 main.py # The start cmd for instance, you can add --secure or --debug options (default to python3 main.py)

```
Execute script:
```shell
python3 scripts/generate_instances --number_of_instances=3 [options]
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
