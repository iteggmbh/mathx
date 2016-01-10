from mathx.web import evaluate

import logging
import os

handler = logging.StreamHandler(open('/dev/stderr', 'w'))
formatter = logging.Formatter( '%(asctime)s %(levelname)s %(message)s') 
handler.setFormatter(formatter)
        
root_logger = logging.getLogger()
root_logger.addHandler(handler)

if os.environ.get("MATHX_MODE") == "development":
    root_logger.setLevel(logging.DEBUG)


log = logging.getLogger("wsgiapp")

handlers = {
            "/mathx/evaluate": evaluate.handler
            }

def application(env, start_response):
    
    pi = env["PATH_INFO"]
    
    handler = handlers.get(pi)
    
    if handler is not None:
        try:
            return handler(env,start_response)
        
        except BaseException as e:
            log.error("Handler for [%s] failed with exception: %s: %s"%(pi,type(e).__name__,e))
            start_response('500 Internal Server Error',[('Content-Type','text/plain;charset=utf-8')])
            return [("Handler for [%s] failed."%pi).encode('utf-8')]
    
    else:
        start_response('404 Not Found',[('Content-Type','text/plain;charset=utf-8')])
        return [("Handler for [%s] not found."%pi).encode('utf-8')]
