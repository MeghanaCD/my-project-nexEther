import os
import pickle
import streamlit as st
import base64
import pandas as pd
import sqlite3
import hashlib

# Database setup
DB_FILE = "user_data.db"

# Function to hash passwords for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

# Add a new user to the database
def add_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()
    return True

# Authenticate user
def authenticate_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user is not None

# Load data
try:
    courses_list = pickle.load(open('courses.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("Required files not found. Please ensure 'courses.pkl' and 'similarity.pkl' are in the same directory.")
    st.stop()

# Recommend function
def recommend(course):
    try:
        index = courses_list[courses_list['Course Name'] == course].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_courses = []

        for i in distances[1:7]:  # Recommend the next 6 courses
            course_data = courses_list.iloc[i[0]]
            recommended_courses.append({
                'name': course_data['Course Name'],
                'university': course_data.get('University', 'N/A'),
                'difficulty': course_data.get('Difficulty Level', 'N/A'),
                'rating': course_data.get('Course Rating', 'N/A'),
                'url': course_data.get('Course URL', '#'),
                'skills': course_data.get('Skills', 'N/A'),
                'description': course_data.get('Course Description', 'No description available.')
            })

        return recommended_courses
    except IndexError:
        st.error("The selected course is not available.")
        return []

# Set page configuration
st.set_page_config(layout="wide")

# Custom CSS for styling
def set_bg_image(image_path):
    with open(image_path, "rb") as f:
        bg_image = f.read()
    encoded_bg = f"data:image/jpg;base64,{base64.b64encode(bg_image).decode()}"
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url({encoded_bg});
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .stTextInput input, .stTextArea textarea {{
            background-color: white !important;
            color: black !important;
            border: 1px solid black;
            padding: 10px;
            border-radius: 4px;
        }}
        .stButton>button {{
            background-color: white;
            color: black;
            border: 1px solid black;
            padding: 10px;
            border-radius: 4px;
        }}
        .stButton>button:hover {{
            background-color: #4682B4;
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Login Functionality
def login():
    set_bg_image("m.jpg")  # Set the background image for the login page
    
    st.title("Login Page")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type='password', key="login_password")

    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state['logged_in'] = True
            st.success("Login successful! Redirecting...")
            st.session_state['page'] = "main"
            st.rerun()
        else:
            st.error("Invalid username or password.")

    # Create a link to sign-up page
    if st.button("Sign Up"):
        st.session_state['page'] = "signup"
        st.rerun()

# Sign-Up Functionality
def signup():
    set_bg_image("m.jpg")
    
    st.title("Sign Up")
    username = st.text_input("Create a Username", key="signup_username")
    password = st.text_input("Create a Password", type='password', key="signup_password")
    confirm_password = st.text_input("Confirm Password", type='password', key="signup_confirm_password")

    # Display success message if signup is successful
    if 'signup_success' in st.session_state and st.session_state['signup_success']:
        st.success("You're signed up successfully! You can now log in.")
        del st.session_state['signup_success']  # Remove the flag after displaying the message

    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters long.")
        elif add_user(username, password):
            st.session_state['signup_success'] = True  # Set flag indicating success
            st.session_state['page'] = "login"  # Redirect to login page after sign-up
            st.rerun()  # Ensure page refreshes after redirect
        else:
            st.error("Username already exists. Please try a different one.")
    
    # Link to login page
    if st.button("Already have an account? Log in here"):
        st.session_state['page'] = "login"
        st.rerun()

# Recommendation Page
def recommendation_page(course):
    set_bg_image("m.jpg")
    st.title("Recommended Courses")

    st.write(f"### Based on your selection: {course}")
    recommended_courses = recommend(course)

    if recommended_courses:
        for idx, course in enumerate(recommended_courses, start=1):
            st.markdown(f"""
            **{idx}. {course['name']}**
            - 🎓 University: {course['university']}
            - 🔹 Difficulty: {course['difficulty']}
            - 🌟 Rating: {course['rating']}
            - 🛠️ Skills: {course['skills']}
            - 🔗 [Course Link]({course['url']})
            - 📄 Description: {course['description']}
            """)
    else:
        st.error("No recommendations available.")

# Main content for logged-in users
def main_content():
    set_bg_image("m.jpg")
    st.title("Course Recommendation System")

    course_list = courses_list['Course Name'].values
    selected_course = st.selectbox("Type or select a course you like:", ["Select your interested field"] + list(course_list), index=0)

    if st.button('Show Recommended Courses'):
        if selected_course == "Select your interested field":
            st.warning("Please select a course to get recommendations.")
        else:
            st.session_state['recommend_course'] = selected_course
            st.session_state['page'] = "recommendation"
            st.rerun()

# Initialize the database if it doesn't exist
if not os.path.exists(DB_FILE):
    init_db()

# Ensure the session state has the 'page' and 'recommend_course' keys
if 'page' not in st.session_state:
    st.session_state['page'] = "login"
if 'recommend_course' not in st.session_state:
    st.session_state['recommend_course'] = None

# Page routing
if st.session_state['page'] == "login":
    login()
elif st.session_state['page'] == "signup":
    signup()
elif st.session_state['page'] == "main":
    main_content()
elif st.session_state['page'] == "recommendation":
    recommendation_page(st.session_state['recommend_course'])
