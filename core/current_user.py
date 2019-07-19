from threading import local
_user = local()


class CurrentUserMiddleware:
    def process_request(self, request):
        _user.value = request.user


def get_current_user():
    return _user.value
