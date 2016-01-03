def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/plain;charset=utf-8')])
    return str(env.keys()).encode('utf-8')
