## PLATER

PLATER is a service to sand up REST endpoint over a neo4j database.

### Installation

To run the web server directly:
Create a virtual Environment and activate.

    cd <PLATER-ROOT>
    python -m venv venv
    source venv/bin/activate
    
 Install dependencies
    
    pip install requirements.txt
    
 
 Configure NEO4J Host settings
 
    export NEO4J_HOST=localhost
    export NEO4J_HTTP_PORT=7474
    export NEO4J_USERNAME=neo4j
    export NEO4J_PASSOWORD=neo4j
    export WEB_HOST=0.0.0.0 # <Ip to use Uvicorn web server host>
    export WEB_PORT=8080 <PORT for the web server >
  
  Run Script
  
    python main.py test_build
 
    
 ### DOCKER 
   Or build an image and run it. 
  
    docker build --tag <image_tag> .
    
    docker run 
   
    docker run -p 0.0.0.0:8999:8080  \
               --env NEO4J_HOST=<your_neo_host> \
               --env NEO4J_HTTP_PORT=<your_neo4j_http_port> \
               --env NEO4J_USERNAME=neo4j\
               --env NEO4J_PASSWORD=<neo4j_password> \
               --env WEB_HOST=0.0.0.0 \
               --network=<docker_network_neo4j_is_running_at> \    
                <image_tag> <build_tag>

    # Currently build tag can be anything. Intent is to identify different instances of PLATER