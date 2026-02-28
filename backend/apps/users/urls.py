from django.urls import path
from .views import RegisterView, MechanicStatusView, LoginView, LogoutView, UserProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('mechanic/status/', MechanicStatusView.as_view(), name='mechanic-status'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]
