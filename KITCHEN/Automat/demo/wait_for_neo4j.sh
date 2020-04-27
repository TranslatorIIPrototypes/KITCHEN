#!/bin/sh

NEO_AUTH=${NEO4J_HOST}:${NEO4_PASSWORD}
NEO4J_URL="http://${NEO4J_HOST}:${NEO4J_HTTP_PORT}/db/data/labels"

response=0
until [ ${response} -gt 0 ]
do
    response="$(curl --write-out %{http_code} -u ${NEO4J_USERNAME}:${NEO4J_PASSWORD} --output /dev/null  --silent --head --fail http://${NEO4J_HOST}:${NEO4J_HTTP_PORT}/db/data/)"
    echo -n $response
    sleep 1
done

python main.py $*