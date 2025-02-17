import streamlit as st
from game_manager import GameManager
from database_manager import DatabaseManager
from question_bank import QuestionBank
import uuid
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key from Streamlit secrets
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# Initialize the app state
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'questions' not in st.session_state:
    st.session_state.questions = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'quiz_complete' not in st.session_state:
    st.session_state.quiz_complete = False

# Initialize managers
try:
    db_manager = DatabaseManager('game_data.json')
    question_bank = QuestionBank()
    game_manager = GameManager(db_manager, question_bank)
except Exception as e:
    st.error(f"Error initializing managers: {str(e)}")
    st.stop()

def reset_quiz():
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.questions = None
    st.session_state.quiz_complete = False
    # Clear the answered questions set
    if 'answered' in st.session_state:
        del st.session_state.answered

def main():
    st.title("Adaptive Learning Quiz")
    
    # Sidebar for user information and subject selection
    with st.sidebar:
        st.header("User Information")
        name = st.text_input("Your Name")
        difficulty_level = st.selectbox(
            "Select Your Difficulty Level",
            [
                "Primary School",
                "Senior School",
                "College",
                "Professional",
                "Master"
            ],
            index=0
        )
        # Convert difficulty level to number for internal use
        difficulty_number = {
            "Primary School": 1,
            "Senior School": 2,
            "College": 3,
            "Professional": 4,
            "Master": 5
        }[difficulty_level]
        
        subject = st.selectbox(
            "Choose Subject",
            ["History", "Physics", "Mathematics", "Economics", "English"]
        )
        
        if st.button("Start New Quiz"):
            reset_quiz()
            if name and subject:
                with st.spinner("Generating questions... This may take a moment."):
                    try:
                        st.session_state.questions = question_bank.generate_adaptive_quiz(subject, difficulty_number)
                        db_manager.add_user(st.session_state.user_id, name)
                        st.success("Quiz generated successfully!")
                    except Exception as e:
                        st.error(f"Error generating quiz: {str(e)}")
                        st.session_state.questions = None

    # Main quiz area
    if st.session_state.questions is None:
        st.info("👈 Please enter your information and click 'Start New Quiz' to begin")
    elif st.session_state.quiz_complete:
        display_results(subject, difficulty_level, name)
    else:
        conduct_quiz(subject, difficulty_number, name)

def conduct_quiz(subject, difficulty_number, name):
    questions = st.session_state.questions
    current_q = st.session_state.current_question
    
    if current_q < len(questions):
        question = questions[current_q]
        
        # Display progress
        st.progress((current_q) / len(questions))
        st.write(f"Question {current_q + 1} of {len(questions)}")
        
        # Display difficulty
        difficulty = int(float(question['difficulty']))
        st.write(f"Difficulty: {'★' * ((difficulty + 1) // 2)}")
        
        # Display question
        st.markdown(f"### {question['question']}")
        
        # Create radio buttons for options
        answer = st.radio(
            "Choose your answer:",
            question['options'],
            key=f"q_{current_q}"
        )

        col1, col2 = st.columns(2)  # Create two columns for buttons

        # Add a key to the submit button to make it unique for each question
        with col1:
            if st.button("Submit Answer", key=f"submit_{current_q}"):
                if answer == question['correct_answer']:
                    st.session_state.score += 1
                    st.success("✅ Correct!")
                else:
                    st.error("❌ Incorrect!")
                    st.write(f"The correct answer was: {question['correct_answer']}")
                
                # Show explanation
                with st.expander("See Explanation"):
                    st.write(question['explanation'])
                    st.write(f"**Concept tested:** {question['concept']}")
                
                # Store that this question has been answered
                if 'answered' not in st.session_state:
                    st.session_state.answered = set()
                st.session_state.answered.add(current_q)

        # Show the Next button only if the current question has been answered
        with col2:
            if hasattr(st.session_state, 'answered') and current_q in st.session_state.answered:
                if st.button("Next Question", key=f"next_{current_q}"):
                    st.session_state.current_question += 1
                    # Clear the radio button selection for the next question
                    if f"q_{current_q + 1}" not in st.session_state:
                        st.session_state[f"q_{current_q + 1}"] = None
                    st.rerun()
    else:
        st.session_state.quiz_complete = True
        st.rerun()

def display_results(subject, difficulty_level, name):
    final_score = (st.session_state.score * 100) // len(st.session_state.questions)
    
    # Convert difficulty_level string to number if it's a string
    if isinstance(difficulty_level, str):
        difficulty_number = {
            "Primary School": 1,
            "Senior School": 2,
            "College": 3,
            "Professional": 4,
            "Master": 5
        }[difficulty_level]
    else:
        difficulty_number = difficulty_level
    
    # Ensure user exists in database before updating score
    db_manager.add_user(st.session_state.user_id, name)
    
    # Update database
    db_manager.update_user_score(st.session_state.user_id, subject, difficulty_number, final_score)
    
    # Get difficulty level name
    level_name = DatabaseManager.DIFFICULTY_LEVELS[difficulty_number]
    
    # Display results
    st.header("Quiz Complete! 🎉")
    st.markdown(f"### Final Score: {final_score}%")
    
    # Display leaderboard
    st.header(f"Leaderboard - {subject} ({level_name})")
    data = db_manager.load_data()
    leaderboard = data["leaderboard"][subject].get(level_name, [])
    
    if leaderboard:
        # Create a formatted table
        st.table(
            [{"Rank": i+1, "Name": entry['name'], "Score": f"{entry['score']}%"} 
             for i, entry in enumerate(leaderboard)]
        )
    else:
        st.info("No entries in leaderboard yet!")
    
    # Option to start new quiz
    if st.button("Start Another Quiz"):
        reset_quiz()
        st.rerun()

if __name__ == "__main__":
    main() 