from django.urls import path
from .views import GarageListView, CreateAppointmentView, AppointmentHistoryView, MechanicAppointmentListView, UpdateAppointmentStatusView
from .revenue_view import MechanicRevenueView
from .review_view import CreateReviewView

urlpatterns = [
    path('garages/', GarageListView.as_view(), name='garage-list'),
    path('book/', CreateAppointmentView.as_view(), name='book-appointment'),
    path('history/', AppointmentHistoryView.as_view(), name='appointment-history'),
    path('mechanic/list/', MechanicAppointmentListView.as_view(), name='mechanic-appt-list'),
    path('<int:pk>/update-status/', UpdateAppointmentStatusView.as_view(), name='update-appt-status'),
    path('mechanic/revenue/', MechanicRevenueView.as_view(), name='mechanic-revenue'),
    path('review/add/', CreateReviewView.as_view(), name='add-review'),
]
