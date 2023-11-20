from flask import Flask,render_template,request
import mysql.connector as ms

app = Flask(__name__)
    

@app.route('/')
def ex():
    name='ADARSH'
    return render_template('swe.html',NM=name)


@app.route('/nde')
def ex2():
    GRT='ADARSH UPADHYAY'
    return render_template('new.html',AD=GRT)
        
        

if __name__=='__main__':
    app.run(debug=True)
