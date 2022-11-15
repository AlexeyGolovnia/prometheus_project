import time

import redis
from flask import Flask

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

from prometheus_client import Counter
c = Counter('my_http_requests', 'HTTP requests count')

def get_hit_count():
    retries = 5
    while True:
        try:
            c.inc()
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return 'Hello World a5! I have been seen {} times.\n'.format(count)
