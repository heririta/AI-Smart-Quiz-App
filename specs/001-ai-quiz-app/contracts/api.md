# API Contracts: AI Smart Quiz App

**Date**: 2025-10-19
**Purpose**: Define internal API contracts for data operations

## Category Management

### Create Category

**Endpoint**: `create_category(data: CategoryCreate) -> Category`

**Request**:
```python
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field("", max_length=500)
```

**Response**:
```python
class Category(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
```

**Validation**: Name must be unique, non-empty

### List Categories

**Endpoint**: `list_categories() -> List[Category]`

**Response**: Array of Category objects

### Update Category

**Endpoint**: `update_category(id: int, data: CategoryUpdate) -> Category`

**Request**:
```python
class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
```

**Response**: Updated Category object

### Delete Category

**Endpoint**: `delete_category(id: int) -> bool`

**Response**: True if deleted successfully

**Constraint**: Cascades delete associated questions

## Question Management

### Create Question

**Endpoint**: `create_question(data: QuestionCreate) -> Question`

**Request**:
```python
class QuestionCreate(BaseModel):
    category_id: int
    question_text: str = Field(..., min_length=1, max_length=1000)
    option_a: str = Field(..., min_length=1, max_length=500)
    option_b: str = Field(..., min_length=1, max_length=500)
    option_c: str = Field(..., min_length=1, max_length=500)
    option_d: str = Field(..., min_length=1, max_length=500)
    correct_answer: Literal["A", "B", "C", "D"]
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None
```

**Response**:
```python
class Question(BaseModel):
    id: int
    category_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    difficulty: Optional[str]
    created_at: datetime
    updated_at: datetime
```

**Validation**: All options unique, valid correct answer, category exists

### Get Questions by Category

**Endpoint**: `get_questions_by_category(category_id: int) -> List[Question]`

**Response**: Array of Question objects for specified category

### Update Question

**Endpoint**: `update_question(id: int, data: QuestionUpdate) -> Question`

**Request**:
```python
class QuestionUpdate(BaseModel):
    question_text: Optional[str] = Field(None, min_length=1, max_length=1000)
    option_a: Optional[str] = Field(None, min_length=1, max_length=500)
    option_b: Optional[str] = Field(None, min_length=1, max_length=500)
    option_c: Optional[str] = Field(None, min_length=1, max_length=500)
    option_d: Optional[str] = Field(None, min_length=1, max_length=500)
    correct_answer: Optional[Literal["A", "B", "C", "D"]] = None
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None
```

**Response**: Updated Question object

### Delete Question

**Endpoint**: `delete_question(id: int) -> bool`

**Response**: True if deleted successfully

## Quiz Session Management

### Start Quiz Session

**Endpoint**: `start_quiz_session(user_name: str, category_id: int) -> QuizSession`

**Response**:
```python
class QuizSession(BaseModel):
    session_id: str
    user_name: str
    category_id: int
    started_at: datetime
    current_question_index: int
    total_questions: int
    questions: List[Question]
    status: Literal["in_progress", "completed", "abandoned"]
```

### Submit Answer

**Endpoint**: `submit_answer(session_id: str, answer: str) -> QuizSession`

**Request**:
```python
class AnswerSubmit(BaseModel):
    session_id: str
    answer: Literal["A", "B", "C", "D"]
```

**Response**: Updated QuizSession with next question or completion status

### Complete Quiz

**Endpoint**: `complete_quiz(session_id: str) -> Result`

**Response**:
```python
class Result(BaseModel):
    id: int
    user_name: str
    age: Optional[int]
    category_id: int
    score: int
    correct_count: int
    wrong_count: int
    total_questions: int
    time_taken: Optional[int]
    completed_at: datetime
```

## Results & Analytics

### Save Result

**Endpoint**: `save_result(data: ResultCreate) -> Result`

**Request**:
```python
class ResultCreate(BaseModel):
    user_name: str
    age: Optional[int]
    category_id: int
    score: int = Field(..., ge=0, le=100)
    correct_count: int = Field(..., ge=0)
    wrong_count: int = Field(..., ge=0)
    total_questions: int = Field(..., gt=0)
    time_taken: Optional[int] = Field(None, ge=0)
```

**Validation**: correct_count + wrong_count == total_questions

### Get Results by User

**Endpoint**: `get_user_results(user_name: str) -> List[Result]`

**Response**: Array of Result objects for specified user

### Get Category Analytics

**Endpoint**: `get_category_analytics(category_id: Optional[int] = None) -> CategoryAnalytics`

**Response**:
```python
class CategoryAnalytics(BaseModel):
    category_id: Optional[int]
    category_name: str
    total_attempts: int
    average_score: float
    best_score: int
    worst_score: int
    recent_scores: List[int]
    score_distribution: Dict[str, int]
```

### Get Performance Trends

**Endpoint**: `get_performance_trends(user_name: str, days: int = 30) -> PerformanceTrend`

**Response**:
```python
class PerformanceTrend(BaseModel):
    user_name: str
    period_days: int
    daily_scores: List[Dict[str, Any]]
    trend_direction: Literal["improving", "declining", "stable"]
    average_score: float
    total_quizzes: int
```

## CSV Import/Export

### Import Questions from CSV

**Endpoint**: `import_questions_from_csv(file_data: bytes, category_id: int) -> ImportResult`

**Request**: CSV file data with columns:
- question_text (required)
- option_a (required)
- option_b (required)
- option_c (required)
- option_d (required)
- correct_answer (required, A/B/C/D)
- difficulty (optional, easy/medium/hard)

**Response**:
```python
class ImportResult(BaseModel):
    total_rows: int
    successful_imports: int
    failed_imports: int
    errors: List[str]
    questions_created: List[Question]
```

### Export Questions to CSV

**Endpoint**: `export_questions_to_csv(category_id: Optional[int] = None) -> bytes`

**Response**: CSV file data for download

## Text-to-Speech

### Generate Speech

**Endpoint**: `generate_speech(text: str, voice: str = "alloy") -> Optional[bytes]`

**Request**:
```python
class SpeechRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "alloy"
```

**Response**: Audio data as bytes or None if failed

**Validation**: Text length limits, rate limiting

## Error Responses

All endpoints return standardized error responses:

```python
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
```

### Common Error Types

- **ValidationError**: Invalid input data
- **NotFoundError**: Resource not found
- **DatabaseError**: Database operation failed
- **RateLimitError**: API rate limit exceeded
- **ExternalServiceError**: TTS API failure
- **ImportError**: CSV import validation failed

## Response Format Standards

### Success Response
```json
{
    "success": true,
    "data": <response_data>,
    "message": "Operation completed successfully"
}
```

### Error Response
```json
{
    "success": false,
    "error": {
        "type": "ValidationError",
        "message": "Invalid input data",
        "details": {...}
    },
    "timestamp": "2025-10-19T10:30:00Z"
}
```

## Rate Limiting

### TTS Generation
- 50 requests per minute per user session
- Automatic retry with exponential backoff
- Graceful degradation when limits exceeded

### File Operations
- CSV import: 1000 rows per file maximum
- Export requests: 10 per minute per user
- File size limits: 10MB maximum