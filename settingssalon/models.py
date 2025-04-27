from django.db import models
from django.core.validators import RegexValidator
from datetime import timedelta, time
from django.contrib.auth.models import AbstractUser

class OpeningDays(models.Model):

   class DayOptions(models.TextChoices):
      Lunes = 'lunes'
      Martes = 'martes'
      Miércoles = 'miércoles'
      Jueves = 'jueves'
      Viernes = 'viernes'
      Sábado = 'sábado'
      Domingo = 'domingo'

   class StateOptions(models.TextChoices):
      Abierto = 'abierto'
      Cerrado = 'cerrado'

   day = models.CharField(max_length=9, choices=DayOptions, unique=True)
   state_day = models.CharField(max_length=7, choices=StateOptions)
   hour_start = models.TimeField(null=True)
   hour_end = models.TimeField(null=True)

class Services(models.Model):

   class CategoryOptions(models.TextChoices):   
      Peluquería = 'Peluqueria'
      Estética = 'Estetica'
      Tratamientos = 'Tratamientos'

   service = models.CharField(max_length=30)
   duration = models.TimeField()
   price = models.DecimalField(max_digits=7, decimal_places=2)
   category = models.CharField(max_length=12, choices=CategoryOptions)
   description = models.CharField(max_length=200)

class Employees(models.Model):
   
   email = models.EmailField()
   name = models.CharField(max_length=30)
   phone_number = models.CharField(
        max_length=12,  
        validators=[
            RegexValidator(
                regex=r'^\+34?3?\d{9}$', 
                message="The phone number must begin with: '+34' and include 9 more digits."
            )
        ]
   )
   services = models.ManyToManyField(Services, related_name='service_employee')

class Schedules(models.Model):

   class DayOptions(models.TextChoices):
      Lunes = 'lunes'
      Martes = 'martes'
      Miércoles = 'miércoles'
      Jueves = 'jueves'
      Viernes = 'viernes'
      Sábado = 'sábado'
      Domingo = 'domingo'

   class StateOptions(models.TextChoices):
      Descanso = 'descanso'
      Trabajo = 'trabajo'

   employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='employee_schedule')
   day = models.CharField(max_length=9, choices=DayOptions)
   state_day = models.CharField(max_length=8, choices=StateOptions)
   hour_start = models.TimeField(null=True)
   hour_end = models.TimeField(null=True)

class Absences(models.Model):

   employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='employee_absence')
   date = models.DateField()
   hour_start = models.TimeField()
   hour_end = models.TimeField()
   reason = models.CharField(max_length=200)

class Clients(models.Model):
   
   email = models.EmailField()
   name = models.CharField(max_length=30)
   phone_number = models.CharField(
        max_length=12,  
        validators=[
            RegexValidator(
                regex=r'^\+34?3?\d{9}$', 
                message="The phone number must begin with: '+34' and include 9 more digits."
            )
        ]
   )

class Dates(models.Model):

   client = models.ForeignKey(Clients, on_delete=models.CASCADE, related_name="client_date")
   employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name="employee_date")
   service = models.ForeignKey(Services, on_delete=models.CASCADE, related_name="service_date")
   date = models.DateField()
   hour_start = models.TimeField()
   hour_end = models.TimeField(editable=False)

   def save(self, *args, **kwargs):
      start = timedelta(hours=self.hour_start.hour, minutes=self.hour_start.minute)
      end = timedelta(hours=self.service.duration.hour, minutes=self.service.duration.minute)
      suma = start +  end
      horas, resto = divmod(suma.total_seconds(), 3600)
      minutos, segundos = divmod(resto, 60)
      self.hour_end = time(int(horas), int(minutos), int(segundos))
      super().save(*args, **kwargs)
