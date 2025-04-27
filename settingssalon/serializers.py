from rest_framework import serializers
from .models import OpeningDays, Services, Employees, Schedules, Absences, Clients, Dates
from rest_framework.validators import UniqueTogetherValidator

class OpeningDaysSerializer(serializers.ModelSerializer):
  class Meta:
    model = OpeningDays
    fields = ['day', 'state_day', 'hour_start', 'hour_end']

class ServicesSerializer(serializers.ModelSerializer):
  class Meta:
    model = Services
    fields = ['service', 'category', 'duration', 'price', 'description']
    validators = [
      UniqueTogetherValidator(
        queryset=Services.objects.all(),
        fields=['service', 'category']
      )
    ]

class EmployeesSerializer(serializers.ModelSerializer):
  class Meta:
    model = Employees
    fields = ['email', 'name', 'phone_number', 'services']
    validators = [
      UniqueTogetherValidator(
        queryset=Employees.objects.all(),
        fields=['email', 'name', 'phone_number', 'services']
      )
    ]

class SchedulesSerializer(serializers.ModelSerializer):
  class Meta:
    model = Schedules
    fields = ['employee', 'day', 'state_day', 'hour_start', 'hour_end']
    validators = [
        UniqueTogetherValidator(
          queryset=Schedules.objects.all(),
          fields=['employee', 'day']
        )
    ]

class AbsencesSerializer(serializers.ModelSerializer):
  class Meta:
    model = Absences
    fields = ['employee', 'date', 'hour_start', 'hour_end', 'reason']
    validators = [
      UniqueTogetherValidator(
        queryset=Absences.objects.all(),
        fields=['employee', 'date']
      )
    ]

class ClientsSerializer(serializers.ModelSerializer):
  class Meta:
    model = Clients
    fields = ['email', 'name', 'phone_number']
    validators = [
      UniqueTogetherValidator(
        queryset=Clients.objects.all(),
        fields=['email', 'name', 'phone_number']
      )
    ]

class DatesSerializer(serializers.ModelSerializer):
  class Meta:
    model = Dates
    fields = ['client', 'employee', 'service', 'date', 'hour_start', 'hour_end']
    validators = [
      UniqueTogetherValidator(
        queryset=Dates.objects.all(),
        fields=['employee', 'service', 'date', 'hour_start']
      )
    ]