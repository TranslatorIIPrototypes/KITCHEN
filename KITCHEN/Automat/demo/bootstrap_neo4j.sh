#!/bin/sh

download_data () {
# get a dumpfile from robokopkg
wget https://robokopkg.renci.org/cord19_scigraph_v2_silo.dump.db -O /data/dump.db --no-check-certificate

# clear out old data if there is any
rm -rf /data/databases/*

echo "loading dump file"
# use neo4j-admin to load downloaded data
neo4j-admin load --from /data/dump.db
#start neo4j server as using the entrypoint script
echo "done loading dump file"
}

# make databases dir if not exists
mkdir -p /data/databases

# download database if not there
if [[ ! -d /data/databases/graph.db ]]
then
    download_data
fi

# start neo4j
/docker-entrypoint.sh neo4j