from functools import wraps

from django.contrib.auth.models import User

def get_request_user(view_func):
    """
    Modify `request.user` with the information in request custom header `x-user`.
    """
    @wraps(view_func)
    def _wrapper_view(request, *args, **kwargs):
        username = request.headers.get('x-user')
        if username is not None:
            request.user = User.objects.get(username=username)
        return view_func(request, *args, **kwargs)
    return _wrapper_view