# mathx
Mathematical Tools for Python3

This library comes with a python3 formula AST parser and formula visualization tools written in Python/GTK3 andthree.js/WebGL

## Public docker image

See https://hub.docker.com/repository/docker/clazzesorg/mathx/general

Built in a node:20 container by ITEG's internal CI chain.

## Running as docker container locally 

Run the shell script

```
./dev-build-run.sh
```

in order to have the web site available under http://localhost:8011

An up-to-date nodejs installation is needed as a prerequisite. 

## HTTP endpoint for formula evaluation

This endpoint may be tested by

```
curl -X POST http://localhost:8011/mathx/evaluate -H 'Content-Type: application/json' -d '{"n":30,"xmin":-1,"xmax":1,"ymin":-1,"ymax":1,"f":"sin(x)*cos(y)"}'
```
