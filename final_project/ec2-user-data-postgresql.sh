#!/bin/bash
set -e

# it’s essential to update your system to ensure you have the latest updates and refresh the DNF package cache.
sudo dnf update

# Installa PostgreSQL
sudo dnf install postgresql15.x86_64 postgresql15-server -y

# Initializing PostgreSQL Database
sudo postgresql-setup --initdb

# Starting and Enabling PostgreSQL Service
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl status postgresql

# Configure PostgreSQL
# Set password for ssh postgres user and admin postgres database password
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'money';"

# Primary Configuration File
sudo cp /var/lib/pgsql/data/postgresql.conf /var/lib/pgsql/data/postgresql.conf.bck

# Optionally, configure PostgreSQL to listen on all interfaces.
#  -  **WARNING:**  This makes your database accessible from anywhere, which can be a security risk.
#  -  Only enable this if you understand the security implications and have appropriate firewall rules in place.
#  -  This is often NOT necessary and is discouraged for production environments.
#  -  If you need remote access, consider using an SSH tunnel instead.
echo "listen_addresses = '*'" | sudo tee -a /var/lib/pgsql/data/postgresql.conf


# Next, you need to configure the pg_hba.conf file to allow connections from your remote EC2 instance. Open the pg_hba.conf file
sudo cp /var/lib/pgsql/data/pg_hba.conf /var/lib/pgsql/data/pg_hba.conf.bck

# Add an entry at the end of the file to allow connections from your remote EC2 instance
echo "host    all             all             0.0.0.0/0            md5" | sudo tee -a /var/lib/pgsql/data/pg_hba.conf

# To apply all the changes, restart the PostgreSQL service using the following command.
sudo systemctl restart postgresql

# Optionally, create a new database and user
#  -  Replace 'your_database_name' and 'your_user_name' with your desired names.
#  -  Replace 'YourNewPassword' with a strong, secure password.
#  -  This is just an example; adapt it to your specific needs.
sudo -u postgres psql -c "CREATE DATABASE iot_project;"
sudo -u postgres psql -c "CREATE USER test WITH PASSWORD 'money';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE iot_project TO test;"

# Create database tables and insert sample data
sudo -u postgres psql -d iot_project <<EOF

CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id VARCHAR(50) PRIMARY KEY,
    make VARCHAR(50),
    model VARCHAR(50),
    year INTEGER,
    last_updated TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sensors (
    sensor_id VARCHAR(50) PRIMARY KEY,
    vehicle_id VARCHAR(50) REFERENCES vehicles(vehicle_id),
    sensor_type VARCHAR(20) CHECK (sensor_type IN ('battery', 'airbag', 'fuel')),
    installation_date DATE,
    last_calibration TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS battery_events (
    reading_id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) REFERENCES sensors(sensor_id),
    voltage FLOAT NOT NULL,
    charge_level INTEGER NOT NULL,
    temperature FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    unit_voltage VARCHAR(10) DEFAULT 'V',
    unit_temperature VARCHAR(10) DEFAULT 'Celsius'
);

CREATE TABLE IF NOT EXISTS airbag_events (
    event_id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) REFERENCES sensors(sensor_id),
    activated BOOLEAN NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    latitude FLOAT,
    longitude FLOAT
);

CREATE TABLE IF NOT EXISTS fuel_events (
    reading_id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) REFERENCES sensors(sensor_id),
    level FLOAT NOT NULL,
    unit VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

CREATE TABLE actuators (
    actuator_id VARCHAR(50) PRIMARY KEY,
    actuator_name VARCHAR(100) NOT NULL,
    sensor_type VARCHAR(50),
    description TEXT,
    code VARCHAR(250) NOT NULL
);

INSERT INTO vehicles (vehicle_id, make, model, year, last_updated)
VALUES ('car001', 'Tesla', 'Model 3', 2023, NOW());

INSERT INTO sensors (sensor_id, vehicle_id, sensor_type, installation_date, last_calibration)
VALUES ('battery001', 'car001', 'battery', '2023-01-15', '2023-06-01');

INSERT INTO sensors (sensor_id, vehicle_id, sensor_type, installation_date, last_calibration)
VALUES ('airbag001', 'car001', 'airbag', '2023-01-15', '2023-01-15');

INSERT INTO sensors (sensor_id, vehicle_id, sensor_type, installation_date, last_calibration)
VALUES ('fuel001', 'car001', 'fuel', '2023-01-15', '2023-06-01');

EOF
