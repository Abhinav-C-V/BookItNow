from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('room_details/<int:id>/', views.room_details, name='room_details'),
    path('hotels/', views.hotels, name='hotels'),
    # path('login/', views.user_login, name='login'),
    # path('logout/', views.user_logout, name='logout'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    # path('staff/', views.staff_dashboard, name='staff_dashboard'),
    # path('superuser/', views.superuser_dashboard, name='superuser_dashboard'),
    # path('check-availability/', views.check_availability, name='check_availability'),
    path('reservation_success/<int:reservation_id>/', views.reservation_success, name='reservation_success'),
    path('book-room/<int:room_id>/', views.book_room, name='book_room'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('cancel_booking/<int:reservation_id>/', views.cancel_booking, name='cancel_booking'),
]
