
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def connect_db():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "medisimplify")
        )
    except mysql.connector.Error as error:
        print(f"MySQL connection error: {error}")
        return None


def test_connection():
    connection = connect_db()

    if connection:
        print("MediSimplify MySQL connection successful!")
        connection.close()
        return True

    print("Could not connect to MySQL.")
    return False



def add_patient(
    name, age=None, gender=None, report_date=None,
    hospital_name=None, blood_group=None,
    emergency_contact=None, allergies=None,
    medical_history=None, medications=None,
    past_surgeries=None, family_history=None
):
    connection = connect_db()

    if not connection:
        return None

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO patients (
                patient_name, age, gender, report_date,
                hospital_name, blood_group, emergency_contact,
                allergies, medical_history, current_medications,
                past_surgeries, family_history
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            name, age, gender, report_date,
            hospital_name, blood_group, emergency_contact,
            allergies, medical_history, medications,
            past_surgeries, family_history
        )

        cursor.execute(query, values)
        connection.commit()

        return cursor.lastrowid

    except mysql.connector.Error as error:
        print(f"Patient save error: {error}")
        connection.rollback()
        return None

    finally:
        if cursor:
            cursor.close()
        connection.close()



def get_patients():
    connection = connect_db()

    if not connection:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT patient_id, patient_name, age, gender,
                   blood_group, emergency_contact, created_at
            FROM patients
            ORDER BY patient_id DESC
        """)

        return cursor.fetchall()

    except mysql.connector.Error as error:
        print(f"Patient retrieval error: {error}")
        return []

    finally:
        cursor.close()
        connection.close()
