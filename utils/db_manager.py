"""
Database manager for AI Smart Quiz App
Handles all SQLite database operations and CRUD functions
"""

import sqlite3
import os
import io
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
from contextlib import contextmanager

from utils.models import (
    Category, CategoryCreate, CategoryUpdate,
    Question, QuestionCreate, QuestionUpdate,
    Result, ResultCreate,
    QuizSession, QuizSessionCreate,
    CategoryAnalytics, PerformanceTrend,
    CSVImportResult
)


class DatabaseManager:
    """Manages SQLite database operations for the quiz app"""

    def __init__(self, db_path: str = "database/quiz.db"):
        """Initialize database manager with database path"""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database with schema"""
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Read and execute initialization script
        init_script_path = "database/init_db.sql"
        if os.path.exists(init_script_path):
            with open(init_script_path, 'r') as f:
                init_script = f.read()
            self.execute_script(init_script)
        else:
            # Fallback: create basic schema
            self._create_basic_schema()

        # Run database migrations
        self._run_migrations()

    def _create_basic_schema(self):
        """Create basic database schema if init script not found"""
        schema = """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
            difficulty TEXT,
            combined_content TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            age INTEGER,
            category_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            correct_count INTEGER NOT NULL,
            wrong_count INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            time_taken INTEGER,
            completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );
        """
        self.execute_script(schema)

    def _run_migrations(self):
        """Run database migrations to add new columns"""
        try:
            # Check if combined_content column exists in questions table
            check_query = """
            PRAGMA table_info(questions);
            """

            columns = self.execute_query(check_query)
            has_combined_content = any(
                col['name'] == 'combined_content' for col in columns
            )

            if not has_combined_content:
                # Add combined_content column
                alter_query = """
                ALTER TABLE questions
                ADD COLUMN combined_content TEXT;
                """
                self.execute_update(alter_query)
                print("Added combined_content column to questions table")

                # Update existing questions with combined content
                update_query = """
                UPDATE questions
                SET combined_content = question_text ||
                    ' A. ' || option_a ||
                    ' B. ' || option_b ||
                    ' C. ' || option_c ||
                    ' D. ' || option_d;
                """
                self.execute_update(update_query)
                print("Updated existing questions with combined content")

        except Exception as e:
            print(f"Migration error: {e}")

    @contextmanager
    def get_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Enable dictionary-like access
            yield conn
        except sqlite3.Error as e:
            raise Exception(f"Database connection error: {e}")
        finally:
            if conn:
                conn.close()

    def execute_script(self, script: str):
        """Execute SQL script"""
        with self.get_connection() as conn:
            conn.executescript(script)
            conn.commit()

    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount

    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT query and return last row ID"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    # ==================== CATEGORY CRUD ====================

    def create_category(self, category: CategoryCreate) -> int:
        """Create new category and return ID"""
        query = """
        INSERT INTO categories (name, description)
        VALUES (?, ?)
        """
        return self.execute_insert(query, (category.name, category.description))

    def get_categories(self) -> List[Category]:
        """Get all categories"""
        query = "SELECT * FROM categories ORDER BY name"
        rows = self.execute_query(query)
        return [Category(**dict(row)) for row in rows]

    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        query = "SELECT * FROM categories WHERE id = ?"
        rows = self.execute_query(query, (category_id,))
        if rows:
            return Category(**dict(rows[0]))
        return None

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get category by name"""
        query = "SELECT * FROM categories WHERE name = ?"
        rows = self.execute_query(query, (name,))
        if rows:
            return Category(**dict(rows[0]))
        return None

    def update_category(self, category_id: int, category: CategoryUpdate) -> bool:
        """Update category"""
        updates = []
        params = []

        if category.name is not None:
            updates.append("name = ?")
            params.append(category.name)
        if category.description is not None:
            updates.append("description = ?")
            params.append(category.description)

        if not updates:
            return False

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(category_id)

        query = f"UPDATE categories SET {', '.join(updates)} WHERE id = ?"
        return self.execute_update(query, tuple(params)) > 0

    def delete_category(self, category_id: int) -> bool:
        """Delete category (cascades to questions)"""
        query = "DELETE FROM categories WHERE id = ?"
        return self.execute_update(query, (category_id,)) > 0

    # ==================== QUESTION CRUD ====================

    def _generate_combined_content(self, question_text: str, option_a: str, option_b: str,
                              option_c: str, option_d: str) -> str:
        """Generate combined content string from question and options"""
        return f"{question_text} A. {option_a} B. {option_b} C. {option_c} D. {option_d}"

    def create_question(self, question: QuestionCreate) -> int:
        """Create new question and return ID"""
        # Generate combined content
        combined_content = self._generate_combined_content(
            question.question_text,
            question.option_a,
            question.option_b,
            question.option_c,
            question.option_d
        )

        query = """
        INSERT INTO questions (category_id, question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty, combined_content)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_insert(query, (
            question.category_id,
            question.question_text,
            question.option_a,
            question.option_b,
            question.option_c,
            question.option_d,
            question.correct_answer,
            question.difficulty.value if question.difficulty else None,
            combined_content
        ))

    def get_questions_by_category(self, category_id: int, limit: Optional[int] = None) -> List[Question]:
        """Get questions by category, optionally limited"""
        query = "SELECT * FROM questions WHERE category_id = ? ORDER BY RANDOM()"
        if limit:
            query += f" LIMIT {limit}"

        rows = self.execute_query(query, (category_id,))
        return [Question(**dict(row)) for row in rows]

    def get_question_by_id(self, question_id: int) -> Optional[Question]:
        """Get question by ID"""
        query = "SELECT * FROM questions WHERE id = ?"
        rows = self.execute_query(query, (question_id,))
        if rows:
            return Question(**dict(rows[0]))
        return None

  
    def delete_question(self, question_id: int) -> bool:
        """Delete question"""
        query = "DELETE FROM questions WHERE id = ?"
        return self.execute_update(query, (question_id,)) > 0

    def get_total_questions_count(self, category_id: int = None) -> int:
        """Get total number of questions (in a category or all questions)"""
        if category_id:
            query = "SELECT COUNT(*) as count FROM questions WHERE category_id = ?"
            rows = self.execute_query(query, (category_id,))
        else:
            query = "SELECT COUNT(*) as count FROM questions"
            rows = self.execute_query(query)
        return rows[0]['count'] if rows else 0

    # ==================== RESULTS ====================

    def save_result(self, result: ResultCreate) -> int:
        """Save quiz result"""
        query = """
        INSERT INTO results (user_name, age, category_id, score, correct_count, wrong_count, total_questions, time_taken)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_insert(query, (
            result.user_name,
            result.age,
            result.category_id,
            result.score,
            result.correct_count,
            result.wrong_count,
            result.total_questions,
            result.time_taken
        ))

    def get_user_results(self, user_name: str, limit: Optional[int] = None) -> List[Result]:
        """Get results for a specific user"""
        query = "SELECT * FROM results WHERE user_name = ? ORDER BY completed_at DESC"
        if limit:
            query += f" LIMIT {limit}"

        rows = self.execute_query(query, (user_name,))
        return [Result(**dict(row)) for row in rows]

    def get_category_results(self, category_id: Optional[int] = None) -> List[Result]:
        """Get results for a category or all categories"""
        if category_id:
            query = "SELECT * FROM results WHERE category_id = ? ORDER BY completed_at DESC"
            rows = self.execute_query(query, (category_id,))
        else:
            query = "SELECT * FROM results ORDER BY completed_at DESC"
            rows = self.execute_query(query)

        return [Result(**dict(row)) for row in rows]

    # ==================== ANALYTICS ====================

    def get_category_analytics(self, category_id: Optional[int] = None) -> List[CategoryAnalytics]:
        """Get performance analytics for categories"""
        if category_id:
            query = """
            SELECT
                c.id as category_id,
                c.name as category_name,
                COUNT(r.id) as total_attempts,
                COALESCE(AVG(r.score), 0) as average_score,
                COALESCE(MAX(r.score), 0) as best_score,
                COALESCE(MIN(r.score), 0) as worst_score
            FROM categories c
            LEFT JOIN results r ON c.id = r.category_id
            WHERE c.id = ?
            GROUP BY c.id, c.name
            """
            rows = self.execute_query(query, (category_id,))
        else:
            query = """
            SELECT
                c.id as category_id,
                c.name as category_name,
                COUNT(r.id) as total_attempts,
                COALESCE(AVG(r.score), 0) as average_score,
                COALESCE(MAX(r.score), 0) as best_score,
                COALESCE(MIN(r.score), 0) as worst_score
            FROM categories c
            LEFT JOIN results r ON c.id = r.category_id
            GROUP BY c.id, c.name
            ORDER BY c.name
            """
            rows = self.execute_query(query)

        analytics = []
        for row in rows:
            # Get recent scores and distribution
            recent_scores_query = """
            SELECT score FROM results
            WHERE category_id = ?
            ORDER BY completed_at DESC
            LIMIT 10
            """
            recent_scores_rows = self.execute_query(recent_scores_query, (row['category_id'],))
            recent_scores = [r['score'] for r in recent_scores_rows]

            # Score distribution
            distribution_query = """
            SELECT
                CASE
                    WHEN score >= 90 THEN 'A (90-100)'
                    WHEN score >= 80 THEN 'B (80-89)'
                    WHEN score >= 70 THEN 'C (70-79)'
                    WHEN score >= 60 THEN 'D (60-69)'
                    ELSE 'F (0-59)'
                END as grade_range,
                COUNT(*) as count
            FROM results
            WHERE category_id = ?
            GROUP BY grade_range
            """
            distribution_rows = self.execute_query(distribution_query, (row['category_id'],))
            score_distribution = {r['grade_range']: r['count'] for r in distribution_rows}

            analytics.append(CategoryAnalytics(
                category_id=row['category_id'],
                category_name=row['category_name'],
                total_attempts=row['total_attempts'],
                average_score=row['average_score'],
                best_score=row['best_score'],
                worst_score=row['worst_score'],
                recent_scores=recent_scores,
                score_distribution=score_distribution
            ))

        return analytics

    def get_performance_trend(self, user_name: str, days: int = 30) -> Optional[PerformanceTrend]:
        """Get performance trend for a user over specified days"""
        query = """
        SELECT
            DATE(completed_at) as date,
            AVG(score) as avg_score,
            COUNT(*) as quiz_count
        FROM results
        WHERE user_name = ?
        AND completed_at >= date('now', '-{} days')
        GROUP BY DATE(completed_at)
        ORDER BY date
        """.format(days)

        rows = self.execute_query(query, (user_name,))

        if not rows:
            return None

        daily_scores = []
        total_score = 0
        total_quizzes = 0

        for row in rows:
            daily_scores.append({
                'date': row['date'],
                'avg_score': row['avg_score'],
                'quiz_count': row['quiz_count']
            })
            total_score += row['avg_score']
            total_quizzes += row['quiz_count']

        # Calculate trend direction
        if len(daily_scores) >= 2:
            recent_avg = daily_scores[-1]['avg_score']
            older_avg = daily_scores[0]['avg_score']
            if recent_avg > older_avg + 5:
                trend = "improving"
            elif recent_avg < older_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return PerformanceTrend(
            user_name=user_name,
            period_days=days,
            daily_scores=daily_scores,
            trend_direction=trend,
            average_score=total_score / len(daily_scores) if daily_scores else 0,
            total_quizzes=total_quizzes
        )

    # ==================== CSV IMPORT/EXPORT ====================

    def import_questions_from_csv(self, csv_data: bytes, category_id: int) -> CSVImportResult:
        """Import questions from CSV data"""
        try:
            df = pd.read_csv(io.BytesIO(csv_data))

            # Validate required columns
            required_columns = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return CSVImportResult(
                    total_rows=len(df),
                    successful_imports=0,
                    failed_imports=len(df),
                    errors=[f"Missing required columns: {', '.join(missing_columns)}"],
                    questions_created=[]
                )

            successful_imports = 0
            failed_imports = 0
            errors = []
            questions_created = []

            for index, row in df.iterrows():
                try:
                    # Validate row data
                    question_data = QuestionCreate(
                        category_id=category_id,
                        question_text=str(row['question_text']).strip(),
                        option_a=str(row['option_a']).strip(),
                        option_b=str(row['option_b']).strip(),
                        option_c=str(row['option_c']).strip(),
                        option_d=str(row['option_d']).strip(),
                        correct_answer=str(row['correct_answer']).upper().strip(),
                        difficulty=str(row['difficulty']).lower().strip() if 'difficulty' in row and pd.notna(row['difficulty']) else None
                    )

                    # Create question
                    question_id = self.create_question(question_data)
                    question = self.get_question_by_id(question_id)

                    if question:
                        questions_created.append(question)
                        successful_imports += 1
                    else:
                        failed_imports += 1
                        errors.append(f"Row {index + 1}: Failed to create question")

                except Exception as e:
                    failed_imports += 1
                    errors.append(f"Row {index + 1}: {str(e)}")

            return CSVImportResult(
                total_rows=len(df),
                successful_imports=successful_imports,
                failed_imports=failed_imports,
                errors=errors,
                questions_created=questions_created
            )

        except Exception as e:
            return CSVImportResult(
                total_rows=0,
                successful_imports=0,
                failed_imports=0,
                errors=[f"Failed to read CSV file: {str(e)}"],
                questions_created=[]
            )

    def export_questions_to_csv(self, category_id: Optional[int] = None) -> bytes:
        """Export questions to CSV format"""
        if category_id:
            questions = self.get_questions_by_category(category_id)
        else:
            # Get all questions
            query = """
            SELECT q.*, c.name as category_name
            FROM questions q
            JOIN categories c ON q.category_id = c.id
            ORDER BY c.name, q.question_text
            """
            rows = self.execute_query(query)
            questions = [Question(**dict(row)) for row in rows]

        if not questions:
            return b"No questions found to export"

        # Convert to DataFrame
        data = []
        for q in questions:
            data.append({
                'question_text': q.question_text,
                'option_a': q.option_a,
                'option_b': q.option_b,
                'option_c': q.option_c,
                'option_d': q.option_d,
                'correct_answer': q.correct_answer,
                'difficulty': q.difficulty.value if q.difficulty else ''
            })

        df = pd.DataFrame(data)
        return df.to_csv(index=False).encode('utf-8')


  # ==================== ADDITIONAL ADMIN METHODS ====================

    def get_questions(self, category_id: Optional[int] = None, limit: Optional[int] = None) -> List[Question]:
        """Get questions with optional category filter and limit"""
        if category_id:
            return self.get_questions_by_category(category_id, limit)
        else:
            query = """
            SELECT q.*, c.name as category_name
            FROM questions q
            JOIN categories c ON q.category_id = c.id
            ORDER BY c.name, q.question_text
            """
            if limit:
                query += f" LIMIT {limit}"

            rows = self.execute_query(query)
            return [Question(**dict(row)) for row in rows]

    
    
    def update_question(self, question_id: int, category_id: int, question_text: str,
                       option_a: str, option_b: str, option_c: str, option_d: str,
                       correct_answer: str, difficulty: str) -> bool:
        """Update an existing question"""
        try:
            # Generate combined content
            combined_content = self._generate_combined_content(question_text, option_a, option_b, option_c, option_d)

            query = """
            UPDATE questions
            SET category_id = ?, question_text = ?, option_a = ?, option_b = ?,
                option_c = ?, option_d = ?, correct_answer = ?, difficulty = ?, combined_content = ?
            WHERE id = ?
            """
            result = self.execute_update(query, (category_id, question_text, option_a, option_b,
                                               option_c, option_d, correct_answer, difficulty, combined_content, question_id))
            return result > 0
        except Exception as e:
            print(f"Error updating question {question_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def get_total_results_count(self) -> int:
        """Get total count of quiz results"""
        query = "SELECT COUNT(*) as count FROM results"
        result = self.execute_query(query)
        return result[0]['count'] if result else 0

    def delete_questions_by_category(self, category_id: int) -> bool:
        """Delete all questions in a specific category"""
        try:
            query = "DELETE FROM questions WHERE category_id = ?"
            result = self.execute_update(query, (category_id,))
            return result > 0
        except Exception as e:
            print(f"Error deleting questions in category {category_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def delete_all_results(self) -> bool:
        """Delete all quiz results"""
        try:
            query = "DELETE FROM results"
            result = self.execute_update(query)
            return result > 0
        except Exception as e:
            print(f"Error deleting all results: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def export_categories_to_csv(self) -> bytes:
        """Export categories to CSV format"""
        categories = self.get_categories()

        if not categories:
            return b"No categories found to export"

        # Convert to DataFrame
        data = []
        for cat in categories:
            data.append({
                'name': cat.name,
                'description': cat.description or ''
            })

        df = pd.DataFrame(data)
        return df.to_csv(index=False).encode('utf-8')

    def export_results_to_csv(self) -> bytes:
        """Export quiz results to CSV format"""
        query = """
        SELECT r.*, c.name as category_name
        FROM results r
        JOIN categories c ON r.category_id = c.id
        ORDER BY r.timestamp DESC
        """
        rows = self.execute_query(query)

        if not rows:
            return b"No results found to export"

        # Convert to DataFrame
        data = []
        for row in rows:
            data.append({
                'user_name': row['user_name'],
                'age': row['age'] or '',
                'category_name': row['category_name'],
                'score': row['score'],
                'correct_count': row['correct_count'],
                'wrong_count': row['wrong_count'],
                'total_questions': row['total_questions'],
                'time_taken': row['time_taken'] or '',
                'timestamp': row['timestamp']
            })

        df = pd.DataFrame(data)
        return df.to_csv(index=False).encode('utf-8')

    def import_categories_from_csv(self, csv_content: str) -> dict:
        """Import categories from CSV content"""
        try:
            from io import StringIO
            df = pd.read_csv(StringIO(csv_content))

            # Validate required columns
            required_columns = ['name']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return {
                    'success_count': 0,
                    'error_count': len(df),
                    'errors': [f"Missing required columns: {', '.join(missing_columns)}"]
                }

            success_count = 0
            error_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    name = str(row['name']).strip()
                    description = str(row.get('description', '')).strip() if pd.notna(row.get('description', '')) else None

                    if not name:
                        error_count += 1
                        errors.append(f"Row {index + 1}: Category name is required")
                        continue

                    # Check if category already exists
                    existing = self.get_category_by_name(name)
                    if existing:
                        error_count += 1
                        errors.append(f"Row {index + 1}: Category '{name}' already exists")
                        continue

                    # Create category
                    if self.create_category(name, description):
                        success_count += 1
                    else:
                        error_count += 1
                        errors.append(f"Row {index + 1}: Failed to create category '{name}'")

                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {index + 1}: {str(e)}")

            return {
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors
            }

        except Exception as e:
            return {
                'success_count': 0,
                'error_count': 0,
                'errors': [f"Failed to read CSV file: {str(e)}"]
            }

    def import_questions_from_csv(self, csv_content: str) -> dict:
        """Import questions from CSV content with category names"""
        try:
            from io import StringIO
            df = pd.read_csv(StringIO(csv_content))

            # Validate required columns
            required_columns = ['category_name', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return {
                    'success_count': 0,
                    'error_count': len(df),
                    'errors': [f"Missing required columns: {', '.join(missing_columns)}"]
                }

            success_count = 0
            error_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    category_name = str(row['category_name']).strip()
                    question_text = str(row['question_text']).strip()
                    option_a = str(row['option_a']).strip()
                    option_b = str(row['option_b']).strip()
                    option_c = str(row['option_c']).strip()
                    option_d = str(row['option_d']).strip()
                    correct_answer = str(row['correct_answer']).strip().upper()
                    difficulty = str(row.get('difficulty', 'medium')).strip().lower()

                    # Validate required fields
                    if not all([category_name, question_text, option_a, option_b, option_c, option_d, correct_answer]):
                        error_count += 1
                        errors.append(f"Row {index + 1}: All required fields must be provided")
                        continue

                    # Validate correct answer
                    if correct_answer not in ['A', 'B', 'C', 'D']:
                        error_count += 1
                        errors.append(f"Row {index + 1}: Correct answer must be A, B, C, or D")
                        continue

                    # Validate difficulty
                    if difficulty not in ['easy', 'medium', 'hard']:
                        difficulty = 'medium'

                    # Find or create category
                    category = self.get_category_by_name(category_name)
                    if not category:
                        # Create new category
                        if self.create_category(category_name):
                            category = self.get_category_by_name(category_name)
                        else:
                            error_count += 1
                            errors.append(f"Row {index + 1}: Failed to create category '{category_name}'")
                            continue

                    # Create question
                    question_create = QuestionCreate(
                        category_id=category.id,
                        question_text=question_text,
                        option_a=option_a,
                        option_b=option_b,
                        option_c=option_c,
                        option_d=option_d,
                        correct_answer=correct_answer,
                        difficulty=difficulty
                    )

                    if self.create_question(question_create):
                        success_count += 1
                    else:
                        error_count += 1
                        errors.append(f"Row {index + 1}: Failed to create question")

                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {index + 1}: {str(e)}")

            return {
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors
            }

        except Exception as e:
            return {
                'success_count': 0,
                'error_count': 0,
                'errors': [f"Failed to read CSV file: {str(e)}"]
            }


# Global database manager instance
db_manager = DatabaseManager()