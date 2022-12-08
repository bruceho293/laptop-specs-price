import base64
import os
from functools import wraps

from django.contrib.auth.models import User

def get_client_credentials(view_func):
    """
    Retrieve client credentials based on the request.
    """
    @wraps(view_func)
    def _wrapper_view(request, *args, **kwargs):
        client_id = request.POST.get('client_id')
        client_secret = os.environ.get('OAUTH2_CLIENT_SECRET')
        client = base64.b64encode('{}:{}'.format(client_id, client_secret).encode()).decode()    
        request.META['HTTP_AUTHORIZATION'] = 'Basic {}'.format(client)
        return view_func(request, *args, **kwargs)
    return _wrapper_view