FROM python:3.12-alpine
# Or any preferred Python version.
RUN pip install aiohttp
COPY src/ /src/
COPY web/dist /web/
ENV HTTP_WEBROOT=/web
EXPOSE 8011
CMD ["/usr/local/bin/python3", "/src/server.py"] 