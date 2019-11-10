from django.shortcuts import redirect
from django.urls import reverse


"""Middleware to make sure anyone using the site has passed the site-wide password."""
class PasscodeMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_path = reverse('pledgetovote:auth')
        self.auth_req_paths = ['pledgetovote:pledge_root']
        self.exempt_paths = ['pledgetovote:auth']

    """Checks if `url` is a URL that requires a passcode to access"""
    def need_passcode(self, url):
        # Check if `url` is a sub-path of any of self.auth_req_paths
        in_required = False
        for path in self.auth_req_paths:
            in_required = in_required or (reverse(path) in url)

        # Check if `url` is a sub-path of any of self.exempt_paths
        in_exempt = False
        for path in self.exempt_paths:
            in_exempt = in_exempt or (reverse(path) in url)

        return in_required and not in_exempt

    def __call__(self, request):
        logged_in = request.session.get('authenticated')
        if not logged_in and self.need_passcode(request.path):
            return redirect(self.auth_path)
        else:
            return self.get_response(request)
