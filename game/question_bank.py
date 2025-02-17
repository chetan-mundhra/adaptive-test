import random
from typing import List, Dict
from crewai import Agent, Task, Crew
import json
from pathlib import Path
import time
import os

class QuestionBank:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QuestionBank, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not QuestionBank._initialized:
            # Create the question generator agent
            self.question_generator = Agent(
                name="Question Generator",
                role="Educational content creator",
                goal="Create engaging questions with increasing difficulty",
                backstory="An expert educator who specializes in adaptive learning",
                verbose=True
            )
            
            # Create a single crew instance
            self.crew = Crew(
                agents=[self.question_generator],
                tasks=[],
                verbose=True
            )
            
            # Create questions directory if it doesn't exist
            self.questions_dir = Path("questions")
            self.questions_dir.mkdir(exist_ok=True)
            
            QuestionBank._initialized = True

    def _get_questions_file(self, subject: str, grade: int = None) -> Path:
        """Get the path to the questions file for a subject and grade"""
        if grade is None:
            return self.questions_dir / f"{subject.lower()}_evaluation.json"
        return self.questions_dir / f"{subject.lower()}_grade_{grade}.json"

    def _load_questions(self, subject: str, grade: int = None) -> List[Dict]:
        """Load questions from file if they exist"""
        file_path = self._get_questions_file(subject, grade)
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return []

    def _save_questions(self, questions: List[Dict], subject: str, grade: int = None):
        """Save questions to file"""
        file_path = self._get_questions_file(subject, grade)
        with open(file_path, 'w') as f:
            json.dump(questions, f, indent=2)

    def generate_adaptive_quiz(self, subject: str, difficulty_level: int) -> List[Dict]:
        """Generate an adaptive quiz with appropriate difficulty"""
        level_names = {
            1: "Primary School",
            2: "Senior School",
            3: "College",
            4: "Professional",
            5: "Master"
        }
        level_name = level_names[difficulty_level]
        
        task = Task(
            description=f"""
            Create 20 multiple-choice questions for a {subject} quiz at {level_name} level with the following requirements:

            1. Questions should be appropriate for {level_name} level students/professionals
            2. Gradually increase difficulty within the {level_name} level
            3. Questions should build upon previous concepts
            4. Final questions should be challenging for {level_name} level

            For {subject} at {level_name} level, ensure questions:
            - Are specific to {subject} concepts appropriate for {level_name}
            - Use real-world examples relevant to the level
            - Test both knowledge and understanding
            - Include clear explanations for learning

            Return response as a JSON array in this exact format:
            {{
                "questions": [
                    {{
                        "question": "The actual question text",
                        "difficulty": "1-10 scale, where 1 is easiest and 10 is hardest",
                        "options": ["First option", "Second option", "Third option", "Fourth option"],
                        "correct_answer": "Exact text of correct option",
                        "explanation": "Detailed explanation of why this is correct",
                        "concept": "The main concept being tested"
                    }}
                ]
            }}

            Order questions from easiest to hardest within the {level_name} level.
            """,
            expected_output=f"A JSON array of 20 progressively harder {subject} questions for {level_name} level",
            agent=self.question_generator
        )

        self.crew.tasks = [task]
        
        try:
            result = str(self.crew.kickoff())
            result = result.strip()
            if '```json' in result:
                result = result.split('```json')[1]
            if '```' in result:
                result = result.split('```')[0]
            
            data = json.loads(result.strip())
            if self._validate_question_set(data):
                return data["questions"]
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            raise

    def _validate_question_set(self, data: Dict) -> bool:
        """Validate the generated question set"""
        if "questions" not in data or not isinstance(data["questions"], list):
            return False
            
        for question in data["questions"]:
            if not self._validate_question_format(question):
                return False
        
        return True

    def ensure_questions_exist(self, subject: str, grade: int = None, count: int = 20):
        """Ensure we have enough questions for the given subject and grade"""
        questions = self._load_questions(subject, grade)
        
        if len(questions) < count:
            print(f"\nGenerating new questions for {subject}" + 
                  (f" Grade {grade}" if grade else " evaluation"))
            
            try:
                # Generate questions in smaller batches if needed
                batch_size = min(10, count)  # Generate 10 questions at a time
                while len(questions) < count:
                    remaining = count - len(questions)
                    current_batch = min(batch_size, remaining)
                    
                    print(f"Generating batch of {current_batch} questions...")
                    new_questions = self.generate_adaptive_quiz(subject, grade)
                    
                    # Filter out any duplicates
                    for question in new_questions:
                        if not any(self._is_similar_question(question, q) for q in questions):
                            questions.append(question)
                    
                    self._save_questions(questions, subject, grade)
                    print(f"✓ Added {len(new_questions)} new questions! Total: {len(questions)}/{count}")
                    
                    if len(questions) < count:
                        print("Waiting before generating more questions...")
                        time.sleep(2)  # Add delay between batches
                
            except Exception as e:
                print(f"× Error generating questions: {str(e)}")
                print("Continuing with available questions...")
        
        return questions

    def _is_similar_question(self, q1: Dict, q2: Dict) -> bool:
        """Check if two questions are similar to avoid duplicates"""
        # Compare questions ignoring case and whitespace
        return (q1['question'].lower().strip() == q2['question'].lower().strip() or
                q1['correct_answer'].lower().strip() == q2['correct_answer'].lower().strip())

    def get_evaluation_questions(self, subject: str) -> List[Dict]:
        """Get evaluation questions"""
        required_count = 10
        all_questions = self.ensure_questions_exist(subject, count=required_count)
        
        # If we have fewer questions than required, return all of them
        if len(all_questions) < required_count:
            print(f"Warning: Only {len(all_questions)} questions available for evaluation")
            return all_questions
        
        return random.sample(all_questions, required_count)

    def get_main_questions(self, subject: str, grade: int) -> List[Dict]:
        """Get questions for the main quiz"""
        required_count = 20
        all_questions = self.ensure_questions_exist(subject, grade, count=required_count)
        
        # If we have fewer questions than required, return all of them
        if len(all_questions) < required_count:
            print(f"Warning: Only {len(all_questions)} questions available for grade {grade}")
            return all_questions
        
        return random.sample(all_questions, required_count)

    def _validate_question_format(self, question_data: Dict) -> bool:
        """Validate that the question has all required fields in correct format"""
        required_fields = ["question", "options", "correct_answer", "explanation", "difficulty", "concept"]
        return all(field in question_data for field in required_fields) 