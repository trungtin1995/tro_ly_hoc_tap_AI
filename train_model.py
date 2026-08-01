import os
import glob
import pickle
import numpy as np
from PIL import Image, ImageDraw
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from src.predictor import preprocess_image, extract_color_histogram_features, PLANT_LABELS


DATASET_DIR = "dataset"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "plant_classifier.pkl")


def generate_mock_dataset_if_needed():
    """Tạo bộ dữ liệu hình ảnh mẫu (Mock Dataset) nếu thư mục dataset/ trống."""
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    # Định nghĩa màu sắc mẫu đặc trưng cho 3 loại thực vật
    plant_colors = {
        "cay_sen": [(235, 130, 160), (255, 200, 220), (50, 160, 90), (30, 140, 70)],   # Hoa sen hồng + lá xanh
        "cay_tre": [(60, 180, 75), (100, 210, 90), (40, 140, 50), (180, 200, 60)],    # Xanh tươi tre luồng + măng
        "cay_thong": [(20, 90, 45), (15, 75, 35), (35, 105, 55), (110, 70, 40)]       # Xanh lá kim thẫm + nón thông
    }
    
    created_any = False
    for label, colors in plant_colors.items():
        folder_path = os.path.join(DATASET_DIR, label)
        os.makedirs(folder_path, exist_ok=True)
        existing_files = glob.glob(os.path.join(folder_path, "*.[jJ][pP][gG]")) + \
                         glob.glob(os.path.join(folder_path, "*.[pP][nN][gG]"))
        
        if len(existing_files) < 10:
            print(f"[DATASET] Dang khoi tao 30 anh mau cho lop '{label}'...")
            for i in range(30):
                img = Image.new("RGB", (224, 224), color=colors[i % len(colors)])
                draw = ImageDraw.Draw(img)
                # Thêm họa tiết nhiễu ngẫu nhiên để tạo tính đa dạng cho dataset
                for _ in range(15):
                    x0 = np.random.randint(0, 180)
                    y0 = np.random.randint(0, 180)
                    x1 = x0 + np.random.randint(10, 40)
                    y1 = y0 + np.random.randint(10, 40)
                    accent_color = colors[(i + _) % len(colors)]
                    draw.ellipse([x0, y0, x1, y1], fill=accent_color)
                
                img_file = os.path.join(folder_path, f"sample_{i+1:03d}.png")
                img.save(img_file)
            created_any = True
            
    if created_any:
        print("[DATASET] Hoan tat khoi tao tap du lieu mau.")


def train_model():
    """Huấn luyện mô hình phân loại thực vật và lưu vào thư mục models/."""
    generate_mock_dataset_if_needed()
    
    X, y = [], []
    print("[TRAIN] Dang doc va trich xuat dac trưng du lieu anh...")
    
    for label_idx, label in enumerate(PLANT_LABELS):
        folder_path = os.path.join(DATASET_DIR, label)
        image_paths = glob.glob(os.path.join(folder_path, "*.png")) + \
                      glob.glob(os.path.join(folder_path, "*.jpg"))
        
        for img_path in image_paths:
            try:
                with Image.open(img_path) as img:
                    img_array = preprocess_image(img)
                    feats = extract_color_histogram_features(img_array)
                    X.append(feats)
                    y.append(label_idx)
            except Exception as e:
                print(f"[WARN] Khong the doc file {img_path}: {e}")
                
    if not X:
        print("[ERROR] Khong tim thay du lieu anh de huan luyen!")
        return

    X = np.array(X)
    y = np.array(y)

    print(f"[DATA] Tong so anh thu thap: {len(X)} anh tu {len(PLANT_LABELS)} lop.")
    
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    train_acc = clf.score(X_train, y_train) * 100
    val_acc = clf.score(X_val, y_val) * 100

    print(f"[SUCCESS] Huan luyen thanh cong!")
    print(f"[METRICS] Do chinh xac tap Train: {train_acc:.1f}%")
    print(f"[METRICS] Do chinh xac tap Validation: {val_acc:.1f}%")

    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)

    print(f"[SAVE] Da luu mo hinh tai: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()
