from flask import Flask, render_template
import mysql.connector
from datetime import datetime

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
    return result

def currentDate():
    # Current date
    current_date = datetime.now()

    # Remove leading zeros from day
    day_without_zeros = current_date.strftime("%d").lstrip("0")

    # Determine the ordinal suffix
    if 10 <= int(day_without_zeros) % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(int(day_without_zeros) % 10, "th")

    # Format the date
    formatted_date = f"{day_without_zeros}{suffix} {current_date.strftime('%B')} {current_date.strftime('%Y')}"

    return formatted_date

@app.route('/')
def index():
    user_name = "Admin"
    query_population = """
    SELECT
    student_population_code_ref,
    student_population_period_ref,
    student_population_year_ref,
    COUNT(*) AS population 
    FROM students
    GROUP BY 
    student_population_code_ref,
    student_population_period_ref,
    student_population_year_ref 
    ORDER BY 
    student_population_code_ref
    """
    
    query_present_population ="""
    SELECT 
    COUNT(*) AS total_attendance,
    SUM(CASE WHEN a.attendance_presence = 1 THEN 1 ELSE 0 END) AS total_present,
    s.student_population_period_ref,
    s.student_population_year_ref,
    s.student_population_code_ref
    FROM 
    students s
    JOIN attendance a 
    ON s.student_epita_email = a.attendance_student_ref
    GROUP BY 
    s.student_population_period_ref,
    s.student_population_year_ref,
    s.student_population_code_ref
    ORDER BY 
    s.student_population_code_ref,
    s.student_population_year_ref;
    """
    student_population = executeQuery(query_population)
    population_percentage = executeQuery(query_present_population)
    
    current_date = currentDate()

    data_with_percentage = []
    for row in population_percentage:
        total_attendance = row[0]
        total_present = row[1]
        percentage =float(total_present * 100) / total_attendance
        data_with_percentage.append((total_attendance, total_present, percentage, row[2], row[3], row[4]))
    
    return render_template('index.html',student_population=student_population,
                           population_percentage=data_with_percentage,
                           current_date=current_date,user_name=user_name)


@app.route('/populations/<int:year>/<batch>/<programme>')
def populations(year, batch, programme):
    current_date = currentDate()
    
    student_population_query = f"""SELECT s.student_epita_email,
    c.contact_first_name ,
    c.contact_last_name,
    COUNT(CASE WHEN g.grade_score  >= 10 THEN 1 END) as passed_grade,
    COUNT(*) AS classes
    FROM students s 
    JOIN contacts c
    ON s.student_contact_ref = c.contact_email
    JOIN grades g 
    ON g.grade_student_epita_email_ref = s.student_epita_email 
    GROUP BY 
    s.student_epita_email,
    s.student_population_code_ref,
    s.student_population_year_ref,
    s.student_population_period_ref
    HAVING  s.student_population_code_ref = '{programme}'
    AND s.student_population_year_ref = {year}
    AND s.student_population_period_ref = '{batch}'
    """
    
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

    population = f"{programme} - {batch} - {year}"
    student_population = executeQuery(student_population_query)
    programme_courses = executeQuery(query_courses)

    return render_template('populations.html',population=population,
                           student_population=student_population,
                           programme_courses=programme_courses,current_date = current_date,
                           prog_year=year, prog_batch=batch, programme=programme)


@app.route('/student-grades/<int:year>/<batch>/<programme>/<student_id>')
def student_grades(year, batch, programme,student_id):
    student_records_query = f"""SELECT 
    s.student_epita_email,
    c.contact_first_name ,
    c.contact_last_name,
    crs.course_name,
    AVG(g.grade_score) AS avg_score
    FROM students s 
    JOIN contacts c
    ON s.student_contact_ref = c.contact_email
    JOIN grades g 
    ON g.grade_student_epita_email_ref = s.student_epita_email
    JOIN courses crs
    ON crs.course_code = g.grade_course_code_ref 
    GROUP BY 
    s.student_epita_email,
    s.student_population_code_ref,
    s.student_population_year_ref, 
    s.student_population_period_ref,
    g.grade_course_code_ref,
    crs.course_name
    HAVING
    s.student_epita_email = '{student_id}'
    AND s.student_population_code_ref = '{programme}'
    AND s.student_population_year_ref = {year} 
    AND s.student_population_period_ref = '{batch}'
    """
    current_date = currentDate()
    population = f"{programme} - {batch} - {year}"
    student_records = executeQuery(student_records_query)

    return render_template('student-grades.html',
                           student_records=student_records,
                           population=population,
                           programme=programme,current_date=current_date)

@app.route('/grades/<int:year>/<batch>/<programme>/<course_id>')
def grades(year, batch, programme,course_id):
    course_record_query = f"""SELECT 
    s.student_epita_email,
    c.contact_first_name ,
    c.contact_last_name,
    crs.course_name,
    AVG(g.grade_score) AS avg_score
    FROM students s 
    JOIN contacts c
    ON s.student_contact_ref = c.contact_email
    JOIN grades g 
    ON g.grade_student_epita_email_ref = s.student_epita_email
    JOIN courses crs
    ON crs.course_code = g.grade_course_code_ref 
    GROUP BY 
    s.student_epita_email,
    s.student_population_code_ref,
    s.student_population_year_ref, 
    s.student_population_period_ref,
    g.grade_course_code_ref,
    crs.course_name
    HAVING 
    s.student_population_code_ref = '{programme}'
    AND s.student_population_year_ref = {year} 
    AND s.student_population_period_ref = '{batch}'
    AND g.grade_course_code_ref = '{course_id}'    
    """
    current_date = currentDate()
    population = f"{programme} - {batch} - {year}"
    course_records = executeQuery(course_record_query)
    
    return render_template('grades.html',course_records=course_records,
                           current_date=current_date,population=population,
                           programme=programme)

if __name__ == '__main__':
    app.run(debug=True)
