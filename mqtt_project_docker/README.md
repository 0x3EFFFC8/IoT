
## Integrantes
- Samuel Escobar 
- Juan Manuel Hurtado
- Frank Rivera

https://docs.google.com/document/d/1dFw7Fzg0b4iVOe_OlebzRJPCuuLNQcg8M-uLompzrKI/edit?tab=t.0

## Topico

data/health/{site}/{floor}/{room}/{'sensor_id'}/vitals"

## Esquema de Base de Datos de Monitoreo Médico
## Tabla `patients`
| Columna       | Tipo         | Descripción                     | Restricciones               |
|---------------|--------------|---------------------------------|-----------------------------|
| `patient_id`  | VARCHAR(50)  | Identificador único del paciente| PRIMARY KEY                 |
| `name`        | VARCHAR(100) | Nombre del paciente             |                             |
| `age`         | INT          | Edad del paciente               |                             |
| `gender`      | VARCHAR(10)  | Género del paciente             |                             |

## Tabla `locations`
| Columna       | Tipo    | Descripción                     | Restricciones               |
|---------------|---------|---------------------------------|-----------------------------|
| `location_id` | SERIAL  | ID único de ubicación           | PRIMARY KEY                 |
| `site`        | VARCHAR(50) | Sitio (ej. hospital, clínica) | UNIQUE(site, floor, room)   |
| `floor`       | VARCHAR(50) | Piso                           | UNIQUE(site, floor, room)   |
| `room`        | VARCHAR(50) | Habitación                     | UNIQUE(site, floor, room)   |

## Tabla `sensors`
| Columna       | Tipo         | Descripción                     | Restricciones                              |
|---------------|--------------|---------------------------------|--------------------------------------------|
| `sensor_id`   | VARCHAR(50)  | ID único del sensor             | PRIMARY KEY                                |
| `patient_id`  | VARCHAR(50)  | ID del paciente asociado         | FOREIGN KEY REFERENCES patients(patient_id)|
| `location_id` | INT          | ID de ubicación del sensor      | FOREIGN KEY REFERENCES locations(location_id)|

## Tabla `medical_records`
| Columna                   | Tipo         | Descripción                     | Restricciones                              |
|---------------------------|--------------|---------------------------------|--------------------------------------------|
| `record_id`               | SERIAL       | ID único del registro médico    | PRIMARY KEY                                |
| `sensor_id`               | VARCHAR(50)  | ID del sensor que generó el dato | FOREIGN KEY REFERENCES sensors(sensor_id)  |
| `timestamp`               | TIMESTAMPTZ  | Fecha y hora del registro       | DEFAULT NOW()                              |
| `temperature`             | FLOAT        | Temperatura corporal (ºC)       |                                            |
| `heart_rate`              | FLOAT        | Frecuencia cardíaca (lpm)       |                                            |
| `blood_pressure_systolic` | FLOAT        | Presión arterial sistólica (mmHg)|                                            |
| `blood_pressure_diastolic`| FLOAT        | Presión arterial diastólica (mmHg)|                                           |

## Relaciones
1. `sensors.patient_id` → `patients.patient_id`  
   
2. `sensors.location_id` → `locations.location_id`  

3. `medical_records.sensor_id` → `sensors.sensor_id`  

