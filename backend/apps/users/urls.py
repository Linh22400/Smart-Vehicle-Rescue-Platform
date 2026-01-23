from django.urls import path
from .views import RegisterView, MechanicStatusView, LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('mechanic/status/', MechanicStatusView.as_view(), name='mechanic-status'),
]
