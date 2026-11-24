
import getpass
import database
import re

print("===== MediSimplify AI - Admin Setup =====")

username = input("Enter admin username: ").strip()
email = input("Enter admin email: ").strip().lower()

if not username or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
    print("Invalid username or email.")
    raise SystemExit

password = getpass.getpass("Enter admin password: ")
confirm_password = getpass.getpass("Confirm admin password: ")

if len(password) < 12:
    print("Password must contain at least 12 characters.")
    raise SystemExit

if password != confirm_password:
    print("Passwords do not match.")
    raise SystemExit

user_id = database.create_user(
    username=username,
    email=email,
    password=password,
    role="admin"
)

if user_id:
    print(f"Admin account created successfully! User ID: {user_id}")
else:
    print("Admin account creation failed. Check whether the username or email already exists.")
