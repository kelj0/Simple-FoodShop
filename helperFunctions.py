from werkzeug.security import check_password_hash, generate_password_hash
import json

def test_db(dataBase,User,Food):
    '''
    Builds base with admin:admin and test:test account
    '''
    dataBase.drop_all()
    dataBase.create_all()
    d = json.loads(open('./db.json').read())
    for u in d['users']:
        dataBase.session.add(User(
            username=u['username'],
            email=u['email'],
            admin=u['admin'],
            password=u['password'])) #password is already hashed
    for f in d['food']:
        for s in d['food'][f]:
            dataBase.session.add(Food(
                name=s['name'],
                amount=s['amount'],
                subclass=f,
                price=s['price'],
                wishlist=s['wishlist']))
    
    dataBase.session.commit()
    print("""
    ------------------------------------
    |   test base build successfully   |
    ------------------------------------
    """)

def backup_db(user,food):
    b = {
        'food':{
            'Desert': [],
            'Glavna jela': [],
            'Pekarski proizvodi': []
        },
        'users':[]}
    for u in user.query.all():
        b['users'].append({
            'username': u.username,
            'password': u.password,
            'email': u.email,
            'admin': u.admin
        })
    for f in food.query.all():
        b['food'][f.subclass].append({
            "name":f.name,
            "amount":f.amount,
            "price":f.price,
            'wishlist':f.wishlist
            })
    with open('db.json', 'w') as outfile:
        json.dump(b, outfile)
        

def binary_to_dict(the_binary):
    jsn = ''.join(chr(int(x, 2)) for x in the_binary.split())
    d = json.loads(jsn)  
    return d

