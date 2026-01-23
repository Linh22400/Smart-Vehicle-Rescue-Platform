from rest_framework.authentication import SessionAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Custom authentication class that ignores CSRF check.
    Only use this for MVP/Development to allow easy Session sharing between Admin and Frontend
    without implementing full CSRF token handling in Vue.
    """
    def enforce_csrf(self, request):
        return  # To bypass csrf check
