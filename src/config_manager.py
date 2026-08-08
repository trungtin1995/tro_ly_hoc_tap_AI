import os
import json
from typing import Dict, Any

CONFIG_PATH = os.path.join("data", "config.json")

DEFAULT_CONFIG = {
    "admin_password": "admin123",
    "google_forms": {
        "C3": "https://forms.google.com",
        "C4": "https://forms.google.com",
        "CAM": "https://forms.google.com"
    }
}


def load_config() -> Dict[str, Any]:
    """Đọc cấu hình hệ thống từ data/config.json."""
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Ensure keys exist
            if "google_forms" not in config:
                config["google_forms"] = DEFAULT_CONFIG["google_forms"]
            if "admin_password" not in config:
                config["admin_password"] = DEFAULT_CONFIG["admin_password"]
            return config
    except Exception as e:
        print(f"[WARN] Error reading config.json: {e}")
        return DEFAULT_CONFIG


def save_config(config: Dict[str, Any]) -> bool:
    """Lưu cấu hình hệ thống vào data/config.json."""
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save config.json: {e}")
        return False


def get_google_form_url(plant_key: str) -> str:
    """Lấy đường dẫn Google Form tương ứng với nhóm thực vật (C3/C4/CAM)."""
    config = load_config()
    forms = config.get("google_forms", {})
    return forms.get(plant_key, "https://forms.google.com")


def update_google_forms(c3_url: str, c4_url: str, cam_url: str) -> bool:
    """Cập nhật đường dẫn Google Form cho cả 3 nhóm cây."""
    config = load_config()
    config["google_forms"] = {
        "C3": c3_url.strip(),
        "C4": c4_url.strip(),
        "CAM": cam_url.strip()
    }
    return save_config(config)


def verify_admin_password(input_password: str) -> bool:
    """Xác thực mật khẩu Admin."""
    config = load_config()
    target_pwd = config.get("admin_password", "admin123")
    return input_password.strip() == target_pwd.strip()


def update_admin_password(new_password: str) -> bool:
    """Đổi mật khẩu Admin."""
    config = load_config()
    config["admin_password"] = new_password.strip()
    return save_config(config)
