# Quick Start Guide: AI Smart Quiz App

**Date**: 2025-10-19
**Purpose**: Get the AI Smart Quiz App running in minutes

## Prerequisites

### System Requirements
- Python 3.8 or higher
- 2GB+ available RAM
- 100MB+ disk space
- Internet connection for TTS features

### Required Accounts
- OpenAI account with API key (for text-to-speech)

## Installation

### 1. Clone or Create Project Structure
```bash
# If using git
git clone <repository-url>
cd ai-smart-quiz-app

# Or create directory structure manually
mkdir ai-smart-quiz-app
cd ai-smart-quiz-app
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
Create `.env` file in project root:
```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Custom Configuration
TTS_DEFAULT_VOICE=alloy
TTS_MODEL=tts-1
MAX_TTS_REQUESTS_PER_MINUTE=50
```

### 5. Initialize Database
The app will automatically create the SQLite database on first run:
```bash
# This will be created automatically as database/quiz.db
# No manual setup required
```

## Running the Application

### Start the App
```bash
streamlit run app.py
```

The app will open in your browser at: `http://localhost:8501`

### First-Time Setup

1. **Database Initialization**: The app automatically creates `database/quiz.db` with required tables
2. **Sample Data**: Import sample questions using the Admin Panel (see below)
3. **API Test**: Test TTS functionality by clicking speaker icons

## Basic Usage

### Taking a Quiz
1. **Enter User Info**: Input your name and optional age
2. **Select Category**: Choose from available quiz categories
3. **Start Quiz**: Click "Start Quiz" to begin
4. **Answer Questions**: Select answers and click "Next"
5. **View Results**: See your score and performance analytics

### Using Voice Features
1. **Question Audio**: Click 🔊 next to questions to hear them read aloud
2. **Option Audio**: Click 🔊 next to each answer option
3. **No Storage**: Audio plays immediately without saving files

### Managing Content (Admin)
1. **Access Admin Panel**: Click "Admin Panel" tab
2. **Add Categories**: Create new question categories
3. **Add Questions**: Create questions with four options and correct answers
4. **Import CSV**: Bulk import questions from CSV files

## Sample Data

### CSV Import Format
Create a CSV file with these columns:
```csv
question_text,option_a,option_b,option_c,option_d,correct_answer,difficulty
What is 2+2?,3,4,5,6,B,easy
What is the capital of France?,London,Berlin,Paris,Madrid,C,medium
```

### Sample Categories
- General Knowledge
- Mathematics
- Science
- Geography
- History

### Sample Questions
```python
# Example: Mathematics
question_text = "What is 15 + 27?"
option_a = "40"
option_b = "42"
option_c = "44"
option_d = "46"
correct_answer = "B"
difficulty = "medium"
```

## Configuration

### TTS Settings
```python
# In app.py or .env
TTS_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
TTS_MODEL = "tts-1"  # or "tts-1-hd" for higher quality
MAX_AUDIO_LENGTH = 1000  # characters
```

### Database Settings
```python
# Database location
DATABASE_PATH = "database/quiz.db"

# Connection settings
DB_TIMEOUT = 30  # seconds
```

### Performance Settings
```python
# Quiz settings
DEFAULT_QUESTIONS_PER_QUIZ = 10
MAX_QUESTIONS_PER_QUIZ = 50
SESSION_TIMEOUT = 3600  # seconds (1 hour)
```

## Troubleshooting

### Common Issues

#### TTS Not Working
```bash
# Check API key
echo $OPENAI_API_KEY

# Test OpenAI connection
python -c "from openai import OpenAI; client = OpenAI(); print('Connection OK')"
```

#### Database Issues
```bash
# Check database file exists
ls -la database/quiz.db

# Recreate database (will lose data)
rm database/quiz.db
streamlit run app.py  # Will recreate automatically
```

#### Performance Issues
```bash
# Check memory usage
python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"

# Clear Streamlit cache
rm -rf .streamlit/cache/
```

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "OpenAI API key not found" | Missing API key | Set OPENAI_API_KEY in .env |
| "Rate limit exceeded" | Too many TTS requests | Wait and retry (50/min limit) |
| "Database locked" | Concurrent access | Restart app |
| "No questions available" | Empty category | Add questions via Admin Panel |

## Development

### Project Structure
```
ai-smart-quiz-app/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── database/
│   └── quiz.db           # SQLite database (auto-created)
├── utils/
│   ├── db_manager.py     # Database operations
│   ├── models.py         # Pydantic models
│   ├── ai_speech.py      # TTS functionality
│   └── chart_utils.py    # Chart generation
└── assets/
    └── sample_data/      # Sample questions CSV
```

### Adding New Features
1. **New Question Types**: Extend `models.py` and database schema
2. **Additional Analytics**: Add new chart types in `chart_utils.py`
3. **Custom TTS Voices**: Modify `ai_speech.py` voice options
4. **UI Enhancements**: Update `app.py` with new Streamlit components

### Testing
```bash
# Run basic functionality test
python -m pytest tests/ -v

# Test TTS specifically
python -c "from utils.ai_speech import test_tts; test_tts()"

# Test database operations
python -c "from utils.db_manager import test_db; test_db()"
```

## Production Deployment

### Streamlit Cloud
1. **Push to GitHub**: Commit code to GitHub repository
2. **Connect to Streamlit Cloud**: Link repository
3. **Set Secrets**: Add OPENAI_API_KEY as secret
4. **Deploy**: Automatic deployment from main branch

### Local Production
```bash
# Install production dependencies
pip install -r requirements.txt

# Set production environment
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run with production settings
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

## Support

### Documentation
- **API Reference**: `specs/001-ai-quiz-app/contracts/api.md`
- **Data Model**: `specs/001-ai-quiz-app/data-model.md`
- **Technical Research**: `specs/001-ai-quiz-app/research.md`

### Resources
- **Streamlit Docs**: https://docs.streamlit.io/
- **OpenAI API**: https://platform.openai.com/docs/
- **Pydantic Docs**: https://pydantic-docs.helpmanual.io/
- **SQLite Docs**: https://sqlite.org/docs.html

### Getting Help
1. Check this guide first
2. Review error messages in app logs
3. Check OpenAI API status
4. Consult Streamlit community forums