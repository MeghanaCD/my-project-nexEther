import unittest
from unittest.mock import patch, MagicMock
import sqlite3
import pandas as pd
import hashlib
import streamlit as st

# Importing from the main application module
from main import (
    hash_password, init_db, add_user, authenticate_user, recommend, login, signup
)

class TestDatabaseFunctions(unittest.TestCase):
    TEST_DB_FILE = "test_user_data.db"

    def setUp(self):
        self.conn = sqlite3.connect(self.TEST_DB_FILE)
        init_db()

    def tearDown(self):
        self.conn.close()
        import os
        os.remove(self.TEST_DB_FILE)

    def test_hash_password(self):
        self.assertEqual(
            hash_password("test123"),
            hashlib.sha256("test123".encode()).hexdigest()
        )

    def test_add_user(self):
        result = add_user("testuser", "password123")
        self.assertTrue(result)

    def test_authenticate_user(self):
        add_user("testuser", "password123")
        self.assertTrue(authenticate_user("testuser", "password123"))
        self.assertFalse(authenticate_user("testuser", "wrongpassword"))

class TestRecommendationLogic(unittest.TestCase):
    def setUp(self):
        self.mock_courses_list = pd.DataFrame({
            'Course Name': ['Course A', 'Course B', 'Course C'],
            'University': ['Uni A', 'Uni B', 'Uni C'],
            'Difficulty Level': ['Beginner', 'Intermediate', 'Advanced'],
            'Course Rating': [4.5, 4.2, 4.8],
            'Course URL': ['url_a', 'url_b', 'url_c'],
            'Skills': ['Skill A', 'Skill B', 'Skill C'],
            'Course Description': ['Description A', 'Description B', 'Description C']
        })
        self.mock_similarity = [[1, 0.8, 0.5], [0.8, 1, 0.6], [0.5, 0.6, 1]]

    @patch("main.courses_list", create=True)
    @patch("main.similarity", create=True)
    def test_recommend(self, mock_similarity, mock_courses_list):
        mock_courses_list.return_value = self.mock_courses_list
        mock_similarity.return_value = self.mock_similarity

        recommended_courses = recommend('Course A')
        self.assertEqual(len(recommended_courses), 2)
        self.assertEqual(recommended_courses[0]['name'], 'Course B')

class TestStreamlitApp(unittest.TestCase):
    @patch('streamlit.session_state', {})
    def test_login_page(self):
        with patch('streamlit.text_input', return_value="testuser"):
            with patch('streamlit.text_input', return_value="password123"):
                with patch('streamlit.button', side_effect=[True, False]) as mock_button:
                    login()
                    self.assertTrue(st.session_state.get('logged_in', False))

if __name__ == "_main_":
    unittest.main()