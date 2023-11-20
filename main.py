from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import os
import math


with open('config.json','r') as c:
    params = json.load(c)["params"]

local_server = True

app = Flask(__name__)
app.secret_key = 'Neeraj Singh'  #There is a seret key for the session['user'] who is admin
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['Piss']
)
    
    
mail= Mail(app)

if(local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']

db = SQLAlchemy(app)

class Contact(db.Model):
    '''
    Name, Email, Mobile_no, MSG, date, S_no
    '''
    Name = db.Column(db.String(12), nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    Mobile_no = db.Column(db.String(12), nullable=False)
    MSG = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=False)
    S_no = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)

class Post(db.Model):
    '''
    S_NO, title, content, date, slug, img_file, sub_head
    '''
    S_NO = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    title = db.Column(db.String(12), nullable=False)
    content = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(12), nullable=False)
    slug = db.Column(db.String(120), nullable=False)
    img_file = db.Column(db.String(12), nullable=False)
    sub_head = db.Column(db.String(12), nullable=False)
    







@app.route('/')
@app.route('/home')
def home():
    post= Post.query.filter_by().all()            #[0:params['no_of_post']]
    last = math.ceil(len(post)/int(params['no_of_post']))
    #Paging Logic
    number = request.args.get('number')
    if (not str(number).isnumeric()):
        number=1
    number=int(number)
    post=post[(number-1)*int(params['no_of_post']):(number-1)*int(params['no_of_post'])+int(params['no_of_post'])]
    #First
  # Change this block in the home route
    if number == 1:
        prev = "#"
        next = "/?number=" + str(number + 1)  # Use '=' instead of ',' to concatenate
    elif number == last:
        prev = "/?number=" + str(number - 1)  # Use '=' instead of ',' to concatenate
        next = "#"
    else:
        prev = "/?number=" + str(number - 1)  # Use '=' instead of ',' to concatenate
        next = "/?number=" + str(number + 1)  # Use '=' instead of ',' to concatenate

    return render_template('index.html', params=params, posts=post, prev=prev, next=next)
    




@app.route('/about')
def about():
    return render_template('about.html',  params=params,)




@app.route('/uploader',methods=['GET','POST'])
def uploder():
    if('user' in session and session['user'] == params['Mobile_no']):
        if request.method=='POST':
            f= request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)  ))
            return "Uploaded Successfully"



@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove the 'user' key from the session
    return redirect('/dashboard')







@app.route('/dashboard',methods=['GET','POST'])
def dashboard():

    if('user' in session and session['user'] == params['Mobile_no']):
        posts = Post.query.all()
        return render_template('dashboard.html', params=params, posts=posts)


    if request.method=='POST':
        #Redirect Admin Panel
        phone_no = request.form.get('Mobile_no')
        pswd = request.form.get('password')
        if(phone_no == params['Mobile_no'] and pswd == params['password']):
            #SET A SESSION VARIABLE
            session['user'] = phone_no
            posts = Post.query.all()
            return render_template('dashboard.html',  params=params,  posts=posts)
    return render_template('login.html',  params=params,)




@app.route('/delete/<string:sno>',methods=['GET','POST'])
def delete(sno):
    if('user' in session and session['user'] == params['Mobile_no']):
        post = Post.query.filter_by(S_NO = sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")



@app.route('/add',  methods=['GET','POST'])
def add():
    if 'user' in session and session['user'] == params['Mobile_no']:
        if request.method == 'POST':
            title = request.form.get('title')
            subhead = request.form.get('subhead')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('image')
            date = datetime.now()
            post = Post(title=title, sub_head=subhead, slug=slug, content=content, img_file=img_file, date=date)
            db.session.add(post)
            db.session.commit()
            return "Add Successful"
        
        return render_template("/Add.html", params=params)
    return render_template("/login.html", params=params)
    



@app.route('/edit/<string:S_NO>', methods=['GET', 'POST'])
def edit(S_NO):
    if 'user' in session and session['user'] == params['Mobile_no']:
        if request.method == 'POST':
            title = request.form.get('title')
            subhead = request.form.get('subhead')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('image')
            date = datetime.now()
            if S_NO== '0':
                post = Post(title=title, sub_head=subhead, slug=slug, content=content, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Post.query.filter_by(S_NO=S_NO).first()
                post.title = title
                post.sub_head = subhead
                post.slug = slug
                post.content = content
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/' + S_NO)
        post = Post.query.filter_by(S_NO=S_NO).first()
        return render_template('edit.html', params=params, post=post)

        







@app.route("/post/<string:post_slug>", methods=['GET'])
def post_read(post_slug):
    post= Post.query.filter_by(slug=post_slug).first()

    return render_template('post.html',  params=params,  posts=post)





@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':  # Use 'POST' instead of 'post'
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('num')
        message = request.form.get('message')  # Correct variable name
        Date = datetime.now()
        entry = Contact(Name=name, Email=email,   date=Date,   Mobile_no=phone, MSG=message)  #entry data to database table
        db.session.add(entry)    #execute entry variable to database 
        db.session.commit() 

        mail.send_message('Message From '+name,
                           sender=email,
                           recipients = [params['gmail-user']] ,
                           body = message+str("\n")+str(phone)
                           )     #save the darta to daatabase
    return render_template('contact.html',  params=params)

if __name__ == '__main__':
    app.run(debug=True, port=3030)
