import logging
import os
from urllib.parse import urlparse

if os.environ.get("MATHX_MODE") == "development":
    level = logging.DEBUG
else:
    level = logging.INFO


handler = logging.StreamHandler()
formatter = logging.Formatter( '%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
handler.setLevel(level)

root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(level)

from mathx.web import evaluate


log = logging.getLogger(__name__)

import asyncio
from aiohttp import web

routes = web.RouteTableDef()

buffersize = max(256,int(os.getenv('HTTP_BUFSIZE','1448')))
listenport = int(os.getenv('HTTP_PORT','8011'))
listenaddr = os.getenv('HTTP_ADDRESS','0.0.0.0')
webroot = os.getenv("HTTP_WEBROOT")

@routes.post('/mathx/evaluate')
async def evaluate_handler(request):
    data = await request.json()
    log.info (f"Got evaluate request {data}")
    iter = evaluate.handler(data)

    response = web.StreamResponse(
        status=200,
        reason='OK',
        headers={'Content-Type': 'application/json'},
    )

    await response.prepare(request)

    buf = bytearray(buffersize)
    nbuf = 0

    for x in iter:
        n = len(x)
        if nbuf + n <= buffersize:
            buf[nbuf:nbuf+n] = x
            nbuf += n
        else:
            nwrite = buffersize-nbuf
            buf[nbuf:buffersize] = x[0:nwrite]
            await response.write(buf)
            nbuf = n - nwrite
            buf[0:nbuf] = x[nwrite:n]

    if nbuf > 0:
        await response.write(buf[0:nbuf])

    await response.write_eof()
    return response

@web.middleware
async def index_rewrite(request,handler):

    if request.path == '/':
        return web.FileResponse(os.path.join(webroot,"index.html"))
    else:
        return await handler(request)

def main():
    log.info(f"Setting up aiohttp application.")


    middlewares = []
    if webroot:
        middlewares.append(index_rewrite)

    app = web.Application(middlewares=middlewares)
    app.add_routes(routes)

    if webroot:
        app.router.add_static('/',webroot)

    log.info(f"Listening on {listenaddr}:{listenport} with buffer size [{buffersize}]")
    web.run_app(app,host=listenaddr,port=listenport)


if __name__ == "__main__":
    main()
