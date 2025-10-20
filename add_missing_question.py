#!/usr/bin/env python3
"""
Add the missing Olimpiade Sains TK question
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.db_manager import db_manager
from utils.models import QuestionCreate

def add_missing_question():
    """Add the missing question"""

    question_data = {
        "question_text": "Apa yang terbit pertama di pagi hari?",
        "option_a": "Matahari",
        "option_b": "Bulan",
        "option_c": "Bintang",
        "option_d": "Satelit",
        "correct_answer": "A",
        "difficulty": "medium"
    }

    category_id = 338  # Olimpiade Sains TK category ID

    try:
        question_create = QuestionCreate(
            category_id=category_id,
            question_text=question_data["question_text"],
            option_a=question_data["option_a"],
            option_b=question_data["option_b"],
            option_c=question_data["option_c"],
            option_d=question_data["option_d"],
            correct_answer=question_data["correct_answer"],
            difficulty=question_data["difficulty"]
        )

        success = db_manager.create_question(question_create)
        if success:
            print("[OK] Pertanyaan berhasil ditambah: Apa yang terbit pertama di pagi hari?")
        else:
            print("[ERROR] Gagal menambah pertanyaan")

    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")

    # Verifikasi total pertanyaan
    try:
        total_questions = db_manager.get_total_questions_count(category_id)
        print(f"\n[VERIFIKASI] Kategori 'Olimpiade Sains TK' sekarang memiliki {total_questions} pertanyaan")
    except Exception as e:
        print(f"\n[WARNING] Error verifikasi: {str(e)}")

if __name__ == "__main__":
    add_missing_question()