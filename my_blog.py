from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)
app.secret_key = "my_blog"

app.config["MYSQL_HOST"] = "127.0.0.1"
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'my_blog'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session: #Giriş yapılmış mı kontrol ediyoruz.
            return f(*args, **kwargs) #giriş yapıldıysa karışmıyoruz.
        else: 
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın.", "danger")
            return redirect(url_for("login"))
    return decorated_function


#Creating user register form:
class RegisterForm(Form):
    name = StringField("İsim ve Soyisim", validators = [validators.Length( min = 4, max = 25), validators.DataRequired(message = "Lütfen İsim ve Soyisim giriniz!")])
    username = StringField("Kullanıcı Adı", validators = [validators.Length( min = 5, max = 35), validators.DataRequired(message = "Lütfen Kullanıcı Adı giriniz!")])
    email = StringField("Email Adresi", validators= [validators.Email(message = "Lütfen geçerli bir Email adresi girin..."),validators.DataRequired(message = "Lütfen Email Adresi giriniz!")])
    password = PasswordField("Parola", validators = [
        validators.Length( min = 4, max = 25), 
        validators.DataRequired(message = "Lütfen bir Parola belirleyin!"),
        validators.EqualTo(fieldname = "confirm", message = "Parolanız uyuşmuyor!")
        ])
    confirm = PasswordField("Parola Doğrulama", validators = [validators.Length( min = 4, max = 25), validators.DataRequired()])



#Creating login form
class LoginForm(Form):
    username_or_email = StringField("Kullanıcı Adı veya Email Adresi", validators = [validators.DataRequired(message = "Lütfen Email Adresi veya Kullanıcı Adı, giriniz!")])
    password = PasswordField("Parola", validators = [validators.DataRequired(message = "Lütfen parolanızı giriniz...")])







@app.route("/")
def index():
    numbers = [1, 2, 3]
    
    return render_template("index.html", numbers = numbers)

@app.route("/about") # İstek(request) atılan URL.
@login_required
def about():         # İsteğe cevap(response) döndüren fonksiyon.
    return render_template("about.html")


@app.route("/about/iammbrn")
def user():
    return "iammbrn Hakkında"

@app.route("/dashboard")
@login_required
def dashboard():
    numbers = [1, 2, 3]
    return render_template("dashboard.html", numbers = numbers)


@app.route("/register", methods = ["GET", "POST"])
def register():

    form =RegisterForm(request.form)

    if request.method == "POST" and form.validate(): #eğer request post ve form değerleri doğru ise çalışır.
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.hash(form.password.data) # Gelen şifre bilgisi şifrelenerek veri tabanına kaydedilir.

        cursor = mysql.connection.cursor()

        query = "INSERT INTO users(name, username, email, password) VALUES(%s, %s, %s, %s)"

        cursor.execute(query, (name, username, email, password))

        mysql.connection.commit()

        cursor.close()

        flash("Kayıt işlemi başarılı :)", "success")

        return redirect(url_for("login")) # index fonksiyonuna istek atan URL' e git.

    else:
        return render_template("register.html", form = form)



@app.route("/login", methods= ["GET", "POST"])
def login():
    form = LoginForm(request.form)

    if request.method == "POST" and form.validate():
        entered_username_or_email = form.username_or_email.data
        entered_password = form.password.data

        cursor = mysql.connection.cursor()

        query = "SELECT username, password FROM users WHERE username = %s OR email = %s"

        cursor.execute(query, (entered_username_or_email, entered_username_or_email))

        user = cursor.fetchone()

        cursor.close()

        stored_password = user["password"]


        if user and sha256_crypt.verify(entered_password, stored_password):     
            flash("Giriş başarılı. Hoşgeldiniz :)", "success")

            session["logged_in"] = True
            session["username"] = user["username"]

            return redirect(url_for("index"))
        
        else:    
            flash("Kullanıcı bulunmadı! Yanlış (Kullanıcı Adı veya Email) veya yanlış şifre.", "danger")
            return render_template("login.html", form = form)
            
    else:
        return render_template("login.html", form = form)

    
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/articles")
def articles():
    articles = [
        {"id": 1, "title": "Flask Nedir?", "content": "Flask, geliştiricilere basit ve anlaşılır bir yapı sunarak, web uygulamaları geliştirmeyi kolaylaştıran, minimalist bir Python framework’üdür. Karmaşıklığı değil, sadeliği sever. Her şeyi kutuyla birlikte sunmaz; ihtiyaç duyduğunda istediğin eklentiyi entegre edersin."},
        {"id": 2, "title": "Machine Learning Nedir?", "content":"Machine Learning, makinelerin verilerden örüntüleri (patterns) öğrenerek yeni durumlarda tahminler yapabilmesini sağlayan matematiksel ve istatistiksel yöntemler bütünüdür."}
    ]
    
    return render_template("articles.html", articles = articles)

@app.route("/article/<string:id>") #Dinamik URL yapısı ve kullanımı.
def article(id):
    return "Article id:" + id


if __name__ == "__main__":
    app.run(debug = True) 
