from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='transcript_db'
    )

def executeQuery(query):
    cursor = mydb.cursor()
    cursor.execute(query)

    result = cursor.fetchall()
    cursor.close()
    mydb.close()
    return result

@app.route('/')
def index():
    query_population = """
    SELECT student_population_code_ref,student_population_period_ref,student_population_year_ref, count(*) AS population FROM students
    GROUP BY student_population_code_ref,student_population_period_ref,student_population_year_ref ORDER BY student_population_code_ref"""

    student_population = executeQuery(query_population)

    return render_template('index.html',student_population=student_population)

@app.route('/populations')
def populations():
    mycursor = mydb.cursor()
    query_population = """
    SELECT student_population_code_ref,student_population_period_ref,student_population_year_ref, count(*) AS population FROM students
    GROUP BY student_population_code_ref,student_population_period_ref,student_population_year_ref ORDER BY student_population_code_ref"""

    mycursor.execute(query_population)
    student_population = mycursor.fetchall()


    # mydb.close()

    return render_template('populations.html',student_population=student_population)


if __name__ == '__main__':
    app.run(debug=True)
