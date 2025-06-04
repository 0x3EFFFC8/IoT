CREATE TABLE patients (
    patient_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    gender VARCHAR(10)
);

CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    site VARCHAR(50),          
    floor VARCHAR(50),        
    room VARCHAR(50),
    UNIQUE(site, floor, room)
);

CREATE TABLE sensors (
    sensor_id VARCHAR(50) PRIMARY KEY,
    patient_id VARCHAR(50) REFERENCES patients(patient_id),
    location_id INT REFERENCES locations(location_id)
);

CREATE TABLE medical_records (
    record_id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) REFERENCES sensors(sensor_id),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    temperature FLOAT,
    heart_rate FLOAT,
    blood_pressure_systolic FLOAT,
    blood_pressure_diastolic FLOAT
);

INSERT INTO patients (patient_id, name, age, gender) VALUES ('001', 'Pedro', 45, 'male') ON CONFLICT (patient_id) DO NOTHING;
INSERT INTO patients (patient_id, name, age, gender) VALUES ('002', 'Valentina', 32, 'female') ON CONFLICT (patient_id) DO NOTHING;
INSERT INTO patients (patient_id, name, age, gender) VALUES ('003', 'Camila', 29, 'female') ON CONFLICT (patient_id) DO NOTHING;

INSERT INTO locations (site, floor, room) VALUES ('north', '3', '2') ON CONFLICT (site, floor, room) DO NOTHING;
INSERT INTO locations (site, floor, room) VALUES ('south', '2', '10') ON CONFLICT (site, floor, room) DO NOTHING;
INSERT INTO locations (site, floor, room) VALUES ('south', '1', '1') ON CONFLICT (site, floor, room) DO NOTHING;

INSERT INTO sensors (sensor_id, patient_id, location_id) VALUES ('01', '001', (SELECT location_id FROM locations WHERE site = 'north' AND floor = '3' AND room = '2')) ON CONFLICT (sensor_id) DO NOTHING;
INSERT INTO sensors (sensor_id, patient_id, location_id) VALUES ('02', '002', (SELECT location_id FROM locations WHERE site = 'south' AND floor = '2' AND room = '10')) ON CONFLICT (sensor_id) DO NOTHING;
INSERT INTO sensors (sensor_id, patient_id, location_id) VALUES ('03', '003', (SELECT location_id FROM locations WHERE site = 'south' AND floor = '1' AND room = '1')) ON CONFLICT (sensor_id) DO NOTHING;
