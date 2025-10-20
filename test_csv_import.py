#!/usr/bin/env python3
"""
Test script to validate CSV import functionality for Olimpiade Sains TK
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db_manager import db_manager

def test_csv_import():
    """Test the CSV import with our sample file"""
    print("Testing CSV Import Functionality")
    print("=" * 50)

    # Read the sample CSV file
    csv_file_path = "sample_olimpiade_sains_tk_questions.csv"

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_content = file.read()

        print(f"Successfully read CSV file: {csv_file_path}")
        print(f"CSV Content Preview:")
        print("-" * 30)
        lines = csv_content.split('\n')
        for i, line in enumerate(lines[:3]):  # Show first 3 lines
            print(f"Line {i+1}: {line}")
        if len(lines) > 3:
            print(f"... and {len(lines)-3} more lines")
        print()

        # Test the import
        print("Starting CSV Import...")
        result = db_manager.import_questions_from_csv(csv_content)

        print("Import Results:")
        print(f"Successfully imported: {result['success_count']} questions")
        print(f"Failed to import: {result['error_count']} questions")

        if result.get('errors'):
            print("Errors encountered:")
            for error in result['errors'][:5]:  # Show first 5 errors
                print(f"  • {error}")
            if len(result['errors']) > 5:
                print(f"  ... and {len(result['errors'])-5} more errors")

        # Verify the import by checking questions in Olimpiade Sains TK
        print("\nVerifying Import...")
        category = db_manager.get_category_by_name("Olimpiade Sains TK")
        if category:
            questions = db_manager.get_questions(category.id)
            print(f"Category '{category.name}' now has {len(questions)} questions")

            if questions:
                print("Sample imported questions:")
                for i, q in enumerate(questions[:3]):  # Show first 3 questions
                    print(f"  {i+1}. {q.question_text[:50]}...")
                    print(f"     A. {q.option_a}  B. {q.option_b}")
                    print(f"     C. {q.option_c}  D. {q.option_d}")
                    print(f"     Correct: {q.correct_answer} ({q.difficulty})")
                    print()
        else:
            print("Category 'Olimpiade Sains TK' not found after import")

    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file_path}' not found")
    except Exception as e:
        print(f"Error during import: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_csv_import()