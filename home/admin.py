from django.contrib import admin
from .models import Hotel, Room, RoomImages, Reservation, SpecialRate

# Register your models here.

admin.site.register(Hotel)
admin.site.register(Room)
admin.site.register(RoomImages)
admin.site.register(Reservation)
admin.site.register(SpecialRate)
