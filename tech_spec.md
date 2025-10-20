## ⚙️ TECHNICAL SPECIFICATION

# AI Smart Quiz App (Single-file / Single-app Streamlit implementation)

**Summary:** The complete technical specification for implementing the AI Smart Quiz App as a standalone Streamlit application (`app.py`) with supporting modules (`utils/*`). It uses Python, SQLite, Pydantic, a LangChain/LangGraph-style pipeline for Text-to-Speech (TTS), and OpenAI TTS/Whisper-like functionality for reading questions. This covers folder structure, DB details, data models, internal APIs (functions), key code examples, Streamlit state management, and dashboard query examples.

-----

## 1 — Project Structure (Recommended)

| File / Folder | Purpose | Development Note |
| :--- | :--- | :--- |
| `ai_smart_quiz_app/` | Project root. | Maintain this structure for modularity, easier maintenance, and testing. |
| ├── **`app.py`** | **Streamlit Entrypoint.** All UI rendering, orchestration, and core application logic. | This is the file developers will run (`streamlit run app.py`). |
| ├── `requirements.txt` | Project dependencies list. | Used for setting up the virtual environment (`pip install -r requirements.txt`). |
| ├── `database/quiz.db` | The local **SQLite database file**. | Must be created automatically if it doesn't exist upon app startup. |
| ├── `utils/` | Contains supporting Python modules. | Keeps `app.py` clean. Developers should focus on completing functions here first. |
| ├── `utils/db_manager.py` | All SQLite operations (CRUD) and statistics queries. | The primary interface for data persistence. **Crucial for both User and Admin modes.** |
| ├── `utils/models.py` | **Pydantic models** for data validation. | Ensures data integrity for questions and results before DB insertion. |
| ├── `utils/ai_speech.py` | Wrapper for the Text-to-Speech (TTS) API (e.g., OpenAI TTS). | Handles the secure API call and audio stream playback via Streamlit. |
| └── `utils/chart_utils.py` | Functions to generate Plotly/Streamlit charts for the Dashboard. | Isolates visualization logic. |

-----

## 2 — Requirements (Example `requirements.txt`)

```python
streamlit>=1.20.0     # Core UI framework
pydantic>=1.10        # Data validation
langchain>=0.0        # Optional: For AI integration pipeline/abstraction
openai>=0.27          # For Text-to-Speech API access
plotly>=5.0           # For interactive dashboard charts
pandas>=2.0           # Useful for data handling and CSV operations
python-dotenv>=1.0    # For local environment variable management (API key)
# Optional:
# SQLAlchemy>=1.4     # If preferring an ORM over raw sqlite3
# openpyxl>=3.0       # For Excel export functionality
```

**Dev Note:** Ensure the correct version of the OpenAI library is used, especially for accessing the TTS endpoint (if using the direct API instead of a LangChain wrapper).

-----

## 3 — Database Schema (SQLite)

**Goal:** Establish the persistent structure for all content and results. This SQL script must run once at startup if the tables do not exist (`init_db` function).

```sql
CREATE TABLE IF NOT EXISTS categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE, -- Name must be unique for easy reference
  description TEXT
);

CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category_id INTEGER NOT NULL,
  question_text TEXT NOT NULL,
  option_a TEXT NOT NULL,
  option_b TEXT NOT NULL,
  option_c TEXT NOT NULL,
  option_d TEXT NOT NULL,
  correct_answer TEXT NOT NULL CHECK (correct_answer IN ('A','B','C','D')), -- Ensures answer is always valid
  FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE -- Delete category automatically deletes its questions
);

CREATE TABLE IF NOT EXISTS results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  age INTEGER,
  category_id INTEGER NOT NULL,
  score INTEGER NOT NULL,
  correct_count INTEGER NOT NULL,
  wrong_count INTEGER NOT NULL,
  date_taken TEXT NOT NULL, -- Stored as ISO format text (e.g., 'YYYY-MM-DD HH:MM:SS')
  FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

**Dev Note:** Use `sqlite3.connect(..., check_same_thread=False)` if you encounter multi-threading issues within the Streamlit environment, although Streamlit is generally single-threaded per session.

-----

## 4 — Models (Pydantic) — `utils/models.py`

**Goal:** Provide clear, validated schemas for data transfer and storage, particularly for forms in the Admin Panel.

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class Category(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1)
    description: Optional[str] = ""

class Question(BaseModel):
    id: Optional[int] = None
    category_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: Literal["A", "B", "C", "D"] # Strict validation

class Result(BaseModel):
    id: Optional[int] = None
    name: str
    age: Optional[int]
    category_id: int
    score: int
    correct_count: int
    wrong_count: int
    date_taken: datetime # Used for capturing the completion time
```

**Dev Note:** The `Literal["A", "B", "C", "D"]` in `Question` is crucial for preventing invalid correct answers from being inserted. Use Pydantic's `model_dump()` or `dict()` method to convert the validated object into a dictionary before passing it to the SQLite `db_manager`.

-----

## 5 — DB Layer / Internal API — `utils/db_manager.py`

**Goal:** Centralize all database communication. This layer should be the only code in the app directly interacting with `sqlite3`.

| Function Group | Key Functions | Dev Note |
| :--- | :--- | :--- |
| **Setup** | `get_conn(db_path)`, `init_db(conn)` | `get_conn` should use `sqlite3.Row` for dictionary-like access to results. |
| **Category CRUD** | `create_category`, `list_categories`, etc. | Use Pydantic models for input validation on `create`/`update`. |
| **Question CRUD** | `create_question`, `list_questions_by_category`, etc. | `list_questions_by_category` is essential for starting a quiz session. |
| **Results & Stats** | `insert_result`, `stats_avg_score_per_category` | **Focus on the aggregation queries (Section 11)** for the dashboard. |

**Example `create_question` implementation:**

```python
import sqlite3
# ... (imports)

def create_question(conn, q: Question): # Takes a validated Pydantic Question object
    cur = conn.cursor()
    # Use the Pydantic model's dictionary representation
    data = q.model_dump() 
    cur.execute("""
      INSERT INTO questions (category_id, question_text, option_a, option_b, option_c, option_d, correct_answer)
      VALUES (:category_id, :question_text, :option_a, :option_b, :option_c, :option_d, :correct_answer)
    """, data)
    conn.commit()
    return cur.lastrowid
```

-----

## 6 — AI Speech (OpenAI TTS) — `utils/ai_speech.py`

**Crucial Clarification:** The original PRD mentioned **Whisper**, which is an **STT** (Speech-to-Text) model. For reading text aloud (🔊 icon), we need a **TTS** (Text-to-Speech) model, like the one provided by the **OpenAI TTS API** (or a similar service like Google TTS).

**Goal:** Stream text to the TTS API, receive audio data, and play it directly in Streamlit.

```python
import io
import streamlit as st
import openai
from typing import Optional

# API Key should be managed via Streamlit secrets for security
# openai.api_key = st.secrets["OPENAI_API_KEY"] 

def text_to_speech_stream(text: str, model: str = "tts-1", voice: str = "alloy"):
    """Calls the OpenAI TTS API and returns the audio bytes."""
    client = openai.OpenAI() # Use the modern OpenAI client
    
    try:
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )
        # Streamlit requires bytes; the response stream can be read into a buffer
        audio_bytes = io.BytesIO(response.content).read()
        return audio_bytes
    except Exception as e:
        st.error(f"TTS Error: Could not generate audio. Check API key/internet. {e}")
        return None

def play_text(text: str):
    """Generates audio and plays it in the Streamlit UI."""
    audio_bytes = text_to_speech_stream(text)
    if audio_bytes:
        # st.audio handles playback from bytes buffer
        st.audio(audio_bytes, format="audio/mp3", autoplay=True) 

# LangChain/LangGraph Integration:
# Implement a simple wrapper function/node that calls play_text(text) when triggered.
```

**Dev Note:** The `autoplay=True` in `st.audio` ensures the sound plays immediately upon the button click, providing a seamless user experience. The TTS model must be configured correctly (e.g., `tts-1` or `tts-1-hd`).

-----

## 7 — Streamlit App Flow (The `app.py` Orchestrator)

**Goal:** Use **`st.session_state`** to manage the application's mutable state (user info, current quiz, answers).

| Component / Function | State Management / Logic | Dev Note |
| :--- | :--- | :--- |
| **`main()`** | Initializes DB connection and table structure. Controls the main navigation (`st.sidebar.radio`). | DB connection (`conn`) should be accessible by all major functions. |
| **`user_mode()`** | Handles Name/Age input and Category selection. | Saves user data to `st.session_state.user`. |
| **`start_quiz()`** | Fetches questions from DB, resets quiz state. | Sets `st.session_state.questions`, `st.session_state.q_index = 0`, `st.session_state.answers = []`. |
| **`render_question()`**| Renders current question. Handles the **Next** button. | `Next` button logic: 1) Appends current choice to `st.session_state.answers`. 2) Increments `st.session_state.q_index`. 3) Calls `compute_and_save_result` if the quiz is over. 4) Calls `st.experimental_rerun()` to refresh the UI. |
| **`compute_and_save_result()`** | Scoring and DB insertion. | Calculates score, creates a Pydantic `Result` object, and calls `db_manager.insert_result`. |

**Dev Note on Rerunning:** Using `st.experimental_rerun()` is essential for immediate state transitions (e.g., moving from the User Form to the Quiz Page, or moving from Question $N$ to Question $N+1$).

-----

## 10 — Scoring & Saving Result (Logic)

**Goal:** Accurately calculate the final score and save the detailed result to the database with a timestamp.

```python
# Part of the compute_and_save_result function
def compute_score(questions, answers):
    total = len(questions)
    correct = sum(1 for q, a in zip(questions, answers) if a == q['correct_answer'])
    wrong = total - correct
    # Scaling to 0-100% based on the number of correct answers
    score = int(round((correct / total) * 100))
    return score, correct, wrong

def save_result(conn, user_data, category_id, score, correct, wrong):
    # Create Pydantic model for validation before insertion
    result_data = Result(
        name=user_data['name'],
        age=user_data['age'],
        category_id=category_id,
        score=score,
        correct_count=correct,
        wrong_count=wrong,
        date_taken=datetime.utcnow() # Use UTC timestamp
    )
    db_manager.insert_result(conn, result_data)
```

-----

## 11 — Dashboard Details & Queries

**Goal:** Use aggregated SQL queries to provide data for the interactive charts.

| Widget | Data Source (SQL Query Example) | Chart Type (Plotly) |
| :--- | :--- | :--- |
| **Avg Score per Category** | `SELECT c.name, AVG(r.score) AS avg_score, COUNT(r.id) AS attempts FROM categories c LEFT JOIN results r ON c.id = r.category_id GROUP BY c.name;` | Bar Chart (`plotly.express.bar`) |
| **Attempts per Category** | `SELECT c.name, COUNT(r.id) AS attempts FROM categories c JOIN results r ON c.id = r.category_id GROUP BY c.name;` | Pie Chart (`plotly.express.pie`) |
| **Score Trend** | `SELECT date_taken, score FROM results WHERE name = ? ORDER BY date_taken;` | Line Chart (`plotly.express.line`) |

**Dev Note:** These queries should be implemented in `db_manager.py` and the returned data should be converted into a **Pandas DataFrame** before being passed to the `chart_utils.py` functions for plotting.

-----

## 12 & 13 — Admin Panel & Validation

**Goal:** Provide full content management with robust Pydantic validation.

| Feature | Implementation Detail |
| :--- | :--- |
| **Category/Question CRUD** | Use Streamlit forms and `st.expander` to manage the input/display. Upon form submission, validate the data using the Pydantic models (e.g., `Question(**form_data)`). |
| **CSV Import** | Use `pandas.read_csv()` to load the file. **Iterate through each row** and attempt to create a Pydantic `Question` object. If validation fails (e.g., missing field, invalid `correct_answer`), skip the row and log an error to `st.error`. |
| **Error Handling** | Wrap DB operations (especially `create` or `update` with unique constraints) in `try...except sqlite3.IntegrityError` and display friendly messages (`st.success`, `st.error`). |

-----

## 15 & 16 — Deployment & Security

| Area | Requirement | Dev Note |
| :--- | :--- | :--- |
| **API Key Security** | **DO NOT hardcode the `OPENAI_API_KEY`.** Use Streamlit Secrets (for Streamlit Cloud deployment) or local environment variables (`.env` file with `python-dotenv`) for local development. |
| **Deployment** | Since it's a single Streamlit app, deploy using `streamlit run app.py` on any compatible platform (Streamlit Cloud, Heroku, etc.). |
| **External Communication** | Clearly inform users that question text is sent to an external API (OpenAI TTS) to generate audio. |

-----

### Next Steps I Can Deliver Now

I can provide the following to jumpstart your development:

1.  A **full, modular, executable `app.py` skeleton** that implements the navigation, session state logic, and calls to the `utils` functions (with mock functions for the DB/TTS), ready for you to fill in the actual DB/TTS implementation.
2.  A **sample CSV file format** that precisely matches the Pydantic `Question` model, ready for immediate testing of the import feature.

Which would you prefer to get started?