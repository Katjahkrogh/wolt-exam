import random
from flask import Flask, session, render_template, redirect, url_for, make_response, request, render_template_string, jsonify
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
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



# ##############################
# @app.get("/test-set-redis")
# def view_test_set_redis():
#     redis_host = "redis"
#     redis_port = 6379
#     redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)    
#     redis_client.set("name", "Santiago", ex=10)
#     # name = redis_client.get("name")
#     return "name saved"


# @app.get("/test-get-redis")
# def view_test_get_redis():
#     redis_host = "redis"
#     redis_port = 6379
#     redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)    
#     name = redis_client.get("name")
#     if not name: name = "no name"
#     return name


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
    return render_template("view_login.html", x=x, title="Login", message=request.args.get("message", ""))


##############################
@app.get("/reset-password/<password_reset_key>")
@x.no_cache
def view_reset_password(password_reset_key):  
    return render_template("view_reset_password.html", x=x, title="Login", password_reset_key=password_reset_key)


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
                roles.role_name
            FROM users
            JOIN users_roles 
            ON users.user_pk = users_roles.user_role_user_fk
            JOIN roles 
            ON users_roles.user_role_role_fk = roles.role_pk
            WHERE roles.role_name = 'restaurant' AND users.user_blocked_at = 0 AND users.user_deleted_at = 0;
        """
        cursor.execute(q)
        restaurants = cursor.fetchall()  # Fetch all restaurants

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
@app.get("/api/restaurants")
def get_restaurants():
    try:
        db, cursor = x.db()
        # Get restaurant details
        q = """
            SELECT 
                users.user_pk,
                users.user_name,
                users.user_address,
                users.user_avatar
            FROM users
            JOIN users_roles ON users.user_pk = users_roles.user_role_user_fk
            JOIN roles ON users_roles.user_role_role_fk = roles.role_pk
            WHERE roles.role_name = 'restaurant' AND users.user_blocked_at = 0 AND users.user_deleted_at = 0
        """
        cursor.execute(q)
        restaurants = cursor.fetchall()

        # Generate random lat/lng near Copenhagen
        def random_coords():
            latitude = random.uniform(55.65, 55.72) 
            longitude = random.uniform(12.48, 12.58)  
            return latitude, longitude

        # Transform rows into JSON structure
        result = []
        for row in restaurants:
            latitude, longitude = random_coords()
            result.append({
                "id": row["user_pk"],
                "name": row["user_name"],
                "address": row["user_address"],
                "avatar_url": url_for('static', filename='dishes/' + row["user_avatar"]),
                "latitude": latitude,
                "longitude": longitude,
                "url": url_for("view_restaurant_items", user_pk=row["user_pk"])
            })

        return {"restaurants": result}, 200

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return """<template mix-target="#toast" mix-bottom>System upgrading</template>""", 500        
        return """<template mix-target="#toast" mix-bottom>System under maintenance</template>""", 500 
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

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
            JOIN users_roles 
            ON users.user_pk = users_roles.user_role_user_fk
            JOIN roles 
            ON users_roles.user_role_role_fk = roles.role_pk
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

        # Get the referrer URL for the back btn otherwise stay on page if it cant get the url
        referrer_url = request.referrer if request.referrer else url_for('view_restaurant_items', user_pk=user_pk)

        # Render the template with the restaurant and its items
        return render_template("view_restaurant_items.html", user_pk=user_pk, restaurant=restaurant, items=items, referrer_url=referrer_url)

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
    try:
        if not session.get("user", ""): 
            return redirect(url_for("view_login"))
        user = session.get("user")
        db, cursor = x.db()
        cursor.execute("SELECT * FROM users WHERE user_pk = %s", (user['user_pk'],))
        user = cursor.fetchone()

        active_tab = request.args.get('tab', 'profile')
        return render_template("view_profile.html", user=user, x=x, active_tab=active_tab, title="Profile")
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
@app.get("/partner")
@x.no_cache
def view_partner():
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    user = session.get("user")
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))
    active_tab = request.args.get('tab', 'profile') 
    return render_template("view_profile.html", user=user, x=x, active_tab=active_tab, title="partner")

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
                WHERE users.user_pk = %s AND users.user_blocked_at = 0 AND users.user_deleted_at = 0
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
        WHERE items.item_user_fk = %s AND items.item_blocked_at = 0 AND items.item_deleted_at = 0
        ORDER BY items.item_title ASC
        """
        cursor.execute(q, (user_pk,))
        items = cursor.fetchall()

        # Determine the active tab
        active_tab = request.args.get('tab', 'your_restaurant')

        # Render the template
        return render_template("view_restaurant.html", active_tab=active_tab, x=x, user=users, items=items, message=request.args.get("message", ""), title="Restaurant")

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
                users.user_deleted_at,
                roles.role_name
                FROM users
                JOIN users_roles 
                ON users.user_pk = users_roles.user_role_user_fk
                JOIN roles 
                ON users_roles.user_role_role_fk = roles.role_pk
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
            items.item_deleted_at,
            users.user_name
        FROM items
        JOIN users 
        ON items.item_user_fk = users.user_pk
        ORDER BY users.user_name ASC, items.item_title ASC
        """
        cursor.execute(q)
        items = cursor.fetchall()

        active_tab = request.args.get('tab', 'users')  

        active_secondary_tab = request.args.get('secondary_tab', 'Customers')  

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
                WHERE role_name = "restaurant" AND user_name LIKE %s AND user_deleted_at = 0 AND user_blocked_at = 0
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
@app.get("/cart-total")
def get_cart_total():
    cart = session.get("cart", [])
    total_items = sum(item["quantity"] for item in cart)
    return jsonify({"total_items": total_items})

##############################
@app.get("/order")
def view_order():
# Retrieve the last order from the session
    last_order = session.get('last_order', {})
    
    # Clear the last order from the session after retrieving
    session.pop('last_order', None)
    session.modified = True
    
    return render_template(
        "view_order.html",
        total_value=last_order.get('total_value', 0),
        cart_items=last_order.get('cart_items', [])
    )


##############################
##############################
##############################

def ______POST______(): pass

##############################
##############################
##############################


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

        # Assign avatar based on role
        if role == "restaurant":
            user_avatar = "dish_" + str(random.randint(1, 100)) + ".jpg"
        else:
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
        
        # Check if the user is blocked
        if rows[0].get("user_blocked_at") != 0: 
            toast = render_template("___toast.html", message="User is blocked")
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
@app.post("/logout")
def logout():
    session.pop("user", None)
    session.pop("cart", None)
    session.modified = True
    # session.clear()
    return redirect(url_for("view_login"))



##############################
@app.post("/reset-password")
def reset_password():
    try: 
        user_email = x.validate_user_email()

        db, cursor = x.db()
        q = """ 
            SELECT user_pk, 
            user_name 
            FROM users 
            WHERE user_email = %s
            """
        cursor.execute(q, (user_email,))  
        user = cursor.fetchone()

        if not user:
            toast = render_template("___toast.html", message="User not found with this email")
            return f"""<template mix-target="#toast">{toast}</template>"""

        user_name = user["user_name"]
        password_reset_key = user["user_pk"] 

        # Prepare the verification email content
        subject = "Reset your password"
        body = f"""
        <html>
            <body>
                <p>Hi {user_name},</p>
                <p>Click the link below to reset your password</p>
                <a href="http://127.0.0.1/reset-password/{password_reset_key}">Reset password</a>
            </body>
        </html>
        """
        
        # Send the email
        x.send_email(user_email, subject, body)

        # Return success message
        return """<template mix-target="#modalContent">
            <h2>Email sent!</h2>
            <p>Click the link in the mail to reset your password</p>
            </template>"""
        
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            return "<template>System upgrading</template>", 500        
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

        return f"""<template mix-redirect="/restaurant"></template>"""
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return f"""<template mix-target="#toast" mix-bottom>System upgrading</template>""", 500        
        return f"""<template mix-target="#toast" mix-bottom>System under maintenance</template>""", 500    
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
@app.post("/add-to-cart")
def add_to_cart():
    try:
        # Parse the incoming JSON data
        data = request.get_json()
        
        if not data or "item_pk" not in data:
            return jsonify({"error": "Invalid data. Must include item_pk."}), 400

        item_pk = data["item_pk"]

        # Fetch item details from the database
        db, cursor = x.db()
        q = """
            SELECT 
                item_pk, item_title, item_price, item_image
            FROM items
            WHERE item_pk = %s 
        """
        cursor.execute(q, (item_pk,))
        item = cursor.fetchone()

        if not item:
            return jsonify({"error": "Item not found."}), 404

        # Extract details from the database query
        item_title = item["item_title"]
        item_price = float(item["item_price"])
        item_image = item["item_image"]

        # Get the cart from the session or initialize it
        cart = session.get("cart", [])

        # Check if the item is already in the cart
        for cart_item in cart:
            if cart_item["item_pk"] == item_pk:
                # Increase quantity and update total price
                cart_item["quantity"] += 1
                cart_item["total_item_price"] = cart_item["quantity"] * item_price
                break
        else:
            # Add new item to the cart
            cart.append({
                "item_pk": item_pk,
                "item_title": item_title,
                "item_price": item_price,
                "item_image": item_image,
                "quantity": 1,
                "total_item_price": item_price,
            })

        # Save updated cart back to the session
        session["cart"] = cart
        session.modified = True

        # Redirect to the restaurant page after adding item to cart
        return jsonify({"cart": cart, "message": f"{item_title} added to cart."}), 200
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            return f"""<template mix-target="#toast" mix-bottom>System upgrading</template>""", 500        
        return f"""<template mix-target="#toast" mix-bottom>System under maintenance</template>""", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.post("/remove-from-cart/<item_pk>")
def remove_from_cart(item_pk):
    try:
        cart = session.get("cart", [])

        # Find the item in the cart
        item = next((item for item in cart if item["item_pk"] == item_pk), None)

        if item:
            if item["quantity"] > 1:
                # Decrease the quantity if it's higher than 1
                item["quantity"] -= 1
                item["total_item_price"] = item["quantity"] * item["item_price"]
            else:
                # Remove the item if the quantity is 1
                cart = [cart_item for cart_item in cart if cart_item["item_pk"] != item_pk]
                
            session["cart"] = cart  
            session.modified = True

            return jsonify({
                "success": True,
                "cart": cart
            })

        return jsonify({"error": "Item not found in cart"}), 404
    
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
@app.post("/checkout")    
def checkout_cart():
    try:
        cart = session.get('cart', [])
        
        if not cart:
            return jsonify({"error": "Cart is empty"}), 400
        
        total_value = sum(item['total_item_price'] for item in cart)

        user_email = session.get("user").get("user_email")

        subject = f"Order Confirmation - Total: DKK {total_value:.2f}"
        body = """
                <h2>Your Order Details:</h2>
                <table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;">
                    <thead>
                        <tr>
                            <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Item</th>
                            <th style="text-align: center; padding: 8px; border-bottom: 2px solid #ddd;">Quantity</th>
                            <th style="text-align: right; padding: 8px; border-bottom: 2px solid #ddd;">Price</th>
                        </tr>
                    </thead>
                    <tbody>
                """
        
        for item in cart:
            body += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{item['item_title']}</td>
                <td style="text-align: center; padding: 8px; border-bottom: 1px solid #ddd;">{item['quantity']}</td>
                <td style="text-align: right; padding: 8px; border-bottom: 1px solid #ddd;">DKK {item['total_item_price']:.2f}</td>
            </tr>
        """

        body += f"""
            </tbody>
            <tfoot>
                <tr>
                    <td colspan="2" style="text-align: right; padding: 8px; font-weight: bold; border-top: 2px solid #ddd;">Total:</td>
                    <td style="text-align: right; padding: 8px; font-weight: bold; border-top: 2px solid #ddd;">DKK {total_value:.2f}</td>
                </tr>
            </tfoot>
        </table>
        """
        
        # Send the email
        x.send_email(user_email, subject, body)
            
        # Store the order details in the session before clearing the cart
        session['last_order'] = {
            'cart_items': cart,
            'total_value': total_value
        }
        
        # Clear the cart after checkout
        session['cart'] = []
        session.modified = True

        return """<template mix-redirect="/order"></template>"""

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

@app.put("/users/<user_pk>")
def user_update(user_pk):
    try:
        user = session.get("user")
        if not user:
            x.raise_custom_exception("please login", 401)
            return redirect(url_for("view_login"))

        user_pk = x.validate_uuid4(user_pk)
        user_name = x.validate_user_name()
        user_last_name = x.validate_user_last_name()
        user_email = x.validate_user_email()
        user_address = x.validate_user_address()

        db, cursor = x.db()
        
        # Fetch current user data from database
        cursor.execute("SELECT user_name, user_last_name, user_email, user_address FROM users WHERE user_pk = %s", (user_pk,))
        current_user = cursor.fetchone()

        # Check if any field has actually changed
        if (
            current_user['user_name'] == user_name and 
            current_user['user_last_name'] == user_last_name and 
            current_user['user_email'] == user_email and 
            current_user['user_address'] == user_address
        ):
            # No changes detected
            toast = render_template("___toast.html", message="No changes were made")
            return f"""<template mix-target="#toast">{toast}</template>""", 400

        user_updated_at = int(time.time())

        # Proceed with update if changes are detected
        q = """ UPDATE users
                SET user_name = %s, user_last_name = %s, user_address = %s, user_email = %s, user_updated_at = %s
                WHERE user_pk = %s
            """
        cursor.execute(q, (user_name, user_last_name, user_address, user_email, user_updated_at, user_pk))
        db.commit()

        # Fetch updated data for the user
        cursor.execute("SELECT user_name, user_last_name, user_email, user_address FROM users WHERE user_pk = %s", (user_pk,))
        updated_user = cursor.fetchone()

        # Update the session user
        session["user"].update({
            "user_name": updated_user["user_name"],
            "user_last_name": updated_user["user_last_name"],
            "user_email": updated_user["user_email"],
            "user_address": updated_user["user_address"],
        })
        session.modified = True

        toast = render_template("___toast_success.html", message="Profile updated successfully!")
        return f"""<template mix-target="#toast" mix-bottom>{toast}</template>"""

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            return "<template>System upgrading</template>", 500        
        return "<template>System under maintenance</template>", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.post("/update-password/<password_reset_key>")
@x.no_cache
def update_password(password_reset_key):
    try:
        password_reset_key = x.validate_uuid4(password_reset_key)
        user_updated_at = int(time.time())

        user_password = x.validate_user_password()
        hashed_password = generate_password_hash(user_password)

        db, cursor = x.db()
        q = """ 
            UPDATE users 
            SET user_password = %s, user_updated_at = %s
            WHERE user_pk = %s 
            """
        cursor.execute(q, (hashed_password, user_updated_at, password_reset_key))

        if cursor.rowcount != 1: x.raise_custom_exception("cannot reset password", 400)

        db.commit()
        # render_template_string to render HTML instead of template file
        return render_template_string("""
                    <template mix-target="#resetPassword">
                        <h2>New password saved</h2>
                        <form method="GET" action="{{ url_for('view_login') }}">
                            <button> 
                                Go to login
                            </button>
                        </form>
                    </template>
                """)

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            return "<template>System upgrading</template>", 500        
        return "<template>System under maintenance</template>", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.put("/users/delete/<user_pk>")
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
            toast = render_template("___toast.html", message="Incorrect password")
            return f"""<template mix-target='#toast'>{toast}</template>""", 403
        
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
        return """<template mix-redirect="/"></template>"""

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            return "<template>System upgrading</template>", 500        
        return "<template>System under maintenance</template>", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


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

        toast = render_template("___toast_success.html", message="User blocked")
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
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            return "<template>System upgrading</template>", 500        
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

        toast = render_template("___toast_success.html", message="User unblocked")
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
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code        
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
@app.put("/items/delete/<item_pk>")
def item_soft_delete(item_pk):
    try:
        # Check if the user is logged in
        user_session = session.get("user", None)
        if not user_session:
            return redirect(url_for("view_login"))
        
        # Validate UUID
        item_pk = x.validate_uuid4(item_pk)

        item_deleted_at = int(time.time())

        # Database connection and update
        db, cursor = x.db()
        q = 'UPDATE items SET item_deleted_at = %s WHERE item_pk = %s'
        cursor.execute(q, (item_deleted_at, item_pk))
        if cursor.rowcount != 1:
            x.raise_custom_exception("Cannot delete item", 400)

        db.commit()

        return """<template mix-redirect="/restaurant"></template>"""

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            return "<template>System upgrading</template>", 500        
        return "<template>System under maintenance</template>", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



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
                JOIN users 
                ON items.item_user_fk = users.user_pk WHERE items.item_pk = %s
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

        toast = render_template("___toast_success.html", message="item blocked")
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
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            return "<template>System upgrading</template>", 500        
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
                JOIN users 
                ON items.item_user_fk = users.user_pk WHERE items.item_pk = %s
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
        # Send email
        x.send_email(item["user_email"], subject, body)

        db.commit()

        toast = render_template("___toast_success.html", message="Item unblocked")
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
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            return "<template>System upgrading</template>", 500        
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
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            return "<template>System upgrading</template>", 500        
        return "<template>System under maintenance</template>", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


