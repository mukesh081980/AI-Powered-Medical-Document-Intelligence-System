
import os
import mysql.connector
from dotenv import load_dotenv
import bcrypt

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

import bcrypt


def create_user(username, email, password, role, patient_id=None):
    connection = connect_db()

    if not connection:
        return False

    cursor = None

    try:
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO users (
                username, email, password_hash, role, patient_id
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (username, email, password_hash, role, patient_id))

        connection.commit()
        return cursor.lastrowid

    except mysql.connector.Error as error:
        print(f"User creation error: {error}")
        connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        connection.close()


def register_patient_account(full_name, username, email, password):

    connection = connect_db()

    if not connection:
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # Create patient record
        cursor.execute("""
            INSERT INTO patients (
                patient_name, age, gender, report_date,
                hospital_name, blood_group, emergency_contact,
                allergies, medical_history, current_medications,
                past_surgeries, family_history
            )
            VALUES (
                %s, NULL, NULL, NULL, NULL, NULL,
                NULL, NULL, NULL, NULL, NULL, NULL
            )
        """, (full_name,))

        patient_id = cursor.lastrowid

        # Create linked patient login account
        cursor.execute("""
            INSERT INTO users (
                username, email, password_hash, role, patient_id
            )
            VALUES (%s, %s, %s, 'patient', %s)
        """, (
            username,
            email,
            password_hash,
            patient_id
        ))

        user_id = cursor.lastrowid

        connection.commit()

        return user_id

    except mysql.connector.Error as error:
        connection.rollback()
        print(f"Patient registration error: {error}")
        return False

    finally:
        if cursor:
            cursor.close()

        connection.close()

def authenticate_user(username, password):
    connection = connect_db()

    if not connection:
        return None

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT user_id, username, email,
                   password_hash, role, patient_id, is_active
            FROM users
            WHERE username = %s
        """, (username,))

        user = cursor.fetchone()

        if not user or not user["is_active"]:
            return None

        password_matches = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )

        if password_matches:
            user.pop("password_hash")
            return user

        return None

    except (mysql.connector.Error, ValueError) as error:
        print(f"Login error: {error}")
        return None

    finally:
        if cursor:
            cursor.close()
        connection.close()

def get_all_users():
    connection = connect_db()

    if not connection:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT user_id, username, email, role,
                   patient_id, is_active, created_at
            FROM users
            ORDER BY user_id DESC
        """)

        return cursor.fetchall()

    except mysql.connector.Error as error:
        print(f"User retrieval error: {error}")
        return []

    finally:
        if cursor:
            cursor.close()
        connection.close()


def update_user_status(user_id, is_active):
    connection = connect_db()

    if not connection:
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE users
            SET is_active = %s
            WHERE user_id = %s
        """, (is_active, user_id))

        connection.commit()

        return cursor.rowcount > 0

    except mysql.connector.Error as error:
        print(f"User status update error: {error}")
        connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        connection.close()
def assign_patient_to_doctor(doctor_user_id, patient_id):
    connection = connect_db()

    if not connection:
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        # Verify that the selected user is an active Doctor
        cursor.execute("""
            SELECT user_id
            FROM users
            WHERE user_id = %s
              AND role = 'doctor'
              AND is_active = TRUE
        """, (doctor_user_id,))

        if not cursor.fetchone():
            return False

        cursor.execute("""
            INSERT INTO doctor_patient_assignments
                (doctor_user_id, patient_id)
            VALUES (%s, %s)
        """, (doctor_user_id, patient_id))

        connection.commit()
        return True

    except mysql.connector.Error as error:
        print(f"Patient assignment error: {error}")
        connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        connection.close()
def get_doctor_assigned_patients(doctor_user_id):
    connection = connect_db()

    if not connection:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT p.*
            FROM doctor_patient_assignments AS a
            JOIN patients AS p
                ON a.patient_id = p.patient_id
            JOIN users AS u
                ON a.doctor_user_id = u.user_id
            WHERE a.doctor_user_id = %s
              AND u.role = 'doctor'
              AND u.is_active = TRUE
            ORDER BY a.assigned_at DESC
        """, (doctor_user_id,))

        return cursor.fetchall()

    except mysql.connector.Error as error:
        print(f"Assigned patient retrieval error: {error}")
        return []

    finally:
        if cursor:
            cursor.close()
        connection.close()
def doctor_can_access_patient(doctor_user_id, patient_id):
    connection = connect_db()

    if not connection:
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT 1
            FROM doctor_patient_assignments a
            JOIN users u ON u.user_id = a.doctor_user_id
            WHERE a.doctor_user_id = %s
              AND a.patient_id = %s
              AND u.role = 'doctor'
              AND u.is_active = TRUE
            LIMIT 1
        """, (doctor_user_id, patient_id))

        return cursor.fetchone() is not None

    except mysql.connector.Error as error:
        print(f"Patient access verification error: {error}")
        return False

    finally:
        if cursor:
            cursor.close()
        connection.close()
def get_doctor_patient_details(doctor_user_id, patient_id):
    connection = connect_db()

    if not connection:
        return None

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT p.*
            FROM patients p
            JOIN doctor_patient_assignments a
                ON p.patient_id = a.patient_id
            JOIN users u
                ON a.doctor_user_id = u.user_id
            WHERE a.doctor_user_id = %s
              AND p.patient_id = %s
              AND u.role = 'doctor'
              AND u.is_active = TRUE
            LIMIT 1
        """, (doctor_user_id, patient_id))

        return cursor.fetchone()

    except mysql.connector.Error as error:
        print(f"Patient details retrieval error: {error}")
        return None

    finally:
        if cursor:
            cursor.close()
        connection.close()
def get_doctor_patient_vitals(doctor_user_id, patient_id):
    connection = connect_db()

    if not connection:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT v.*
            FROM vital_signs v
            JOIN doctor_patient_assignments a
                ON v.patient_id = a.patient_id
            JOIN users u
                ON a.doctor_user_id = u.user_id
            WHERE a.doctor_user_id = %s
              AND v.patient_id = %s
              AND u.role = 'doctor'
              AND u.is_active = TRUE
            ORDER BY v.recorded_at DESC
        """, (doctor_user_id, patient_id))

        return cursor.fetchall()

    except mysql.connector.Error as error:
        print(f"Patient vitals retrieval error: {error}")
        return []

    finally:
        if cursor:
            cursor.close()
        connection.close()
def get_doctor_patient_reports(doctor_user_id, patient_id):
    connection = connect_db()

    if not connection:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT mr.report_id,
                   mr.patient_id,
                   mr.report_date,
                   mr.hospital_name,
                   mr.file_name,
                   mr.extracted_text,
                   mr.ai_explanation,
                   mr.created_at
            FROM medical_reports mr
            JOIN doctor_patient_assignments a
                ON mr.patient_id = a.patient_id
            JOIN users u
                ON a.doctor_user_id = u.user_id
            WHERE a.doctor_user_id = %s
              AND mr.patient_id = %s
              AND u.role = 'doctor'
              AND u.is_active = TRUE
            ORDER BY mr.created_at DESC
        """, (doctor_user_id, patient_id))

        return cursor.fetchall()

    except mysql.connector.Error as error:
        print(f"Medical report retrieval error: {error}")
        return []

    finally:
        if cursor:
            cursor.close()
        connection.close()
def get_patient_profile(user_id):
    connection = connect_db()

    if not connection:
        return None

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT p.*
            FROM users u
            JOIN patients p ON u.patient_id = p.patient_id
            WHERE u.user_id = %s
              AND u.role = 'patient'
              AND u.is_active = TRUE
            LIMIT 1
        """, (user_id,))

        return cursor.fetchone()

    except mysql.connector.Error as error:
        print(f"Patient profile error: {error}")
        return None

    finally:
        if cursor:
            cursor.close()
        connection.close()
def get_patient_vitals(user_id):
    connection = connect_db()

    if not connection:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT v.*
            FROM vital_signs v
            JOIN users u ON u.patient_id = v.patient_id
            WHERE u.user_id = %s
              AND u.role = 'patient'
              AND u.is_active = TRUE
            ORDER BY v.recorded_at DESC
        """, (user_id,))

        return cursor.fetchall()

    except mysql.connector.Error as error:
        print(f"Patient vitals error: {error}")
        return []

    finally:
        if cursor:
            cursor.close()
        connection.close()
def get_patient_reports(user_id):
    connection = connect_db()

    if not connection:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT mr.*
            FROM medical_reports mr
            JOIN users u ON u.patient_id = mr.patient_id
            WHERE u.user_id = %s
              AND u.role = 'patient'
              AND u.is_active = TRUE
            ORDER BY mr.created_at DESC
        """, (user_id,))

        return cursor.fetchall()

    except mysql.connector.Error as error:
        print(f"Patient reports error: {error}")
        return []

    finally:
        if cursor:
            cursor.close()
        connection.close()
def get_active_user(user_id):
    connection = connect_db()

    if not connection:
        return None

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT user_id, username, email,
                   role, patient_id, is_active
            FROM users
            WHERE user_id = %s
              AND is_active = TRUE
        """, (user_id,))

        return cursor.fetchone()

    except mysql.connector.Error as error:
        print(f"Active user verification error: {error}")
        return None

    finally:
        if cursor:
            cursor.close()
        connection.close()



