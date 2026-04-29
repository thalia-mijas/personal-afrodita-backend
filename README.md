# Afrodita Backend

> API REST para la gestión integral de un centro de estética: servicios, empleados, horarios, ausencias, clientes y reserva de citas.

[![Django](https://img.shields.io/badge/Django-5.1.4-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15.2-A30000?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-23.0-499848?logo=gunicorn&logoColor=white)](https://gunicorn.org/)

---

## Tabla de contenidos

- [Descripción](#descripción)
- [Stack tecnológico](#stack-tecnológico)
- [Arquitectura del proyecto](#arquitectura-del-proyecto)
- [Modelo de datos](#modelo-de-datos)
- [Endpoints de la API](#endpoints-de-la-api)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Configuración](#configuración)
- [Despliegue](#despliegue)
- [Estructura de directorios](#estructura-de-directorios)
- [Buenas prácticas y notas](#buenas-prácticas-y-notas)

---

## Descripción

**Afrodita Backend** es una API construida con **Django REST Framework** que da soporte a la operación de un salón de estética. Permite administrar el calendario de apertura, el catálogo de servicios, la plantilla de empleados, sus horarios y ausencias, así como gestionar clientes y la agenda de citas con cálculo automático de horas disponibles.

### Características principales

- **Gestión de apertura del centro** por día de la semana con validación de horas.
- **Catálogo de servicios** clasificados por categoría (`Peluquería`, `Estética`, `Tratamientos`).
- **Empleados** con servicios asociados (relación *many-to-many*).
- **Horarios laborales** por empleado validados contra el horario del centro.
- **Ausencias** puntuales por fecha y franja horaria.
- **Clientes** con validación de teléfono español (`+34`).
- **Citas** con cálculo automático de la hora de finalización a partir de la duración del servicio.
- **Algoritmo de disponibilidad** que devuelve los huecos válidos para reservar dado un servicio, un empleado y un día.
- Internacionalización en español (`es-es`) y zona horaria `Europe/Madrid`.

---

## Stack tecnológico

| Componente              | Versión   | Rol                                       |
| ----------------------- | --------- | ----------------------------------------- |
| Python                  | 3.13.0    | Lenguaje                                  |
| Django                  | 5.1.4     | Framework web                             |
| Django REST Framework   | 3.15.2    | Construcción de la API REST               |
| SimpleJWT               | 5.4.0     | Autenticación basada en JSON Web Tokens   |
| SQLite                  | 3         | Base de datos por defecto                 |
| Gunicorn                | 23.0.0    | Servidor WSGI para producción             |
| python-dotenv           | 1.0.1     | Carga de variables de entorno             |

---

## Arquitectura del proyecto

El proyecto se organiza en dos módulos Django:

- **`afroditaapi/`** — proyecto principal: configuración (`settings.py`), enrutado raíz (`urls.py`) y entradas WSGI/ASGI.
- **`settingssalon/`** — aplicación de dominio: modelos, serializadores, vistas y rutas del salón.

### Flujo general

```text
Cliente HTTP
      │
      ▼
┌───────────────────────┐
│   afroditaapi/urls    │  ── /admin/ ────────────► Django Admin
│                       │  ── /api-settings/ ─────► settingssalon.urls
└───────────────────────┘
                                       │
                                       ▼
                       ┌────────────────────────────┐
                       │   ViewSets + Serializers   │
                       └────────────────────────────┘
                                       │
                                       ▼
                       ┌────────────────────────────┐
                       │      Modelos (ORM)         │
                       └────────────────────────────┘
                                       │
                                       ▼
                                   SQLite
```

---

## Modelo de datos

| Modelo          | Descripción                                                                 | Campos clave                                                                       |
| --------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `OpeningDays`   | Día de apertura del centro y franja horaria.                                | `day` (único), `state_day` (`abierto`/`cerrado`), `hour_start`, `hour_end`         |
| `Services`      | Servicios ofertados.                                                        | `service`, `category`, `duration`, `price`, `description`                          |
| `Employees`     | Plantilla del centro, vinculada a uno o varios servicios.                   | `email`, `name`, `phone_number` (regex `+34`), `services` *(M2M)*                  |
| `Schedules`     | Horario semanal de cada empleado.                                           | `employee` *(FK)*, `day`, `state_day` (`trabajo`/`descanso`), `hour_start`, `hour_end` |
| `Absences`      | Ausencias puntuales del empleado.                                           | `employee` *(FK)*, `date`, `hour_start`, `hour_end`, `reason`                      |
| `Clients`       | Clientes del centro.                                                        | `email`, `name`, `phone_number` (regex `+34`)                                      |
| `Dates`         | Citas reservadas. La hora de fin se calcula a partir de la duración.        | `client`, `employee`, `service` *(FK)*, `date`, `hour_start`, `hour_end` *(auto)*  |

> **Validación de teléfono.** Tanto `Employees` como `Clients` exigen el formato español `+34` seguido de 9 dígitos.

> **Cálculo automático.** El método `Dates.save()` suma `hour_start + service.duration` para fijar `hour_end` antes de persistir, evitando inconsistencias de duración.

---

## Endpoints de la API

> **Prefijo base:** `/api-settings/`

### Recursos CRUD (ViewSets)

| Método HTTP | Ruta                  | Descripción                                |
| ----------- | --------------------- | ------------------------------------------ |
| `GET/POST`  | `/openingdays/`       | Listar y crear días de apertura            |
| `GET/PUT/DELETE` | `/openingdays/{id}/` | Detalle, actualización y borrado        |
| `GET/POST`  | `/services/`          | Listar y crear servicios                   |
| `GET/POST`  | `/employees/`         | Listar y crear empleados                   |
| `GET/POST`  | `/schedules/`         | Listar y crear horarios                    |
| `GET/POST`  | `/absences/`          | Listar y crear ausencias                   |
| `GET/POST`  | `/clients/`           | Listar y crear clientes                    |
| `GET/POST`  | `/dates/`             | Listar y crear citas                       |

> Cada ViewSet expone también las rutas `PUT`, `PATCH` y `DELETE` sobre `{id}/`.

### Endpoints especializados

| Método | Ruta                                                                 | Propósito                                                                  |
| ------ | -------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `GET`  | `/servicesbyemployee/{pk}/`                                          | Servicios que ofrece un empleado.                                          |
| `GET`  | `/employeesbyservice/{pk}/`                                          | Empleados que prestan un servicio.                                         |
| `GET`  | `/schedulesbyemployee/sr={service_id}/em={employee_id}/dt={day}/`    | Horas disponibles para reservar (servicio + empleado + fecha `YYYY-MM-DD`). |

### Reglas de negocio destacadas

- **`OpeningDays.create/update`**: si el día está `abierto`, exige `hour_start < hour_end`; si está `cerrado`, fuerza ambas horas a `null`.
- **`Schedules.create/update`**: si el empleado está en `trabajo`, sus horas deben caber dentro del horario del centro para ese día.
- **`get_schedules_available`**: combina horarios, citas existentes y ausencias para devolver únicamente los huecos en los que cabe íntegramente la duración del servicio.

---

## Instalación

### Requisitos previos

- Python **3.13.0**
- `pip` y `venv`
- Git

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/thalia-mijas/personal-afrodita-backend.git
cd personal-afrodita-backend

# 2. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate          # macOS / Linux
# .\venv\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Aplicar migraciones
python manage.py migrate

# 5. (Opcional) Crear superusuario para el panel /admin
python manage.py createsuperuser
```

---

## Ejecución

### Modo desarrollo

```bash
python manage.py runserver
```

La API quedará disponible en `http://127.0.0.1:8000/` y el panel administrativo en `http://127.0.0.1:8000/admin/`.

### Modo producción (local con Gunicorn)

```bash
python manage.py collectstatic --noinput
gunicorn afroditaapi.wsgi
```

---

## Configuración

### Variables y ajustes relevantes (`afroditaapi/settings.py`)

| Ajuste              | Valor por defecto              | Notas                                                            |
| ------------------- | ------------------------------ | ---------------------------------------------------------------- |
| `DEBUG`             | `True`                         | Cambiar a `False` en producción.                                 |
| `ALLOWED_HOSTS`     | `['*']`                        | Restringir a dominios concretos en producción.                   |
| `LANGUAGE_CODE`     | `es-es`                        | Localización española.                                           |
| `TIME_ZONE`         | `Europe/Madrid`                | Hora local para citas y horarios.                                |
| `DATABASES.default` | SQLite (`db.sqlite3`)          | Reemplazable por PostgreSQL/MySQL ajustando la clave `default`.  |
| `STATIC_URL`        | `/static/`                     | Archivos estáticos servidos desde `staticfiles/`.                |

> **Aviso de seguridad.** `SECRET_KEY` está incluida en el repositorio con fines de desarrollo. **Reemplázala** y muévela a una variable de entorno antes de desplegar.

---

## Despliegue

El proyecto incluye los archivos necesarios para desplegar en plataformas tipo **Heroku / Render**:

- **`Procfile`** — define el proceso `web: gunicorn afroditaapi.wsgi`.
- **`runtime.txt`** — fija la versión de Python (`python-3.13.0`).
- **`requirements.txt`** — dependencias congeladas.
- **`staticfiles/`** — destino de `collectstatic`.

Pasos resumidos:

1. Configurar `DEBUG=False` y `ALLOWED_HOSTS` con el dominio real.
2. Mover `SECRET_KEY` y credenciales a variables de entorno.
3. Ejecutar `python manage.py collectstatic --noinput`.
4. Aplicar migraciones en el host de destino.

---

## Estructura de directorios

```text
personal-afrodita-backend/
├── afroditaapi/                # Proyecto Django (configuración)
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── settingssalon/              # Aplicación de dominio
│   ├── migrations/             # Historial de migraciones
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               # Modelos del dominio
│   ├── serializers.py          # Serializadores DRF
│   ├── tests.py
│   ├── urls.py                 # Rutas de la app
│   └── views.py                # ViewSets y vistas funcionales
├── staticfiles/                # Salida de collectstatic
├── db.sqlite3                  # Base de datos local
├── manage.py                   # Utilidad de gestión Django
├── Procfile                    # Comando de arranque (gunicorn)
├── requirements.txt            # Dependencias del proyecto
├── runtime.txt                 # Versión de Python
└── README.md
```

---

## Buenas prácticas y notas

- **Validaciones de unicidad** aplicadas mediante `UniqueTogetherValidator` en los serializadores (p. ej. `service + category`, `employee + day`).
- **Borrado en cascada** desde `Employees`, `Services` y `Clients` hacia sus relaciones dependientes (`Schedules`, `Absences`, `Dates`).
- **Internacionalización** activa: el cálculo de disponibilidad traduce el día de la semana al español usando `gettext` para casar contra los valores de `DayOptions`.
- **Recomendaciones para producción**:
  - Reemplazar SQLite por una base de datos persistente.
  - Externalizar `SECRET_KEY`, credenciales y `DEBUG` a variables de entorno.
  - Cerrar `ALLOWED_HOSTS` al dominio del despliegue.
  - Añadir cabeceras CORS si la API se consume desde un frontend separado.

---

<p align="center"><sub>Hecho con Django REST Framework · Localización <strong>es-es</strong> · Zona horaria <strong>Europe/Madrid</strong></sub></p>
