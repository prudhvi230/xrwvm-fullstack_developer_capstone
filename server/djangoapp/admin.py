from django.contrib import admin
from .models import CarMake, CarModel


# Inline class to show CarModels inside CarMake admin
class CarModelInline(admin.TabularInline):  # Use StackedInline if you prefer vertical layout
    model = CarModel
    extra = 1  # Number of blank forms to display


# Admin class for CarModel
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'car_make', 'type', 'year')  # Show these columns in list view
    list_filter = ('type', 'year', 'car_make')           # Add filters on sidebar
    search_fields = ('name', 'car_make__name')           # Enable search on car model name and make name


# Admin class for CarMake with inline CarModels
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Show these columns
    search_fields = ('name',)
    inlines = [CarModelInline]              # Inline related models


# Register models with their respective admin classes
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)
