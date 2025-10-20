-- AI Smart Quiz App Database Schema
-- SQLite initialization script

-- Categories table: Defines question groups
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK (length(name) > 0 AND length(name) <= 100),
    description TEXT CHECK (length(description) <= 500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Questions table: Stores quiz content
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    question_text TEXT NOT NULL CHECK (length(question_text) > 0 AND length(question_text) <= 1000),
    option_a TEXT NOT NULL CHECK (length(option_a) > 0 AND length(option_a) <= 500),
    option_b TEXT NOT NULL CHECK (length(option_b) > 0 AND length(option_b) <= 500),
    option_c TEXT NOT NULL CHECK (length(option_c) > 0 AND length(option_c) <= 500),
    option_d TEXT NOT NULL CHECK (length(option_d) > 0 AND length(option_d) <= 500),
    correct_answer TEXT NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
    difficulty TEXT CHECK (difficulty IN ('easy', 'medium', 'hard')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- Results table: Stores completed quiz performance
CREATE TABLE IF NOT EXISTS results (
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_questions_category_id ON questions(category_id);
CREATE INDEX IF NOT EXISTS idx_results_user_name ON results(user_name);
CREATE INDEX IF NOT EXISTS idx_results_category_id ON results(category_id);
CREATE INDEX IF NOT EXISTS idx_results_completed_at ON results(completed_at);
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);

-- Insert sample data (optional - can be removed for production)
INSERT OR IGNORE INTO categories (name, description) VALUES
('General Knowledge', 'General knowledge questions covering various topics'),
('Mathematics', 'Mathematical problems and equations'),
('Science', 'Science questions covering physics, chemistry, and biology'),
('Geography', 'Questions about countries, capitals, and geographical features'),
('History', 'Historical events and figures');

-- Insert sample questions (optional - can be removed for production)
INSERT OR IGNORE INTO questions (category_id, question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty) VALUES
(1, 'What is the capital of France?', 'London', 'Berlin', 'Paris', 'Madrid', 'C', 'easy'),
(1, 'Which planet is known as the Red Planet?', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'B', 'easy'),
(2, 'What is 15 + 27?', '40', '42', '44', '46', 'B', 'medium'),
(2, 'What is 8 × 7?', '54', '56', '58', '60', 'B', 'medium'),
(3, 'What is the chemical symbol for gold?', 'Go', 'Gd', 'Au', 'Ag', 'C', 'medium'),
(3, 'What is the speed of light in vacuum?', '299,792,458 m/s', '199,792,458 m/s', '399,792,458 m/s', '99,792,458 m/s', 'A', 'hard');