from .views import (OpeningDaysViewSet,
                    ServicesViewSet,
                    EmployeesViewSet,
                    get_services_employee,
                    get_employees_service,
                    SchedulesViewSet,
                    AbsencesViewSet,
                    ClientsViewSet,
                    get_schedules_available,
                    DatesViewSet)
from rest_framework.routers import DefaultRouter
from django.urls import path

urlpatterns = [
    path('servicesbyemployee/<int:pk>/', get_services_employee, name='get_services'),
    path('employeesbyservice/<int:pk>/', get_employees_service, name='get_employees'),
    path('schedulesbyemployee/sr=<int:service_id>/em=<int:employee_id>/dt=<str:day>/', get_schedules_available, name='get_schedule'),
]

router_days = DefaultRouter()
router_days.register('openingdays', OpeningDaysViewSet, basename="openingdays")
urlpatterns += router_days.urls

router_serv = DefaultRouter()
router_serv.register('services', ServicesViewSet, basename="services")
urlpatterns += router_serv.urls

router_empl = DefaultRouter()
router_empl.register('employees', EmployeesViewSet, basename="employees")
urlpatterns += router_empl.urls

router_sche = DefaultRouter()
router_sche.register('schedules', SchedulesViewSet, basename="schedule")
urlpatterns += router_sche.urls

router_abs = DefaultRouter()
router_abs.register('absences', AbsencesViewSet, basename="absence")
urlpatterns += router_abs.urls

router_cl = DefaultRouter()
router_cl.register('clients', ClientsViewSet, basename="client")
urlpatterns += router_cl.urls

router_dt = DefaultRouter()
router_dt.register('dates', DatesViewSet, basename="date")
urlpatterns += router_dt.urls