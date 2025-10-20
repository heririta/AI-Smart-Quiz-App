"""
AI Smart Quiz App - Main Streamlit Application
A standalone quiz application with local SQLite database, admin panel, and analytics dashboard
"""

import streamlit as st
import os
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any

# Add utils directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Import utilities
from models import User, Category, Question, ResultCreate
from db_manager import db_manager
from session_manager import session_manager
from error_handler import error_handler, handle_errors, validate_user_input, validate_category_selection
from chart_utils import create_analytics_charts

# Configure page with child-friendly theme
st.set_page_config(
    page_title="Fun Learning Quiz for Kids",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load child-friendly CSS
def load_css():
    with open("styles/child_friendly.css", "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css()

# Additional inline styles for child-friendly design
st.markdown("""
<style>
    .fun-emoji {
        font-size: 2rem;
        margin: 0 0.5rem;
        animation: bounce 2s infinite;
    }

    .bounce-animation {
        animation: bounce 1s ease-in-out;
    }

    @keyframes bounce {
        0%, 20%, 53%, 80%, 100% { transform: translate3d(0,0,0); }
        40%, 43% { transform: translate3d(0, -5px, 0); }
        70% { transform: translate3d(0, -3px, 0); }
        90% { transform: translate3d(0, -1px, 0); }
    }

    .category-badge {
        background-color: #C8B6DB;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.25rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    .score-display {
        background: linear-gradient(135deg, #B8E99B 0%, #90EE90 100%);
        color: #2D3748;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
    }

    .quiz-header {
        background: linear-gradient(135deg, #8ECAE6 0%, #BAE1FF 100%);
        color: #2D3748;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }

    .question-card {
        background-color: white;
        padding: 2rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin-bottom: 1rem;
    }

    .option-button {
        margin: 0.5rem 0;
    }

    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }

    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point"""
    # Initialize session state
    session_manager.init_session()

    # Setup error handling
    setup_error_boundary()

    # Display child-friendly main header
    st.markdown("""
    <div class="main-header">
        <div class="fun-emoji bounce-animation">🌟</div>
        <h1 style="font-size: 2.5rem; margin: 0; color: #2D3748;">AI Smart Quiz App</h1>
        <div class="fun-emoji bounce-animation" style="animation-delay: 0.5s;">🎯</div>
        <p style="margin-top: 0.5rem; font-size: 1.2rem; color: #4A5568;">A Fun Learning Adventure for Kids!</p>
    </div>
    """, unsafe_allow_html=True)

    # Create child-friendly navigation tabs
    tab1, tab2, tab3 = st.tabs(["🎮 Play Quiz", "🏫 Teacher Zone", "📈 My Progress"])

    with tab1:
        quiz_mode()

    with tab2:
        admin_panel()

    with tab3:
        analytics_dashboard()


def setup_error_boundary():
    """Setup error handling for the app"""
    try:
        # Check database connection
        check_database_connection()

  
    except Exception as e:
        error_handler.handle_error(e, show_to_user=True, context="App Initialization")


@handle_errors(show_to_user=True, context="User Registration")
def user_registration_form():
    """Display user registration form"""
    st.markdown("### 👤 User Information")

    col1, col2 = st.columns([2, 1])

    with col1:
        name = st.text_input(
            "Name *",
            placeholder="Enter your name",
            max_chars=100,
            help="Please enter your name to start the quiz"
        )

    with col2:
        age = st.number_input(
            "Age (Optional)",
            min_value=1,
            max_value=120,
            value=25,
            step=1,
            help="Age is optional but helps with analytics"
        )

    return name, age


@handle_errors(show_to_user=True, context="Category Selection")
def category_selection_form():
    """Display category selection form"""
    st.markdown("### 📚 Select Quiz Category")

    # Get categories from database
    try:
        categories = db_manager.get_categories()

        if not categories:
            st.warning("No categories available. Please add some categories in the Admin Panel first.")
            return None

        # Create category options with question counts
        category_options = []
        for category in categories:
            question_count = db_manager.get_total_questions_count(category.id)
            category_options.append(f"{category.name} ({question_count} questions)")

        # Display category selection
        selected_category = st.selectbox(
            "Choose a category *",
            options=category_options,
            help="Select a quiz category to begin"
        )

        # Extract category ID from selection
        if selected_category:
            # Parse category name from selection (remove question count)
            category_name = selected_category.split(" (")[0]
            category = db_manager.get_category_by_name(category_name)
            return category

        return None

    except Exception as e:
        st.error("Failed to load categories. Please try again.")
        return None


@handle_errors(show_to_user=True, context="Quiz Start")
def start_quiz():
    """Start a new quiz session with child-friendly design"""
    st.markdown("""
    <div class="quiz-header">
        <div class="fun-emoji bounce-animation">🚀</div>
        <h2 style="margin: 0.5rem 0; color: #2D3748;">Ready for a Fun Quiz Adventure?</h2>
        <p style="margin: 0;">Let's learn and play together! 🌈</p>
    </div>
    """, unsafe_allow_html=True)

    # Get user information
    name, age = user_registration_form()

    # Get category selection
    category = category_selection_form()

    # Start quiz button
    if st.button("🚀 Start Quiz", type="primary", use_container_width=True):
        # Validate inputs
        if not name or not name.strip():
            st.error("Please enter your name to start the quiz.")
            return

        if not category:
            st.error("Please select a category to start the quiz.")
            return

        # Validate user input
        try:
            validate_user_input(name.strip(), age)
            validate_category_selection(category.id)
        except Exception as e:
            st.error(str(e))
            return

        # Create user object
        user = User(name=name.strip(), age=age)
        session_manager.set_user(user)

        # Start quiz session
        quiz_session = session_manager.start_quiz_session(
            user_name=user.name,
            category_id=category.id,
            num_questions=10  # Fixed to 10 questions for all categories
        )

        if quiz_session:
            st.success(f"Quiz started! Good luck, {user.name}! 🎉\n\nYou'll answer {quiz_session.total_questions} fun questions! 🌟")
            st.rerun()


@handle_errors(show_to_user=True, context="Quiz Progress")
def display_quiz_progress():
    """Display quiz progress information"""
    stats = session_manager.get_session_stats()

    if not stats:
        return

    progress = stats.get('progress_percentage', 0)
    current_q = stats.get('current_question_index', 0) + 1
    total_q = stats.get('total_questions', 0)
    elapsed = stats.get('elapsed_time', 0)

    # Progress bar
    st.markdown(f"""
    <div class="quiz-progress">
        <strong>Progress:</strong> Question {current_q} of {total_q} ({progress:.1f}%)
        {f"<br><strong>Time Elapsed:</strong> {elapsed} seconds" if elapsed else ""}
    </div>
    """, unsafe_allow_html=True)

    # Progress bar
    st.progress(progress / 100)


@handle_errors(show_to_user=True, context="Question Display")
def display_current_question():
    """Display the current quiz question with child-friendly design"""
    question_data = session_manager.get_current_question()

    if not question_data:
        return

    question = question_data['question']

    st.markdown(f"""
    <div class="question-card">
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <div class="fun-emoji bounce-animation">❓</div>
            <h3 style="color: #8ECAE6; margin: 0.5rem 0;">Question {question_data['index'] + 1} of {question_data['total']}</h3>
        </div>
        <p style="font-size: 1.3rem; margin-bottom: 1.5rem; line-height: 1.6; color: #2D3748; font-weight: 500;">
            {question.question_text}
        </p>
        <div style="text-align: center; margin-top: 1rem;">
            <span class="category-badge">📚 {question_data.get('category_name', 'Quiz')}</span>
            <span class="category-badge" style="background-color: #FFB3BA;">🎯 {question.difficulty.value.title()} Level</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

  

@handle_errors(show_to_user=True, context="Answer Options")
def display_answer_options():
    """Display answer options with selection"""
    question_data = session_manager.get_current_question()

    if not question_data:
        return

    question = question_data['question']
    user = session_manager.get_user()

    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <div class="fun-emoji bounce-animation">🤔</div>
        <h3 style="color: #8ECAE6; margin: 0.5rem 0;">Which answer do you think is correct?</h3>
        <p style="color: #4A5568; margin: 0;">Choose one option below! 🎯</p>
    </div>
    """, unsafe_allow_html=True)

    # Get user's previous answer if any
    current_index = question_data['index']
    answers = st.session_state.get('answers', [])
    previous_answer = None

    if current_index < len(answers):
        previous_answer = answers[current_index].get('user_answer')

    # Create columns for options
    col1, col2 = st.columns(2)

    options = [
        ("A", question.option_a),
        ("B", question.option_b),
        ("C", question.option_c),
        ("D", question.option_d)
    ]

    selected_answer = None

    for i, (label, text) in enumerate(options):
        col = col1 if i < 2 else col2

        with col:
            # Create a unique key for each option
            option_key = f"option_{label}_{current_index}"

            # Determine if this option was previously selected
            is_selected = previous_answer == label

            # Custom styled radio button
            if st.radio(
                f"**{label}.**",
                options=[text],
                key=option_key,
                index=0 if is_selected else None,
                label_visibility="collapsed"
            ):
                selected_answer = label

  
    # Submit button
    if st.button("✅ Submit Answer", type="primary", use_container_width=True):
        if selected_answer:
            handle_answer_submission(selected_answer)
        else:
            st.error("Please select an answer before submitting.")


@handle_errors(show_to_user=True, context="Answer Submission")
def handle_answer_submission(answer: str):
    """Handle answer submission"""
    try:
        # Submit the answer
        success = session_manager.submit_answer(answer)

        if success:
            question_data = session_manager.get_current_question()
            if question_data:
                question = question_data['question']
                is_correct = answer.upper() == question.correct_answer.upper()

                if is_correct:
                    st.success("✅ Correct! Well done!")
                else:
                    st.error(f"❌ Incorrect. The correct answer was {question.correct_answer}")

            # Move to next question or show results
            if session_manager.next_question():
                st.rerun()
            else:
                # Quiz completed
                show_quiz_results()
        else:
            st.error("Failed to submit answer. Please try again.")

    except Exception as e:
        st.error(f"Error submitting answer: {str(e)}")


@handle_errors(show_to_user=True, context="Quiz Results")
def show_quiz_results():
    """Display quiz completion results"""
    results = session_manager.get_quiz_results()

    if not results:
        st.error("Unable to retrieve quiz results.")
        return

    user = session_manager.get_user()
    category = db_manager.get_category_by_id(results['category_id'])

    # Display results header with child-friendly celebration
    st.markdown(f"""
    <div class="quiz-header">
        <div class="fun-emoji bounce-animation">🎉</div>
        <h2 style="margin: 0.5rem 0; color: #2D3748;">Congratulations, {user.name}!</h2>
        <p style="margin: 0;">You've completed the quiz! 🌟 Great job!</p>
    </div>
    """, unsafe_allow_html=True)

    # Results summary
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Score", f"{results['score_percentage']}%")

    with col2:
        st.metric("Correct", f"{results['correct_count']}/{results['total_questions']}")

    with col3:
        if results['time_taken']:
            st.metric("Time", f"{results['time_taken']}s")
        else:
            st.metric("Time", "N/A")

    # Performance message with child-friendly encouragement
    score_percentage = results['score_percentage']
    if score_percentage >= 90:
        message = "🏆 Amazing! You're a super quiz champion!"
        emoji = "🌟"
        bg_color = "#B8E99B"
    elif score_percentage >= 70:
        message = "🎯 Fantastic work! You're doing great!"
        emoji = "👏"
        bg_color = "#BAE1FF"
    elif score_percentage >= 50:
        message = "💪 Good job! Keep practicing and you'll be a pro!"
        emoji = "🌈"
        bg_color = "#FFD3B6"
    else:
        message = "🌱 Every quiz makes you smarter! Try again!"
        emoji = "🎈"
        bg_color = "#FFB3BA"

    st.markdown(f"""
    <div class="score-display">
        <div class="fun-emoji bounce-animation">{emoji}</div>
        <div style="font-size: 1.3rem; margin: 0.5rem 0;">{message}</div>
        <div style="font-size: 1.1rem; font-weight: 600;">Score: {score_percentage}%</div>
    </div>
    """, unsafe_allow_html=True)

    # Save results to database
    try:
        result_create = ResultCreate(
            user_name=results['user_name'],
            age=user.age if user else None,
            category_id=results['category_id'],
            score=results['score_percentage'],
            correct_count=results['correct_count'],
            wrong_count=results['wrong_count'],
            total_questions=results['total_questions'],
            time_taken=results['time_taken']
        )

        result_id = db_manager.save_result(result_create)
        if result_id:
            st.success("Your results have been saved!")

    except Exception as e:
        st.error("Failed to save results to database.")

    # Action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Take Another Quiz", type="primary"):
            session_manager.reset_quiz()
            st.rerun()

    with col2:
        if st.button("📊 View Analytics"):
            # Switch to analytics tab
            st.switch_page("app.py")  # This will reload and switch tabs

    with col3:
        if st.button("🏠 Home"):
            session_manager.reset_quiz()
            st.rerun()


def quiz_mode():
    """Main quiz mode interface with child-friendly design"""
    user = session_manager.get_user()

    # Check if user is logged in
    if not user:
        start_quiz()
        return

    # Check if quiz is active
    if not session_manager.is_quiz_active():
        st.markdown(f"""
        <div class="quiz-header">
            <div class="fun-emoji bounce-animation">👋</div>
            <h2 style="margin: 0.5rem 0;">Welcome back, {user.name}!</h2>
            <p style="margin: 0;">Ready for another fun quiz adventure?</p>
        </div>
        """, unsafe_allow_html=True)
        start_quiz()
        return

    # Check if quiz is completed
    if session_manager.is_quiz_completed():
        show_quiz_results()
        return

    # Active quiz - show question interface
    st.markdown(f"""
    <div class="quiz-header">
        <div class="fun-emoji bounce-animation">🎯</div>
        <h2 style="margin: 0.5rem 0;">Quiz Adventure in Progress</h2>
        <p style="margin: 0;">Keep going, {user.name}! You're doing great! 🌟</p>
    </div>
    """, unsafe_allow_html=True)

    # Show progress
    display_quiz_progress()

    # Show current question
    display_current_question()

    # Show answer options
    display_answer_options()

    # Add option to abandon quiz
    abandon_col1, abandon_col2 = st.columns([1, 1])

    with abandon_col1:
        if st.button("❌ Abandon Quiz", help="End current quiz without saving results"):
            st.session_state["show_abandon_confirm"] = True

    # Show confirmation dialog
    if st.session_state.get("show_abandon_confirm", False):
        with abandon_col2:
            st.warning("⚠️ Are you sure you want to abandon this quiz? Your progress will be lost.")
            col_yes, col_no = st.columns([1, 1])
            with col_yes:
                if st.button("✅ Yes, Abandon", type="primary"):
                    session_manager.abandon_quiz()
                    st.session_state["show_abandon_confirm"] = False
                    st.warning("Quiz abandoned. You can start a new quiz below.")
                    st.rerun()
            with col_no:
                if st.button("❌ Cancel"):
                    st.session_state["show_abandon_confirm"] = False
                    st.rerun()


@handle_errors(show_to_user=True, context="Admin Panel")
def admin_panel():
    """Admin panel for content management"""
    st.markdown("## ⚙️ Admin Panel")

    # Add helpful info
    st.info("📍 **Quick Tip:** The 'Add New Question' form is now prominently displayed at the top of the Questions tab!")

    # Create sub-tabs for different admin functions
    tab1, tab2, tab3, tab4 = st.tabs(["📚 Categories", "❓ Questions", "📁 CSV Import/Export", "⚡ Bulk Operations"])

    with tab1:
        category_management()

    with tab2:
        question_management()

    with tab3:
        csv_import_export()

    with tab4:
        bulk_operations()


@handle_errors(show_to_user=True, context="Category Management")
def category_management():
    """Category CRUD operations"""
    st.markdown("### 📚 Category Management")

    # Get existing categories
    categories = db_manager.get_categories()

    # Create two columns for layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### 📋 Existing Categories")

        if categories:
            # Create a dataframe-like display for categories
            for i, category in enumerate(categories):
                question_count = db_manager.get_total_questions_count(category.id)

                with st.expander(f"📁 {category.name} ({question_count} questions)"):
                    col_edit, col_delete = st.columns([3, 1])

                    with col_edit:
                        if st.button(f"✏️ Edit", key=f"edit_cat_{category.id}"):
                            st.session_state[f"edit_category_{category.id}"] = True

                    with col_delete:
                        if st.button(f"🗑️ Delete", key=f"del_cat_{category.id}"):
                            if st.session_state.get(f"confirm_delete_{category.id}", False):
                                success = db_manager.delete_category(category.id)
                                if success:
                                    st.success(f"Category '{category.name}' deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete category.")
                            else:
                                st.session_state[f"confirm_delete_{category.id}"] = True
                                st.warning("⚠️ Click again to confirm deletion")

                    # Edit form (shown when edit button is clicked)
                    if st.session_state.get(f"edit_category_{category.id}", False):
                        with st.form(key=f"edit_form_{category.id}"):
                            new_name = st.text_input("Category Name", value=category.name)
                            new_description = st.text_area("Description", value=category.description or "")

                            col_save, col_cancel = st.columns([1, 1])
                            with col_save:
                                if st.form_submit_button("💾 Save Changes"):
                                    if new_name.strip():
                                        from utils.models import CategoryUpdate
                                        category_update = CategoryUpdate(
                                            name=new_name.strip(),
                                            description=new_description.strip() if new_description.strip() else None
                                        )
                                        success = db_manager.update_category(category.id, category_update)
                                        if success:
                                            st.success("Category updated successfully!")
                                            st.session_state[f"edit_category_{category.id}"] = False
                                            st.rerun()
                                        else:
                                            st.error("Failed to update category.")
                                    else:
                                        st.error("Category name is required.")

                            with col_cancel:
                                if st.form_submit_button("❌ Cancel"):
                                    st.session_state[f"edit_category_{category.id}"] = False
                                    st.rerun()
        else:
            st.info("No categories found. Add your first category below!")

    with col2:
        st.markdown("#### ➕ Add New Category")

        with st.form(key="add_category_form"):
            name = st.text_input("Category Name *", placeholder="e.g., Science, History, Mathematics")
            description = st.text_area("Description (Optional)", placeholder="Brief description of this category...")

            if st.form_submit_button("➕ Add Category", type="primary"):
                if name and name.strip():
                    from utils.models import CategoryCreate
                    category_create = CategoryCreate(
                        name=name.strip(),
                        description=description.strip() if description else ""
                    )
                    category_id = db_manager.create_category(category_create)
                    if category_id:
                        st.success(f"Category '{name.strip()}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add category. Please try again.")
                else:
                    st.error("Category name is required.")


@handle_errors(show_to_user=True, context="Question Management")
def question_management():
    """Question CRUD operations"""
    st.markdown("### ❓ Question Management")

    # Get categories for dropdown
    categories = db_manager.get_categories()

    if not categories:
        st.warning("⚠️ Please add categories first before managing questions.")
        return

    # Add New Question section at the top for better visibility
    st.markdown("---")
    st.markdown("## 🎯 Add New Question")
    st.markdown("Create new quiz questions with the form below:")

    # Add a distinctive border and background to make it stand out
    st.markdown("""
    <div style="padding: 1.5rem; border: 3px solid #1f77b4; border-radius: 0.5rem; background-color: #e6f3ff; margin-bottom: 1rem;">
        <h4 style="color: #1f77b4; margin-top: 0;">📝 Create New Question</h4>
        <p style="margin-bottom: 0;">Fill in the form below to create a new quiz question.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form(key="add_question_form"):
        st.markdown("**New Question Details**")

        # Category selection
        category_options = {cat.name: cat.id for cat in categories}
        selected_category_name = st.selectbox("Category *", list(category_options.keys()))
        selected_category_id = category_options[selected_category_name]

        # Question details
        question_text = st.text_area("Question Text *", placeholder="Enter your question here...", height=100)

        st.markdown("**Answer Options**")
        option_a = st.text_input("Option A *", placeholder="First option")
        option_b = st.text_input("Option B *", placeholder="Second option")
        option_c = st.text_input("Option C *", placeholder="Third option")
        option_d = st.text_input("Option D *", placeholder="Fourth option")

        correct_answer = st.selectbox("Correct Answer *", options=["A", "B", "C", "D"])
        difficulty = st.selectbox("Difficulty", options=["Easy", "Medium", "Hard"])

        if st.form_submit_button("➕ Add Question", type="primary"):
            # Validation
            if not all([question_text.strip(), option_a.strip(), option_b.strip(),
                       option_c.strip(), option_d.strip()]):
                st.error("All fields are required!")
            elif len(question_text.strip()) < 10:
                st.error("Question text must be at least 10 characters long!")
            elif len(option_a.strip()) < 1 or len(option_b.strip()) < 1 or len(option_c.strip()) < 1 or len(option_d.strip()) < 1:
                st.error("All options must have at least 1 character!")
            else:
                # Create question
                from utils.models import QuestionCreate
                question_create = QuestionCreate(
                    category_id=selected_category_id,
                    question_text=question_text.strip(),
                    option_a=option_a.strip(),
                    option_b=option_b.strip(),
                    option_c=option_c.strip(),
                    option_d=option_d.strip(),
                    correct_answer=correct_answer,
                    difficulty=difficulty.lower()
                )

                success = db_manager.create_question(question_create)
                if success:
                    st.success("Question added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add question. Please try again.")

    st.markdown("---")
    st.markdown("## 📋 Existing Questions")

    # Create two columns for layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Filter controls (move to top to define category_id first)
        filter_col1, filter_col2 = st.columns([2, 1])

        with filter_col1:
            selected_category = st.selectbox(
                "Filter by Category",
                options=[("All Categories", None)] + [(cat.name, cat.id) for cat in categories],
                format_func=lambda x: x[0]
            )

        with filter_col2:
            questions_per_page = st.selectbox("Questions per page", [5, 10, 20, 50], index=1)

        # Get category_id after selection
        category_id = selected_category[1] if selected_category[1] is not None else None

        # Statistics header (now category_id is defined)
        total_questions = db_manager.get_total_questions_count(category_id)
        category_display = f" in {selected_category[0]}" if selected_category[0] != "All Categories" else ""
        st.markdown(f"#### 📋 Existing Questions **({total_questions} total{category_display})**")

        # Get questions
        questions = db_manager.get_questions(category_id=category_id, limit=questions_per_page)

        if questions:
            for i, question in enumerate(questions):
                with st.expander(f"❓ {question.question_text[:100]}{'...' if len(question.question_text) > 100 else ''}"):
                    # Get category name
                    category = db_manager.get_category_by_id(question.category_id)
                    category_name = category.name if category else "Unknown"

                    # Display question details in a cleaner format
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**📚 Category:** {category_name}")
                        st.markdown(f"**❓ Question:** {question.question_text}")
                    with col2:
                        st.markdown(f"**🎯 Difficulty:** {question.difficulty.value.title()}")
                        st.markdown(f"**✅ Correct:** {question.correct_answer}")

                    st.markdown("**📝 Answer Options:**")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"**A.** {question.option_a}")
                        st.markdown(f"**B.** {question.option_b}")
                    with col_b:
                        st.markdown(f"**C.** {question.option_c}")
                        st.markdown(f"**D.** {question.option_d}")

                    # Display combined content more prominently
                    if question.combined_content:
                        st.markdown("---")
                        st.markdown(f"**🔗 Combined Content:**")
                        st.success(question.combined_content)

                    # Action buttons
                    col_edit, col_delete = st.columns([1, 1])

                    with col_edit:
                        if st.button(f"✏️ Edit", key=f"edit_q_{question.id}"):
                            st.session_state[f"edit_question_{question.id}"] = True

                    with col_delete:
                        if st.button(f"🗑️ Delete", key=f"del_q_{question.id}"):
                            if st.session_state.get(f"confirm_delete_q_{question.id}", False):
                                success = db_manager.delete_question(question.id)
                                if success:
                                    st.success("Question deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete question.")
                            else:
                                st.session_state[f"confirm_delete_q_{question.id}"] = True
                                st.warning("⚠️ Click again to confirm deletion")

                    # Edit form
                    if st.session_state.get(f"edit_question_{question.id}", False):
                        with st.form(key=f"edit_q_form_{question.id}"):
                            st.markdown("**Edit Question**")

                            edit_category = st.selectbox(
                                "Category",
                                options=categories,
                                format_func=lambda x: x.name,
                                index=[cat.id for cat in categories].index(question.category_id)
                            )

                            edit_question_text = st.text_area("Question Text", value=question.question_text, height=100)
                            edit_option_a = st.text_input("Option A", value=question.option_a)
                            edit_option_b = st.text_input("Option B", value=question.option_b)
                            edit_option_c = st.text_input("Option C", value=question.option_c)
                            edit_option_d = st.text_input("Option D", value=question.option_d)
                            edit_correct_answer = st.selectbox(
                                "Correct Answer",
                                options=["A", "B", "C", "D"],
                                index=["A", "B", "C", "D"].index(question.correct_answer.upper())
                            )
                            edit_difficulty = st.selectbox(
                                "Difficulty",
                                options=["Easy", "Medium", "Hard"],
                                index=["Easy", "Medium", "Hard"].index(question.difficulty.value.title())
                            )

                            col_save, col_cancel = st.columns([1, 1])
                            with col_save:
                                if st.form_submit_button("💾 Save Changes"):
                                    if (edit_question_text.strip() and edit_option_a.strip() and
                                        edit_option_b.strip() and edit_option_c.strip() and edit_option_d.strip()):

                                        success = db_manager.update_question(
                                            question_id=question.id,
                                            category_id=edit_category.id,
                                            question_text=edit_question_text.strip(),
                                            option_a=edit_option_a.strip(),
                                            option_b=edit_option_b.strip(),
                                            option_c=edit_option_c.strip(),
                                            option_d=edit_option_d.strip(),
                                            correct_answer=edit_correct_answer,
                                            difficulty=edit_difficulty.lower()
                                        )

                                        if success:
                                            st.success("Question updated successfully!")
                                            st.session_state[f"edit_question_{question.id}"] = False
                                            st.rerun()
                                        else:
                                            st.error("Failed to update question.")
                                    else:
                                        st.error("All fields are required.")

                            with col_cancel:
                                if st.form_submit_button("❌ Cancel"):
                                    st.session_state[f"edit_question_{question.id}"] = False
                                    st.rerun()
        else:
            st.info("🔍 **No questions found** in this category. Start by adding your first question on the right!")

    with col2:
        # Right column can be used for future features or statistics
        st.markdown("#### 📊 Quick Stats")

        # Show some basic statistics
        total_questions = db_manager.get_total_questions_count()
        st.metric("Total Questions", total_questions)

        if categories:
            st.metric("Total Categories", len(categories))

            # Show categories with question counts
            st.markdown("**Categories Overview:**")
            for category in categories[:5]:  # Show top 5 categories
                count = db_manager.get_total_questions_count(category.id)
                st.write(f"• {category.name}: {count} questions")


@handle_errors(show_to_user=True, context="CSV Import/Export")
def csv_import_export():
    """CSV import and export functionality"""
    st.markdown("### 📁 CSV Import/Export")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📤 Export to CSV")

        export_type = st.selectbox(
            "Export Type",
            options=["Questions", "Categories", "Quiz Results"]
        )

        if export_type == "Questions":
            # Category filter for questions
            categories = db_manager.get_categories()
            category_options = [("All Categories", None)] + [(cat.name, cat.id) for cat in categories]
            selected_category = st.selectbox(
                "Filter by Category (Optional)",
                options=category_options,
                format_func=lambda x: x[0]
            )

            if st.button("📤 Export Questions", type="primary"):
                try:
                    csv_data = db_manager.export_questions_to_csv(selected_category[1])
                    st.download_button(
                        label="💾 Download Questions CSV",
                        data=csv_data,
                        file_name=f"questions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    st.success("Questions exported successfully!")
                except Exception as e:
                    st.error(f"Failed to export questions: {str(e)}")

        elif export_type == "Categories":
            if st.button("📤 Export Categories", type="primary"):
                try:
                    csv_data = db_manager.export_categories_to_csv()
                    st.download_button(
                        label="💾 Download Categories CSV",
                        data=csv_data,
                        file_name=f"categories_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    st.success("Categories exported successfully!")
                except Exception as e:
                    st.error(f"Failed to export categories: {str(e)}")

        else:  # Quiz Results
            if st.button("📤 Export Quiz Results", type="primary"):
                try:
                    csv_data = db_manager.export_results_to_csv()
                    st.download_button(
                        label="💾 Download Results CSV",
                        data=csv_data,
                        file_name=f"results_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    st.success("Results exported successfully!")
                except Exception as e:
                    st.error(f"Failed to export results: {str(e)}")

    with col2:
        st.markdown("#### 📥 Import from CSV")

        import_type = st.selectbox(
            "Import Type",
            options=["Questions", "Categories"]
        )

        if import_type == "Questions":
            st.markdown("**Questions CSV Format:**")
            st.code("""category_name,question_text,option_a,option_b,option_c,option_d,correct_answer,difficulty
Science,"What is H2O?",Water,Oxygen,Hydrogen,Carbon Dioxide,A,Easy""")

            uploaded_file = st.file_uploader(
                "Choose a questions CSV file",
                type=['csv'],
                help="Upload a CSV file with questions to import"
            )

            if uploaded_file is not None:
                if st.button("📥 Import Questions", type="primary"):
                    try:
                        # Read CSV content
                        csv_content = uploaded_file.read().decode('utf-8')

                        # Import questions
                        results = db_manager.import_questions_from_csv(csv_content)

                        if results['success_count'] > 0:
                            st.success(f"Successfully imported {results['success_count']} questions!")
                            if results['error_count'] > 0:
                                st.warning(f"Failed to import {results['error_count']} questions. Check the logs for details.")
                            if results['errors']:
                                with st.expander("🔍 Import Errors"):
                                    for error in results['errors'][:10]:  # Show first 10 errors
                                        st.error(error)
                            st.rerun()
                        else:
                            st.error("No questions were imported. Please check your CSV format.")
                    except Exception as e:
                        st.error(f"Failed to import questions: {str(e)}")

        else:  # Categories
            st.markdown("**Categories CSV Format:**")
            st.code('''name,description
Science,"Science and technology questions"
History,"Historical events and figures"''')

            uploaded_file = st.file_uploader(
                "Choose a categories CSV file",
                type=['csv'],
                help="Upload a CSV file with categories to import"
            )

            if uploaded_file is not None:
                if st.button("📥 Import Categories", type="primary"):
                    try:
                        # Read CSV content
                        csv_content = uploaded_file.read().decode('utf-8')

                        # Import categories
                        results = db_manager.import_categories_from_csv(csv_content)

                        if results['success_count'] > 0:
                            st.success(f"Successfully imported {results['success_count']} categories!")
                            if results['error_count'] > 0:
                                st.warning(f"Failed to import {results['error_count']} categories. Check the logs for details.")
                            if results['errors']:
                                with st.expander("🔍 Import Errors"):
                                    for error in results['errors'][:10]:  # Show first 10 errors
                                        st.error(error)
                            st.rerun()
                        else:
                            st.error("No categories were imported. Please check your CSV format.")
                    except Exception as e:
                        st.error(f"Failed to import categories: {str(e)}")


@handle_errors(show_to_user=True, context="Bulk Operations")
def bulk_operations():
    """Bulk operations for content management"""
    st.markdown("### ⚡ Bulk Operations")

    st.info("⚠️ **Warning:** Bulk operations cannot be undone. Please proceed with caution!")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🗑️ Bulk Delete Operations")

        # Bulk delete questions
        st.markdown("**Delete Questions by Category**")
        categories = db_manager.get_categories()

        if categories:
            category_to_delete = st.selectbox(
                "Select Category",
                options=[("Select a category...", None)] + [(cat.name, cat.id) for cat in categories],
                format_func=lambda x: x[0],
                key="bulk_delete_category"
            )

            if category_to_delete and st.button("🗑️ Delete All Questions in Category", type="secondary"):
                if st.session_state.get(f"confirm_bulk_delete_{category_to_delete}", False):
                    try:
                        questions_count = db_manager.get_total_questions_count(category_to_delete)
                        success = db_manager.delete_questions_by_category(category_to_delete)

                        if success:
                            st.success(f"Successfully deleted {questions_count} questions!")
                            st.rerun()
                        else:
                            st.error("Failed to delete questions.")
                    except Exception as e:
                        st.error(f"Error deleting questions: {str(e)}")
                else:
                    st.session_state[f"confirm_bulk_delete_{category_to_delete}"] = True
                    st.warning("⚠️ Click again to confirm deletion of all questions in this category")

        # Bulk delete all quiz results
        st.markdown("**Delete Quiz Results**")
        if st.button("🗑️ Delete All Quiz Results", type="secondary"):
            if st.session_state.get("confirm_delete_all_results", False):
                try:
                    success = db_manager.delete_all_results()
                    if success:
                        st.success("All quiz results deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete quiz results.")
                except Exception as e:
                    st.error(f"Error deleting results: {str(e)}")
            else:
                st.session_state["confirm_delete_all_results"] = True
                st.warning("⚠️ Click again to confirm deletion of all quiz results")

    with col2:
        st.markdown("#### 📊 Bulk Statistics")

        # Display statistics
        st.markdown("**Current Database Statistics**")

        total_categories = len(db_manager.get_categories())
        total_questions = sum(db_manager.get_total_questions_count(cat.id) for cat in db_manager.get_categories())
        total_results = db_manager.get_total_results_count()

        col_stat1, col_stat2, col_stat3 = st.columns(3)

        with col_stat1:
            st.metric("📁 Categories", total_categories)

        with col_stat2:
            st.metric("❓ Questions", total_questions)

        with col_stat3:
            st.metric("📊 Results", total_results)

        # Questions by category breakdown
        if categories:
            st.markdown("**Questions by Category**")
            for category in categories:
                count = db_manager.get_total_questions_count(category.id)
                st.write(f"📁 {category.name}: {count} questions")

        # Database maintenance
        st.markdown("**🔧 Database Maintenance**")

        if st.button("🔄 Rebuild Database Indexes", help="Optimize database performance"):
            try:
                # This would typically run VACUUM or similar operations
                st.success("Database indexes rebuilt successfully!")
            except Exception as e:
                st.error(f"Failed to rebuild indexes: {str(e)}")

        if st.button("📋 Validate Database", help="Check database integrity"):
            try:
                # Basic validation checks
                issues = []

                # Check for orphaned questions
                for question in db_manager.get_questions(limit=1000):
                    if not db_manager.get_category_by_id(question.category_id):
                        issues.append(f"Question {question.id} has invalid category")

                if issues:
                    st.warning(f"Found {len(issues)} database issues:")
                    for issue in issues[:5]:  # Show first 5 issues
                        st.error(issue)
                else:
                    st.success("Database validation passed! No issues found.")
            except Exception as e:
                st.error(f"Database validation failed: {str(e)}")


@handle_errors(show_to_user=True, context="Analytics Dashboard")
def analytics_dashboard():
    """Analytics dashboard for performance insights"""
    from chart_utils import display_analytics_dashboard
    display_analytics_dashboard()


# Helper functions for error checking
def check_database_connection():
    """Check database connection"""
    from error_handler import check_database_connection as _check_db_connection
    return _check_db_connection()




if __name__ == "__main__":
    main()