from chalice import Chalice
from psycopg2 import pool
import os

app = Chalice(app_name='vehiculos-api')

# Database connection pool
connection_pool = None

def initialize_db_pool():
    """Initialize PostgreSQL connection pool."""
    global connection_pool
    try:
        connection_pool = pool.ThreadedConnectionPool(
            minconn=int(os.environ["min_connections"]),
            maxconn=int(os.environ["max_connections"]),
            host=os.environ["DB_HOST"],
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASS"]
        )
        print("Database connection pool initialized successfully")
    except Exception as e:
        print(f"Error initializing connection pool: {e}")
        sys.exit(1)

def get_db_connection():
    """Get a connection from the pool."""
    try:
        return connection_pool.getconn()
    except Exception as e:
        print(f"Error getting connection: {e}")
        return None

def release_db_connection(conn):
    """Release a connection back to the pool."""
    if conn:
        try:
            connection_pool.putconn(conn)
        except Exception as e:
            print(f"Error releasing connection: {e}")

# Initialize the pool when the app starts (once)
initialize_db_pool()

@app.route('/data', methods=['GET'])
def message():
    return {'message': "Welcome to the project API"}

# -------------------------
# SENSOR REGISTRATION
# -------------------------

@app.route('/data/{vehicle_id}/sensors', methods=['POST'])
def register_sensor(vehicle_id):
    data = app.current_request.json_body
    conn = get_db_connection()
    if conn is None:
        return {'error': 'Could not get DB connection'}, 500
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sensors (sensor_id, vehicle_id, sensor_type, installation_date, last_calibration, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['sensor_id'],
            vehicle_id,
            data['sensor_type'],
            data['installation_date'],
            data.get('last_calibration'),
            data.get('status', 'active')
        ))
        conn.commit()
        cur.close()
        return {'message': f"Sensor '{data['sensor_type']}' successfully registered."}
    except Exception as e:
        print(f"Error register_sensor: {e}")
        return {'error': str(e)}, 500
    finally:
        release_db_connection(conn)

# -------------------------
# LIST SENSORS BY VEHICLE
# -------------------------
@app.route('/data/{vehicle_id}/sensors', methods=['GET'])
def list_sensors(vehicle_id):
    conn = get_db_connection()
    if conn is None:
        return {'error': 'Could not get DB connection'}, 500
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT sensor_id, sensor_type, installation_date, status
            FROM sensors
            WHERE vehicle_id = %s
        """, (vehicle_id,))
        results = cur.fetchall()
        cur.close()

        # Convert dates to string
        sensors = []
        for row in results:
            sensors.append({
                'sensor_id': row[0],
                'sensor_type': row[1],
                'installation_date': row[2].isoformat() if row[2] else None,
                'status': row[3]
            })
        return {'sensors': sensors}
    except Exception as e:
        print(f"Error list_sensors: {e}")
        return {'error': str(e)}, 500
    finally:
        release_db_connection(conn)

# -------------------------
# REGISTER SENSOR EVENTS
# -------------------------

@app.route('/data/{vehicle_id}/sensors/airbag/{sensor_id}', methods=['POST'])
def register_airbag_data(vehicle_id, sensor_id):
    data = app.current_request.json_body
    conn = get_db_connection()
    if conn is None:
        return {'error': 'Could not get DB connection'}, 500
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO airbag_events (sensor_id, activated, timestamp, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            sensor_id,
            data['airbag_activated'],
            data['timestamp'],
            data['location']['latitude'],
            data['location']['longitude']
        ))
        conn.commit()
        cur.close()
        return {'message': 'Airbag sensor data registered'}
    except Exception as e:
        print(f"Error register_airbag_data: {e}")
        return {'error': str(e)}, 500
    finally:
        release_db_connection(conn)


@app.route('/data/{vehicle_id}/sensors/battery/{sensor_id}', methods=['POST'])
def register_battery_data(vehicle_id, sensor_id):
    data = app.current_request.json_body
    conn = get_db_connection()
    if conn is None:
        return {'error': 'Could not get DB connection'}, 500
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO battery_events (sensor_id, voltage, charge_level, temperature, status, timestamp, unit_voltage, unit_temperature)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            sensor_id,
            data['voltage'],
            data['charge_level'],
            data['temperature'],
            data['status'],
            data['timestamp'],
            data.get('unit_voltage', 'V'),
            data.get('unit_temperature', 'Celsius')
        ))
        conn.commit()
        cur.close()
        return {'message': 'Battery sensor data registered'}
    except Exception as e:
        print(f"Error register_battery_data: {e}")
        return {'error': str(e)}, 500
    finally:
        release_db_connection(conn)

@app.route('/data/{vehicle_id}/sensors/fuel/{sensor_id}', methods=['POST'])
def register_fuel_data(vehicle_id, sensor_id):
    data = app.current_request.json_body
    conn = get_db_connection()
    if conn is None:
        return {'error': 'Could not get DB connection'}, 500
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO fuel_events (sensor_id, level, unit, timestamp)
            VALUES (%s, %s, %s, %s)
        """, (
            sensor_id,
            data['level'],
            data['unit'],
            data['timestamp']
        ))
        conn.commit()
        cur.close()
        return {'message': 'Fuel sensor data registered'}
    except Exception as e:
        print(f"Error register_fuel_data: {e}")
        return {'error': str(e)}, 500
    finally:
        release_db_connection(conn)

# -------------------------
# QUERY SENSOR EVENTS
# -------------------------

@app.route('/data/{vehicle_id}/sensors/{sensor_type}/{sensor_id}/events', methods=['GET'])
def get_sensor_events(vehicle_id, sensor_type, sensor_id):
    conn = get_db_connection()
    if conn is None:
        return {'error': 'Could not get DB connection'}, 500
    try:
        cur = conn.cursor()
        events = []

        if sensor_type == 'airbag':
            cur.execute("""
                SELECT timestamp, latitude, longitude, activated
                FROM airbag_events
                WHERE sensor_id = %s
                ORDER BY timestamp DESC
                LIMIT 50
            """, (sensor_id,))
            for row in cur.fetchall():
                events.append({
                    'timestamp': row[0].isoformat(),
                    'latitude': row[1],
                    'longitude': row[2],
                    'activated': row[3]
                })

        elif sensor_type == 'battery':
            cur.execute("""
                SELECT timestamp, voltage, charge_level, temperature, status, unit_voltage, unit_temperature
                FROM battery_events
                WHERE sensor_id = %s
                ORDER BY timestamp DESC
                LIMIT 50
            """, (sensor_id,))
            for row in cur.fetchall():
                events.append({
                    'timestamp': row[0].isoformat(),
                    'voltage': float(row[1]),
                    'charge_level': int(row[2]),
                    'temperature': float(row[3]),
                    'status': row[4],
                    'unit_voltage': row[5],
                    'unit_temperature': row[6]
                })

        elif sensor_type == 'fuel':
            cur.execute("""
                SELECT timestamp, level, unit
                FROM fuel_events
                WHERE sensor_id = %s
                ORDER BY timestamp DESC
                LIMIT 50
            """, (sensor_id,))
            for row in cur.fetchall():
                events.append({
                    'timestamp': row[0].isoformat(),
                    'level': float(row[1]),
                    'unit': row[2]
                })

        else:
            return {'error': 'Invalid sensor type'}, 400

        cur.close()
        return {'events': events}

    except Exception as e:
        print(f"Error get_sensor_events: {e}")
        return {'error': str(e)}, 500
    finally:
        release_db_connection(conn)

# -------------------------
# ACTUATORS
# -------------------------

@app.route('/data/{vehicle_id}/actuators', methods=['GET'])
def get_actuators(vehicle_id):
    conn = get_db_connection()
    if conn is None:
        return {'error': 'Could not get DB connection'}, 500
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT actuator_id, actuator_name, sensor_type, description, code
            FROM actuators
            ORDER BY actuator_name ASC
        """)
        actuators = []
        for row in cur.fetchall():
            actuators.append({
                'actuator_id': row[0],
                'actuator_name': row[1],
                'sensor_type': row[2],
                'description': row[3],
                'code': row[4]
            })
        cur.close()
        return {'actuators': actuators}
    except Exception as e:
        print(f"Error get_actuators: {e}")
        return {'error': str(e)}, 500
    finally:
        release_db_connection(conn)

@app.route('/data/{vehicle_id}/actuators', methods=['POST'])
def register_actuator(vehicle_id):
    conn = get_db_connection()
    if conn is None:
        return {'error': 'Could not get DB connection'}, 500

    try:
        request = app.current_request
        data = request.json_body

        actuator_id = data.get('actuator_id')
        actuator_name = data.get('actuator_name')
        sensor_type = data.get('sensor_type')
        description = data.get('description')
        code = data.get('code')

        if not actuator_id or not actuator_name or not code:
            return {'error': 'Fields actuator_id, actuator_name, and code are required.'}, 400

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO actuators (actuator_id, actuator_name, sensor_type, description, code)
            VALUES (%s, %s, %s, %s, %s)
        """, (actuator_id, actuator_name, sensor_type, description, code))

        conn.commit()
        cur.close()
        return {'message': 'Actuator successfully registered'}

    except Exception as e:
        print(f"Error register_actuator: {e}")
        return {'error': str(e)}, 500
    finally:
        release_db_connection(conn)
