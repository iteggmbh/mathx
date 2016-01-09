from mathx.web import evaluate

import logging

handler = logging.StreamHandler(open('/dev/stderr', 'w'))
formatter = logging.Formatter( '%(asctime)s %(levelname)s %(message)s') 
handler.setFormatter(formatter)
        
root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.DEBUG)


handlers = {
            "/mathx/evaluate": evaluate.handler
            }

def application(env, start_response):
    
    pi = env["PATH_INFO"]
    
    handler = handlers.get(pi)
    
    if handler is not None:
        return handler(env,start_response)
    
    else:
        start_response('404 Not Found', [('Content-Type','text/plain;charset=utf-8')])
        return [("Handler for [%s] not found."%pi).encode('utf-8')]
