from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Hotel, RoomImages, Reservation
from django.http import FileResponse, HttpResponse ,Http404, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.http import HttpResponse
from datetime import datetime
from django.utils import timezone

# Create your views here.


# from .forms import CustomLoginForm

def home(request):
    hotel_rooms = Room.objects.prefetch_related('images').all()
   
    context = {
        'hotel_rooms': hotel_rooms,
    }
    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html')
def contact(request):
    return render(request, 'contact.html')

def room_details(request, id):
    room = get_object_or_404(Room, id=id)
    
    room_images = room.images.all()
    related_rooms = Room.objects.all()
    context = {
        'room': room,
        'room_images': room_images,
        'related_rooms': related_rooms
    }
    return render(request, 'room-single.html', context)


def hotels(request):
    hotel_rooms = Room.objects.all()
    if request.method == 'POST':
        location = request.POST.get('location')
        checkin_date = request.POST.get('checkin_date')
        checkout_date = request.POST.get('checkout_date')
        room_cat = request.POST.get('room_cat') 
        try:
            if checkin_date:
                checkin_date = datetime.strptime(checkin_date, '%m/%d/%Y').strftime('%Y-%m-%d')
            if checkout_date:
                checkout_date = datetime.strptime(checkout_date, '%m/%d/%Y').strftime('%Y-%m-%d')
        except ValueError:
            
            return render(request, 'hotels.html', {
                'error': 'Invalid date format. Please enter a valid date in MM/DD/YYYY format.'})
        if location:
            hotel_rooms = hotel_rooms.filter(location__icontains=location)

        if room_cat:
            hotel_rooms = hotel_rooms.filter(category=room_cat)

        if checkin_date and checkout_date:

            available_rooms = []
            for room in hotel_rooms:
                overlapping_reservations = Reservation.objects.filter(
                    room=room,
                    start_date__lt=checkout_date,
                    end_date__gt=checkin_date
                )
                if not overlapping_reservations.exists():
                    available_rooms.append(room)
            print(f"available_rooms -- {available_rooms}")
            hotel_rooms = Room.objects.filter(id__in=[room.id for room in available_rooms])
            print(f"hotel_rooms -- {hotel_rooms}")
        
    hotel_rooms = hotel_rooms.order_by('id')
    paginator = Paginator(hotel_rooms, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        # 'location': location,
        # 'checkin_date': checkin_date,
        # 'checkout_date': checkout_date,
        # 'room_cat': room_cat,
    }
    return render(request, 'hotels.html', context)


# def is_staff(user):
#     return user.groups.filter(name='Hotel Staff').exists()

# def is_superuser(user):
#     return user.is_superuser

# def user_login(request):
#     if request.method == 'POST':
#         form = CustomLoginForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect('dashboard')
#     else:
#         form = CustomLoginForm()
#     return render(request, 'login.html', {'form': form})

# def user_logout(request):
#     logout(request)
#     return redirect('login')

# @login_required
# def dashboard(request):
#     return render(request, 'home.html')

# @login_required
# @user_passes_test(is_staff)
# def staff_dashboard(request):
#     return render(request, 'staff_dashboard.html')

# @login_required
# @user_passes_test(is_superuser)
# def superuser_dashboard(request):
#     return render(request, 'superuser_dashboard.html')




# @login_required
def check_availability(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        room_category = request.POST.get('room_category')
        hotel_id = request.POST.get('hotel')

        available_rooms = Room.objects.filter(
            hotel_id=hotel_id,
            category=room_category,
            is_available=True,
            reservation__start_date__gte=end_date,
            reservation__end_date__lte=start_date
        )

        return render(request, 'availability.html', {'rooms': available_rooms})
    
    room_categories = Room.objects.all()
    return render(request, 'check_availability.html', {'room_categories': room_categories,})




@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        customer_name = request.POST.get('c_name')
        customer_email = request.POST.get('email')
        customer_phone = request.POST.get('phone')
        start_date = request.POST.get('checkin_date')
        end_date = request.POST.get('checkout_date')
        
        start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()
        print("POST", customer_name, customer_email, customer_email, start_date, end_date)
        
        if start_date < timezone.now().date():
            return HttpResponse("Error: Dates cannot be in the past.")
        if not room.is_available and room.available_rooms <= 0:
            return HttpResponse("Sorry, no available rooms for the selected category.")
        
        try:
            reservation = Reservation.objects.create(
                room=room,
                user=request.user,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                start_date=start_date,
                end_date=end_date
            )
            print(reservation)
            return HttpResponseRedirect(reverse('reservation_success', args=[reservation.id]))

        except ValueError as e:
            print("error")
            return HttpResponse(f"Error: {e}")

    context = {
        'room': room,
    }
    return render(request, 'book_room.html', context)

@login_required
def reservation_success(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    return render(request, 'reservation_success.html', {'reservation': reservation})


@login_required
def user_dashboard(request):
    user = request.user
    context ={
        'user':user
    }
    return render(request, 'user_dashboard.html')


@login_required
def my_bookings(request):
    user = request.user
    reservations = Reservation.objects.filter(user=user).order_by('id')
    paginator = Paginator(reservations, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'my_bookings.html', context)


@login_required
def cancel_booking(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    try:
        message = reservation.cancel_booking()
        return HttpResponse(message) 
    except ValueError as e:
        return HttpResponse(f"Error: {e}")