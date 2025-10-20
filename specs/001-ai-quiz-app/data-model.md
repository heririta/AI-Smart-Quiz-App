# Data Model: AI Smart Quiz App

**Date**: 2025-10-19
**Purpose**: Define data entities, relationships, and validation rules

## Core Entities

### User

Represents quiz participants with basic demographic information.

**Fields**:
- `name` (string, required): User's display name
- `age` (integer, optional): User's age for analytics
- `session_id` (string, auto-generated): Unique session identifier

**Validation Rules**:
- Name must be non-empty and <= 100 characters
- Age must be between 1 and 120 if provided
- Session ID auto-generated using UUID

### Category

Defines question groups for organization and filtering.

**Fields**:
- `id` (integer, primary key): Unique category identifier
- `name` (string, required): Category display name
- `description` (text, optional): Category description
- `created_at` (datetime, auto): Creation timestamp
- `updated_at` (datetime, auto): Last update timestamp

**Validation Rules**:
- Name must be unique and non-empty
- Name length <= 100 characters
- Description length <= 500 characters

### Question

Individual quiz questions with multiple-choice options.

**Fields**:
- `id` (integer, primary key): Unique question identifier
- `category_id` (integer, foreign key): Associated category
- `question_text` (text, required): Question content
- `option_a` (string, required): First option
- `option_b` (string, required): Second option
- `option_c` (string, required): Third option
- `option_d` (string, required): Fourth option
- `correct_answer` (enum, required): A, B, C, or D
- `difficulty` (enum, optional): easy, medium, hard
- `created_at` (datetime, auto): Creation timestamp
- `updated_at` (datetime, auto): Last update timestamp

**Validation Rules**:
- All text fields must be non-empty
- Options must be unique within a question
- Correct answer must be valid (A, B, C, D)
- Question text length <= 1000 characters
- Option text length <= 500 characters

### QuizSession

Manages active quiz sessions and progress.

**Fields**:
- `session_id` (string, primary key): Unique session identifier
- `user_name` (string, required): Participant's name
- `category_id` (integer, foreign key): Quiz category
- `started_at` (datetime, auto): Session start time
- `current_question_index` (integer, default 0): Current question position
- `total_questions` (integer, required): Total questions in quiz
- `answers` (json, required): Array of user answers
- `status` (enum, required): in_progress, completed, abandoned

**Validation Rules**:
- User name must match an existing user or be provided
- Category must exist and have available questions
- Current question index must be within valid range
- Answers array length must equal current_question_index

### Result

Stores completed quiz performance data.

**Fields**:
- `id` (integer, primary key): Unique result identifier
- `user_name` (string, required): Participant's name
- `age` (integer, optional): User's age at quiz time
- `category_id` (integer, foreign key): Quiz category
- `score` (integer, required): Percentage score (0-100)
- `correct_count` (integer, required): Number of correct answers
- `wrong_count` (integer, required): Number of wrong answers
- `total_questions` (integer, required): Total questions in quiz
- `time_taken` (integer, optional): Time in seconds
- `completed_at` (datetime, auto): Completion timestamp

**Validation Rules**:
- Score must be between 0 and 100
- Correct + wrong count must equal total_questions
- Age must be between 1 and 120 if provided
- All numeric fields must be non-negative

## Relationships

```
Category (1) ──────── (N) Question
  │                     │
  │                     │
  │                 QuizSession
  │                     │
  │                     │
  └─────── Result ───────┘
    (category_id)      (user_name)
```

- Each Category can have multiple Questions
- Each Question belongs to exactly one Category
- Each QuizSession belongs to one Category and User
- Each Result belongs to one Category and references a User

## State Transitions

### QuizSession Lifecycle

```
[CREATED] → [IN_PROGRESS] → [COMPLETED]
    │            │              │
    └───────────┴──────────────┴─→ [ABANDONED]
```

1. **CREATED**: Session initialized, user and category selected
2. **IN_PROGRESS**: User actively answering questions
3. **COMPLETED**: All questions answered, score calculated
4. **ABANDONED**: Session expired or user left early

### Answer Validation

```
Question Display → User Selection → Answer Validation → Next Question
       │                │                  │                │
       └────────────────┴──────────────────┴────────────────┘
                            │
                    [Invalid Answer]
                            │
                       Error Display
```

## Data Constraints

### Database-Level Constraints

```sql
-- Categories table
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK (length(name) > 0 AND length(name) <= 100),
    description TEXT CHECK (length(description) <= 500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Questions table
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    question_text TEXT NOT NULL CHECK (length(question_text) > 0),
    option_a TEXT NOT NULL CHECK (length(option_a) > 0),
    option_b TEXT NOT NULL CHECK (length(option_b) > 0),
    option_c TEXT NOT NULL CHECK (length(option_c) > 0),
    option_d TEXT NOT NULL CHECK (length(option_d) > 0),
    correct_answer TEXT NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
    difficulty TEXT CHECK (difficulty IN ('easy', 'medium', 'hard')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- Results table
CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    age INTEGER CHECK (age >= 1 AND age <= 120),
    category_id INTEGER NOT NULL,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    correct_count INTEGER NOT NULL CHECK (correct_count >= 0),
    wrong_count INTEGER NOT NULL CHECK (wrong_count >= 0),
    total_questions INTEGER NOT NULL CHECK (total_questions > 0),
    time_taken INTEGER CHECK (time_taken >= 0),
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

### Application-Level Validation

- Pydantic models for input validation
- Custom validators for business logic
- Error handling for constraint violations
- Graceful degradation for missing data

## Performance Considerations

### Indexing Strategy

- Primary keys automatically indexed
- Foreign keys indexed for join performance
- Category.name indexed for uniqueness checks
- Results.completed_at indexed for time-based queries

### Query Optimization

- Use parameterized queries to prevent SQL injection
- Implement connection pooling for concurrent access
- Cache frequently accessed categories and questions
- Batch insert for CSV import operations

## Security & Privacy

### Data Protection

- No personal identifiers beyond name and age
- Local storage only, no external data transmission
- Optional fields (age) for privacy protection
- Session data cleared on completion

### Input Sanitization

- All user inputs validated and sanitized
- SQL injection prevention through parameterized queries
- XSS protection through proper output encoding
- File upload validation for CSV imports