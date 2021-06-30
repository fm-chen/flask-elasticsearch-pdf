#!/bin/bash
# setting up prerequisites
bin/elasticsearch-plugin install --batch [ingest-attachment]
exec /usr/local/bin/docker-entrypoint.sh elasticsearch