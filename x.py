from flask import request, make_response
from functools import wraps
import mysql.connector
import re
import os
import uuid
import os

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)

UNSPLASH_ACCESS_KEY = 'YOUR_KEY_HERE'
ADMIN_ROLE_PK = "16fd2706-8baf-433b-82eb-8c7fada847da"
CUSTOMER_ROLE_PK = "c56a4180-65aa-42ec-a945-5fd21dec0538"
PARTNER_ROLE_PK = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
RESTAURANT_ROLE_PK = "9f8c8d22-5a67-4b6c-89d7-58f8b8cb4e15"


# form to get data from input fields
# args to get data from the url
# values to get data from the url and from the form

class CustomException(Exception):
    def __init__(self, message, code):
        super().__init__(message)  # Initialize the base class with the message
        self.message = message  # Store additional information (e.g., error code)
        self.code = code  # Store additional information (e.g., error code)

def raise_custom_exception(error, status_code):
    raise CustomException(error, status_code)

##############################

BASE_URL = "https://katjakrogh.pythonanywhere.com" if "PYTHONANYWHERE_DOMAIN" in os.environ else "http://127.0.0.1"

##############################
def db():
    host = "katjakrogh.mysql.pythonanywhere-services.com" if "PYTHONANYWHERE_DOMAIN" in os.environ else "mysql"
    database = "katjakrogh$company" if "PYTHONANYWHERE_DOMAIN" in os.environ else "company"
    user = "katjakrogh" if "PYTHONANYWHERE_DOMAIN" in os.environ else "root"
    password = "mysqlpassword" if "PYTHONANYWHERE_DOMAIN" in os.environ else "password"

    db = mysql.connector.connect(
        host = host,
        user = user,
        password = password,
        database = database
    )
    cursor = db.cursor(dictionary=True)
    return db, cursor

##############################
def no_cache(view):
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return no_cache_view


##############################
def allow_origin(origin="*"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Call the wrapped function
            response = make_response(f(*args, **kwargs))
            # Add Access-Control-Allow-Origin header to the response
            response.headers["Access-Control-Allow-Origin"] = origin
            # Optionally allow other methods and headers for full CORS support
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response
        return decorated_function
    return decorator


##############################
USER_NAME_MIN = 2
USER_NAME_MAX = 20
USER_NAME_REGEX = f"^.{{{USER_NAME_MIN},{USER_NAME_MAX}}}$"
def validate_user_name():
    error = f"Name must be {USER_NAME_MIN} to {USER_NAME_MAX} characters"
    user_name = request.form.get("user_name", "").strip()
    if not re.match(USER_NAME_REGEX, user_name): raise_custom_exception(error, 400)
    return user_name

##############################
USER_LAST_NAME_MIN = 2
USER_LAST_NAME_MAX = 20
USER_LAST_NAME_REGEX = f"^.{{{USER_LAST_NAME_MIN},{USER_LAST_NAME_MAX}}}$"
def validate_user_last_name():
    error = f"Last name must be {USER_LAST_NAME_MIN} to {USER_LAST_NAME_MAX} characters"
    user_last_name = request.form.get("user_last_name", "").strip() 
    if not re.match(USER_LAST_NAME_REGEX, user_last_name): raise_custom_exception(error, 400)
    return user_last_name

##############################
USER_ADDRESS_MIN = 2
USER_ADDRESS_MAX = 50
USER_ADDRESS_REGEX = r"^(?=.*\d)(?=.*[a-zA-Z]).+$" # CHATGPT pattern to check for a number and a word
def validate_user_address():
    user_address = request.form.get("user_address", "").strip()

    # Check min and max lenght
    if not (USER_ADDRESS_MIN <= len(user_address) <= USER_ADDRESS_MAX):
        raise_custom_exception("Address must contain both letters and a number", 400)

    # Validate against the regex 
    if not re.match(USER_ADDRESS_REGEX, user_address):
        raise_custom_exception("Address invalid", 400)

    return user_address

##############################
# CHATGPT pattern to check email pattern
REGEX_EMAIL = "^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$" 
def validate_user_email():
    error = "Email invalid"
    user_email = request.form.get("user_email", "").strip()
    if not re.match(REGEX_EMAIL, user_email): raise_custom_exception(error, 400)
    return user_email

##############################
USER_PASSWORD_MIN = 8
USER_PASSWORD_MAX = 50
REGEX_USER_PASSWORD = f"^.{{{USER_PASSWORD_MIN},{USER_PASSWORD_MAX}}}$"
def validate_user_password():
    error = f"Password must be {USER_PASSWORD_MIN} to {USER_PASSWORD_MAX} characters"
    user_password = request.form.get("user_password", "").strip()
    if not re.match(REGEX_USER_PASSWORD, user_password): raise_custom_exception(error, 400)
    return user_password

##############################
SEARCH_TEXT_MIN = 2
SEARCH_TEXT_MAX = 50
SEARCH_TEXT_REGEX = f"^.{{{SEARCH_TEXT_MIN},{SEARCH_TEXT_MAX}}}$"
def validate_search_text():
    error = f"Search text must be between {SEARCH_TEXT_MIN} and {SEARCH_TEXT_MAX} characters."
    empty_error = "Missing search text"

    search_text = request.form.get("search", "").strip()

    # Check if the search field is empty
    if not search_text:
        raise_custom_exception(empty_error, 400)

    # Validate the length and pattern of the search text
    if not re.match(SEARCH_TEXT_REGEX, search_text):
        raise_custom_exception(error, 400)

    return search_text

##############################
REGEX_UUID4 = "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
def validate_uuid4(uuid4 = ""):
    error = f"Invalid uuid4"
    if not uuid4:
        uuid4 = request.values.get("uuid4", "").strip()
    if not re.match(REGEX_UUID4, uuid4): raise_custom_exception(error, 400)
    return uuid4


##############################
ITEM_TITLE_MIN = 2
ITEM_TITLE_MAX = 20
ITEM_TITLE_REGEX = f"^.{{{ITEM_TITLE_MIN},{ITEM_TITLE_MAX}}}$"
def validate_item_title():
    error = f"Title {ITEM_TITLE_MIN} to {ITEM_TITLE_MAX} characters"
    item_title = request.form.get("item_title", "").strip()
    if not re.match(ITEM_TITLE_REGEX, item_title): raise_custom_exception(error, 400)
    return item_title

##############################
ITEM_PRICE_REGEX = f"^\d+(\.\d+)?$" #CHATGPT to make price pattern 
def validate_item_price():
        error = f"Price must be a number "
        item_price = request.form.get("item_price", "").strip()
        if not re.match(ITEM_PRICE_REGEX, item_price): raise_custom_exception(error, 400)
        return item_price

##############################
UPLOAD_ITEM_FOLDER = "/home/katjakrogh/wolt-exam/static/dishes" if "PYTHONANYWHERE_DOMAIN" in os.environ else "./static/dishes" #saves img in static/dishes folder
ALLOWED_ITEM_FILE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
def validate_item_image():
    # Check if 'item_image' is in the request and is not empty
    if 'item_image' not in request.files or not request.files['item_image']:
        raise_custom_exception("Image file missing", 400)

    file = request.files.get("item_image")
    # Check if the filename is valid
    if not file or file.filename.strip() == "":
        raise_custom_exception("File name invalid", 400)

    # Extract the file extension and validate it
    file_extension = os.path.splitext(file.filename)[1][1:].lower()
    if file_extension not in ALLOWED_ITEM_FILE_EXTENSIONS:
        raise_custom_exception(f"Invalid file type. Allowed types: {', '.join(ALLOWED_ITEM_FILE_EXTENSIONS)}", 400)

    # Generate a unique filename
    filename = f"{uuid.uuid4()}.{file_extension}"
    return file, filename



##############################
def send_email(user_email, subject, body):
    try:
        # Email and password of the sender's Gmail account
        sender_email = "deterhannahs@gmail.com"
        password = "jenghzgwfcvrsuiz"  # Use an App Password if 2FA is enabled

        # Create the email message
        message = MIMEMultipart()
        message["From"] = "My Company Name"
        message["To"] = user_email
        message["Subject"] = subject

        # Attach the email body
        message.attach(MIMEText(body, "html"))

        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, user_email, message.as_string())
        
        return "Email sent successfully!"
    
    except Exception as ex:
        raise_custom_exception("cannot send email", 500)
    finally:
        pass



