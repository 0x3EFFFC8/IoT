## Integrantes
- Samuel Escobar 
- Juan Manuel Hurtado
- Frank Rivera

https://docs.google.com/document/d/1MZ8h5XanAYkXcgOK2XCBNIp3fPMgTngc8YaF_UPmnyA/edit?tab=t.0

## Topicos

 - data/{vehicle_id}/battery/{sensor_id}/metrics
 - data/{vehicle_id}/airbag/{sensor_id}/events
 - data/{vehicle_id}/fuel/{sensor_id}/level

## Esquema de Base de Datos de Monitoreo de Vehículos
## Tabla `vehicles`
| Columna        | Tipo       | Descripción                     | Restricciones               |
|----------------|------------|---------------------------------|-----------------------------|
| `vehicle_id`   | VARCHAR(50)| Identificador único del vehículo | PRIMARY KEY                 |
| `make`         | VARCHAR(50)| Marca del vehículo              |                             |
| `model`        | VARCHAR(50)| Modelo del vehículo             |                             |
| `year`         | INTEGER    | Año de fabricación              |                             |
| `last_updated` | TIMESTAMP  | Fecha de última actualización   |                             |

## Tabla `sensors`
| Columna             | Tipo        | Descripción                    | Restricciones                               |
| ------------------- | ----------- | ------------------------------ | ------------------------------------------- |
| `sensor_id`         | VARCHAR(50) | Identificador único del sensor | PRIMARY KEY                                 |
| `vehicle_id`        | VARCHAR(50) | ID del vehículo asociado       | FOREIGN KEY REFERENCES vehicles(vehicle_id) |
| `sensor_type`       | VARCHAR(20) | Tipo de sensor                 | CHECK (battery, airbag, fuel)               |
| `installation_date` | DATE        | Fecha de instalación           |                                             |
| `last_calibration`  | TIMESTAMP   | Fecha de última calibración    |                                             |
| `status`            | VARCHAR(20) | Estado del sensor              | DEFAULT 'active'                            |

## Tabla `battery_events`
| Columna           | Tipo        | Descripción                          | Restricciones                              |
|-------------------|-------------|--------------------------------------|--------------------------------------------|
| `reading_id`      | SERIAL      | ID único de lectura                 | PRIMARY KEY                                |
| `sensor_id`       | VARCHAR(50) | ID del sensor de batería            | FOREIGN KEY REFERENCES sensors(sensor_id)  |
| `voltage`         | FLOAT       | Voltaje medido                      | NOT NULL                                   |
| `charge_level`    | INTEGER     | Nivel de carga (porcentaje)         | NOT NULL                                   |
| `temperature`     | FLOAT       | Temperatura de la batería           | NOT NULL                                   |
| `status`          | VARCHAR(20) | Estado de la batería                | NOT NULL                                   |
| `timestamp`       | TIMESTAMP   | Fecha y hora de la lectura          | NOT NULL                                   |
| `unit_voltage`    | VARCHAR(10) | Unidad de medida del voltaje        | DEFAULT 'V'                                |
| `unit_temperature`| VARCHAR(10) | Unidad de medida de temperatura     | DEFAULT 'Celsius'                          |

## Tabla `airbag_events`
| Columna     | Tipo        | Descripción                      | Restricciones                             |
| ----------- | ----------- | -------------------------------- | ----------------------------------------- |
| `event_id`  | SERIAL      | ID único del evento              | PRIMARY KEY                               |
| `sensor_id` | VARCHAR(50) | ID del sensor de airbag          | FOREIGN KEY REFERENCES sensors(sensor_id) |
| `activated` | BOOLEAN     | Indica si el airbag se activó    | NOT NULL                                  |
| `timestamp` | TIMESTAMP   | Fecha y hora del evento          | NOT NULL                                  |
| `latitude`  | FLOAT       | Latitud donde ocurrió el evento  |                                           |
| `longitude` | FLOAT       | Longitud donde ocurrió el evento |                                           |

## Tabla `fuel_events`
| Columna       | Tipo        | Descripción                          | Restricciones                              |
|---------------|-------------|--------------------------------------|--------------------------------------------|
| `reading_id`  | SERIAL      | ID único de lectura                 | PRIMARY KEY                                |
| `sensor_id`   | VARCHAR(50) | ID del sensor de combustible        | FOREIGN KEY REFERENCES sensors(sensor_id)  |
| `level`       | FLOAT       | Nivel de combustible                | NOT NULL                                   |
| `unit`        | VARCHAR(10) | Unidad de medida                    | NOT NULL                                   |
| `timestamp`   | TIMESTAMP   | Fecha y hora de la lectura          | NOT NULL                                   |

## Tabla `actuators`
| Columna          | Tipo        | Descripción                          | Restricciones               |
|------------------|-------------|--------------------------------------|-----------------------------|
| `actuator_id`    | VARCHAR(50) | ID único del actuador               | PRIMARY KEY                 |
| `actuator_name`  | VARCHAR(100)| Nombre del actuador                 | NOT NULL                    |
| `sensor_type`    | VARCHAR(50) | Tipo de sensor asociado             |                             |
| `description`    | TEXT        | Descripción del actuador            |                             |
| `code`           | VARCHAR(250)| Código o identificador único        | NOT NULL                    |

## Relaciones
- `sensors.vehicle_id` → `vehicles.vehicle_id`
- `battery_events.sensor_id` → `sensors.sensor_id`
- `airbag_events.sensor_id` → `sensors.sensor_id`
- `fuel_events.sensor_id` → `sensors.sensor_id`
