## PLATER

PLATER is a service to stand up REST endpoint over a neo4j database.
There are some restrictions on the data structure of the Neo4j backend to be fully utilized through PLATER.

> **NEO4J data structure restrictions:**
> * All nodes should have an `id` to be searchable (Used in querying single Nodes)
> * All edges should have an `id` to be searchable (Used in generating ReasonerAPI)
> * Nodes labeled `Concept` are ignored. 

### Installation

To run the web server directly:

Create a virtual Environment and activate.

    cd <PLATER-ROOT>
    python<version> -m venv venv
    source venv/bin/activate
    
 Install dependencies
    
    pip install -r requirements.txt
    
 
 Configure NEO4J Host settings
 
    export NEO4J_HOST=localhost
    export NEO4J_HTTP_PORT=7474
    export NEO4J_USERNAME=neo4j
    export NEO4J_PASSOWORD=neo4j
    export WEB_HOST=0.0.0.0 # <Ip to use Uvicorn web server host>
    export WEB_PORT=8080 <PORT for the web server >
  
  Run Script
  
    python main.py <plater_build_tag>
 
    
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
                <image_tag> <plater_build_tag>

 
 ### Linking to Automat Server \[Optional\]
 You can also serve several instances of plater through a common gateway(Automat). By 
 passing `-a <automat_address>` to `main.py`. Usage: 
 
 #####Python 
    
    python main.py -a <automat_address> <plater_build_tag>
    
 #####Docker
    
    docker run -p 0.0.0.0:8999:8080  \
               --env NEO4J_HOST=<your_neo_host> \
               --env NEO4J_HTTP_PORT=<your_neo4j_http_port> \
               --env NEO4J_USERNAME=neo4j\
               --env NEO4J_PASSWORD=<neo4j_password> \
               --env WEB_HOST=0.0.0.0 \
               --network=<docker_network_neo4j_is_running_at> \    
                <image_tag> -a <automat_address> <plater_build_tag>
    
    
   
    
    