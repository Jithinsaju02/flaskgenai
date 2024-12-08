from flask import Flask, render_template, flash
from flask import request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, login_required, current_user, UserMixin, LoginManager
#UserMixin is used to perform flask login operations like is_authenticated, is_active, is_anonymous, get_id
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'MITS@123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///players.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True) #primary key autgenerates the id
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)


app.app_context().push()
db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/')
def hello():
    return render_template('home.html')


@app.route('/about')
def about():
    name = "John"
    age = 44
    runs = {"John":23,"Kevin":32,"Sanjay":43}
    return render_template('index.html',name=name, age=age, runs=runs)

@app.route('/contact')
def contact():
    return render_template('contact.html')



@app.route('/userdetails/<int:id>')
def userdetails(id):
    return "User id is: " + str(id)

@app.route('/addplayer', methods=['GET','POST'])
@login_required
def addplayer():
    
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        p = Player(name=name, age=age)
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('player'))
    return render_template('addp.html')

@app.route('/editplayer/<int:id>', methods=['GET','POST'])
@login_required
def editplayer(id):
    if request.method == 'POST':
        player = db.session.get(Player,id)
        player.name = request.form['name']
        player.age = request.form['age']
        db.session.commit()
        return redirect(url_for('player'))
    player = Player.query.get(id)

    return render_template('editplayer.html', player=player)

@app.route('/deleteplayer/<int:id>')
@login_required
def deleteplayer(id):
    player = Player.query.get(id)
    db.session.delete(player)
    db.session.commit()
    return redirect(url_for('player'))

@app.route('/player')
@login_required
def player():
    players = Player.query.all()
    return render_template('player.html',players=players)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user = current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# @app.route('/addplayer', methods=['POST'])
# def addplayer_post():
#     name = request.form['name']
#     age = request.form['age']
#     return "Name: " + name + " Age: " + age

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            flash("User already exists")
            return redirect(url_for('signup'))
        new_user = User(username=username, email=email, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        flash("User created successfully")
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password")
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('profile'))
    return render_template('login.html')


app.run(debug=True)