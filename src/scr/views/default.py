from pyramid.view import view_config

from ..session import require_logged_in


@view_config(route_name='root', renderer='scr:templates/root.jinja2')
@require_logged_in()
def root(request):
    return {}
