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
    # cursor.close()
    # mydb.close()
    return result

@app.route('/')
def index():
    query_population = """
    SELECT student_population_code_ref,student_population_period_ref,student_population_year_ref, count(*) AS population FROM students
    GROUP BY student_population_code_ref,student_population_period_ref,student_population_year_ref ORDER BY student_population_code_ref"""

    student_population = executeQuery(query_population)

    return render_template('index.html',student_population=student_population)


@app.route('/populations/<int:year>/<batch>/<programme>')
def populations(year, batch, programme):
    student_population_query = f"""SELECT s.student_epita_email,c.contact_first_name ,c.contact_last_name
FROM students s 
JOIN contacts c
ON s.student_contact_ref = c.contact_email WHERE s.student_population_code_ref = '{programme}' AND s.student_population_year_ref = {year} AND s.student_population_period_ref = '{batch}'"""

    query_courses = """
    SELECT student_population_code_ref,student_population_period_ref,student_population_year_ref, count(*) AS population FROM students
    GROUP BY student_population_code_ref,student_population_period_ref,student_population_year_ref ORDER BY student_population_code_ref"""

    student_population = executeQuery(student_population_query)

    return render_template('populations.html',student_population=student_population)


@app.route('/populationss/<int:year>/<batch>/<programme>')
def populationss(year, batch, programme):
    test_query = f"SELECT * FROM students WHERE student_population_year_ref = {year} AND student_population_period_ref = '{batch}' AND student_population_code_ref = '{programme}'"
    student_population_query = f"""SELECT s.student_epita_email,c.contact_first_name ,c.contact_last_name
FROM students s 
JOIN contacts c
ON s.student_contact_ref = c.contact_email WHERE s.student_population_code_ref = '{programme}' AND s.student_population_year_ref = {year} AND s.student_population_period_ref = '{batch}'"""
    student_population = executeQuery(student_population_query)
    return render_template('populations.html',student_population=student_population)

if __name__ == '__main__':
    app.run(debug=True)
