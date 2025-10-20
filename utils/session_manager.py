"""
Session state management for AI Smart Quiz App
Handles Streamlit session state operations and quiz flow
"""

import streamlit as st
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from utils.models import User, QuizSession, QuizSessionCreate, QuizStatus
from utils.db_manager import db_manager


class SessionManager:
    """Manages Streamlit session state for quiz application"""

    # Session state keys
    USER_KEY = "user"
    QUIZ_SESSION_KEY = "quiz_session"
    CURRENT_QUESTION_KEY = "current_question"
    ANSWERS_KEY = "answers"
    SCORE_KEY = "score"
    START_TIME_KEY = "start_time"

    @staticmethod
    def init_session():
        """Initialize session state with default values"""
        if SessionManager.USER_KEY not in st.session_state:
            st.session_state[SessionManager.USER_KEY] = None

        if SessionManager.QUIZ_SESSION_KEY not in st.session_state:
            st.session_state[SessionManager.QUIZ_SESSION_KEY] = None

        if SessionManager.CURRENT_QUESTION_KEY not in st.session_state:
            st.session_state[SessionManager.CURRENT_QUESTION_KEY] = 0

        if SessionManager.ANSWERS_KEY not in st.session_state:
            st.session_state[SessionManager.ANSWERS_KEY] = []

        if SessionManager.SCORE_KEY not in st.session_state:
            st.session_state[SessionManager.SCORE_KEY] = 0

        if SessionManager.START_TIME_KEY not in st.session_state:
            st.session_state[SessionManager.START_TIME_KEY] = None

    @staticmethod
    def set_user(user: User):
        """Set current user in session"""
        st.session_state[SessionManager.USER_KEY] = user

    @staticmethod
    def get_user() -> Optional[User]:
        """Get current user from session"""
        return st.session_state.get(SessionManager.USER_KEY)

    @staticmethod
    def is_user_logged_in() -> bool:
        """Check if user is logged in"""
        return st.session_state.get(SessionManager.USER_KEY) is not None

    @staticmethod
    def start_quiz_session(user_name: str, category_id: int, num_questions: int = 10) -> Optional[QuizSession]:
        """Start a new quiz session"""
        try:
            # Get questions for the category
            questions = db_manager.get_questions_by_category(category_id, limit=num_questions)

            if not questions:
                st.error("No questions available for this category")
                return None

            # Create quiz session
            session_id = str(uuid.uuid4())
            quiz_session_create = QuizSessionCreate(
                user_name=user_name,
                category_id=category_id,
                total_questions=len(questions),
                questions=questions,
                status=QuizStatus.IN_PROGRESS
            )

            quiz_session = QuizSession(
                session_id=session_id,
                started_at=datetime.now(),
                **quiz_session_create.dict()
            )

            # Store in session state
            st.session_state[SessionManager.QUIZ_SESSION_KEY] = quiz_session
            st.session_state[SessionManager.CURRENT_QUESTION_KEY] = 0
            st.session_state[SessionManager.ANSWERS_KEY] = []
            st.session_state[SessionManager.SCORE_KEY] = 0
            st.session_state[SessionManager.START_TIME_KEY] = datetime.now()

            return quiz_session

        except Exception as e:
            st.error(f"Failed to start quiz: {str(e)}")
            return None

    @staticmethod
    def get_quiz_session() -> Optional[QuizSession]:
        """Get current quiz session"""
        return st.session_state.get(SessionManager.QUIZ_SESSION_KEY)

    @staticmethod
    def is_quiz_active() -> bool:
        """Check if a quiz is currently active"""
        session = SessionManager.get_quiz_session()
        return session is not None and session.status == QuizStatus.IN_PROGRESS

    @staticmethod
    def get_current_question() -> Optional[dict]:
        """Get current question in the quiz"""
        session = SessionManager.get_quiz_session()
        if not session:
            return None

        current_index = st.session_state.get(SessionManager.CURRENT_QUESTION_KEY, 0)

        if 0 <= current_index < len(session.questions):
            question = session.questions[current_index]
            return {
                'index': current_index,
                'total': session.total_questions,
                'question': question,
                'progress': (current_index / session.total_questions) * 100
            }

        return None

    @staticmethod
    def submit_answer(answer: str) -> bool:
        """Submit answer for current question"""
        session = SessionManager.get_quiz_session()
        if not session:
            return False

        current_index = st.session_state.get(SessionManager.CURRENT_QUESTION_KEY, 0)

        # Validate answer
        if answer not in ['A', 'B', 'C', 'D']:
            st.error("Invalid answer. Please select A, B, C, or D.")
            return False

        # Get current question to check if correct
        if current_index < len(session.questions):
            current_question = session.questions[current_index]
            is_correct = answer.upper() == current_question.correct_answer.upper()

            # Store answer
            answers = st.session_state.get(SessionManager.ANSWERS_KEY, [])
            answers.append({
                'question_index': current_index,
                'question_text': current_question.question_text,
                'user_answer': answer.upper(),
                'correct_answer': current_question.correct_answer,
                'is_correct': is_correct,
                'options': {
                    'A': current_question.option_a,
                    'B': current_question.option_b,
                    'C': current_question.option_c,
                    'D': current_question.option_d
                }
            })
            st.session_state[SessionManager.ANSWERS_KEY] = answers

            # Update score
            current_score = st.session_state.get(SessionManager.SCORE_KEY, 0)
            if is_correct:
                current_score += 1
            st.session_state[SessionManager.SCORE_KEY] = current_score

            return True

        return False

    @staticmethod
    def next_question() -> bool:
        """Move to next question"""
        session = SessionManager.get_quiz_session()
        if not session:
            return False

        current_index = st.session_state.get(SessionManager.CURRENT_QUESTION_KEY, 0)

        if current_index < session.total_questions - 1:
            st.session_state[SessionManager.CURRENT_QUESTION_KEY] = current_index + 1
            return True

        return False  # Quiz completed

    @staticmethod
    def is_quiz_completed() -> bool:
        """Check if quiz is completed"""
        session = SessionManager.get_quiz_session()
        if not session:
            return False

        current_index = st.session_state.get(SessionManager.CURRENT_QUESTION_KEY, 0)
        answers = st.session_state.get(SessionManager.ANSWERS_KEY, [])

        return current_index >= session.total_questions or len(answers) >= session.total_questions

    @staticmethod
    def get_quiz_results() -> Optional[Dict[str, Any]]:
        """Get final quiz results"""
        session = SessionManager.get_quiz_session()
        if not session:
            return None

        answers = st.session_state.get(SessionManager.ANSWERS_KEY, [])
        score = st.session_state.get(SessionManager.SCORE_KEY, 0)
        start_time = st.session_state.get(SessionManager.START_TIME_KEY)

        # Calculate time taken
        time_taken = None
        if start_time:
            time_taken = int((datetime.now() - start_time).total_seconds())

        # Calculate final score as percentage
        final_score = int((score / session.total_questions) * 100) if session.total_questions > 0 else 0

        # Update session status
        session.status = QuizStatus.COMPLETED
        st.session_state[SessionManager.QUIZ_SESSION_KEY] = session

        return {
            'session_id': session.session_id,
            'user_name': session.user_name,
            'category_id': session.category_id,
            'total_questions': session.total_questions,
            'correct_count': score,
            'wrong_count': session.total_questions - score,
            'score_percentage': final_score,
            'time_taken': time_taken,
            'answers': answers,
            'completed_at': datetime.now()
        }

    @staticmethod
    def reset_quiz():
        """Reset quiz session state"""
        st.session_state[SessionManager.QUIZ_SESSION_KEY] = None
        st.session_state[SessionManager.CURRENT_QUESTION_KEY] = 0
        st.session_state[SessionManager.ANSWERS_KEY] = []
        st.session_state[SessionManager.SCORE_KEY] = 0
        st.session_state[SessionManager.START_TIME_KEY] = None

    @staticmethod
    def abandon_quiz():
        """Mark current quiz as abandoned"""
        session = SessionManager.get_quiz_session()
        if session:
            session.status = QuizStatus.ABANDONED
            st.session_state[SessionManager.QUIZ_SESSION_KEY] = session
        SessionManager.reset_quiz()

    @staticmethod
    def get_session_stats() -> Dict[str, Any]:
        """Get current session statistics"""
        session = SessionManager.get_quiz_session()
        if not session:
            return {}

        current_index = st.session_state.get(SessionManager.CURRENT_QUESTION_KEY, 0)
        answers = st.session_state.get(SessionManager.ANSWERS_KEY, [])
        score = st.session_state.get(SessionManager.SCORE_KEY, 0)
        start_time = st.session_state.get(SessionManager.START_TIME_KEY)

        # Calculate elapsed time
        elapsed_time = None
        if start_time:
            elapsed_time = int((datetime.now() - start_time).total_seconds())

        return {
            'session_id': session.session_id,
            'current_question_index': current_index,
            'total_questions': session.total_questions,
            'answered_questions': len(answers),
            'correct_answers': score,
            'progress_percentage': (current_index / session.total_questions) * 100 if session.total_questions > 0 else 0,
            'elapsed_time': elapsed_time
        }

    @staticmethod
    def cleanup_expired_sessions():
        """Clean up expired sessions (placeholder for future implementation)"""
        # This could be implemented to clean up old sessions
        # For now, sessions are cleaned up when user abandons or completes quiz
        pass


# Create global session manager instance
session_manager = SessionManager()