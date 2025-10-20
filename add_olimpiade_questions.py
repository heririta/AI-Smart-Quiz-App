#!/usr/bin/env python3
"""
Add Olimpiade Sains TK questions to the database
Age-appropriate science questions for kindergarten children
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.db_manager import db_manager
from utils.models import QuestionCreate

def add_olimpiade_sains_tk_questions():
    """Add kindergarten science olympiad questions"""

    questions_data = [
        # Colors and Light
        {
            "question_text": "Apa warna pelangi yang ada di langit?",
            "option_a": "Merah",
            "option_b": "Biru",
            "option_c": "Kuning",
            "option_d": "Semua warna ada",
            "correct_answer": "D",
            "difficulty": "easy"
        },
        {
            "question_text": "Apa yang membuat benda terlihat di siang hari?",
            "option_a": "Matahari",
            "option_b": "Bulan",
            "option_c": "Bintang",
            "option_d": "Lampu",
            "correct_answer": "A",
            "difficulty": "easy"
        },
        {
            "question_text": "Warna apa yang dihasilkan saat mencampur warna merah dan biru?",
            "option_a": "Hijau",
            "option_b": "Ungu",
            "option_c": "Orange",
            "option_d": "Hitam",
            "correct_answer": "C",
            "difficulty": "medium"
        },

        # Animals and Nature
        {
            "question_text": "Hewan apa yang menghasilkan susu untuk kita minum?",
            "option_a": "Ayam",
            "option_b": "Sapi",
            "option_c": "Kucing",
            "option_d": "Anjing",
            "correct_answer": "B",
            "difficulty": "easy"
        },
        {
            "question_text": "Hewan apa yang bisa terbang?",
            "option_a": "Ikan",
            "option_b": "Burung",
            "option_c": "Kelinci",
            "option_d": "Kura-kura",
            "correct_answer": "B",
            "difficulty": "easy"
        },
        {
            "question_text": "Kupu-kupu metamorfosa dari apa?",
            "option_a": "Telur",
            "option_b": "Bunga",
            "option_c": "Ulat",
            "option_d": "Daun",
            "correct_answer": "C",
            "difficulty": "medium"
        },

        # Plants and Growth
        {
            "question_text": "Apa yang dibutuhkan tanaman untuk tumbuh?",
            "option_a": "Es batu",
            "option_b": "Air dan cahaya matahari",
            "option_c": "Garam",
            "option_d": "Minyak",
            "correct_answer": "B",
            "difficulty": "easy"
        },
        {
            "question_text": "Bagian tanaman yang menyerap cahaya matahari disebut?",
            "option_a": "Akar",
            "option_b": "Batang",
            "option_c": "Daun",
            "option_d": "Bunga",
            "correct_answer": "C",
            "difficulty": "easy"
        },
        {
            "question_text": "Buah apa yang tumbuh di pohon?",
            "option_a": "Wortel",
            "option_b": "Kentang",
            "option_c": "Apel",
            "option_d": "Bayam",
            "correct_answer": "C",
            "difficulty": "easy"
        },

        # Weather and Seasons
        {
            "question_text": "Apa yang turun dari langit saat hujan?",
            "option_a": "Salju",
            "option_b": "Air hujan",
            "option_c": "Daun",
            "option_d": "Bunga",
            "correct_answer": "B",
            "difficulty": "easy"
        },
        {
            "question_text": "Apa yang terasa hangat di siang hari?",
            "option_a": "Matahari",
            "option_b": "Bulan",
            "option_c": "Angin",
            "option_d": "Awan",
            "correct_answer": "A",
            "difficulty": "easy"
        },
        {
            "question_text": "Musim apa yang biasanya ada salju?",
            "option_a": "Musim panas",
            "option_b": "Musim hujan",
            "option_c": "Musim dingin",
            "option_d": "Musim kemarau",
            "correct_answer": "C",
            "difficulty": "medium"
        },

        # Human Body
        {
            "question_text": "Kita menggunakan apa untuk bernapas?",
            "option_a": "Mata",
            "option_b": "Hidung",
            "option_c": "Telinga",
            "option_d": "Mulut",
            "correct_answer": "B",
            "difficulty": "easy"
        },
        {
            "question_text": "Kita memiliki berapa mata?",
            "option_a": "Satu",
            "option_b": "Dua",
            "option_c": "Tiga",
            "option_d": "Empat",
            "correct_answer": "B",
            "difficulty": "easy"
        },
        {
            "question_text": "Bagian tubuh yang kita gunakan untuk mendengar?",
            "option_a": "Hidung",
            "option_b": "Mulut",
            "option_c": "Telinga",
            "option_d": "Mata",
            "correct_answer": "C",
            "difficulty": "easy"
        },

        # Basic Physics
        {
            "question_text": "Benda apa yang jatuh ke bawah saat dilepaskan?",
            "option_a": "Bola",
            "option_b": "Balon",
            "option_c": "Bulu",
            "option_d": "Pesawat",
            "correct_answer": "A",
            "difficulty": "easy"
        },
        {
            "question_text": "Apa yang membuat benda mengapung di air?",
            "option_a": "Batu",
            "option_b": "Kayu",
            "option_c": "Daun kering",
            "option_d": "Plastik",
            "correct_answer": "D",
            "difficulty": "medium"
        },
        {
            "question_text": "Apa yang terlihat di cermin?",
            "option_a": "Bayangan kita",
            "option_b": "Gambar di dinding",
            "option_c": "Mainan kita",
            "option_d": "Ibu kita",
            "correct_answer": "A",
            "difficulty": "medium"
        },

        # Earth and Environment
        {
            "question_text": "Kita tinggal di planet apa?",
            "option_a": "Mars",
            "option_b": "Bulan",
            "option_c": "Bumi",
            "option_d": "Matahari",
            "correct_answer": "C",
            "difficulty": "easy"
        },
        {
            "question_text": "Apa yang mengelilingi di langit malam hari?",
            "option_a": "Matahari",
            "option_b": "Bulan",
            "option_c": "Awan",
            "option_d": "Pelangi",
            "correct_answer": "B",
            "difficulty": "easy"
        },
        {
            "question_text": "Apa warna air laut yang dalam?",
            "option_a": "Merah",
            "option_b": "Kuning",
            "option_c": "Biru",
            "option_d": "Hijau",
            "correct_answer": "C",
            "difficulty": "medium"
        },

        # Materials and Objects
        {
            "question_text": "Apa yang keras seperti batu?",
            "option_a": "Bantal",
            "option_b": "Mainan karet",
            "option_c": "Besi",
            "option_d": "Kertas",
            "correct_answer": "C",
            "difficulty": "medium"
        },
        {
            "question_text": "Apa yang bisa dipotong dengan gunting?",
            "option_a": "Batu",
            "option_b": "Kertas",
            "option_c": "Kayu tebal",
            "option_d": "Logam",
            "correct_answer": "B",
            "difficulty": "easy"
        },
        {
            "question_text": "Apa yang lembut seperti kapas?",
            "option_a": "Besi",
            "option_b": "Plastik",
            "option_c": "Kain",
            "option_d": "Kaca",
            "correct_answer": "C",
            "difficulty": "easy"
        },

        # Daily Life Science
        {
            "question_text": "Apa yang terjadi saat es mencair?",
            "option_a": "Menjadi uap",
            "option_b": "Menjadi air",
            "option_c": "Menjadi beku",
            "option_d": "Hilang",
            "correct_answer": "B",
            "difficulty": "medium"
        },
        {
            "question_text": "Apa yang kita gunakan untuk minum saat haus?",
            "option_a": "Susu",
            "option_b": "Air",
            "option_c": "Jus",
            "option_d": "Teh",
            "correct_answer": "B",
            "difficulty": "easy"
        },
        {
            "question_text": "Makanan apa yang baik untuk tulang?",
            "option_a": "Permen",
            "option_b": "Susu",
            "option_c": "Kerupuk",
            "option_d": "Cokelat",
            "correct_answer": "B",
            "difficulty": "medium"
        },

        # Numbers and Counting (Applied Science)
        {
            "question_text": "Berapa kaki yang dimiliki kucing?",
            "option_a": "Dua",
            "option_b": "Empat",
            "option_c": "Enam",
            "option_d": "Delapan",
            "correct_answer": "B",
            "difficulty": "easy"
        },
        {
            "question_text": "Berapa sayap yang dimiliki kupu-kupu?",
            "option_a": "Dua",
            "option_b": "Empat",
            "option_c": "Enam",
            "option_d": "Delapan",
            "correct_answer": "B",
            "difficulty": "easy"
        },
        {
            "question_text": "Berapa hari dalam seminggu?",
            "option_a": "Lima",
            "option_b": "Enam",
            "option_c": "Tujuh",
            "option_d": "Delapan",
            "correct_answer": "C",
            "difficulty": "easy"
        },

        # Sounds and Senses
        {
            "question_text": "Apa yang menghasilkan suara 'meong'?",
            "option_a": "Anjing",
            "option_b": "Kucing",
            "option_c": "Sapi",
            "option_d": "Ayam",
            "correct_answer": "B",
            "difficulty": "easy"
        },
        {
            "question_text": "Apa yang menghasilkan suara 'guk-guk'?",
            "option_a": "Kucing",
            "option_b": "Kelinci",
            "option_c": "Anjing",
            "option_d": "Bebek",
            "correct_answer": "C",
            "difficulty": "easy"
        },
        {
            "question_text": "Apa yang menghasilkan suara 'moo'?",
            "option_a": "Kambing",
            "option_b": "Ayam",
            "option_c": "Sapi",
            "option_d": "Babi",
            "correct_answer": "C",
            "difficulty": "easy"
        },

        # Safety and Health
        {
            "question_text": "Apa yang harus kita lakukan sebelum makan?",
            "option_a": "Tidur",
            "option_b": "Main",
            "option_c": "Cuci tangan",
            "option_d": "Lari",
            "correct_answer": "C",
            "difficulty": "easy"
        },
        {
            "question_text": "Apa yang membuat kita sehat?",
            "option_a": "Makan sayur dan buah",
            "option_b": "Makan permen terus",
            "option_c": "Tidur sepanjang hari",
            "option_d": "Main HP terus",
            "correct_answer": "A",
            "difficulty": "medium"
        },
        {
            "question_text": "Apa yang terasa panas dan bisa membakar?",
            "option_a": "Air",
            "option_b": "Api",
            "option_c": "Es",
            "option_d": "Angin",
            "correct_answer": "B",
            "difficulty": "medium"
        },

        # Shapes and Forms
        {
            "question_text": "Bentuk apa bola?",
            "option_a": "Persegi",
            "option_b": "Segitiga",
            "option_c": "Lingkaran",
            "option_d": "Persegi panjang",
            "correct_answer": "C",
            "difficulty": "easy"
        },
        {
            "question_text": "Bentuk apa atap rumah?",
            "option_a": "Lingkaran",
            "option_b": "Segitiga",
            "option_c": "Persegi",
            "option_d": "Layang-layang",
            "correct_answer": "C",
            "difficulty": "medium"
        },
        {
            "question_text": "Bentuk apa kue ulang tahun?",
            "option_a": "Persegi panjang",
            "option_b": "Bulat",
            "option_c": "Segitiga",
            "option_d": "Lingkaran",
            "correct_answer": "D",
            "difficulty": "medium"
        },

        # Time and Calendar
        {
            "question_text": "Apa yang terbit pertama di pagi hari?",
            "option_a": "Matahari",
            "option_b": "Bulan",
            "option_c": "Bintang",
            "option_d": "Satelit",
            "correct_answer": "A",
            "difficulty": "medium"
        },
        {
            "question_text": "Apa yang bersinar terang di malam hari?",
            "option_a": "Matahari",
            "option_b": "Bulan",
            "option_c": "Planet Mars",
            "option_d": "Awan",
            "correct_answer": "B",
            "difficulty": "easy"
        },
        {
            "question_text": "Berapa jam dalam satu hari?",
            "option_a": "12 jam",
            "option_b": "24 jam",
            "option_c": "18 jam",
            "option_d": "6 jam",
            "correct_answer": "B",
            "difficulty": "medium"
        },

        # Living vs Non-Living
        {
            "question_text": "Manusia termasuk makhluk?",
            "option_a": "Hidup",
            "option_b": "Mati",
            "option_c": "Benda",
            "option_d": "Mainan",
            "correct_answer": "A",
            "difficulty": "easy"
        },
        {
            "question_text": "Meja termasuk benda?",
            "option_a": "Hidup",
            "option_b": "Mati",
            "option_c": "Benda mati",
            "option_d": "Makanan",
            "correct_answer": "C",
            "difficulty": "easy"
        },
        {
            "question_text": "Pohon bisa tumbuh besar, ini termasuk sifat?",
            "option_a": "Hidup",
            "option_b": "Mati",
            "option_c": "Keras",
            "option_d": "Lembut",
            "correct_answer": "A",
            "difficulty": "medium"
        }
    ]

    category_id = 338  # Olimpiade Sains TK category ID
    added_count = 0
    failed_count = 0

    print("Menambahkan pertanyaan Olimpiade Sains TK...")
    print("=" * 50)

    for i, q_data in enumerate(questions_data, 1):
        try:
            question_create = QuestionCreate(
                category_id=category_id,
                question_text=q_data["question_text"],
                option_a=q_data["option_a"],
                option_b=q_data["option_b"],
                option_c=q_data["option_c"],
                option_d=q_data["option_d"],
                correct_answer=q_data["correct_answer"],
                difficulty=q_data["difficulty"]
            )

            success = db_manager.create_question(question_create)
            if success:
                added_count += 1
                print(f"[OK] Pertanyaan {i}: {q_data['question_text'][:50]}...")
            else:
                failed_count += 1
                print(f"[ERROR] Gagal menambah pertanyaan {i}")

        except Exception as e:
            failed_count += 1
            print(f"[ERROR] Error pada pertanyaan {i}: {str(e)}")

    print("\n" + "=" * 50)
    print(f"Hasil:")
    print(f"   [OK] Berhasil ditambah: {added_count} pertanyaan")
    print(f"   [ERROR] Gagal ditambah: {failed_count} pertanyaan")
    print(f"   [TOTAL] Total: {len(questions_data)} pertanyaan")

    # Verifikasi - hitung total pertanyaan di kategori
    try:
        total_questions = db_manager.get_total_questions_count(category_id)
        print(f"\n[VERIFIKASI] Kategori 'Olimpiade Sains TK' sekarang memiliki {total_questions} pertanyaan")
    except Exception as e:
        print(f"\n[WARNING] Error verifikasi: {str(e)}")

if __name__ == "__main__":
    add_olimpiade_sains_tk_questions()