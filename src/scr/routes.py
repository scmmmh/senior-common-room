import json

from base64 import urlsafe_b64encode, urlsafe_b64decode


def encode_route(request):
    """Jinja2 filter that returns the current route as a JSON object, which is then URL-safe base64 encoded."""
    if request.matched_route:
        data = {'route': request.matched_route.name,
                'params': request.matchdict,
                'query': list(request.params.items())}
        return urlsafe_b64encode(json.dumps(data).encode('utf-8')).decode()
    return None


def decode_route(request, default_route='root', default_route_params=None, default_route_query=None):
    """Jinja2 filter that decodes and returns the route URL encoded with :func:`~toja.routes.encode_route`."""
    if 'redirect' in request.params and request.params['redirect']:
        try:
            data = json.loads(urlsafe_b64decode(request.params['redirect'].encode()).decode('utf-8'))
            return request.route_url(data['route'], **data['params'], _query=data['query'])
        except Exception:
            pass
    if not default_route_params:
        default_route_params = {}
    return request.route_url(default_route, **default_route_params, _query=default_route_query)


def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('root', '/')

    config.add_route('user.login', '/users/login')
    config.add_route('user.logout', '/users/logout')
