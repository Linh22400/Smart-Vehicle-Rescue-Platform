from django.urls import path
from .views import SOSFindMechanicsView, CreateBookingView, BookingHistoryView, MechanicBookingListView, UpdateBookingStatusView, BookingTrackingView, ConfirmPaymentView

urlpatterns = [
    path('sos/', SOSFindMechanicsView.as_view(), name='sos-find-mechanics'),
    path('create/', CreateBookingView.as_view(), name='create-booking'),
    path('history/', BookingHistoryView.as_view(), name='booking-history'),
    path('mechanic/list/', MechanicBookingListView.as_view(), name='mechanic-booking-list'),
    path('<int:pk>/update-status/', UpdateBookingStatusView.as_view(), name='update-status'),
    path('<int:pk>/tracking/', BookingTrackingView.as_view(), name='booking-tracking'),
    path('<int:pk>/confirm-payment/', ConfirmPaymentView.as_view(), name='confirm-payment'),
]
