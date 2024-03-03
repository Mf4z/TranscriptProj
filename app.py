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

    query_courses = f"""
    SELECT c.course_name  FROM programs p
JOIN courses c 
ON p.program_course_code_ref  = c.course_code
WHERE p.program_assignment = '{programme}'"""
    
    query_courses = f"""SELECT s.session_course_ref ,
c.course_name,
COUNT(s.session_course_ref ) AS session_count,
p.program_assignment,
s.session_population_year,
s.session_population_period 
FROM programs p
JOIN courses c 
ON p.program_course_code_ref  = c.course_code 
JOIN sessions s  
ON s.session_course_ref = c.course_code 
GROUP BY 
s.session_course_ref,
p.program_assignment,
c.course_name,
s.session_population_year,
s.session_population_period
HAVING 
p.program_assignment = '{programme}' AND
s.session_population_year = {year} AND 
s.session_population_period = '{batch}'
"""

    student_population = executeQuery(student_population_query)
    programme_courses = executeQuery(query_courses)

    return render_template('populations.html',student_population=student_population,programme_courses=programme_courses)


@app.route('/populationss/<int:year>/<batch>/<programme>')
def populationss(year, batch, programme):
    test_query = f"SELECT * FROM students WHERE student_population_year_ref = {year} AND student_population_period_ref = '{batch}' AND student_population_code_ref = '{programme}'"
    student_population_query = f"""SELECT s.student_epita_email,c.contact_first_name ,c.contact_last_name
FROM students s 
JOIN contacts c
ON s.student_contact_ref = c.contact_email WHERE s.student_population_code_ref = '{programme}' AND s.student_population_year_ref = {year} AND s.student_population_period_ref = '{batch}'"""
    
    cour
    student_population = executeQuery(student_population_query)
    return render_template('populations.html',student_population=student_population)

if __name__ == '__main__':
    app.run(debug=True)
