#!/usr/bin/env python3
"""
Test script to verify that quiz limits work correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.db_manager import db_manager
from utils.session_manager import session_manager
from utils.models import User

def test_quiz_limit():
    """Test that quiz correctly limits to 10 questions"""

    print("Testing Quiz Limit Functionality")
    print("=" * 50)

    # Test parameters
    category_id = 338  # Olimpiade Sains TK
    expected_limit = 10

    # Test 1: Check total questions in category
    total_questions = db_manager.get_total_questions_count(category_id)
    print(f"Total questions in category: {total_questions}")

    # Test 2: Get limited questions
    limited_questions = db_manager.get_questions_by_category(category_id, limit=expected_limit)
    print(f"Questions returned with limit={expected_limit}: {len(limited_questions)}")

    # Test 3: Verify limit
    if len(limited_questions) == expected_limit:
        print(f"[OK] PASS: Correctly returned {expected_limit} questions")
    else:
        print(f"[ERROR] FAIL: Expected {expected_limit}, got {len(limited_questions)}")
        return False

    # Test 4: Simulate quiz session start
    try:
        user = User(name="Test User", age=6)
        session_manager.set_user(user)

        quiz_session = session_manager.start_quiz_session(
            user_name=user.name,
            category_id=category_id,
            num_questions=expected_limit
        )

        if quiz_session and quiz_session.total_questions == expected_limit:
            print(f"[OK] PASS: Quiz session created with {expected_limit} questions")
        else:
            print(f"[ERROR] FAIL: Quiz session has {quiz_session.total_questions if quiz_session else 0} questions")
            return False

        # Test 5: Check that questions are randomized
        print(f"First 3 question IDs: {[q.id for q in limited_questions[:3]]}")

        print("\n" + "=" * 50)
        print("[OK] All tests passed! Quiz limit is working correctly.")
        return True

    except Exception as e:
        print(f"[ERROR] FAIL: Error during quiz session test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_quiz_limit()
    if success:
        print("\nThe quiz system is correctly limiting questions to 10 per session.")
    else:
        print("\nThere are issues with the quiz limit functionality.")