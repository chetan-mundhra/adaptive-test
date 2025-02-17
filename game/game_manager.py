import uuid
from typing import List, Dict

class GameManager:
    def __init__(self, db_manager, question_bank):
        self.db_manager = db_manager
        self.question_bank = question_bank
        self.subjects = ["History", "Physics", "Mathematics", "Economics", "English"]

    def start_game(self):
        print("Welcome to the Adaptive Learning Quiz!")
        name = input("Please enter your name: ")
        
        print("\nAt what grade level would you rate your knowledge (1-5)?")
        while True:
            try:
                user_grade = int(input("Grade: "))
                if 1 <= user_grade <= 5:
                    break
                print("Please enter a grade between 1 and 5")
            except ValueError:
                print("Please enter a valid number")

        print("\nAvailable subjects:")
        for i, subject in enumerate(self.subjects, 1):
            print(f"{i}. {subject}")

        while True:
            try:
                subject_choice = int(input("\nChoose a subject (1-5): ")) - 1
                if 0 <= subject_choice < len(self.subjects):
                    break
                print("Please enter a number between 1 and 5")
            except ValueError:
                print("Please enter a valid number")

        subject = self.subjects[subject_choice]
        
        print(f"\nGenerating an adaptive quiz for {subject} at grade {user_grade}...")
        score = self.conduct_adaptive_quiz(subject, user_grade, name)
        
        # Update database with results
        user_id = str(uuid.uuid4())
        self.db_manager.add_user(user_id, name)
        self.db_manager.update_user_score(user_id, subject, user_grade, score)
        
        # Show results and leaderboard
        print(f"\nFinal Score: {score}%")
        self.display_leaderboard(subject, user_grade)

    def conduct_adaptive_quiz(self, subject: str, grade: int, name: str) -> int:
        questions = self.question_bank.generate_adaptive_quiz(subject, grade)
        correct_answers = 0
        total_questions = len(questions)

        print(f"\nStarting {subject} quiz for {name}...")
        print("Questions will get progressively harder. Good luck!\n")

        for i, question in enumerate(questions, 1):
            print(f"\nQuestion {i}/{total_questions}")
            print(f"Difficulty: {'★' * int(float(question['difficulty'])/2)}")
            print(f"\n{question['question']}")
            
            for j, option in enumerate(question['options'], 1):
                print(f"{j}. {option}")
            
            while True:
                try:
                    answer = int(input("\nYour answer (1-4): ")) - 1
                    if 0 <= answer < 4:
                        break
                    print("Please enter a number between 1 and 4")
                except ValueError:
                    print("Please enter a valid number")

            if question['options'][answer] == question['correct_answer']:
                correct_answers += 1
                print("\n✅ Correct!")
            else:
                print("\n❌ Incorrect!")
            
            print(f"Explanation: {question['explanation']}")
            print(f"Concept tested: {question['concept']}")
            input("\nPress Enter to continue...")

        return (correct_answers * 100) // total_questions

    def display_leaderboard(self, subject: str, grade: int):
        data = self.db_manager.load_data()
        leaderboard = data["leaderboard"][subject].get(str(grade), [])

        print(f"\nLeaderboard for {subject} - Grade {grade}")
        print("-" * 40)
        print("Rank  Name                  Score")
        print("-" * 40)

        for i, entry in enumerate(leaderboard, 1):
            print(f"{i:<6}{entry['name']:<22}{entry['score']}") 