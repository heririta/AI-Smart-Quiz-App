"""
Error handling and logging utilities for AI Smart Quiz App
Provides centralized error handling and logging functionality
"""

import streamlit as st
import logging
import traceback
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps
import os


class QuizAppError(Exception):
    """Base exception for quiz application errors"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now()


class DatabaseError(QuizAppError):
    """Database-related errors"""
    pass


class ValidationError(QuizAppError):
    """Data validation errors"""
    pass


class TTSError(QuizAppError):
    """Text-to-speech related errors"""
    pass


class QuizSessionError(QuizAppError):
    """Quiz session related errors"""
    pass


class ErrorHandler:
    """Centralized error handling for the application"""

    def __init__(self):
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/quiz_app.log'),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)

    def handle_error(self, error: Exception, show_to_user: bool = True, context: str = "") -> Dict[str, Any]:
        """Handle and log errors"""
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'traceback': traceback.format_exc() if isinstance(error, Exception) else None
        }

        # Log the error
        self.logger.error(f"Error in {context}: {error_info}")

        # Show error to user if requested
        if show_to_user:
            self.display_error_to_user(error)

        return error_info

    def display_error_to_user(self, error: Exception):
        """Display user-friendly error messages"""
        if isinstance(error, DatabaseError):
            st.error("🗄️ Database Error: Unable to access or save data. Please try again.")
        elif isinstance(error, ValidationError):
            st.error("⚠️ Validation Error: Please check your input and try again.")
        elif isinstance(error, TTSError):
            st.error("🔊 Voice Error: Unable to generate speech. You can continue without audio.")
        elif isinstance(error, QuizSessionError):
            st.error("📝 Quiz Error: There was an issue with the quiz. Please start over.")
        else:
            st.error("❌ An unexpected error occurred. Please try again or contact support.")

        # Show details in expander for debugging
        with st.expander("Error Details"):
            st.code(str(error))
            if st.checkbox("Show technical details"):
                st.code(traceback.format_exc())

    def log_info(self, message: str, context: str = ""):
        """Log informational messages"""
        log_message = f"{context}: {message}" if context else message
        self.logger.info(log_message)

    def log_warning(self, message: str, context: str = ""):
        """Log warning messages"""
        log_message = f"{context}: {message}" if context else message
        self.logger.warning(log_message)

    def log_debug(self, message: str, context: str = ""):
        """Log debug messages"""
        log_message = f"{context}: {message}" if context else message
        self.logger.debug(log_message)

    def log_error(self, message: str, context: str = ""):
        """Log error messages"""
        log_message = f"{context}: {message}" if context else message
        self.logger.error(log_message)


# Global error handler instance
error_handler = ErrorHandler()


def handle_errors(show_to_user: bool = True, context: str = ""):
    """Decorator for handling errors in functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_error(e, show_to_user, context or func.__name__)
                return None
        return wrapper
    return decorator


def safe_execute(func, default_value=None, show_error: bool = True, context: str = ""):
    """Safely execute a function with error handling"""
    try:
        return func()
    except Exception as e:
        error_handler.handle_error(e, show_error, context)
        return default_value


def validate_user_input(name: str, age: Optional[int] = None) -> bool:
    """Validate user input for registration"""
    errors = []

    if not name or not name.strip():
        errors.append("Name is required")
    elif len(name.strip()) > 100:
        errors.append("Name must be less than 100 characters")

    if age is not None:
        if not isinstance(age, int) or age < 1 or age > 120:
            errors.append("Age must be between 1 and 120")

    if errors:
        error_message = "; ".join(errors)
        raise ValidationError(error_message, error_code="INVALID_USER_INPUT")

    return True


def validate_quiz_answer(answer: str) -> bool:
    """Validate quiz answer format"""
    if not answer or answer.upper() not in ['A', 'B', 'C', 'D']:
        raise ValidationError("Invalid answer. Please select A, B, C, or D.", error_code="INVALID_ANSWER")
    return True


def validate_category_selection(category_id: Optional[int]) -> bool:
    """Validate category selection"""
    if category_id is None or not isinstance(category_id, int) or category_id <= 0:
        raise ValidationError("Please select a valid category.", error_code="INVALID_CATEGORY")
    return True


def check_database_connection() -> bool:
    """Check if database connection is working"""
    try:
        from utils.db_manager import db_manager
        # Simple query to test connection
        db_manager.execute_query("SELECT 1")
        return True
    except Exception as e:
        raise DatabaseError(f"Database connection failed: {str(e)}", error_code="DB_CONNECTION_FAILED")


def check_openai_api_key() -> bool:
    """Check if OpenAI API key is configured"""
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or api_key == "your_openai_api_key_here":
        raise TTSError("OpenAI API key not configured. Please set OPENAI_API_KEY in your environment.", error_code="MISSING_API_KEY")

    return True


def create_error_report(error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create a detailed error report"""
    return {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'timestamp': datetime.now().isoformat(),
        'context': context or {},
        'traceback': traceback.format_exc(),
        'streamlit_state': {
            'page': st.get_option('theme.base'),
            'is_user_logged_in': bool(st.session_state.get('user')),
            'quiz_active': bool(st.session_state.get('quiz_session'))
        }
    }


def show_error_report(error_report: Dict[str, Any]):
    """Display detailed error report in UI"""
    st.error("🚨 An error occurred. Here are the details:")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Error Information**")
        st.write(f"Type: `{error_report['error_type']}`")
        st.write(f"Message: `{error_report['error_message']}`")
        st.write(f"Time: `{error_report['timestamp']}`")

    with col2:
        st.write("**Context**")
        for key, value in error_report.get('context', {}).items():
            st.write(f"{key}: `{value}`")

    if st.checkbox("Show Technical Details"):
        st.code(error_report.get('traceback', 'No traceback available'))


def setup_error_boundary():
    """Setup error boundaries for the Streamlit app"""
    # Configure Streamlit to handle errors gracefully
    st.set_option('logger.error', 'error')

    # Set custom error message
    st.set_option('client.showErrorDetails', False)

    # Add error handling to session state
    if 'error_reports' not in st.session_state:
        st.session_state['error_reports'] = []


def add_error_report(error_report: Dict[str, Any]):
    """Add error report to session state"""
    if 'error_reports' not in st.session_state:
        st.session_state['error_reports'] = []

    st.session_state['error_reports'].append(error_report)

    # Keep only last 10 error reports
    if len(st.session_state['error_reports']) > 10:
        st.session_state['error_reports'] = st.session_state['error_reports'][-10:]


def get_error_reports() -> list:
    """Get all error reports from session state"""
    return st.session_state.get('error_reports', [])


def clear_error_reports():
    """Clear all error reports from session state"""
    st.session_state['error_reports'] = []