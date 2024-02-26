from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

@app.route('/')
def index():
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='transcript_db'
    )

    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM students LIMIT 10")
    records = mycursor.fetchall()

    mydb.close()

    return render_template('index.html', records=records)

if __name__ == '__main__':
    app.run(debug=True)
