import json
import os
from datetime import datetime
from typing import Dict, Any, Tuple, List, Optional


SUBMISSIONS_FILE = "data/submissions.json"
QUESTIONS_FILE = "data/questions.json"


def load_quiz_data(filepath: str = QUESTIONS_FILE) -> Dict[str, Any]:
    """Tải toàn bộ dữ liệu ngân hàng câu hỏi trắc nghiệm từ file JSON."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Không tìm thấy file ngân hàng câu hỏi tại {filepath}")
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_plant_quiz(plant_key: str, filepath: str = QUESTIONS_FILE) -> Dict[str, Any]:
    """Lấy thông tin loài thực vật và danh sách câu hỏi trắc nghiệm tương ứng."""
    all_data = load_quiz_data(filepath)
    if plant_key not in all_data:
        # Mặc định lấy loại đầu tiên nếu không khớp
        plant_key = list(all_data.keys())[0]
    return all_data[plant_key]


def evaluate_quiz(user_answers: Dict[int, str], questions: List[Dict[str, Any]]) -> Tuple[int, int, float, List[Dict[str, Any]], str]:
    """
    Đánh giá bài trắc nghiệm của học sinh.
    Trả về: (số_câu_đúng, tổng_câu, tỷ_lệ_%, danh_sách_chi_tiết, huy_hiệu)
    """
    correct_count = 0
    total_questions = len(questions)
    details = []

    for q in questions:
        q_id = q["id"]
        correct_ans = q["answer"]
        user_ans = user_answers.get(q_id, "Chưa chọn")
        is_correct = (user_ans == correct_ans)
        
        if is_correct:
            correct_count += 1
            
        details.append({
            "id": q_id,
            "question": q["question"],
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "explanation": q.get("explanation", "")
        })

    percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0.0

    # Cấp huy hiệu khen thưởng dựa trên kết quả
    if percentage == 100:
        badge = "🏆 Nhà Thực Vật Học Nhí Xuất Sắc"
    elif percentage >= 66:
        badge = "🌟 Nhà Khám Phá Thiên Nhiên Giỏi"
    else:
        badge = "🌱 Học Viên Chăm Chỉ - Cố Gắng Lần Sau!"

    return correct_count, total_questions, percentage, details, badge


def load_submissions(filepath: str = SUBMISSIONS_FILE) -> List[Dict[str, Any]]:
    """Tải toàn bộ lịch sử bài làm đã nộp."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def has_student_submitted(
    student_id: str,
    plant_key: str,
    filepath: str = SUBMISSIONS_FILE
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Kiểm tra xem học sinh có student_id này đã từng nộp bài cho plant_key chưa.
    Trả về: (True/False, submission_object_nếu_có)
    """
    if not student_id or not student_id.strip():
        return False, None
    
    clean_id = student_id.strip().lower()
    submissions = load_submissions(filepath)
    
    for sub in submissions:
        sub_student_id = str(sub.get("student_id", "")).strip().lower()
        sub_plant_key = sub.get("plant_key", "")
        if sub_student_id == clean_id and sub_plant_key == plant_key:
            return True, sub
            
    return False, None


def save_submission(
    student_name: str,
    student_id: str,
    plant_key: str,
    plant_name: str,
    correct_count: int,
    total_count: int,
    percentage: float,
    details: List[Dict[str, Any]],
    badge: str,
    filepath: str = SUBMISSIONS_FILE
) -> Dict[str, Any]:
    """Lưu bài làm mới của học sinh vào file data/submissions.json."""
    submissions = load_submissions(filepath)
    
    new_sub = {
        "student_name": student_name.strip(),
        "student_id": student_id.strip(),
        "plant_key": plant_key,
        "plant_name": plant_name,
        "correct_count": correct_count,
        "total_count": total_count,
        "percentage": percentage,
        "badge": badge,
        "details": details,
        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    submissions.append(new_sub)
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(submissions, f, ensure_ascii=False, indent=2)
        
    return new_sub


def reset_submissions(filepath: str = SUBMISSIONS_FILE) -> bool:
    """Xóa toàn bộ lịch sử nộp bài trong file submissions.json."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False
