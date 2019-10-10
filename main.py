from flask import *
import sqlite3, hashlib, os
from flaskext.mysql import MySQL
from werkzeug.utils import secure_filename
import traceback

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# MySQL configurations
mysql = MySQL(app)
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = '1ns2deout'
app.config['MYSQL_DATABASE_DB'] = 'database'
app.config['MYSQL_DATABASE_HOST'] = 'devstack3-dbcluster-xp4up3zn8jhh.cluster-czlpjerozeu2.us-east-1.rds.amazonaws.com'

def getLoginDetails():
    with mysql.connect() as conn:
        cur = mysql.get_db().cursor()
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT userId, firstName FROM users WHERE email = '" + session['email'] + "'")
            userId, firstName = cur.fetchone()
            cur.execute("SELECT count(productId) FROM kart WHERE userId = " + str(userId))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, firstName, noOfItems)

@app.route("/")
def root():
    loggedIn, firstName, noOfItems = getLoginDetails()
    with mysql.connect() as conn:
        cur = mysql.get_db().cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('home.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData)

@app.route("/add")
def admin():
    with mysql.connect() as conn:
        cur = mysql.get_db().cursor()
        cur.execute("SELECT categoryId, name FROM categories")
        categories = cur.fetchall()
    conn.close()
    return render_template('add.html', categories=categories)

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        with mysql.connect() as conn:
            try:
                cur = mysql.get_db().cursor()
                cur.execute('''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (%s, %s, %s, %s, %s, %s)''', (name, price, description, imagename, stock, categoryId))
                mysql.get_db().commit()
                msg="added successfully"
            except Exception as e:
                traceback.print_exc()
                mysql.connect().rollback()
                msg = "Error occured"
        conn.close()
        print(msg)
        return redirect(url_for('root'))

@app.route("/remove")
def remove():
    with mysql.connect() as conn:
        cur = mysql.get_db().cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        data = cur.fetchall()
    conn.close()
    return render_template('remove.html', data=data)

@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    with mysql.connect() as conn:
        try:
            cur = mysql.get_db().cursor()
            cur.execute('DELETE FROM products WHERE productID = ' + productId)
            mysql.get_db().commit()
            msg = "Deleted successsfully"
        except Exception as e:
            traceback.print_exc()
            mysql.connect().rollback()
            msg = "Error occured"
    conn.close()
    print(msg)
    return redirect(url_for('root'))

@app.route("/displayCategory")
def displayCategory():
        loggedIn, firstName, noOfItems = getLoginDetails()
        categoryId = request.args.get("categoryId")
        with mysql.connect() as conn:
            cur = mysql.get_db().cursor()
            cur.execute("SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = " + categoryId)
            data = cur.fetchall()
        conn.close()
        categoryName = data[0][4]
        data = parse(data)
        return render_template('displayCategory.html', data=data, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryName=categoryName)

@app.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    return render_template("profileHome.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    with mysql.connect() as conn:
        cur = mysql.get_db().cursor()
        cur.execute("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = '" + session['email'] + "'")
        profileData = cur.fetchone()
    conn.close()
    return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with mysql.connect() as conn:
            cur = mysql.get_db().cursor()
            cur.execute("SELECT userId, password FROM users WHERE email = '" + session['email'] + "'")
            userId, password = cur.fetchone()
            if (password == oldPassword):
                try:
                    cur.execute("UPDATE users SET password = %s WHERE userId = %s", (newPassword, userId))
                    mysql.get_db().commit()
                    msg="Changed successfully"
                except Exception as e:
                    traceback.print_exc()
                    mysql.connect().rollback()
                    msg = "Failed"
                return render_template("changePassword.html", msg=msg)
            else:
                msg = "Wrong password"
        conn.close()
        return render_template("changePassword.html", msg=msg)
    else:
        return render_template("changePassword.html")

@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        with mysql.connect() as con:
                try:
                    cur = mysql.get_db().cursor()
                    cur.execute('UPDATE users SET firstName = %s, lastName = %s, address1 = %s, address2 = %s, zipcode = %s, city = %s, state = %s, country = %s, phone = %s WHERE email = %s', (firstName, lastName, address1, address2, zipcode, city, state, country, phone, email))

                    mysql.get_db().commit()
                    msg = "Saved Successfully"
                except:
                    mysql.connect().rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for('editProfile'))

@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)

@app.route("/productDescription")
def productDescription():
    loggedIn, firstName, noOfItems = getLoginDetails()
    productId = request.args.get('productId')
    with mysql.connect() as conn:
        cur = mysql.get_db().cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = ' + productId)
        productData = cur.fetchone()
    conn.close()
    return render_template("productDescription.html", data=productData, loggedIn = loggedIn, firstName = firstName, noOfItems = noOfItems)

@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        with mysql.connect() as conn:
            cur = mysql.get_db().cursor()
            cur.execute("SELECT userId FROM users WHERE email = '" + session['email'] + "'")
            userId = cur.fetchone()[0]
            try:
                cur.execute("INSERT INTO kart (userId, productId) VALUES (%s, %s)", (userId, productId))
                mysql.get_db().commit()
                msg = "Added successfully"
            except:
                mysql.connect().rollback()
                msg = "Error occured"
        conn.close()
        return redirect(url_for('root'))

@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with mysql.connect() as conn:
        cur = mysql.get_db().cursor()
        cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
        userId = cur.fetchone()[0]
        cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = " + str(userId))
        products = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId'))
    with mysql.connect() as conn:
        cur = mysql.get_db().cursor()
        cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
        userId = cur.fetchone()[0]
        try:
            cur.execute("DELETE FROM kart WHERE userId = " + str(userId) + " AND productId = " + str(productId))
            mysql.get_db().commit()
            msg = "removed successfully"
        except:
            mysql.connect().rollback()
            msg = "error occured"
    conn.close()
    return redirect(url_for('root'))

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))

def is_valid(email, password):
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT email, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False


@app.route("/checkout", methods=['GET','POST'])
def payment():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']

    with mysql.connect() as conn:
        cur = mysql.get_db().cursor()
        cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
        userId = cur.fetchone()[0]
        cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = " + str(userId))
        products = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
        print(row)
        cur.execute("INSERT INTO orders1 (userId, productId) VALUES (%s, %s)", (userId, row[0]))
    cur.execute("DELETE FROM kart WHERE userId = " + str(userId))
    mysql.get_db().commit()



    return render_template("checkout.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']

        with mysql.connect() as conn:
            try:
                cur = mysql.get_db().cursor()
                cur.execute('INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, address1, address2, zipcode, city, state, country, phone))

                mysql.get_db().commit()
                msg = "Registered Successfully"

            except Exception as e:
                traceback.print_exc()
                mysql.connect().rollback()
                msg = "Error occured"

        conn.close()
        return render_template("login.html", error=msg)

@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
