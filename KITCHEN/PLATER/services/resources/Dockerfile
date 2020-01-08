#Neo4j image
FROM neo4j:3.5.4
RUN apk --no-cache add openjdk11 --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community
ENV APOC_URI https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/3.5.0.2/apoc-3.5.0.2-all.jar

RUN wget $APOC_URI \
    && mv apoc-3.5.0.2-all.jar /plugins

RUN mkdir -p /data2/

CMD ["sh"]