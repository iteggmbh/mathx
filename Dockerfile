FROM python:3.12-alpine
# Or any preferred Python version.

# not as root, dude
RUN adduser -D worker
USER worker
WORKDIR /home/worker

RUN pip install aiohttp

COPY --chown=worker:worker src/ /src/
COPY --chown=worker:worker web/dist /web/

ENV PATH="/home/worker/.local/bin:${PATH}"

ENV HTTP_WEBROOT=/web

LABEL description="MathX by ITEG GmbH, see github.com/iteggmbh/mathx/"

EXPOSE 8011

CMD ["/usr/local/bin/python3", "/src/server.py"] 

