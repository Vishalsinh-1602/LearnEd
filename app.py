from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mysqldb import MySQL
import config
import openai  # For AI tutor functionality
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(config.Config)
mysql = MySQL(app)

# Initialize OpenAI
openai.api_key = app.config['OPENAI_API_KEY']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/courses')
def courses():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM courses ORDER BY created_at DESC LIMIT 8")
    courses = cur.fetchall()
    cur.close()
    return render_template('courses.html', courses=courses)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    cur = mysql.connection.cursor()
    
    # Get course details
    cur.execute("SELECT * FROM courses WHERE course_id = %s", (course_id,))
    course = cur.fetchone()
    
    # Get lessons for this course
    cur.execute("SELECT * FROM lessons WHERE course_id = %s ORDER BY sequence_order", (course_id,))
    lessons = cur.fetchall()
    
    # Get user progress if logged in
    progress = []
    if 'user_id' in session:
        user_id = session['user_id']
        cur.execute("""
            SELECT lesson_id, completed 
            FROM user_progress 
            WHERE user_id = %s AND course_id = %s
        """, (user_id, course_id))
        progress = {row[0]: row[1] for row in cur.fetchall()}
    
    cur.close()
    return render_template('course-detail.html', course=course, lessons=lessons, progress=progress)

@app.route('/ai-tutor', methods=['GET', 'POST'])
def ai_tutor():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_id = session['user_id']
        question = request.form.get('question')
        course_context = request.form.get('course_context', None)
        lesson_context = request.form.get('lesson_context', None)
        
        # Get course/lesson context for better responses
        context_prompt = ""
        if course_context:
            cur = mysql.connection.cursor()
            cur.execute("SELECT title FROM courses WHERE course_id = %s", (course_context,))
            course_title = cur.fetchone()[0]
            context_prompt += f" The user is currently studying '{course_title}'."
            if lesson_context:
                cur.execute("SELECT title FROM lessons WHERE lesson_id = %s", (lesson_context,))
                lesson_title = cur.fetchone()[0]
                context_prompt += f" They're specifically on the lesson about '{lesson_title}'."
            cur.close()
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are an AI tutor for an online education platform. {context_prompt} Provide clear, concise explanations and ask follow-up questions to ensure understanding."},
                {"role": "user", "content": question}
            ]
        )
        
        ai_response = response.choices[0].message['content']
        
        # Store interaction in database
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO ai_tutor_interactions 
            (user_id, question, response, course_context, lesson_context)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, question, ai_response, course_context, lesson_context))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'response': ai_response})
    
    return render_template('ai-tutor.html')

# Add authentication routes (login, register, logout) here
# Add API endpoints for tracking progress, etc.

if __name__ == '__main__':
    app.run(debug=True)