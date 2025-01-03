from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import cv2
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed to secure sessions

# Hardcoded user credentials for demonstration
USERNAME = 'aaa'
PASSWORD = 'aaa'

@app.route('/')
def home():
    # If user is logged in, redirect to welcome page
    if 'username' in session:
        return redirect(url_for('welcome'))
    # Otherwise, show the login page
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form['username']
        password = request.form['password']
        
        # Check credentials
        if username == USERNAME and password == PASSWORD:
            # Store username in session and redirect to welcome
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('welcome'))
        else:
            flash('username 혹은 비밀번호가 올바르지 않습니다!', 'danger')
            return redirect(url_for('login'))
    
    # Display login page for GET requests
    # return render_template('login.html')
    return render_template('c2_login_center.html')

@app.route('/welcome')
def welcome():
    # Ensure user is logged in
    if 'username' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('login'))
    # return render_template('welcome.html', username=session['username'])
    return render_template('c2_welcome_center_cam.html', username=session['username'])

def generate_frames():
    camera = cv2.VideoCapture(0)  # 0 is the default camera

    while True:
        # Read the camera frame
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # Concatenate frame bytes with multipart data structure
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
def get_detection_entries():

    # Connect to SQLite database (or create it if it doesn't exist)
    connection = sqlite3.connect('mydatabase.db')

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # SQL command to select all data from the table
    select_query = "SELECT * FROM detection_table;"

    # Execute the command and fetch all results
    cursor.execute(select_query)
    rows = cursor.fetchall()

    # Print each row
    for row in rows:
        print(row)

    # Commit the changes and close the connection
    connection.commit()
    connection.close()
    return rows
    


# Define route for displaying the detection table data
@app.route('/detection')
def detection_page():
    # Fetch the detection table data
    data = get_detection_entries()
    
    # Render the data in a HTML template
    return render_template('detection.html', data=data)


@app.route('/video_feed')
def video_feed():
    # Returns the video stream response
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logout')
def logout():
    # Clear the session and redirect to login
    session.pop('username', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
