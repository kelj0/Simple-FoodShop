import os, ast
from flask import Flask, url_for, Response, jsonify, render_template, session, redirect, send_file, send_from_directory
from flask import request as frequest
from flask_wtf import Form
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

from helperFunctions import test_db,check_password_hash,generate_password_hash,binary_to_dict,json,backup_db


app = Flask(__name__)
app.config['DATABASE_FILE'] = 'users.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
app.secret_key = "SESSION_RANDOM_KEY_CHANGE_THIS_IN_PRODUCTION"


db = SQLAlchemy(app)

# =========CLASSES=========
class User(db.Model):
    '''
    username[string],
    admin[string(True or False)],
    password[hashed str],
    email[string]
    '''
    id = db.Column('user_id',db.Integer,primary_key=True)
    username = db.Column(db.String(16), unique=True,nullable=False)
    admin = db.Column(db.String(5))
    password = db.Column(db.String(64),nullable=False)
    email = db.Column(db.String(64),nullable=False)
    def __repr__(self):
        return '<User {}>'.format(self.username)


class Food(db.Model):
    '''
    name[string],
    amount[int],
    subclass[string]
    '''
    id = db.Column('food_id',db.Integer,primary_key=True)
    name = db.Column(db.String(32), unique=True,nullable=False)
    amount = db.Column(db.Integer)
    subclass = db.Column(db.String(32),nullable=False)
    wishlist = db.Column(db.Text)
    price = db.Column(db.Float,nullable=False)
    def __repr__(self):
        return '''
        \nSubclass: {0}\nName: {1}\nPrice: {2}\nAmount left: {3}\nWishlist count: {4}\nUsers: {5}
        '''.format(
            self.subclass,
            self.name,
            self.price,
            self.amount,
            json.loads(self.wishlist)['count'],
            json.loads(self.wishlist)['users'])

# =========Permissions=========
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if session.get('logged_in'):
            return test(*args,**kwargs)
        else:
            return redirect(url_for('home'))
    return wrap

def admin_required(test):
    @wraps(test)
    def wrap(*args,**kwargs):
        if session.get('admin'):
            return test(*args,**kwargs)
        else:
            return render_template(
                    'unauthorized.html',
                    error=jsonify({
                        'status': 401,
                        'message': 'You are not allowed to visit this url'
                    })
                )
    return wrap

# =========APP.ROUTE=========
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')

@app.route('/deleteUser',methods=['POST'])
@admin_required
def deleteUser():
    error = None
    if frequest.method == 'POST':
        resp = ast.literal_eval(frequest.data.decode('utf-8'))
        if resp['username'] == 'admin':
            return jsonify({
                'status': 403,
                'message': 'Using CSRF to delete admin?'
                })
        t = User.query.filter_by(username=resp['username']).first()
        db.session.delete(t)
        db.session.commit()
        backup_db(User,Food)
        print("Backup complete!")
        print("Successfully deleted {}".format(resp['username']))
        error = jsonify({
            'status': 200,
            'message': 'User <{0}> deleted'.format(resp['username'])
        })
    else:
        error = jsonify({
                'status': 405,
                'message': 'POST request required'
            })
    return error

@app.route('/admin',methods=['GET','POST'])
@admin_required
def admin():
    return render_template('admin.html')
    
@app.route('/alterFood',methods=['GET','POST'])
@admin_required
def alterFood():
    error = None
    if frequest.method == 'POST':
        resp = ast.literal_eval(frequest.data.decode('utf-8'))
        t = Food.query.filter_by(name=resp['name']).first()
        alterFood = int(resp['number'])
        if resp['what']=="add":
            if t.amount<=200:
                t.amount+=alterFood
                print("Added 1 to {0} ({1})".format(t.name,t.amount))
                error = jsonify({
                    'status': 200,
                    'message': str("{0} pieces left of {1}".format(t.amount,t.name))
                })
            else:
                error = jsonify({
                    'status': 200,
                    'message': str("You reached maximum amount of {0} you can store".format(t.name))
                })
        elif resp['what']=='remove':
            if t.amount==0:
                error = jsonify({
                    'status': 400,
                    'message': str("You have 0 pieces of {0}".format(t.name))
                })
            else:
                if int(t.amount) < alterFood:
                    return jsonify({
                        'status': 400,
                        'message': str("You cant remove {0} from {1} cause there is only {2} left".format(alterFood,t.name,t.amount))
                        })
                t.amount-=alterFood
                print("Removed 1 from {0} ({1})".format(t.name,t.amount))
                error = jsonify({
                    'status': 200,
                    'message': str("{0} pieces left of {1}".format(t.amount,t.name))
                })
        db.session.commit()
        backup_db(User,Food)
        print("Backup complete!")
    else:
        error = jsonify({
                'status': 405,
                'message': 'POST request required'
        })
    return error

@app.route('/registration',methods=['GET','POST'])
def registration():
    error = None
    if frequest.method == 'POST':
        uname = frequest.form['username']
        passw = frequest.form['password']
        rpassw = frequest.form['rpassword']
        email = frequest.form['email']
        setToAdmin = "False"
        if frequest.form.get('admin'):
            setToAdmin = "True"
        if User.query.filter_by(username=uname).first() != None:
            error = ""
            return render_template(
                    'registration.html',
                    error=jsonify({
                            'status': 400,
                            'message': 'Username already taken!'
                        })
                    )
        elif User.query.filter_by(email=email).first() != None:
            return render_template(
                    'registration.html',
                    error=jsonify({
                            'status': 400,
                            'message': 'Email already taken!'
                        })
                    )
        elif passw!=rpassw:
            return render_template(
                    'registration.html',
                    error=jsonify({
                            'status': 400,
                            'message': 'Your passwords dont match'
                        })
                    )    
        if uname == "" or passw == "" or email == "":
            return render_template(
                        'registration.html',
                        error=jsonify({
                            'status': 400,
                            'message': 'Please fill in empty fields'
                            })
                        )
        u = User(username=uname,email=email, admin=setToAdmin ,password=generate_password_hash(passw)[20:])        
        db.session.add(u)
        db.session.commit()
        backup_db(User,Food)
        print("Backup complete!")
        return redirect(url_for('success'))
    else:
        return render_template('registration.html',error=error)

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if frequest.method == 'POST':
        uname = frequest.form['username']
        passw = frequest.form['password']

        if uname=="test":
            print("test")
        t = User.query.filter_by(username=uname).first()
        if t==None:
            error = "There is no user with that name"
        elif t.admin == "True" and check_password_hash("pbkdf2:sha256:50000$"+t.password,passw):
            session['admin'] = True
            session['logged_in'] = True
            return redirect(url_for('home'))
        elif check_password_hash("pbkdf2:sha256:50000$"+t.password,passw):
            session['logged_in'] = True
            session['admin'] = False
            return redirect(url_for('home'))
        else:
            error = "Wrong username/password"
    return render_template('login.html',error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in',False)
    session.pop('admin',False)
    return redirect(url_for('home'))


# =========API=========
@app.route('/users')
def usersAPI():
    l = []
    for u in User.query.all():
        l.append(
            {
                'username':u.username,
                'password':u.password,
                'email': u.email,
                'admin': u.admin
            })
    return jsonify(l)

@app.route('/food')
def foodAPI():
    d = {}
    for f in Food.query.all():
        if f.subclass not in d.keys():
            d[f.subclass] = [{
                "name":f.name,
                "amount":f.amount,
                "price":f.price,
                'wishlist':f.wishlist
            }]
        else:
            d[f.subclass].append({
                "name":f.name,
                "amount":f.amount,
                "price":f.price,
                'wishlist':f.wishlist
                })
    return jsonify(d)

@app.route('/img/<path:filename>',methods=['GET'])
@login_required
def imgAPI(filename):
    if os.path.exists("images/"+filename):
        return send_file('./images/{0}'.format(filename))
    else:
        return "Error no file!" # TODO: handle no file with json response


@app.route('/stream_data/<path:filename>',methods=['GET'])
def stream_data(filename):
    if os.path.exists("images/"+filename):
        return send_from_directory("images",filename)
    else:
        return "Error no file!" # TODO: handle no file with json response
    


# =========ERROR HANDLERS=========
@app.errorhandler(404)
def not_found():
    return "This is a 404 page(work in progress)"


def main():
    print("Starting server...")
    app_dir = os.path.realpath(os.path.dirname(__file__))
    db_path = os.path.join(app_dir,app.config['DATABASE_FILE'])

    if not os.path.exists(db_path):
        print("""
        ------------------------------------
        |Cannot find db..Building test base|
        ------------------------------------
        """)
        test_db(db,User,Food)

    app.run(host='0.0.0.0',debug=True)
    

if __name__ == '__main__':
    main()
