from django.urls import path
from .views import SOSFindMechanicsView, CreateBookingView, BookingHistoryView, MechanicBookingListView, UpdateBookingStatusView

urlpatterns = [
    path('sos/', SOSFindMechanicsView.as_view(), name='sos-find-mechanics'),
    path('create/', CreateBookingView.as_view(), name='create-booking'),
    path('history/', BookingHistoryView.as_view(), name='booking-history'),
    path('mechanic/list/', MechanicBookingListView.as_view(), name='mechanic-booking-list'),
    path('<int:pk>/update-status/', UpdateBookingStatusView.as_view(), name='update-status'),
]
