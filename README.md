# math
Mathematical Tools for Python3

This library comes with a python3 formula AST parser and formula visualization tools written in Python/GTK3 andthree.js/WebGL

## HTTP endpoint for formula ecaluation

This endpoint may be tested by

```
curl -X POST http://localhost:8011/mathx/evaluate -H 'Content-Type: application/json' -d '{"n":30,"xmin":-1,"xmax":1,"ymin":-1,"ymax":1,"f":"sin(x)*cos(y)"}'
```
