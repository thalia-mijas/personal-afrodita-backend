from itertools import chain
import requests
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import OpeningDays, Services, Employees, Schedules, Absences, Clients, Dates
from .serializers import (OpeningDaysSerializer,
                          ServicesSerializer,
                          EmployeesSerializer,
                          SchedulesSerializer,
                          AbsencesSerializer,
                          ClientsSerializer,
                          DatesSerializer)
from rest_framework.decorators import api_view
from django.utils.translation import gettext
from datetime import datetime, time, timedelta, date

class OpeningDaysViewSet(viewsets.ModelViewSet):
  queryset = OpeningDays.objects.all()
  serializer_class = OpeningDaysSerializer

  def create(self, request):
    serializer = OpeningDaysSerializer(data=request.data)
    if serializer.is_valid():
      if (serializer.validated_data['state_day'] == 'abierto'):
        if ((serializer.validated_data['hour_start'] != None) and (serializer.validated_data['hour_end'] != None)):
          if (serializer.validated_data['hour_start'] > serializer.validated_data['hour_end']):
            return Response({'detail': 'Hora de inicio debe ser anterior a hora de fin.'}, status=status.HTTP_400_BAD_REQUEST)
          else:
            serializer.save()
            return Response(serializer.data)
        else:
          return Response({'detail': 'Hora de inicio y fin deberían tener un valor.'}, status=status.HTTP_400_BAD_REQUEST)
      else:
        serializer.validated_data['hour_start'] = None
        serializer.validated_data['hour_end'] = None
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)
  
  def update(self, request, pk=None):
    try:
      op_days = OpeningDays.objects.get(pk=pk)
      op_days.delete()
      serializer = OpeningDaysSerializer(data=request.data)
      if serializer.is_valid():
        serializer.validated_data['id'] = pk
        if (serializer.validated_data['state_day'] == 'abierto'):
          if ((serializer.validated_data['hour_start'] != None) and (serializer.validated_data['hour_end'] != None)):
            if (serializer.validated_data['hour_start'] > serializer.validated_data['hour_end']):
              return Response({'detail': 'Hora de inicio debe ser anterior a hora de fin.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
              serializer.save()
              return Response(serializer.data)
          else:
            return Response({'detail': 'Hora de inicio y fin deberían tener un valor.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
          serializer.validated_data['hour_start'] = None
          serializer.validated_data['hour_end'] = None
          serializer.save()
          return Response(serializer.data)
      return Response(serializer.errors)
    except OpeningDays.DoesNotExist:
      return Response({'detail': 'El día no existe'}, status=status.HTTP_404_NOT_FOUND)

class ServicesViewSet(viewsets.ModelViewSet):
  queryset = Services.objects.all()
  serializer_class = ServicesSerializer

class EmployeesViewSet(viewsets.ModelViewSet):
  queryset = Employees.objects.all()
  serializer_class = EmployeesSerializer

@api_view(['GET'])
def get_services_employee(request, pk):
    services_employee = Employees.objects.filter(pk=pk).values('services__service')

    return Response(services_employee, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_employees_service(request, pk):
    employees_service = Services.objects.filter(pk=pk).values('service_employee__name')

    return Response(employees_service, status=status.HTTP_200_OK)

class SchedulesViewSet(viewsets.ModelViewSet):
  queryset = Schedules.objects.all()
  serializer_class = SchedulesSerializer

  def create(self, request):
    serializer = SchedulesSerializer(data=request.data)
    if serializer.is_valid():
      day_state = OpeningDays.objects.filter(day=serializer.validated_data['day']).values()
      if (serializer.validated_data['state_day'] == 'trabajo') and (day_state[0]['state_day'] == 'abierto'):
        day_hour_start = day_state[0]['hour_start']
        day_hour_end = day_state[0]['hour_end']
        if ((serializer.validated_data['hour_start'] != None) and (serializer.validated_data['hour_end'] != None)):
          if (serializer.validated_data['hour_start'] < day_hour_start):
            return Response({'detail': 'Hora de inicio debería ser mayor o igual al inicio de atención del centro.'}, status=status.HTTP_400_BAD_REQUEST)
          elif (serializer.validated_data['hour_end'] > day_hour_end):
            return Response({'detail': 'Hora de fin debería ser menor o igual al fin de atención del centro.'}, status=status.HTTP_400_BAD_REQUEST)
          else:
            serializer.save()
            return Response(serializer.data)
        else:
          return Response({'detail': 'Hora de inicio y fin deberían tener un valor.'}, status=status.HTTP_400_BAD_REQUEST)
      else:
        serializer.validated_data['state_day'] = 'descanso'
        serializer.validated_data['hour_start'] = None
        serializer.validated_data['hour_end'] = None
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)
  
  def update(self, request, pk=None):
    try:
      schedule = Schedules.objects.get(pk=pk)
      schedule.delete()
      serializer = SchedulesSerializer(data=request.data)
      if serializer.is_valid():
        serializer.validated_data['id'] = pk
        day_state = OpeningDays.objects.filter(day=serializer.validated_data['day']).values()
        if (serializer.validated_data['state_day'] == 'trabajo') and (day_state[0]['state_day'] == 'abierto'):
          day_hour_start = day_state[0]['hour_start']
          day_hour_end = day_state[0]['hour_end']
          if (serializer.validated_data['hour_start'] != None) and (serializer.validated_data['hour_end'] != None):
            if (serializer.validated_data['hour_start'] < day_hour_start):
              return Response({'detail': 'Hora de inicio debería ser mayor o igual al inicio de atención del centro.'}, status=status.HTTP_400_BAD_REQUEST)
            elif (serializer.validated_data['hour_end'] > day_hour_end):
              return Response({'detail': 'Hora de fin debería ser menor o igual al fin de atención del centro.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
              serializer.save()
              return Response(serializer.data)
          else:
            return Response({'detail': 'Hora de inicio y fin deberían tener un valor.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
          serializer.validated_data['state_day'] = 'descanso'
          serializer.validated_data['hour_start'] = None
          serializer.validated_data['hour_end'] = None
          serializer.save()
          return Response(serializer.data)
      return Response(serializer.errors)
    except Schedules.DoesNotExist:
      return Response({'detail': 'El día no existe'}, status=status.HTTP_404_NOT_FOUND)

class AbsencesViewSet(viewsets.ModelViewSet):
  queryset = Absences.objects.all()
  serializer_class = AbsencesSerializer

  # def create(self, request):
  #   serializer = AbsencesSerializer(data=request.data)
  #   if serializer.is_valid():
  #     day_of_date = gettext(serializer.validated_data['date'].strftime("%A")) #gettext + setting language me traduce el dia
  #     schedule_day = Schedules.objects.filter(day=day_of_date, employee_sc_id=serializer.validated_data['employee']).values('hour_start', 'hour_end')
  #     if (len(schedule_day) > 0):
  #       if (serializer.validated_data['hour_start'] < schedule_day[0]['hour_start']):
  #         return Response({'detail': 'La hora de inicio debe ser igual o mayor a la hora de apertura del centro.'}, status=status.HTTP_400_BAD_REQUEST)
  #       elif (serializer.validated_data['hour_end'] > schedule_day[0]["hour_end"]):
  #         return Response({'detail': 'La hora de fin debe ser igual o menor a la hora de cierre del centro.'}, status=status.HTTP_400_BAD_REQUEST)
  #       else:
  #         serializer.save()
  #         return Response(serializer.data)
  #     else:
  #       return Response({'detail': 'El empleado no trabaja ese día.'}, status=status.HTTP_400_BAD_REQUEST)
  #   return Response(serializer.errors)
  
  # def update(self, request, pk=None):
  #   absence = Schedules.objects.get(pk=pk)
  #   absence.delete()
  #   serializer = AbsencesSerializer(data=request.data)
  #   if serializer.is_valid():
  #     serializer.validated_data['id'] = pk
  #     day_of_date = gettext(serializer.validated_data['date'].strftime("%A")) #gettext + setting language me traduce el dia
  #     schedule_day = Schedules.objects.filter(day=day_of_date, employee_sc_id=serializer.validated_data['employee']).values('hour_start', 'hour_end')
  #     if (len(schedule_day) > 0):
  #       if (serializer.validated_data['hour_start'] < schedule_day[0]['hour_start']):
  #         return Response({'detail': 'La hora de inicio debe ser igual o mayor a la hora de apertura del centro.'}, status=status.HTTP_400_BAD_REQUEST)
  #       elif (serializer.validated_data['hour_end'] > schedule_day[0]["hour_end"]):
  #         return Response({'detail': 'La hora de fin debe ser igual o menor a la hora de cierre del centro.'}, status=status.HTTP_400_BAD_REQUEST)
  #       else:
  #         serializer.save()
  #         return Response(serializer.data)
  #     else:
  #       return Response({'detail': 'El empleado no trabaja ese día.'}, status=status.HTTP_400_BAD_REQUEST)
  #   return Response(serializer.errors)

class ClientsViewSet(viewsets.ModelViewSet):
  queryset = Clients.objects.all()
  serializer_class = ClientsSerializer

class DatesViewSet(viewsets.ModelViewSet):
  queryset = Dates.objects.all()
  serializer_class = DatesSerializer

@api_view(['GET'])
def get_schedules_available(request, service_id, employee_id, day):
    
  try:
    day = date.fromisoformat(day)
    day_of_week = gettext(day.strftime("%A")) #gettext + setting language me traduce el dia
    schedule_employee = Schedules.objects.filter(day=day_of_week, employee_id=employee_id, state_day='trabajo').values('hour_start', 'hour_end')[0]
    dates_employee = Dates.objects.filter(date=day, employee=employee_id).values('hour_start', 'hour_end')
    absences_employee = Absences.objects.filter(date=day, employee_id=employee_id).values('hour_start', 'hour_end')
    service_duration = Services.objects.filter(id=service_id).values('duration')[0]
    
    print('horario: ', schedule_employee)
    print('=============================')
    # print(datetime.now().strftime("%H:%M"))
    # print(datetime.today().strftime("%Y-%m-%d"))

    #Redondear hora de la peticion
    # ahora = datetime.now()
    # minutos_redondeados = (ahora.minute // 30 + 1) * 30
    # hora_redondeada = ahora.replace(minute=0) + timedelta(minutes=minutos_redondeados)

    # # Convertir a formato HH:MM
    # hora_final = hora_redondeada.strftime("%H:%M")

    # print(hora_final)

    not_available = list(chain(dates_employee, absences_employee))

    not_available = sorted(not_available, key=lambda not_available: not_available["hour_start"])

    print('citas: ', not_available)
    print('=============================')

    # Generar horas del horario de atencion
    # if day == datetime.today().strftime("%Y-%m-%d"):
    #   start = hora_final
    # else:
    start = schedule_employee['hour_start']
    end = schedule_employee['hour_end']
    interval = timedelta(hours=0, minutes=15)
    available_hours = []

    # Convertir a datetime para manipularlo
    act = datetime.combine(datetime.today(), start)

    while act.time() < end:
        available_hours.append(act.time())
        act += interval  # Sumar el intervalo

    print('horas: ', available_hours)
    print('=============================')

    # Generar horas ocupadas
    busy_hours = []

    for i in range(0, len(not_available)):
      start = not_available[i]['hour_start']
      end = not_available[i]['hour_end']

      # Convertir a datetime para manipularlo
      act = datetime.combine(datetime.today(), start)

      while act.time() < end:
          busy_hours.append(act.time())
          act += interval  # Sumar el intervalo

    print('ocupadas: ', busy_hours)
    print('=============================')

    #Eliminar horas ocupadas de horas disponibles
    for hour in busy_hours:
      available_hours.remove(hour)

    print('disponibles-ocupadas: ', available_hours)
    print('=============================')

    # Generar las franjas disponibles
    available_slots = []

    start_act = schedule_employee["hour_start"]

    if len(not_available) != 0:
      for appointment in not_available:

          if start_act < appointment["hour_start"]:
              slots = {
                  "hour_start": start_act,
                  "hour_end": appointment["hour_start"]
              }
              available_slots.append(slots)

          start_act = appointment["hour_end"]

      if start_act < schedule_employee["hour_end"]:
          slots = {
              "hour_start": start_act,
              "hour_end": schedule_employee["hour_end"]
          }
          available_slots.append(slots)
    else:
      slots = {
          "hour_start": schedule_employee["hour_start"],
          "hour_end": schedule_employee["hour_end"]
      }
      available_slots.append(slots)

    print('franjas: ', available_slots)
    print('=============================')

    #Generar posibles citas   
    possible_date = []

    for hour in available_hours:
      serv = service_duration['duration']
      start = timedelta(hours=hour.hour, minutes=hour.minute)
      serv = timedelta(hours=serv.hour, minutes=serv.minute)
      sum = start +  serv
      horas, resto = divmod(sum.total_seconds(), 3600)
      minutos, segundos = divmod(resto, 60)
      end = time(int(horas), int(minutos), int(segundos))
      possible_date.append({'hour_start': hour, 'hour_end': end})   

    print('posibles: ', possible_date)
    print('=============================')         

    #Eliminar de posibles citas las que se cruzan con las registradas
    hour_options = []
    for slots in available_slots:
      for appointment in possible_date:
        if appointment['hour_start'] >= slots['hour_start'] and appointment['hour_end'] <= slots['hour_end']:
          hour_options.append(appointment['hour_start'])

    return Response(hour_options, status=status.HTTP_200_OK)
  
  except:
    if date.fromisoformat(day) == 'domingo':
      return Response({'detail': 'Día no laborable.'}, status=status.HTTP_404_NOT_FOUND)
    else:
      return Response({'detail': 'No existen horas disponibles.'}, status=status.HTTP_404_NOT_FOUND)