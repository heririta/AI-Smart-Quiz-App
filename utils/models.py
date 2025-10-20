"""
Pydantic models for AI Smart Quiz App
Data validation and serialization for all entities
"""

from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, List
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    """Quiz difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuizStatus(str, Enum):
    """Quiz session status"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


# ==================== CATEGORY MODELS ====================

class CategoryBase(BaseModel):
    """Base category model"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field("", max_length=500)


class CategoryCreate(CategoryBase):
    """Category creation model"""
    pass


class CategoryUpdate(BaseModel):
    """Category update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class Category(CategoryBase):
    """Complete category model"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== QUESTION MODELS ====================

class QuestionBase(BaseModel):
    """Base question model"""
    category_id: int
    question_text: str = Field(..., min_length=1, max_length=1000)
    option_a: str = Field(..., min_length=1, max_length=500)
    option_b: str = Field(..., min_length=1, max_length=500)
    option_c: str = Field(..., min_length=1, max_length=500)
    option_d: str = Field(..., min_length=1, max_length=500)
    correct_answer: Literal["A", "B", "C", "D"]
    difficulty: Optional[DifficultyLevel] = None
    combined_content: Optional[str] = None

    @validator('option_a', 'option_b', 'option_c', 'option_d')
    def validate_options(cls, v):
        if not v.strip():
            raise ValueError('Option cannot be empty')
        return v.strip()

    @validator('correct_answer')
    def validate_correct_answer(cls, v):
        return v.upper()

    @validator('question_text')
    def validate_question_text(cls, v):
        if not v.strip():
            raise ValueError('Question text cannot be empty')
        return v.strip()


class QuestionCreate(QuestionBase):
    """Question creation model"""
    pass


class QuestionUpdate(BaseModel):
    """Question update model"""
    question_text: Optional[str] = Field(None, min_length=1, max_length=1000)
    option_a: Optional[str] = Field(None, min_length=1, max_length=500)
    option_b: Optional[str] = Field(None, min_length=1, max_length=500)
    option_c: Optional[str] = Field(None, min_length=1, max_length=500)
    option_d: Optional[str] = Field(None, min_length=1, max_length=500)
    correct_answer: Optional[Literal["A", "B", "C", "D"]] = None
    difficulty: Optional[DifficultyLevel] = None


class Question(QuestionBase):
    """Complete question model"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== USER MODELS ====================

class UserBase(BaseModel):
    """Base user model"""
    name: str = Field(..., min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=1, le=120)

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class UserCreate(UserBase):
    """User creation model"""
    pass


class User(UserBase):
    """User model with session info"""
    session_id: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== QUIZ SESSION MODELS ====================

class QuizSessionBase(BaseModel):
    """Base quiz session model"""
    user_name: str
    category_id: int
    current_question_index: int = 0
    total_questions: int
    answers: List[str] = []
    status: QuizStatus = QuizStatus.IN_PROGRESS

    @validator('answers')
    def validate_answers(cls, v):
        """Ensure all answers are valid"""
        valid_answers = {"A", "B", "C", "D"}
        for answer in v:
            if answer not in valid_answers:
                raise ValueError(f'Invalid answer: {answer}')
        return v


class QuizSessionCreate(QuizSessionBase):
    """Quiz session creation model"""
    questions: List[Question] = []


class QuizSession(QuizSessionBase):
    """Complete quiz session model"""
    session_id: str
    started_at: datetime
    questions: List[Question] = []

    class Config:
        from_attributes = True

    @property
    def current_question(self) -> Optional[Question]:
        """Get current question"""
        if 0 <= self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None

    @property
    def is_completed(self) -> bool:
        """Check if quiz is completed"""
        return self.current_question_index >= self.total_questions

    @property
    def progress_percentage(self) -> float:
        """Get progress as percentage"""
        if self.total_questions == 0:
            return 0.0
        return (self.current_question_index / self.total_questions) * 100


# ==================== RESULT MODELS ====================

class ResultBase(BaseModel):
    """Base result model"""
    user_name: str
    age: Optional[int] = Field(None, ge=1, le=120)
    category_id: int
    score: int = Field(..., ge=0, le=100)
    correct_count: int = Field(..., ge=0)
    wrong_count: int = Field(..., ge=0)
    total_questions: int = Field(..., gt=0)
    time_taken: Optional[int] = Field(None, ge=0)

    @validator('score')
    def validate_score_range(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Score must be between 0 and 100')
        return v

    @validator('total_questions')
    def validate_question_count(cls, v, values):
        if 'correct_count' in values and 'wrong_count' in values:
            if values['correct_count'] + values['wrong_count'] != v:
                raise ValueError('Correct + wrong count must equal total questions')
        return v


class ResultCreate(ResultBase):
    """Result creation model"""
    pass


class Result(ResultBase):
    """Complete result model"""
    id: int
    completed_at: datetime

    class Config:
        from_attributes = True


# ==================== ANALYTICS MODELS ====================

class CategoryAnalytics(BaseModel):
    """Category performance analytics"""
    category_id: Optional[int]
    category_name: str
    total_attempts: int
    average_score: float
    best_score: int
    worst_score: int
    recent_scores: List[int]
    score_distribution: dict


class PerformanceTrend(BaseModel):
    """User performance trend over time"""
    user_name: str
    period_days: int
    daily_scores: List[dict]
    trend_direction: Literal["improving", "declining", "stable"]
    average_score: float
    total_quizzes: int


# ==================== TTS MODELS ====================

class SpeechRequest(BaseModel):
    """Text-to-speech request model"""
    text: str = Field(..., min_length=1, max_length=1000)
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "alloy"

    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()


# ==================== CSV IMPORT MODELS ====================

class CSVImportResult(BaseModel):
    """CSV import result model"""
    total_rows: int
    successful_imports: int
    failed_imports: int
    errors: List[str]
    questions_created: List[Question]


# ==================== RESPONSE MODELS ====================

class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool
    message: str
    data: Optional[dict] = None
    errors: Optional[List[str]] = None