import random
from flask import Flask, session, render_template, redirect, url_for, make_response, request
from flask_session import Session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
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

def _________GET_________(): pass

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
    return render_template("view_index.html", name=name)

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
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    user = session.get("user")
    print(user)
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))
    active_tab = request.args.get('tab', 'restaurants')
    return render_template("view_customer.html", user=user, active_tab=active_tab)


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
    return render_template("view_profile.html", user=user, active_tab=active_tab)

##############################
@app.get("/partner")
@x.no_cache
def view_partner():
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    user = session.get("user")
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))
    return make_response


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

        # Hent brugere
        q = """ SELECT 
                users.user_pk,
                users.user_name,
                users.user_last_name,
                users.user_email,
                users.user_blocked_at,
                roles.role_name
                FROM users
                LEFT JOIN users_roles ON users.user_pk = users_roles.user_role_user_fk
                LEFT JOIN roles ON users_roles.user_role_role_fk = roles.role_pk
            """
        cursor.execute(q)
        users = cursor.fetchall()

        # Hent items
        q = """
        SELECT 
            items.item_pk,
            items.item_title,
            items.item_price,
            items.item_image,
            users.user_name
        FROM items
        LEFT JOIN users ON items.item_user_fk = users.user_pk
        """
        cursor.execute(q)
        items = cursor.fetchall()

        active_tab = request.args.get('tab', 'users')

        return render_template("view_admin.html", users=users, active_tab=active_tab, items=items, user=user)

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
##############################
##############################

def _________POST_________(): pass

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
@app.post("/users")
@x.no_cache
def signup():
    try:
        # Validate input fields
        user_name = x.validate_user_name()
        user_last_name = x.validate_user_last_name()
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
        
        # Insert user into the `users` table
        q1 = 'INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(q1, (user_pk, user_name, user_last_name, user_email, 
                            hashed_password, user_avatar, user_created_at, 
                            user_deleted_at, user_blocked_at, user_updated_at, 
                            user_verified_at, user_verification_key))

        # Assign default role to the user -- TODO: Change this so its whatever user chooses
        default_role_pk = "c56a4180-65aa-42ec-a945-5fd21dec0538"  
        q2 = 'INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES (%s, %s)'
        cursor.execute(q2, (user_pk, default_role_pk))

        # Commit changes
        db.commit()
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
            return f"""<template mix-target="#toast" mix-bottom>System upgrating</template>""", 500        
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
        ic(user_email)  # Debug email
        ic(q)  # Debug query


        cursor.execute(q, (user_email,))
        rows = cursor.fetchall()
        ic(rows)  # Debug query results
        if not rows:
            toast = render_template("___toast.html", message="user not registered")
            return f"""<template mix-target="#toast">{toast}</template>""", 400     
        if not check_password_hash(rows[0]["user_password"], user_password):
            toast = render_template("___toast.html", message="invalid credentials")
            return f"""<template mix-target="#toast">{toast}</template>""", 401
        roles = []
        for row in rows:
            roles.append(row["role_name"])
        user = {
            "user_pk": rows[0]["user_pk"],
            "user_name": rows[0]["user_name"],
            "user_last_name": rows[0]["user_last_name"],
            "user_email": rows[0]["user_email"],
            "user_avatar": rows[0].get("user_avatar"), 
            "roles": roles
        }
        ic(user)
        print(user)
        session["user"] = user
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
        # TODO: validate item_title, item_description, item_price
        file, item_image_name = x.validate_item_image()

        # Save the image
        # db, cursor = x.db() -- add somewhere

        file.save(os.path.join(x.UPLOAD_ITEM_FOLDER, item_image_name))
        db, cursor = x.db()
        # TODO: if saving the image went wrong, then rollback by going to the exception
        # TODO: Success, commit
        return item_image_name
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
@app.post("/users/<user_pk>")
def user_soft_delete(user_pk):
    try:
        # Check if the user is logged in
        user_session = session.get("user", None)
        if not user_session:
            return redirect(url_for("view_login"))

        # Ensure the user can only delete their own profile
        if user_pk != user_session.get("user_pk"):
            return """<template mix-target='#toast'>You can only delete your own account</template>""", 403

        # Validate UUID
        user_pk = x.validate_uuid4(user_pk)
        user_deleted_at = int(time.time())

        # Database connection and update
        db, cursor = x.db()
        query = 'UPDATE users SET user_deleted_at = %s WHERE user_pk = %s'
        cursor.execute(query, (user_deleted_at, user_pk))
        if cursor.rowcount != 1:
            x.raise_custom_exception("Cannot delete user", 400)

        db.commit()

        # Log the user out
        session.clear()

        # Redirect to the index page
        return f"""<template mix-redirect="/"></template>"""

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
##############################
##############################

def _________PUT_________(): pass

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
##############################
##############################

def _________DELETE_________(): pass

##############################
##############################
##############################



##############################
##############################
##############################

def _________BRIDGE_________(): pass

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

    
##############################
@app.get("/users/block/<user_pk>")
def block_user(user_pk):
    try:        
        if not "admin" in session.get("user").get("roles"): return redirect(url_for("view_login"))
    
        user_pk = x.validate_uuid4(user_pk)
        user_blocked_at = int(time.time())
        user_updated_at = int(time.time())

        db, cursor = x.db()
        q = 'UPDATE users SET user_blocked_at = %s, user_updated_at = %s WHERE user_pk = %s'
        cursor.execute(q, (user_blocked_at, user_updated_at, user_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot block user", 400)

        # Prepare the block email content
        q = 'SELECT user_name, user_email FROM `users` WHERE user_pk = %s'
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

        btn_unblock = render_template("___btn_unblock_user.html", user={"user_pk": user_pk})
        toast = render_template("___toast.html", message="User blocked")
        return f"""
                <template 
                mix-target='#block-{user_pk}' 
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
@app.get("/users/unblock/<user_pk>")
def unblock_user(user_pk):
    try:
        if not "admin" in session.get("user").get("roles"): return redirect(url_for("view_login"))

        user_pk = x.validate_uuid4(user_pk)
        user_blocked_at = int(time.time())
        user_updated_at = int(time.time())

        db, cursor = x.db()
        q = 'UPDATE users SET user_blocked_at = %s, user_updated_at = %s WHERE user_pk = %s'
        cursor.execute(q, (user_blocked_at, user_updated_at, user_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot unblock user", 400)

        # Prepare the block email content
        q = 'SELECT user_name, user_email FROM `users` WHERE user_pk = %s'
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

        btn_block = render_template("___btn_block_user.html", user={"user_pk": user_pk})
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