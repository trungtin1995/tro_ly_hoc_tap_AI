import os
import json
from typing import Dict, Any

PLANT_INFO_PATH = os.path.join("data", "plant_info.json")


def load_all_plant_info() -> Dict[str, Any]:
    """Tải dữ liệu thông tin hiển vi, giải phẫu và ví dụ của tất cả loài cây."""
    if not os.path.exists(PLANT_INFO_PATH):
        return {}
    try:
        with open(PLANT_INFO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to load plant_info.json: {e}")
        return {}


def get_plant_details(plant_key: str) -> Dict[str, Any]:
    """Lấy thông tin chi tiết đầy đủ của nhóm thực vật theo plant_key (C3/C4/CAM)."""
    all_info = load_all_plant_info()
    if plant_key in all_info:
        return all_info[plant_key]
    
    # Fallback default to first key
    if all_info:
        return list(all_info.values())[0]
        
    return {
        "display_name": f"THỰC VẬT {plant_key}",
        "scientific_name": plant_key,
        "group": plant_key,
        "badge_text": f"AI xác định tiêu bản thuộc nhóm thực vật {plant_key}.",
        "sample_info": {
            "sample_type": "Lá (lát cắt ngang)",
            "method": "Ảnh hiển vi",
            "magnification": "100x",
            "morphology_desc": "Chưa có mô tả hình thái chi tiết."
        },
        "summary": "Chưa có tóm tắt nội dung loài.",
        "highlights": [],
        "examples": []
    }
