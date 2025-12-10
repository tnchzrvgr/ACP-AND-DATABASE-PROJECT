import os
from flask import Flask, render_template, request, redirect, session, url_for, flash
import pymysql
from werkzeug.utils import secure_filename
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

EMAIL_ADDRESS = "vergaratoni783@gmail.com"
EMAIL_PASSWORD = "atry ksuc jasz zddl"

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(body)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def get_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="sustainify",
        cursorclass=pymysql.cursors.DictCursor
    )

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_username():
    return dict(username=session.get("username"))

@app.route("/about")
def about():
    return render_template("about_us.html", title="About Us")

@app.context_processor
def utility_processor():
    def get_rating_info(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT AVG(rating) as avg_rating, COUNT(*) as total_ratings FROM ratings WHERE rated_id=%s", (user_id,))
        return cursor.fetchone()
    return dict(get_rating_info=get_rating_info)

@app.route("/")
def index():
    return render_template('base.html', title = "Home")

@app.route("/home")
def home():
    db = get_db()
    cursor = db.cursor()
    
    category_filter = request.args.get("category")
    if category_filter:
        cursor.execute("SELECT * FROM items WHERE category=%s ORDER BY created_at DESC", (category_filter,))
    else:
        cursor.execute("SELECT * FROM items ORDER BY created_at DESC")
    
    items = cursor.fetchall()
    return render_template("home.html", title="Home", items=items)

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s,%s)", (username,password))
        db.commit()
        flash("Account created! Please login.")
        return redirect("/login")
    return render_template("signup.html", title="Sign Up")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username,password))
        user = cursor.fetchone()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/home")
        else:
            flash("Invalid credentials")
            return redirect("/login")
    return render_template("login.html", title="Login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/post_item", methods=["GET","POST"])
def post_item():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        condition = request.form.get("condition")
        quantity = int(request.form.get("quantity", 1))
        location = request.form.get("location")
        category = request.form.get("category")
        type_ = request.form.get("type")  
        price = request.form.get("price")
        price = float(price) if price else None


        file = request.files.get("image")
        image_filename = ""
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_filename = filename

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO items 
            (user_id, title, description, `condition`, quantity, `location`, category, `type`, image_path, price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (session["user_id"], title, description, condition, quantity, location, category, type_, image_filename, price))
        db.commit()

        flash("Item posted successfully!")
        return redirect("/home")

    return render_template("post_item.html", title="Post Item")

@app.route("/item/<int:item_id>")
def view_item(item_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT i.*, u.username AS seller_name, u.id AS seller_id
        FROM items i
        JOIN users u ON i.user_id = u.id
        WHERE i.id=%s
    """, (item_id,))
    item = cursor.fetchone()
    if not item:
        flash("Item not found")
        return redirect("/home")

    cursor.execute("SELECT AVG(rating) AS avg_rating FROM ratings WHERE rated_id=%s", (item["seller_id"],))
    avg_rating_result = cursor.fetchone()
    avg_rating = avg_rating_result["avg_rating"]
    if avg_rating:
        avg_rating = round(avg_rating, 1) 
    else:
        avg_rating = None

    return render_template("item_detail.html", title=item["title"], item=item, avg_rating=avg_rating,)

@app.route("/item/<int:item_id>/buy", methods=["GET","POST"])
def buy_item(item_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM items WHERE id=%s", (item_id,))
    item = cursor.fetchone()
    
    if not item:
        flash("Item not found")
        return redirect("/home")

    if request.method == "POST":
        user_id = session["user_id"]
        username = session["username"]
        item_title = item["title"]
        seller_id = item["user_id"]

        def notify(seller_msg, buyer_msg=None):
            add_notification(seller_id, seller_msg, link=url_for("view_item", item_id=item_id))
            if buyer_msg:
                add_notification(user_id, buyer_msg, link=url_for("view_item", item_id=item_id))

        if item["type"] == "Sell":
            name = request.form["buyer_name"]
            email = request.form["buyer_email"]
            phone = request.form["buyer_phone"]
            quantity = int(request.form["quantity"])
            payment_method = request.form.get("payment_method", "Cash")
            delivery_option = request.form.get("delivery_option", "Pickup")
            delivery_address = request.form.get("delivery_address", "")
            note = request.form.get("note", "")

            cursor.execute("""
                INSERT INTO buyers 
                (item_id, buyer_name, buyer_email, buyer_phone, quantity, payment_method, delivery_option, delivery_address, note)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (item_id, name, email, phone, quantity, payment_method, delivery_option, delivery_address, note))
            db.commit()

            cursor.execute("""
                INSERT INTO transactions (item_id, type, user_from, user_to, quantity, status)
                VALUES (%s, 'Sell', %s, %s, %s, 'Pending')
            """, (item_id, user_id, seller_id, item["price"]))
            db.commit()

            notify(
                f"{username} has requested to buy your item '{item_title}'",
                f"Your purchase request for '{item_title}' has been sent to {item['user_id']}"
            )

            subject = f"Your purchase request for '{item_title}' is received"
            body = f"Hi {name},\n\nYour request to buy '{item_title}' has been submitted successfully.\n" \
                f"Quantity: {quantity}\nPayment Method: {payment_method}\nDelivery Option: {delivery_option}\n"
            if delivery_option == "Delivery" and delivery_address:
                body += f"Delivery Address: {delivery_address}\n"
            body += "\nThank you for using Sustainify!"
            send_email(email, subject, body)

            flash("Purchase request submitted successfully!")
            return redirect(url_for("home"))

        elif item["type"] == "Swap":
            name = request.form["swapper_name"]
            email = request.form["swapper_email"]
            phone = request.form["swapper_phone"]
            offered_item = request.form["offered_item"]
            offered_item_condition = request.form.get("offered_item_condition", "Used")
            category = request.form.get("category", "")
            note = request.form.get("note", "")

            swapper_id = user_id

            cursor.execute("""
                INSERT INTO swap_details 
                (item_id, swapper_name, swapper_email, swapper_phone, offered_item, offered_item_condition, category, note)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (item_id, name, email, phone, offered_item, offered_item_condition, category, note))
            db.commit()

            cursor.execute("""
                INSERT INTO swap_requests (item_id, swapper_id, offered_item)
                VALUES (%s, %s, %s)
            """, (item_id, swapper_id, offered_item))
            db.commit()

            cursor.execute("""
                INSERT INTO transactions (item_id, type, user_from, user_to, quantity, status)
                VALUES (%s, 'Swap', %s, %s, %s, 'Pending')
            """, (item_id, user_id, seller_id, 0))
            db.commit()

            notify(
                f"{username} has requested to swap for your item '{item_title}'",
                f"Your swap request for '{item_title}' has been sent to {item['user_id']}"
            )

            message_text = f"""
            Swap Request Received:
            Name: {name}
            Email: {email}
            Phone: {phone}
            Offered Item: {offered_item}
            Condition: {offered_item_condition}
            Category: {category}
            Note: {note}
            """
            cursor.execute("""
                INSERT INTO messages (sender_id, receiver_id, message)
                VALUES (%s, %s, %s)
            """, (swapper_id, seller_id, message_text))
            db.commit()

            flash("Swap request submitted successfully!")
            return redirect(url_for("home"))

        elif item["type"] == "Donate":
            name = request.form["donor_name"]
            email = request.form["donor_email"]
            phone = request.form["donor_phone"]
            pickup_address = request.form["pickup_address"]
            pickup_time = request.form.get("pickup_time")
            note = request.form.get("note", "")

            cursor.execute("""
                INSERT INTO donations 
                (item_id, donor_name, donor_email, donor_phone, pickup_address, pickup_time, note)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (item_id, name, email, phone, pickup_address, pickup_time, note))
            db.commit()

            cursor.execute("""
                INSERT INTO transactions (item_id, type, user_from, user_to, quantity, status)
                VALUES (%s, 'Donate', %s, %s, %s, 'Pending')
            """, (item_id, user_id, seller_id, 0))
            db.commit()

            notify(
                f"{username} has requested to donate your item '{item_title}'",
                f"Your donation request for '{item_title}' has been sent to {item['user_id']}"
            )

            subject = f"Your donation request for '{item_title}' is received"
            body = f"Hi {name},\n\nYour donation request for '{item_title}' has been submitted successfully.\n" \
                f"Pickup Address: {pickup_address}\n"
            if pickup_time:
                body += f"Pickup Time: {pickup_time}\n"
            if note:
                body += f"Note: {note}\n"
            body += "\nThank you for using Sustainify!"
            send_email(email, subject, body)

            flash("Donation request submitted successfully!")
            return redirect(url_for("home"))

    if item["type"] == "Sell":
        return render_template("buy_item.html", item=item, title="Purchase Item")
    elif item["type"] == "Swap":
        return render_template("swap_item.html", item=item, title="Swap Item")
    else:
        return render_template("donate_item.html", item=item, title="Request Donation")




@app.route("/donation/<int:donation_id>/complete")
def complete_donation(donation_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("UPDATE donations SET status='completed' WHERE id=%s", (donation_id,))
    db.commit()

    cursor.execute("SELECT donor_email, donor_name, item_id FROM donations WHERE id=%s", (donation_id,))
    donation = cursor.fetchone()

    cursor.execute("SELECT title, user_id FROM items WHERE id=%s", (donation["item_id"],))
    item = cursor.fetchone()

    subject = f"Your donation of '{item['title']}' has been completed!"
    body = f"Hi {donation['donor_name']},\n\nYour donation of '{item['title']}' has been successfully completed. Thank you!\n\n- Sustainify"
    send_email(donation["donor_email"], subject, body)

    flash("Donation marked as completed and email sent!")
    return redirect(url_for("rate_user", user_id=item["user_id"], item_id=item["id"]))

@app.route("/rate_user/<int:user_id>/<int:item_id>", methods=["GET","POST"])
def rate_user(user_id, item_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT id, username FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    if not user:
        flash("User not found")
        return redirect("/home")

    if request.method == "POST":
        rating = int(request.form["rating"])
        comment = request.form.get("comment", "")
        cursor.execute("""
            INSERT INTO ratings (rated_id, rater_id, item_id, rating, comment)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, session["user_id"], item_id, rating, comment))
        db.commit()
        flash("Rating submitted successfully!")
        return redirect("/home")

    return render_template("rate_user.html", user=user, item_id=item_id, title=f"Rate {user['username']}")

@app.route("/chat")
def chat():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT DISTINCT 
            CASE 
                WHEN sender_id = %s THEN receiver_id
                ELSE sender_id
            END AS user_id
        FROM messages
        WHERE sender_id = %s OR receiver_id = %s
    """, (session["user_id"], session["user_id"], session["user_id"]))

    user_ids = [row["user_id"] for row in cursor.fetchall()]

    chat_users = []
    for uid in user_ids:
        cursor.execute("SELECT username FROM users WHERE id=%s", (uid,))
        username = cursor.fetchone()["username"]

        cursor.execute("""
            SELECT message, created_at
            FROM messages
            WHERE (sender_id=%s AND receiver_id=%s)
            OR (sender_id=%s AND receiver_id=%s)
            ORDER BY created_at DESC LIMIT 1
        """, (session["user_id"], uid, uid, session["user_id"]))
        last = cursor.fetchone()

        chat_users.append({
            "user_id": uid,
            "username": username,
            "last_message": last["message"] if last else None,
            "last_message_time": last["created_at"] if last else None
        })

    return render_template("chat.html", chat_users=chat_users, chats=[], active_user=None, title="Chats")


@app.route("/chat_with/<int:user_id>", methods=["GET", "POST"])
def chat_with_user(user_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()

    if request.method == "POST":
        message = request.form["message"]
        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, message)
            VALUES (%s, %s, %s)
        """, (session["user_id"], user_id, message))
        db.commit()
        return redirect(url_for('chat_with_user', user_id=user_id))

    cursor.execute("""
        SELECT m.*, u.username AS sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE (sender_id=%s AND receiver_id=%s) 
        OR (sender_id=%s AND receiver_id=%s)
        ORDER BY created_at ASC
    """, (session["user_id"], user_id, user_id, session["user_id"]))
    chats = cursor.fetchall()

    cursor.execute("SELECT id, username FROM users WHERE id=%s", (user_id,))
    active_user = cursor.fetchone()

    cursor.execute("""
        SELECT DISTINCT 
            CASE 
                WHEN sender_id = %s THEN receiver_id
                ELSE sender_id
            END AS user_id
        FROM messages
        WHERE sender_id = %s OR receiver_id = %s
    """, (session["user_id"], session["user_id"], session["user_id"]))

    user_ids = [row["user_id"] for row in cursor.fetchall()]

    chat_users = []
    for uid in user_ids:
        cursor.execute("SELECT username FROM users WHERE id=%s", (uid,))
        username = cursor.fetchone()["username"]

        cursor.execute("""
            SELECT message, created_at
            FROM messages
            WHERE (sender_id=%s AND receiver_id=%s)
            OR (sender_id=%s AND receiver_id=%s)
            ORDER BY created_at DESC LIMIT 1
        """, (session["user_id"], uid, uid, session["user_id"]))
        last = cursor.fetchone()

        chat_users.append({
            "user_id": uid,
            "username": username,
            "last_message": last["message"] if last else None,
            "last_message_time": last["created_at"] if last else None
        })

    return render_template("chat.html", chats=chats, chat_users=chat_users, active_user=active_user)

@app.route("/delete_item/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM buyers WHERE item_id=%s", (item_id,))
    cursor.execute("DELETE FROM swap_details WHERE item_id=%s", (item_id,))
    cursor.execute("DELETE FROM donations WHERE item_id=%s", (item_id,))
    cursor.execute("DELETE FROM ratings WHERE item_id=%s", (item_id,))

    cursor.execute("DELETE FROM items WHERE id=%s", (item_id,))
    db.commit()

    flash("Item deleted successfully!")
    return redirect("/home")




@app.route("/swap/accept/<int:request_id>", methods=["POST"])
def accept_swap(request_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT sr.*, i.title, sd.swapper_name 
        FROM swap_requests sr
        JOIN items i ON sr.item_id = i.id
        JOIN swap_details sd ON sd.item_id = sr.item_id AND sd.offered_item = sr.offered_item
        WHERE sr.id=%s
    """, (request_id,))
    req = cursor.fetchone()
    
    add_notification(
        req["swapper_id"],
        f"Your swap request for '{req['title']}' has been ACCEPTED",
        link=url_for("swap_requests"))

    if not req:
        flash("Swap request not found.")
        return redirect("/swap_requests")

    cursor.execute("UPDATE swap_requests SET status='Accepted' WHERE id=%s", (request_id,))
    db.commit()

    msg = f"Your swap request for '{req['title']}' has been ACCEPTED!"
    cursor.execute("""
        INSERT INTO messages (sender_id, receiver_id, message)
        VALUES (%s, %s, %s)
    """, (session["user_id"], req["swapper_id"], msg))
    db.commit()

    flash("Swap accepted ✔ The swapper has been notified.")
    return redirect("/swap_requests")

@app.route("/swap/decline/<int:request_id>", methods=["POST"])
def decline_swap(request_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT sr.*, i.title
        FROM swap_requests sr
        JOIN items i ON sr.item_id = i.id
        WHERE sr.id=%s
    """, (request_id,))
    req = cursor.fetchone()
    
    add_notification(
        req["swapper_id"],
        f"Your swap request for '{req['title']}' has been DECLINED",
        link=url_for("swap_requests"))

    if not req:
        flash("Swap request not found.")
        return redirect("/swap_requests")

    cursor.execute("UPDATE swap_requests SET status='Declined' WHERE id=%s", (request_id,))
    db.commit()

    msg = f"Your swap request for '{req['title']}' has been DECLINED."
    cursor.execute("""
        INSERT INTO messages (sender_id, receiver_id, message)
        VALUES (%s, %s, %s)
    """, (session["user_id"], req["swapper_id"], msg))
    db.commit()

    flash("Swap declined The swapper has been notified.")
    return redirect("/swap_requests")

@app.route("/requests")
def swap_requests():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT 
            sr.id AS request_id,
            'Swap' AS request_type,
            i.title AS item_title,
            sd.swapper_name AS requester_name,
            sd.swapper_email AS requester_email,
            sd.swapper_phone AS requester_phone,
            sr.offered_item AS offered_item,
            sr.swapper_id AS user_id
        FROM swap_requests sr
        JOIN items i ON sr.item_id = i.id
        JOIN swap_details sd ON sd.item_id = sr.item_id AND sd.offered_item = sr.offered_item
        WHERE i.user_id = %s
        ORDER BY sr.id DESC
    """, (session["user_id"],))
    swap_requests = list(cursor.fetchall())

    cursor.execute("""
        SELECT 
            d.id AS request_id,
            'Donate' AS request_type,
            i.title AS item_title,
            d.donor_name AS requester_name,
            d.donor_email AS requester_email,
            d.donor_phone AS requester_phone,
            d.pickup_address AS offered_item,
            NULL AS user_id
        FROM donations d
        JOIN items i ON d.item_id = i.id
        WHERE i.user_id = %s
        ORDER BY d.id DESC
    """, (session["user_id"],))
    donation_requests = list(cursor.fetchall())

    all_requests = swap_requests + donation_requests
    all_requests.sort(key=lambda x: x['request_id'], reverse=True)

    return render_template("requests.html", requests=all_requests)

@app.route("/notification")
def notification():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT id, user_id, message, link, read_status, created_at
        FROM notifications 
        WHERE user_id=%s 
        ORDER BY created_at DESC
    """, (session["user_id"],))
    user_notifications = cursor.fetchall()

    if user_notifications:
        cursor.execute("""
            UPDATE notifications 
            SET read_status=1 
            WHERE user_id=%s AND read_status=0
        """, (session["user_id"],))
        db.commit()

    return render_template("notification.html", notifications=user_notifications, title="Notifications")

@app.context_processor
def inject_notifications():
    if "user_id" in session:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, message, link, read_status, created_at 
            FROM notifications 
            WHERE user_id=%s 
            ORDER BY created_at DESC
        """, (session["user_id"],))
        notifications = cursor.fetchall()
        unread_count = sum(1 for n in notifications if n["read_status"] == 0)
    else:
        notifications = []
        unread_count = 0

    return dict(notifications=notifications, unread_count=unread_count)



def add_notification(user_id, message, link=None):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO notifications (user_id, message, link)
        VALUES (%s, %s, %s)
    """, (user_id, message, link))
    db.commit()

    cursor.execute("SELECT LAST_INSERT_ID() AS notification_id")
    notif_id = cursor.fetchone()["notification_id"]
    return notif_id

    
if __name__=="__main__":
    app.run(debug=True)
