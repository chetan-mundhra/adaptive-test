import json
from pathlib import Path
import os
import streamlit as st

class DatabaseManager:
    DIFFICULTY_LEVELS = {
        1: "Primary School",
        2: "Senior School",
        3: "College",
        4: "Professional",
        5: "Master"
    }

    def __init__(self, db_file):
        self.db_file = db_file
        self.initialize_db()

    def initialize_db(self):
        # Use Streamlit's session state for persistence
        if 'database' not in st.session_state:
            initial_data = {
                "users": {},
                "leaderboard": {
                    "History": {},
                    "Physics": {},
                    "Mathematics": {},
                    "Economics": {},
                    "English": {}
                }
            }
            # Initialize leaderboard with new difficulty levels
            for subject in initial_data["leaderboard"]:
                for level in self.DIFFICULTY_LEVELS.values():
                    initial_data["leaderboard"][subject][level] = []
            
            st.session_state.database = initial_data

    def load_data(self):
        return st.session_state.database

    def save_data(self, data):
        st.session_state.database = data

    def add_user(self, user_id, name):
        data = self.load_data()
        # Only create new user entry if user doesn't exist
        if user_id not in data["users"]:
            data["users"][user_id] = {
                "name": name,
                "subjects": [],
                "grades": {},
                "scores": {}
            }
            self.save_data(data)
        # Update name if user exists but name is different
        elif data["users"][user_id]["name"] != name:
            data["users"][user_id]["name"] = name
            self.save_data(data)

    def update_user_score(self, user_id, subject, difficulty_level, score):
        data = self.load_data()
        user_data = data["users"][user_id]
        
        if subject not in user_data["subjects"]:
            user_data["subjects"].append(subject)
        
        level_name = self.DIFFICULTY_LEVELS[difficulty_level]
        user_data["grades"][subject] = level_name
        user_data["scores"][subject] = score

        # Update leaderboard
        if level_name not in data["leaderboard"][subject]:
            data["leaderboard"][subject][level_name] = []

        # Remove previous entry if exists
        data["leaderboard"][subject][level_name] = [
            entry for entry in data["leaderboard"][subject][level_name]
            if entry["user_id"] != user_id
        ]

        # Add new entry
        data["leaderboard"][subject][level_name].append({
            "user_id": user_id,
            "name": user_data["name"],
            "score": score
        })

        # Sort leaderboard
        data["leaderboard"][subject][level_name].sort(
            key=lambda x: x["score"], 
            reverse=True
        )

        self.save_data(data) 