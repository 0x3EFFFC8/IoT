import psycopg2
from psycopg2 import pool

DB_CONFIG = {"host": "postgres","database": "health_data","user": "health_user","password": "health_password"}

connection_pool = psycopg2.pool.SimpleConnectionPool(minconn=1,maxconn=5,**DB_CONFIG)

def save_to_db(data):
    conn = None
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO medical_records (
                sensor_id,
                timestamp,
                temperature,
                heart_rate,
                blood_pressure_systolic,
                blood_pressure_diastolic
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data["sensor_id"],
            data.get("timestamp",None),
            data["vitals"].get("temperature"),
            data["vitals"].get("heart_rate"),
            data["vitals"].get("blood_pressure", {}).get("systolic"),
            data["vitals"].get("blood_pressure", {}).get("diastolic")
        ))

        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        if conn: conn.rollback()
    finally:
        if conn: connection_pool.putconn(conn)
