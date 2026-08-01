import os
import numpy as np
from PIL import Image
from typing import Tuple, Dict, Any, Optional

# Danh sách các nhãn thực vật hỗ trợ
PLANT_LABELS = ["cay_sen", "cay_tre", "cay_thong"]

PLANT_DISPLAY_NAMES = {
    "cay_sen": "Cây Sen (Nelumbo nucifera)",
    "cay_tre": "Cây Tre / Luồng (Bambusoideae)",
    "cay_thong": "Cây Thông (Pinus)"
}


def preprocess_image(image: Image.Image, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """Tiền xử lý ảnh: Resize về 224x224 và chuẩn hóa mảng numpy."""
    if image.mode != "RGB":
        image = image.convert("RGB")
    image_resized = image.resize(target_size)
    img_array = np.array(image_resized, dtype=np.float32) / 255.0
    return img_array


def extract_color_histogram_features(img_array: np.ndarray) -> np.ndarray:
    """Trích xuất đặc trưng màu sắc và không gian phân bố cho phân loại thực vật."""
    # Compute histogram for R, G, B channels
    r_hist, _ = np.histogram(img_array[:, :, 0], bins=8, range=(0, 1))
    g_hist, _ = np.histogram(img_array[:, :, 1], bins=8, range=(0, 1))
    b_hist, _ = np.histogram(img_array[:, :, 2], bins=8, range=(0, 1))
    
    # Calculate channel means & stds
    means = np.mean(img_array, axis=(0, 1))
    stds = np.std(img_array, axis=(0, 1))
    
    features = np.concatenate([r_hist, g_hist, b_hist, means, stds])
    # Normalize feature vector
    norm = np.linalg.norm(features)
    if norm > 0:
        features = features / norm
    return features


def predict_plant_image(
    image: Image.Image,
    model: Optional[Any] = None,
    confidence_threshold: float = 0.50
) -> Dict[str, Any]:
    """
    Dự đoán loài thực vật từ hình ảnh.
    Trả về dictionary thông tin:
    - plant_key: 'cay_sen' | 'cay_tre' | 'cay_thong'
    - display_name: Tên hiển thị tiếng Việt
    - confidence: Tỷ lệ tin cậy (0.0 - 1.0)
    - is_reliable: True nếu confidence >= threshold
    """
    img_array = preprocess_image(image)
    
    if model is not None and hasattr(model, "predict_proba"):
        features = extract_color_histogram_features(img_array).reshape(1, -1)
        probabilities = model.predict_proba(features)[0]
        best_idx = int(np.argmax(probabilities))
        confidence = float(probabilities[best_idx])
        predicted_key = PLANT_LABELS[best_idx] if best_idx < len(PLANT_LABELS) else "cay_sen"
    else:
        # Giải thuật phân tích màu chủ đạo (Color Dominance Heuristic) phục vụ demo/kiểm thử
        features = extract_color_histogram_features(img_array)
        r_mean, g_mean, b_mean = np.mean(img_array, axis=(0, 1))
        
        # Cây Sen (Hoa hồng/trắng, lá xanh trên nước): Tỷ lệ Đỏ/Xanh cao hơn hoặc có sắc tố hoa
        # Cây Thông (Xanh thẫm/Lá kim): Tỷ lệ G đậm & B nhẹ
        # Cây Tre (Xanh tươi/Vàng lục)
        if r_mean > 0.45 or (r_mean > g_mean * 0.85 and b_mean > 0.35):
            predicted_key = "cay_sen"
            confidence = 0.88
        elif g_mean > r_mean and g_mean > b_mean:
            if g_mean > 0.40:
                predicted_key = "cay_tre"
                confidence = 0.85
            else:
                predicted_key = "cay_thong"
                confidence = 0.82
        else:
            predicted_key = "cay_sen"
            confidence = 0.75

    is_reliable = confidence >= confidence_threshold

    return {
        "plant_key": predicted_key,
        "display_name": PLANT_DISPLAY_NAMES.get(predicted_key, predicted_key),
        "confidence": confidence,
        "confidence_percentage": round(confidence * 100, 1),
        "is_reliable": is_reliable
    }
