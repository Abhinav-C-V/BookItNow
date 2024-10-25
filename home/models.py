from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from decimal import Decimal
from django.utils import timezone



# Create your models here.
class Hotel(models.Model):
    HOTEL_STAR_CHOICES = [
        ('1', '1 Star'),
        ('2', '2 Star'),
        ('3', '3 Star'),
        ('4', '4 Star'),
        ('5', '5 Star'),
    ]
    hotel_name = models.CharField(max_length=100)
    category = models.CharField(max_length=10, choices=HOTEL_STAR_CHOICES, default='3')
    address = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.hotel_name


class Room(models.Model):
    BED_TYPE_CHOICES = [
        ('SINGLE', 'Single Bed'),
        ('DOUBLE', 'Double Bed'),
        ('SUITE', 'Suite'),
        ('DELUXE', 'Deluxe'),
        ('KING', 'King Size Bed'),
        ('QUEEN', 'Queen Size Bed'),
    ]
    AC_CHOICES = [
        ('AC', 'AC'),
        ('NON_AC', 'Non-AC')
    ]
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    category = models.CharField(max_length=20, choices=BED_TYPE_CHOICES, default='SINGLE')
    ac_type = models.CharField(max_length=6, choices=AC_CHOICES, default='AC')
    is_available = models.BooleanField(default=True)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_rooms = models.PositiveIntegerField(default=0)
    available_rooms = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.is_available:
            self.available_rooms = 0
        elif self.is_available and self.available_rooms == 0:
            self.is_available = False
            
        elif self.available_rooms > 0:
            self.is_available = True

        super(Room, self).save(*args, **kwargs)

    def __str__(self):
        return f"Room {self.hotel.hotel_name} {self.ac_type} - {self.category}"


class RoomImages(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name= 'images')
    image = models.ImageField(upload_to='room_images/')


class Reservation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE) 
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True) 
    customer_name = models.CharField(max_length=100, null=True, )  
    customer_email = models.CharField(max_length=50, null=True, ) 
    customer_phone = models.CharField(max_length=50, null=True, )
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.start_date >= self.end_date:
            raise ValueError("End date must be after start date.")
        
        overlapping_reservations = Reservation.objects.filter(
            room=self.room,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date
        )
        if overlapping_reservations.exists():
            raise ValueError("This room is already booked during the selected dates.")

        special_rate = SpecialRate.objects.filter(
            room=self.room,
            start_date__lte=self.start_date,
            end_date__gte=self.end_date
        ).first()

        offer = special_rate.offer if special_rate else 1.0
        num_days = (self.end_date - self.start_date).days
        offer = Decimal(offer)
        self.total_price = self.room.base_price * offer * num_days

        if not self.pk:
            if self.room.available_rooms <= 0:
                raise ValueError("No available rooms for the selected category.")
            self.room.available_rooms -= 1
            self.room.save()

        super().save(*args, **kwargs)

    def cancel_booking(self, *args, **kwargs):
        
        if self.start_date > timezone.now().date():
            if self.room.available_rooms < self.room.total_rooms:
                self.room.available_rooms += 1
                if not self.room.is_available:
                    self.room.is_available = True
                self.room.save()
                print(self.room)
            super().delete(*args, **kwargs)
            return "Booking canceled successfully."
        else:
            raise ValueError("Booking cannot be canceled as the check-in date is today or has already passed.")

    def __str__(self):
        return f"Reservation for Room {self.room.category} by {self.customer_name}"



class SpecialRate(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    offer = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"Special Rate for {self.room.hotel.hotel_name} from {self.start_date} to {self.end_date}"



