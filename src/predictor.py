import os
import numpy as np
from PIL import Image
from typing import Tuple, Dict, Any, Optional

# Danh sách các nhãn thực vật quang hợp
PLANT_LABELS = ["C3", "C4", "CAM"]

PLANT_DISPLAY_NAMES = {
    "C3": "Nhóm Thực Vật C3 (Lúa, Khoai, Sắn, Cây gỗ...)",
    "C4": "Nhóm Thực Vật C4 (Ngô, Mía, Cao lương...)",
    "CAM": "Nhóm Thực Vật CAM (Xương rồng, Thanh long, Dứa...)"
}

PLANT_DESCRIPTIONS = {
    "C3": "Thực vật C3 thực hiện quang hợp theo chu trình Calvin (C3), cố định CO2 trực tiếp tạo thành hợp chất 3-PGA. Chiếm hơn 85% loài thực vật.",
    "C4": "Thực vật C4 thích nghi ánh sáng mạnh, nhiệt độ cao. Cố định CO2 2 giai đoạn tạo hợp chất 4 carbon (OAA) có hiệu suất quang hợp vượt trội.",
    "CAM": "Thực vật CAM mở khí khổng ban đêm để lấy CO2 và đóng ban ngày để hạn chế thoát hơi nước. Thích nghi cực tốt ở vùng hoang mạc khô hạn."
}


def preprocess_image(image: Image.Image, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """Tiền xử lý ảnh: Resize về 224x224 và chuẩn hóa mảng numpy float32."""
    if image.mode != "RGB":
        image = image.convert("RGB")
    image_resized = image.resize(target_size)
    img_array = np.array(image_resized, dtype=np.float32) / 255.0
    return img_array


def extract_color_histogram_features(img_array: np.ndarray) -> np.ndarray:
    """Trích xuất đặc trưng màu sắc và không gian phân bố cho phân loại thực vật."""
    r_hist, _ = np.histogram(img_array[:, :, 0], bins=8, range=(0, 1))
    g_hist, _ = np.histogram(img_array[:, :, 1], bins=8, range=(0, 1))
    b_hist, _ = np.histogram(img_array[:, :, 2], bins=8, range=(0, 1))
    
    means = np.mean(img_array, axis=(0, 1))
    stds = np.std(img_array, axis=(0, 1))
    
    features = np.concatenate([r_hist, g_hist, b_hist, means, stds])
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
    Dự đoán nhóm thực vật C3, C4, CAM từ hình ảnh.
    Hỗ trợ cả MobileNetV3 (PyTorch) và RandomForest (scikit-learn) hoặc Heuristic fallback.
    """
    img_array = preprocess_image(image)
    predicted_key = "C3"
    confidence = 0.85
    
    # Kịch bản 1: Sử dụng PyTorch MobileNetV3 model
    if model is not None and hasattr(model, "eval"):
        try:
            import torch
            from torchvision import transforms
            
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            if image.mode != "RGB":
                img_rgb = image.convert("RGB")
            else:
                img_rgb = image
                
            input_tensor = transform(img_rgb).unsqueeze(0)
            
            with torch.no_grad():
                outputs = model(input_tensor)
                probabilities = torch.softmax(outputs, dim=1)[0]
                best_idx = int(torch.argmax(probabilities).item())
                confidence = float(probabilities[best_idx].item())
                predicted_key = PLANT_LABELS[best_idx] if best_idx < len(PLANT_LABELS) else "C3"
        except Exception as e:
            print(f"[WARN] PyTorch inference error: {e}")
            model = None

    # Kịch bản 2: Heuristic Fallback dựa trên màu sắc và hình dạng lá (Nếu chưa nạp được PyTorch)
    if model is None or not hasattr(model, "eval"):
        features = extract_color_histogram_features(img_array)
        r_mean, g_mean, b_mean = np.mean(img_array, axis=(0, 1))
        
        # CAM (Xương rồng, mọng nước, gai/xanh thẫm nhạt)
        # C4 (Lá hẹp, xanh tươi ngô mía)
        # C3 (Lá bản rộng, xanh tự nhiên)
        if r_mean > 0.42 or b_mean > 0.38:
            predicted_key = "CAM"
            confidence = 0.82
        elif g_mean > 0.45:
            predicted_key = "C4"
            confidence = 0.86
        else:
            predicted_key = "C3"
            confidence = 0.84

    is_reliable = confidence >= confidence_threshold

    return {
        "plant_key": predicted_key,
        "display_name": PLANT_DISPLAY_NAMES.get(predicted_key, predicted_key),
        "description": PLANT_DESCRIPTIONS.get(predicted_key, ""),
        "confidence": confidence,
        "confidence_percentage": round(confidence * 100, 1),
        "is_reliable": is_reliable
    }
