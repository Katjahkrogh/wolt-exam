import random
from flask import Flask, session, render_template, redirect, url_for, make_response, request
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import x
import uuid 
import time
import redis
import os

from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'  # or 'redis', etc.
Session(app)


# app.secret_key = "your_secret_key"

##############################
##############################
##############################

def ______GET______(): pass

##############################
##############################

##############################
@app.get("/test-set-redis")
def view_test_set_redis():
    redis_host = "redis"
    redis_port = 6379
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)    
    redis_client.set("name", "Santiago", ex=10)
    # name = redis_client.get("name")
    return "name saved"

@app.get("/test-get-redis")
def view_test_get_redis():
    redis_host = "redis"
    redis_port = 6379
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)    
    name = redis_client.get("name")
    if not name: name = "no name"
    return name

##############################
@app.get("/")
def view_index():
    name = "X"
    return render_template("view_index.html", name=name, title="Volt exam")

##############################
@app.get("/signup")
@x.no_cache
def view_signup():  
    ic(session)
    if session.get("user"):
        if len(session.get("user").get("roles")) > 1:
            return redirect(url_for("view_choose_role")) 
        if "admin" in session.get("user").get("roles"):
            return redirect(url_for("view_admin"))
        if "customer" in session.get("user").get("roles"):
            return redirect(url_for("view_customer")) 
        if "partner" in session.get("user").get("roles"):
            return redirect(url_for("view_partner"))         
    return render_template("view_signup.html", x=x, title="Signup")

##############################
@app.get("/signup-partner")
@x.no_cache
def view_signup_partner():  
    ic(session)
    if session.get("user"):
        if len(session.get("user").get("roles")) > 1:
            return redirect(url_for("view_choose_role")) 
        if "admin" in session.get("user").get("roles"):
            return redirect(url_for("view_admin"))
        if "customer" in session.get("user").get("roles"):
            return redirect(url_for("view_customer")) 
        if "partner" in session.get("user").get("roles"):
            return redirect(url_for("view_partner"))         
    return render_template("view_signup_partner.html", x=x, title="Signup partner")

##############################
@app.get("/signup-restaurant")
@x.no_cache
def view_signup_restaurant():  
    ic(session)
    if session.get("user"):
        if len(session.get("user").get("roles")) > 1:
            return redirect(url_for("view_choose_role")) 
        if "admin" in session.get("user").get("roles"):
            return redirect(url_for("view_admin"))
        if "customer" in session.get("user").get("roles"):
            return redirect(url_for("view_customer")) 
        if "partner" in session.get("user").get("roles"):
            return redirect(url_for("view_partner"))         
    return render_template("view_signup_res.html", x=x, title="Signup restaurant")


##############################
@app.get("/login")
@x.no_cache
def view_login():  
    # ic("#"*20, "VIEW_LOGIN")
    ic(session)
    # print(session, flush=True)  
    if session.get("user"):
        if len(session.get("user").get("roles")) > 1:
            return redirect(url_for("view_choose_role")) 
        if "admin" in session.get("user").get("roles"):
            return redirect(url_for("view_admin"))
        if "customer" in session.get("user").get("roles"):
            return redirect(url_for("view_customer")) 
        if "partner" in session.get("user").get("roles"):
            return redirect(url_for("view_partner"))         
    return render_template("view_login.html", x=x, title="Login", message=request.args.get("message", ""))


##############################
@app.get("/customer")
@x.no_cache
def view_customer():
    try:
        if not session.get("user", ""): 
            return redirect(url_for("view_login"))
        
    
        db, cursor = x.db()
        q = """
            SELECT 
                users.user_pk,
                users.user_name,
                users.user_last_name,
                users.user_address,
                users.user_email,
                users.user_avatar,
                roles.role_name,
                (
                    SELECT item_image
                    FROM items
                    WHERE items.item_user_fk = users.user_pk
                    AND (items.item_deleted_at = 0 OR items.item_deleted_at IS NULL)
                    AND (items.item_blocked_at = 0 OR items.item_blocked_at IS NULL)
                    LIMIT 1
                ) AS item_image
            FROM users
            LEFT JOIN users_roles ON users.user_pk = users_roles.user_role_user_fk
            LEFT JOIN roles ON users_roles.user_role_role_fk = roles.role_pk
            WHERE roles.role_name = 'restaurant';
        """
        cursor.execute(q)
        rows = cursor.fetchall()

        # Process the query results directly into a list
        restaurants = []
        for row in rows:
            restaurants.append({
                "user_pk": row["user_pk"],
                "user_name": row["user_name"],
                "user_last_name": row["user_last_name"],
                "user_address": row["user_address"],
                "user_email": row["user_email"],
                "user_avatar": row["user_avatar"],
                "role_name": row["role_name"],
                "item_image": row["item_image"] or "dish_1.jpg",  # Default image if no item_image
            })

        # Pass restaurant and active_tab to the template
        active_tab = request.args.get('tab', 'restaurants')
        return render_template("view_customer.html", restaurants=restaurants, active_tab=active_tab, title="Volt")

    except Exception as ex:
        ic(ex)
        # Rollback the database if it exists
        if "db" in locals(): 
            db.rollback()

        # Return an error message
        return "<p>System under maintenance. Please try again later.</p>", 500

    finally:
        # Close database resources
        if "cursor" in locals(): 
            cursor.close()
        if "db" in locals(): 
            db.close()

##############################

@app.get("/restaurant/<user_pk>")
@x.no_cache
def view_restaurant_items(user_pk):
    try:
        if not session.get("user", ""): 
            return redirect(url_for("view_login"))

        user_pk = x.validate_uuid4(user_pk)

        db, cursor = x.db()

        # Fetch the restaurant's information
        q = """
            SELECT 
                users.user_pk,
                users.user_name,
                users.user_last_name,
                users.user_address,
                users.user_email,
                users.user_avatar,
                roles.role_name
            FROM users
            LEFT JOIN users_roles ON users.user_pk = users_roles.user_role_user_fk
            LEFT JOIN roles ON users_roles.user_role_role_fk = roles.role_pk
            WHERE users.user_pk = %s AND roles.role_name = 'restaurant'
        """
        cursor.execute(q, (user_pk,))
        restaurant = cursor.fetchone()

        if not restaurant:
            return "<p>Restaurant not found.</p>", 404

        # Fetch the items for this restaurant
        q = """
            SELECT 
                item_pk,
                item_title,
                item_price,
                item_image
            FROM items
            WHERE item_user_fk = %s AND item_deleted_at = 0 AND item_blocked_at = 0
        """
        cursor.execute(q, (user_pk,))
        items = cursor.fetchall()

        # Render the template with the restaurant and its items
        return render_template("view_restaurant_items.html", restaurant=restaurant, items=items)

    except Exception as ex:
        ic(ex)
        # Rollback if needed
        if "db" in locals(): 
            db.rollback()
        return "<p>System under maintenance. Please try again later.</p>", 500

    finally:
        if "cursor" in locals(): 
            cursor.close()
        if "db" in locals(): 
            db.close()

##############################
@app.get("/profile")
@x.no_cache
def view_profile():
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    user = session.get("user")
    print(user)
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))
    active_tab = request.args.get('tab', 'profile')
    return render_template("view_profile.html", user=user, x=x, active_tab=active_tab, title="Profile")

##############################
@app.get("/partner")
@x.no_cache
def view_partner():
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    user = session.get("user")
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))
    return render_template("view_profile.html", user=user, x=x, title="partner")

##############################
@app.get("/restaurant")
@x.no_cache
def view_restaurant():
    try:
        user = session.get("user")
        if not user:
            return redirect(url_for("view_login"))
        
        user_pk = user.get("user_pk")

        db, cursor = x.db()

        # Get users
        q = """ SELECT 
                users.user_pk,
                users.user_name,
                users.user_last_name,
                users.user_address,
                users.user_email,
                users.user_blocked_at,
                roles.role_name
                FROM users
                JOIN users_roles ON users.user_pk = users_roles.user_role_user_fk
                JOIN roles ON users_roles.user_role_role_fk = roles.role_pk
                WHERE users.user_pk = %s
            """
        cursor.execute(q, (user_pk,))
        users = cursor.fetchall()

        # Get items
        q = """
        SELECT 
            items.item_pk,
            items.item_title,
            items.item_price,
            items.item_image,
            items.item_blocked_at,
            users.user_name
        FROM items
        JOIN users ON items.item_user_fk = users.user_pk
        WHERE items.item_user_fk = %s AND items.item_blocked_at = 0
        ORDER BY items.item_title ASC
        """
        cursor.execute(q, (user_pk,))
        items = cursor.fetchall()

        # Determine the active tab
        active_tab = request.args.get('tab', 'your_restaurant')

        # Render the template
        return render_template("view_restaurant.html", active_tab=active_tab, x=x, user=users, items=items, title="Restaurant")

    except Exception as ex:
        ic(ex)
        # Rollback if needed
        if "db" in locals():
            db.rollback()
        return "<p>System under maintenance. Please try again later.</p>", 500

    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()


##############################
@app.get("/items/<item_pk>")
@x.no_cache
def view_edit_items(item_pk):
    try:
        db, cursor = x.db()

        # Fetch the item info
        q = """
            SELECT 
                item_title, 
                item_price, 
                item_image
            FROM items
            WHERE item_pk = %s
        """
        cursor.execute(q, (item_pk,))
        item = cursor.fetchone()

        if not item:
            return "<h2>Item not found</h2>", 404

        return render_template(
            "view_edit_items.html", item=item, item_pk=item_pk, x=x )
    
    except Exception as ex:
        ic(ex)
        return "<p>Error occurred</p>", 500

    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()


##############################
@app.get("/admin")
@x.no_cache
def view_admin():
    try:
        user = session.get("user")
        if not user:
            return redirect(url_for("view_login"))

        if "admin" not in user.get("roles", []):
            return redirect(url_for("view_login"))

        db, cursor = x.db()

        # Get users
        q = """ SELECT 
                users.user_pk,
                users.user_name,
                users.user_last_name,
                users.user_address,
                users.user_email,
                users.user_blocked_at,
                roles.role_name
                FROM users
                LEFT JOIN users_roles ON users.user_pk = users_roles.user_role_user_fk
                LEFT JOIN roles ON users_roles.user_role_role_fk = roles.role_pk
                ORDER BY roles.role_name ASC, users.user_name ASC
            """
        cursor.execute(q)
        users = cursor.fetchall()

        # Get items
        q = """
        SELECT 
            items.item_pk,
            items.item_title,
            items.item_price,
            items.item_image,
            items.item_blocked_at,
            users.user_name
        FROM items
        LEFT JOIN users ON items.item_user_fk = users.user_pk
        ORDER BY users.user_name ASC, items.item_title ASC
        """
        cursor.execute(q)
        items = cursor.fetchall()

        allowed_tabs = ['users', 'items']
        active_tab = request.args.get('tab', 'users')  
        # Set default 'users', if something fails
        if active_tab not in allowed_tabs:
            active_tab = 'users'

        allowed_secondary_tabs = ['Customers', 'Restaurants', 'Partners']
        active_secondary_tab = request.args.get('secondary_tab', 'Customers')  
        # Set default 'customers', if something fails
        if active_secondary_tab not in allowed_secondary_tabs:
            active_secondary_tab = 'Customers'

        return render_template("view_admin.html", users=users, active_tab=active_tab, active_secondary_tab=active_secondary_tab, items=items, user=user, title="Volt - admin")

    except Exception as ex:
        ic(ex)
        if "db" in locals():
            db.rollback()
        return "An error occurred", 500

    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()


##############################
@app.get("/choose-role")
@x.no_cache
def view_choose_role():
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    if not len(session.get("user").get("roles")) >= 2:
        return redirect(url_for("view_login"))
    user = session.get("user")
    return render_template("view_choose_role.html", user=user, title="Choose role")

##############################
@app.get("/search-results")
def view_search_results():
    try:
        search_text = request.args.get("search", "").replace("-", " ")

        db, cursor = x.db()
        # SELECT USERS THAT ARE RESTAURANT AND MATCH RESULT
        q = """SELECT user_pk, user_avatar, user_address, user_name FROM users 
                JOIN users_roles
                ON user_pk = user_role_user_fk
                JOIN roles
                ON role_pk = user_role_role_fk
                WHERE role_name = "restaurant" AND user_name LIKE %s AND user_deleted_at = 0
            """
        cursor.execute(q, (f"%{search_text}%", ))
        restaurant_results = cursor.fetchall()

        # SELECT ALL ITEMS THAT MATCH RESULT
        q = """SELECT item_pk, item_title, item_price, item_image, user_name FROM items 
                JOIN users
                ON user_pk = item_user_fk
                WHERE item_title LIKE %s AND item_deleted_at = 0 
            """
        cursor.execute(q, (f"%{search_text}%", ))
        item_results = cursor.fetchall()

        return render_template("view_search_results.html", search_text=search_text, restaurant_results=restaurant_results, item_results=item_results )
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrating</template>", 500        
        return "<template>System under maintenance</template>", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
##############################
##############################

def ______POST______(): pass

##############################
##############################
##############################

@app.post("/logout")
def logout():
    # ic("#"*30)
    # ic(session)
    session.pop("user", None)
    # session.clear()
    # session.modified = True
    # ic("*"*30)
    # ic(session)
    return redirect(url_for("view_login"))


##############################
@app.post("/users/<role>")
@x.no_cache
def signup(role):
    try:
        # Validate input fields
        user_name = x.validate_user_name()
        user_last_name = x.validate_user_last_name()
        user_address = x.validate_user_address()
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()
        hashed_password = generate_password_hash(user_password)
        
        # Generate user details
        user_pk = str(uuid.uuid4())
        user_avatar = "profile_" + str(random.randint(1, 100)) + ".jpg"
        user_created_at = int(time.time())
        user_deleted_at = 0
        user_blocked_at = 0
        user_updated_at = 0
        user_verified_at = 0
        user_verification_key = str(uuid.uuid4())

        # Database connection
        db, cursor = x.db()

        # fetch the role_pk based on the `role` route parameter
        q_fetch_role = "SELECT role_pk FROM roles WHERE role_name = %s"
        cursor.execute(q_fetch_role, (role,))
        role_row = cursor.fetchone()

        #validate role 
        if not role_row:
            return "<template mix-target='main'>Role not found. Please contact support.</template>", 400

        user_role_pk = role_row["role_pk"]

        # Insert user into the `users` table
        q1 = 'INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(q1, (user_pk, user_name, user_last_name, user_address, user_email, 
                            hashed_password, user_avatar, user_created_at, 
                            user_deleted_at, user_blocked_at, user_updated_at, 
                            user_verified_at, user_verification_key))

        # Assign the fetched role to the user
        q2 = 'INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES (%s, %s)'
        cursor.execute(q2, (user_pk, user_role_pk))

        # Commit changes
        db.commit()

        ic(user_role_pk)

        # Prepare the verification email content
        subject = "Verify Your Account"
        body = f"""
        <html>
            <body>
                <p>Hi {user_name},</p>
                <p>Thank you for signing up! Please verify your account by clicking the link below:</p>
                <p><a href="http://127.0.0.1/verify/{user_verification_key}">Verify My Account</a></p>
            </body>
        </html>
        """
        
        # Send the email
        x.send_email(user_email, subject, body)

        # Return success message
        return "<template mix-target='main'>Please check your email to verify your account.</template>", 200

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            if "users.user_email" in str(ex): 
                toast = render_template("___toast.html", message="email not available")
                return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400
            return f"""<template mix-target="#toast" mix-bottom>System upgrading</template>""", 500        
        return f"""<template mix-target="#toast" mix-bottom>System under maintenance</template>""", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.post("/login")
def login():
    try:
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()

        db, cursor = x.db()
        q = """ SELECT * FROM users 
                JOIN users_roles 
                ON user_pk = user_role_user_fk 
                JOIN roles
                ON role_pk = user_role_role_fk
                WHERE LOWER(user_email) = %s """
        cursor.execute(q, (user_email,))
        rows = cursor.fetchall()

        #check if user exists
        if not rows:
            toast = render_template("___toast.html", message="user not registered")
            return f"""<template mix-target="#toast">{toast}</template>""", 400     
        
        #check if user is deleted
        if rows[0].get("user_deleted_at") != 0:
            toast = render_template("___toast.html", message="user is deleted")
            return f"""<template mix-target="#toast">{toast}</template>""", 400     

        #check password
        if not check_password_hash(rows[0]["user_password"], user_password):
            toast = render_template("___toast.html", message="invalid credentials")
            return f"""<template mix-target="#toast">{toast}</template>""", 401
        
        # Check if the user is verified
        if rows[0].get("user_verified_at") in [0, None]: 
            toast = render_template("___toast.html", message="User not verified, please check email for the verification link")
            return f"""<template mix-target="#toast">{toast}</template>""", 403

        roles = []
        for row in rows:
            roles.append(row["role_name"])
        user = {
            "user_pk": rows[0]["user_pk"],
            "user_name": rows[0]["user_name"],
            "user_last_name": rows[0]["user_last_name"],
            "user_address": rows[0]["user_address"],
            "user_email": rows[0]["user_email"],
            "user_avatar": rows[0].get("user_avatar"), 
            "roles": roles
        }
        session["user"] = user
        
        # Redirect based on roles
        if len(roles) == 1:
            return f"""<template mix-redirect="/{roles[0]}"></template>"""
        return f"""<template mix-redirect="/choose-role"></template>"""
    

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrating</template>", 500        
        return "<template>System under maintenance</template>", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.post("/items")
def create_item():
    try:
        # Validate inputs
        item_title = x.validate_item_title()
        item_price = x.validate_item_price()
        file, item_image_name = x.validate_item_image()

        item_pk = str(uuid.uuid4())
        item_user_fk = session.get("user").get("user_pk")
        item_created_at = int(time.time())
        item_deleted_at = 0
        item_blocked_at = 0
        item_updated_at = 0

        # Save the image to the upload folder
        os.makedirs(x.UPLOAD_ITEM_FOLDER, exist_ok=True)
        file.save(os.path.join(x.UPLOAD_ITEM_FOLDER, item_image_name))

        # Insert item into the database
        db, cursor = x.db()
        q = """
            INSERT INTO items (item_pk, item_user_fk, item_title, item_price, item_image, item_created_at, item_deleted_at, item_blocked_at, item_updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(q, (item_pk, item_user_fk, item_title, item_price, item_image_name, item_created_at, item_deleted_at, item_blocked_at, item_updated_at))
        db.commit()

        # Success response
        toast = render_template("___toast.html", message="Item added successfully!")
        return f"""<template mix-target="#toast" mix-bottom>{toast}</template>"""
    
    except x.CustomException as ex:
        if "db" in locals(): db.rollback()
        toast = render_template("___toast.html", message=ex.message)
        return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
    
    except Exception as ex:
        if "db" in locals(): db.rollback()
        return "<template>System under maintenance</template>", 500
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
@app.post("/get-results")
def send_search_text():
    try:
        text = x.validate_search_text()

        if text == "":
            toast = render_template("___toast", message="Missing search text")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>"""
        return f"""<template mix-redirect="/search-results?search={text}"></template>"""
    except Exception as ex:
        ic(ex)
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrating</template>", 500        
        return "<template>System under maintenance</template>", 500  
    finally:
        pass    



##############################
##############################
##############################

def ______PUT_______(): pass

##############################
##############################
##############################

@app.put("/users")
def user_update():
    try:
        if not session.get("user"): x.raise_custom_exception("please login", 401)

        user_pk = session.get("user").get("user_pk")
        user_name = x.validate_user_name()
        user_last_name = x.validate_user_last_name()
        user_email = x.validate_user_email()

        user_updated_at = int(time.time())

        db, cursor = x.db()
        q = """ UPDATE users
                SET user_name = %s, user_last_name = %s, user_email = %s, user_updated_at = %s
                WHERE user_pk = %s
            """
        cursor.execute(q, (user_name, user_last_name, user_email, user_updated_at, user_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot update user", 401)
        db.commit()
        return """<template>user updated</template>"""
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            if "users.user_email" in str(ex): return "<template>email not available</template>", 400
            return "<template>System upgrating</template>", 500        
        return "<template>System under maintenance</template>", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.put("/users/<user_pk>")
def user_soft_delete(user_pk):
    try:
        # Check if the user is logged in
        user_session = session.get("user", None)
        if not user_session:
            return redirect(url_for("view_login"))
        
        # Validate UUID
        user_pk = x.validate_uuid4(user_pk)

        #getting and validating the entered password
        entered_password = request.form.get("entered_password") 

        #getting stored password from user
        db, cursor = x.db()
        query = "SELECT user_password FROM users WHERE user_pk = %s"
        cursor.execute(query, (user_pk,))
        user = cursor.fetchone()

        if not user:
            x.raise_custom_exception("User not found", 404)

        stored_password_hash = user['user_password']

        # Check if the entered password matches the stored password
        if not check_password_hash(stored_password_hash, entered_password):
            return """<template mix-target='#toast'>Incorrect password</template>""", 403
        
        ##### if password check passes =

        user_deleted_at = int(time.time())

        # Database connection and update
        db, cursor = x.db()
        q = 'UPDATE users SET user_deleted_at = %s WHERE user_pk = %s'
        cursor.execute(q, (user_deleted_at, user_pk))
        if cursor.rowcount != 1:
            x.raise_custom_exception("Cannot delete user", 400)

        db.commit()


        # Prepare the block email content
        q2 = 'SELECT user_name, user_email FROM users WHERE user_pk = %s'
        cursor.execute(q2, (user_pk,))
        user = cursor.fetchone()
        subject = "Your Account Has Been Deleted"
        body = f"""
        <html>
            <body>
                <p>Hi {user['user_name']},</p>
                <p>Your account has been deleted. If you believe this is an error, please contact support.</p>
            </body>
        </html>
        """
        # Send the email
        x.send_email(user["user_email"], subject, body)

        # Log the user out
        session.clear()

        # return  f"""<template mix-target="#modal">User is deleted</template>"""
        # Redirect to the index page
        return """<template mix-redirect="/"></template>"""

    except Exception as ex:
        ic(ex)

        # Rollback in case of database error
        if "db" in locals():
            db.rollback()

        # Handle custom exceptions
        if isinstance(ex, x.CustomException):
            return f"""<template mix-target="#toast">{ex.message}</template>""", ex.code

        # Handle database errors
        if isinstance(ex, x.mysql.connector.Error):
            return "<template>Database error</template>", 500        

        # Handle unexpected errors
        return "<template>System under maintenance</template>", 500  

    finally:
        # Close database resources
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()


##############################
@app.put("/users/block/<user_pk>")
def block_user(user_pk):
    try:        
        if not "admin" in session.get("user").get("roles"): return redirect(url_for("view_login"))
    
        user_pk = x.validate_uuid4(user_pk)
        user_blocked_at = int(time.time())
        user_updated_at = int(time.time())

        user = {
            "user_pk" : user_pk,
            "user_blocked_at" : user_blocked_at,
            "user_updated_at" : user_updated_at
        }

        db, cursor = x.db()
        q = 'UPDATE users SET user_blocked_at = %s, user_updated_at = %s WHERE user_pk = %s'
        cursor.execute(q, (user_blocked_at, user_updated_at, user_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot block user", 400)

        btn_unblock = render_template("___btn_unblock_user.html", user=user)

        # Prepare the block email content
        q = 'SELECT user_name, user_email FROM users WHERE user_pk = %s'
        cursor.execute(q, (user_pk,))
        user = cursor.fetchone()
        subject = "Your Account Has Been Blocked"
        body = f"""
        <html>
            <body>
                <p>Hi {user['user_name']},</p>
                <p>Your account has been blocked. If you believe this is an error, please contact support.</p>
            </body>
        </html>
        """
        # Send the email
        x.send_email(user["user_email"], subject, body)

        db.commit()

        toast = render_template("___toast.html", message="User blocked")
        return f"""
                <template mix-target="#block-{user_pk}"
                mix-replace>{btn_unblock}
                </template>
                <template mix-target="#toast">
                {toast}
                </template>
                """
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.put("/users/unblock/<user_pk>")
def unblock_user(user_pk):
    try:
        if not "admin" in session.get("user").get("roles"): return redirect(url_for("view_login"))

        user_pk = x.validate_uuid4(user_pk)
        user_updated_at = int(time.time())
        user_blocked_at = 0

        user = {
            "user_pk" : user_pk,
            "user_updated_at" : user_updated_at,
            "user_blocked_at": user_blocked_at
        }

        db, cursor = x.db()
        q = ('UPDATE users SET user_blocked_at = %s, user_updated_at = %s WHERE user_pk = %s')
        cursor.execute(q, (user_blocked_at, user_updated_at, user_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot unblock user", 400)

        btn_block = render_template("___btn_block_user.html", user=user)

        # Prepare the block email content
        q = 'SELECT user_name, user_email FROM users WHERE user_pk = %s'
        cursor.execute(q, (user_pk,))
        user = cursor.fetchone()
        subject = "Your Account Has Been Unblocked"
        body = f"""
        <html>
            <body>
                <p>Hi {user['user_name']},</p>
                <p>Your account has been unblocked. You can now log in and continue using our services.</p>
            </body>
        </html>
        """
        # Send the email
        x.send_email(user["user_email"], subject, body)
        db.commit()

        toast = render_template("___toast.html", message="User unblocked")
        return f"""
                <template 
                mix-target='#unblock-{user_pk}'
                mix-replace>
                    {btn_block}
                </template>
                <template mix-target="#toast" mix-bottom>
                    {toast}
                </template>
                """
        
    except Exception as ex:

        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
@app.put("/items/<item_pk>")
def update_item(item_pk):
    try:
        print(f"Item PK: {item_pk}")
        # Ensure the user is logged in
        user = session.get("user")
        if not user:
            return redirect(url_for("view_login"))

        item_title = x.validate_item_title()
        item_price = x.validate_item_price()
        
        # Check if a new image is uploaded, otherwise keep current
        file = request.files.get("item_image", None)
        if file and file.filename != "":
            # Validate and save the new image if present
            file, item_image_name = x.validate_item_image()
            os.makedirs(x.UPLOAD_ITEM_FOLDER, exist_ok=True)
            file.save(os.path.join(x.UPLOAD_ITEM_FOLDER, item_image_name))
        else:
            # Keep the current image name if no new file is uploaded
            item_image_name = request.form.get("existing_item_image", None)  # Make sure this is sent in the form

        item_updated_at = int(time.time())

        # Database update
        db, cursor = x.db()

        q = """
        UPDATE items
        SET item_title = %s, item_price = %s, item_image = %s, item_updated_at = %s
        WHERE item_pk = %s
        """
        cursor.execute(q, (item_title, item_price, item_image_name, item_updated_at, item_pk))

        # Check for changes
        if cursor.rowcount == 0:
            toast = render_template("___toast.html", message="No changes made")
            return f"""<template mix-target="#toast">{toast}</template>""", 400

        db.commit()
        
        return """<template mix-redirect='/restaurant'></template>""", 200

    except Exception as e:
        ic(e)
        if "db" in locals(): db.rollback()
        return "<p>System under maintenance. Please try again later.</p>", 500

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


# @app.put("/items/<item_pk>")
# def update_item(item_pk):
#     try:
#         print(f"Item PK: {item_pk}")
#         # Ensure the user is logged in
#         user = session.get("user")
#         if not user:
#             return redirect(url_for("view_login"))

#         item_title = x.validate_item_title()
#         item_price = x.validate_item_price()
#         file, item_image = x.validate_item_image()

#         item_updated_at = int(time.time())

#         # Database update
#         db, cursor = x.db()

#         q = """
#         UPDATE items
#         SET item_title = %s, item_price = %s, item_image = %s, item_updated_at = %s
#         WHERE item_pk = %s 
#         """
#         cursor.execute(q, (item_title, item_price, item_image, item_pk, item_updated_at))

#         #check for changes
#         if cursor.rowcount == 0:
#             toast = render_template("___toast.html", message="No changes made")
#             return f"""<template mix-target="#toast">{toast}</template>""", 400

#         db.commit()
        
#         return """<template mix-redirect='/restaurant'></template>""", 200

#     except Exception as e:
#         ic(e)
#         db.rollback()
#         return "<p>System under maintenance. Please try again later.</p>", 500

#     finally:
#         if "cursor" in locals():
#             cursor.close()
#         if "db" in locals():
#             db.close()

##############################
@app.put("/items/block/<item_pk>")
def block_item(item_pk):
    try:        
        if not "admin" in session.get("user").get("roles"): return redirect(url_for("view_login"))
    
        item_pk = x.validate_uuid4(item_pk)
        item_blocked_at = int(time.time())
        item_updated_at = int(time.time())

        item = {
            "item_pk" : item_pk,
            "item_blocked_at" : item_blocked_at,
            "item_updated_at" : item_updated_at
        }

        db, cursor = x.db()
        q = 'UPDATE items SET item_blocked_at = %s, item_updated_at = %s WHERE item_pk = %s'
        cursor.execute(q, (item_blocked_at, item_updated_at, item_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot block item", 400)

        btn_unblock = render_template("___btn_unblock_item.html", item=item)

        # Get info on item and user
        q = f"""SELECT 
                items.item_title, 
                users.user_name, 
                users.user_email 
                FROM items 
                LEFT JOIN users ON items.item_user_fk = users.user_pk WHERE items.item_pk = %s
                """
        cursor.execute(q, (item_pk,))
        item = cursor.fetchone()
        
        # Prepare the block email content
        subject = f"Your item '{item['item_title']}' has been blocked"
        body = f"""
        <html>
            <body>
                <p>Hi {item['user_name']},</p>
                <p>Your item '{item['item_title']}' has been blocked. If you believe this is an error, please contact support.</p>
            </body>
        </html>
        """
        # Send email
        x.send_email(item["user_email"], subject, body)

        db.commit()

        toast = render_template("___toast.html", message="item blocked")
        return f"""
                <template 
                mix-target='#block-{item_pk}' 
                mix-replace>
                    {btn_unblock}
                </template>
                <template mix-target="#toast" mix-bottom>
                    {toast}
                </template>
                """
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.put("/items/unblock/<item_pk>")
def unblock_item(item_pk):
    try:
        if not "admin" in session.get("user").get("roles"): return redirect(url_for("view_login"))

        item_pk = x.validate_uuid4(item_pk)
        item_updated_at = int(time.time())
        item_blocked_at = 0

        item = {
            "item_pk" : item_pk,
            "item_blocked_at" : item_blocked_at,
            "item_updated_at" : item_updated_at
        }

        db, cursor = x.db()
        q = 'UPDATE items SET item_blocked_at = %s, item_updated_at = %s WHERE item_pk = %s'
        cursor.execute(q, (item_blocked_at, item_updated_at, item_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot unblock item", 400)

        btn_block = render_template("___btn_block_item.html", item=item)

        # Get info on item and user
        q = f"""SELECT 
                items.item_title, 
                users.user_name, 
                users.user_email 
                FROM items 
                LEFT JOIN users ON items.item_user_fk = users.user_pk WHERE items.item_pk = %s
                """
        cursor.execute(q, (item_pk,))
        item = cursor.fetchone()
        
        # Prepare the unblock email content
        subject = f"Your item '{item['item_title']}' has been unblocked"
        body = f"""
        <html>
            <body>
                <p>Hi {item['user_name']},</p>
                <p>Your item '{item['item_title']}' has been unblocked. You can now list it for sale again.</p>
            </body>
        </html>
        """
        # Send emailen
        x.send_email(item["user_email"], subject, body)

        db.commit()

        toast = render_template("___toast.html", message="Item unblocked")
        return f"""
                <template 
                mix-target='#unblock-{item_pk}'
                mix-replace>
                    {btn_block}
                </template>
                <template mix-target="#toast" mix-bottom>
                    {toast}
                </template>
                """
        
    except Exception as ex:

        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()




##############################
##############################
##############################

# def ______DELETE______(): pass

##############################
##############################
##############################



##############################
##############################
##############################

def ______BRIDGE____(): pass

##############################
##############################
##############################


##############################
@app.get("/verify/<verification_key>")
@x.no_cache
def verify_user(verification_key):
    try:
        ic(verification_key)
        verification_key = x.validate_uuid4(verification_key)
        user_verified_at = int(time.time())

        db, cursor = x.db()
        q = """ UPDATE users 
                SET user_verified_at = %s 
                WHERE user_verification_key = %s"""
        cursor.execute(q, (user_verified_at, verification_key))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot verify account", 400)
        db.commit()
        return redirect(url_for("view_login", message="User verified, please login"))

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): return ex.message, ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "Database under maintenance", 500        
        return "System under maintenance", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()    
