from crewai import Agent, Task, Crew
from .game_manager import GameManager
from .database_manager import DatabaseManager
from .question_bank import QuestionBank
import os
from dotenv import load_dotenv

def main():
    # Use environment variable instead
    load_dotenv()

    # Initialize managers
    db_manager = DatabaseManager('game_data.json')
    question_bank = QuestionBank()
    game_manager = GameManager(db_manager, question_bank)

    # Create CrewAI agents
    question_generator = Agent(
        name="Question Generator",
        role="Educational content creator",
        goal="Create appropriate and engaging questions based on subject and grade level",
        backstory="An expert educator with deep knowledge across multiple subjects",
        tools=[],  # You can add specific tools here if needed
        allow_delegation=False
    )

    quiz_master = Agent(
        name="Quiz Master",
        role="Quiz conductor and evaluator",
        goal="Conduct quizzes and evaluate user performance",
        backstory="An expert quiz master who ensures fair evaluation"
    )

    grading_expert = Agent(
        name="Grading Expert",
        role="Grade assessor",
        goal="Assess user performance and assign appropriate grades",
        backstory="An experienced educator who specializes in assessment"
    )

    leaderboard_manager = Agent(
        name="Leaderboard Manager",
        role="Rankings manager",
        goal="Maintain and update user rankings",
        backstory="A statistics expert who manages competitive rankings"
    )

    # Create tasks
    generate_questions = Task(
        description="Generate appropriate questions based on subject and grade level",
        expected_output="A list of multiple choice questions with answers and explanations",
        agent=question_generator
    )

    conduct_quiz = Task(
        description="Conduct the quiz and collect user responses",
        expected_output="Quiz results including user responses and score",
        agent=quiz_master
    )

    assess_grade = Task(
        description="Evaluate performance and assign grade",
        expected_output="Grade level assignment based on quiz performance",
        agent=grading_expert
    )

    update_rankings = Task(
        description="Update leaderboard with new scores",
        expected_output="Updated leaderboard rankings",
        agent=leaderboard_manager
    )

    # Create crew
    game_crew = Crew(
        agents=[question_generator, quiz_master, grading_expert, leaderboard_manager],
        tasks=[generate_questions, conduct_quiz, assess_grade, update_rankings]
    )

    # Start the game
    game_manager.start_game()

if __name__ == "__main__":
    main() 