# Automat

## About Automat
Automat is a common proxy PLATER instances. It aggregates the apidocs
coming from multiple PLATER instances and displays them in the common platform.
Each of the PLATER instance can be accessed using it's `Build-tag`


## Setting up
### Python

#### Setup python

```
cd KITCHEN/KITCHEN
python -m venv venv
source venv/bin/activate
export PYTHONPATH=$PWD/Automat:$PWD
```

#### Automat
Automat by default will run on `127.0.0.1:8081`. But this values can be overridden by
providing these values in `WEB_HOST` and `WEB_PORT`

```bash
pip install -r Automat/requirements.txt
python Automat/main.py 
```

#### Plater 

Plater can be run as standalone webservice with a neo4j backend. But also can be configured 
to join an automat cluster.

##### Starting the web server

By default is will run at `127.0.0.1:8080`. Also this can be overridden by providing these 
values in `WEB_HOST` and `WEB_PORT`. Be sure to run in a different terminal to avoid port clashes 
with Automat.  



Environment :

Configure the following environment variables for PLATER.

* `NEO4J_HOST` Host name of neo4j instance.
* `NEO4J_HTTP_PORT` HTTP port for neo4j.
* `NEO4J_USER_NAME` Neo4j user name.
* `NEO4J_PASSWORD` Neo4j password.
* `PLATER_SERVICE_ADDRESS` This is the callback address to send to Automat. It will be the address of the
server that PLATER is hosted on Eg. `localhost`.

After setting the environment variables, to run PLATER in clustered mode: 

```bash
cd PLATER
pip install -r requirements.txt
# In this eg, PLATER will in clustered mode and will join automat if its available
python main.py --automat_host http://127.0.0.1:8081 --validate <build-tag>
```

Plater can do validation via `--validate` argument on the backend graph using the [KGX-toolkit](https://github.com/NCATS-Tangerine/kgx/tree/master/kgx)


### Docker 

Run Automat via docker.

```bash
cd <KITCHEN-DIR>/KITCHEN/Automat
docker build --tag automat .
docker run --rm --name \ 
       automat -p 8081:8081 \
       --network automat_default  automat
```

Run plater via docker 

```bash
cd <KITCHEN-DIR>/KITCHEN/PLATER
docker build --tag plater . 
docker run --rm --name plater \
       --env PLATER_SERVICE_ADDRESS=plater plater \
       --automat_host http://automat:8081 
       \ <build_tag>
```

#### Demo

A demo docker compose file is found in `KITCHEN/KITCHEN/Automat/demo`. To run 
add config parameters to the `.env.sample` save it as `.env`:
```bash
cd KITCHEN/KITCHEN/Automat/demo
docker-compose up 
``` 

 
 