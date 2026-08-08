import os
import time
from datetime import datetime
import streamlit as st
from PIL import Image

from src.predictor import predict_plant_image
from src.plant_manager import get_plant_details, load_all_plant_info
from src.config_manager import (
    load_config,
    get_google_form_url,
    update_google_forms,
    verify_admin_password,
    update_admin_password
)

# ---------------------------------------------------------
# 1. Page Configuration & Custom CSS Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Sinh Học THCS - AI Nhận Diện Thực Vật C3 C4 CAM",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    /* Top Hero Banner */
    .top-hero-banner {
        background: linear-gradient(135deg, #064e3b 0%, #047857 60%, #059669 100%);
        border-radius: 16px;
        padding: 1.8rem 2.2rem;
        color: white;
        margin-bottom: 1.8rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 10px 25px rgba(6, 78, 59, 0.2);
    }
    .top-hero-title {
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #ffffff;
        margin-bottom: 0.6rem;
    }
    .top-hero-sub {
        font-size: 1.15rem;
        font-weight: 600;
        color: #e2e8f0;
        line-height: 1.5;
        max-width: 720px;
        margin-bottom: 1.2rem;
    }
    .top-hero-highlight {
        color: #facc15;
        font-weight: 800;
    }
    .top-hero-tags {
        display: flex;
        gap: 1.8rem;
        font-size: 0.9rem;
        color: #a7f3d0;
        font-weight: 600;
    }
    .top-hero-pills {
        display: flex;
        flex-direction: column;
        gap: 8px;
        align-items: center;
    }
    .pill-c3 {
        background: #16a34a;
        color: white;
        font-weight: 800;
        font-size: 0.9rem;
        padding: 0.35rem 1.1rem;
        border-radius: 20px;
        box-shadow: 0 3px 8px rgba(22, 163, 74, 0.3);
    }
    .pill-c4 {
        background: #f59e0b;
        color: white;
        font-weight: 800;
        font-size: 0.9rem;
        padding: 0.35rem 1.1rem;
        border-radius: 20px;
        box-shadow: 0 3px 8px rgba(245, 158, 11, 0.3);
    }
    .pill-cam {
        background: #8b5cf6;
        color: white;
        font-weight: 800;
        font-size: 0.9rem;
        padding: 0.35rem 1.1rem;
        border-radius: 20px;
        box-shadow: 0 3px 8px rgba(139, 92, 246, 0.3);
    }

    /* Mobile Responsive Optimizations */
    @media (max-width: 768px) {
        .top-hero-banner {
            flex-direction: column;
            align-items: flex-start;
            padding: 1.3rem 1.4rem;
            gap: 1rem;
        }
        .top-hero-title {
            font-size: 1.4rem;
        }
        .top-hero-sub {
            font-size: 0.95rem;
            margin-bottom: 0.8rem;
        }
        .top-hero-tags {
            flex-direction: column;
            gap: 0.4rem;
            font-size: 0.82rem;
        }
        .top-hero-pills {
            flex-direction: row;
            width: 100%;
            justify-content: flex-start;
            gap: 10px;
        }
        .card-box {
            padding: 1rem 1.1rem;
        }
        .info-table td {
            font-size: 0.85rem;
        }
        .comp-table {
            font-size: 0.78rem;
        }
        .comp-table th, .comp-table td {
            padding: 0.4rem 0.3rem;
        }
    }

    /* Result Header */
    .result-header-container {
        background: linear-gradient(135deg, #065f46 0%, #047857 100%);
        padding: 1.8rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px rgba(6, 95, 70, 0.15);
    }
    .result-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        color: #ffffff;
    }
    .result-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 0.35rem 1rem;
        border-radius: 30px;
        background: #d1fae5;
        color: #065f46;
        font-weight: 700;
        font-size: 0.95rem;
        margin-top: 0.6rem;
    }
    .result-subtext {
        color: #a7f3d0;
        font-size: 1rem;
        margin-top: 0.4rem;
        font-style: italic;
    }

    /* Cards System */
    .card-box {
        background: #ffffff;
        border-radius: 14px;
        padding: 1.3rem 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        margin-bottom: 1.3rem;
    }
    .card-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #065f46;
        margin-bottom: 1rem;
        border-bottom: 2px solid #ecfdf5;
        padding-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }

    /* Info Table */
    .info-table {
        width: 100%;
        border-collapse: collapse;
    }
    .info-table td {
        padding: 0.5rem 0.4rem;
        font-size: 0.95rem;
    }
    .info-table td.label-col {
        color: #475569;
        font-weight: 600;
        width: 45%;
    }
    .info-table td.val-col {
        color: #0f172a;
        font-weight: 700;
    }

    /* Comparison Table Styling */
    .comp-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    .comp-table th, .comp-table td {
        border: 1px solid #e2e8f0;
        padding: 0.6rem 0.5rem;
        text-align: center;
    }
    .comp-table th {
        background-color: #f8fafc;
        color: #0f172a;
        font-weight: 700;
    }
    .comp-table th.highlight-cam {
        background-color: #fef3c7;
        color: #92400e;
    }
    .comp-table th.highlight-c3 {
        background-color: #e0f2fe;
        color: #075985;
    }
    .comp-table th.highlight-c4 {
        background-color: #dcfce7;
        color: #166534;
    }

    /* Google Form Banner */
    .gf-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border-radius: 16px;
        padding: 1.8rem 2rem;
        color: white;
        text-align: center;
        margin-top: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(30, 27, 75, 0.2);
    }
    .gf-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #fef08a;
        margin-bottom: 0.5rem;
    }
    .gf-subtitle {
        color: #c7d2fe;
        font-size: 1rem;
        margin-bottom: 1.2rem;
    }
    .gf-button {
        display: inline-block;
        background: #22c55e;
        color: #ffffff !important;
        font-weight: 800;
        font-size: 1.1rem;
        padding: 0.8rem 2.2rem;
        border-radius: 30px;
        text-decoration: none !important;
        box-shadow: 0 4px 14px rgba(34, 197, 94, 0.4);
        transition: all 0.2s ease;
    }
    .gf-button:hover {
        background: #16a34a;
        transform: translateY(-2px);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. Model Loading & Cache
# ---------------------------------------------------------
@st.cache_resource
def load_trained_model():
    model_path_pt = os.path.join("models", "plant_mobilenetv3.pt")
    if os.path.exists(model_path_pt):
        try:
            import torch
            import torch.nn as nn
            from torchvision import models
            
            weights = models.MobileNet_V3_Small_Weights.DEFAULT
            model = models.mobilenet_v3_small(weights=weights)
            in_features = model.classifier[3].in_features
            model.classifier[3] = nn.Linear(in_features, 3)
            model.load_state_dict(torch.load(model_path_pt, map_location="cpu"))
            model.eval()
            return model
        except Exception as e:
            print(f"[WARN] Failed to load PyTorch model: {e}")
            return None
    return None

model = load_trained_model()


# ---------------------------------------------------------
# 3. Sidebar Navigation
# ---------------------------------------------------------
with st.sidebar:
    st.title("🌿 Trợ Lý Học Tập Thông Minh")
    st.caption("Ứng dụng học tập & phân loại tiêu bản thực vật")
    
    menu = st.radio(
        "Chuyển trang:",
        [
            "🔬 Nhận Diện AI",
            "🔑 Quản Trị Admin"
        ]
    )
    
    st.divider()
    st.markdown("### 📌 Các nhóm thực vật hỗ trợ")
    st.markdown("• 🌾 **Thực vật C3** *(Lúa, Khoai, Sắn...)*")
    st.markdown("• 🌽 **Thực vật C4** *(Ngô, Mía, Cao lương...)*")
    st.markdown("• 🌵 **Thực vật CAM** *(Xương rồng, Nha đam, Dứa...)*")


# ---------------------------------------------------------
# 4. TAB 1: NHẬN DIỆN AI & GIAO DIỆN HIỂN VI TRUYỀN THỐNG
# ---------------------------------------------------------
if menu == "🔬 Nhận Diện AI":
    st.markdown("""
    <div class="top-hero-banner">
        <div>
            <div class="top-hero-title">🌿 TRỢ LÝ HỌC TẬP THÔNG MINH</div>
            <div class="top-hero-sub">
                Ứng dụng trí tuệ nhân tạo hỗ trợ nhận diện và học tập giải phẫu lá thực vật <span class="top-hero-highlight">C3, C4, CAM</span>
            </div>
            <div class="top-hero-tags">
                <span>🎯 Nhận diện chính xác</span>
                <span>📚 Học tập hiệu quả</span>
                <span>🍃 Hiểu sâu kiến thức sinh học</span>
            </div>
        </div>
        <div class="top-hero-pills">
            <div class="pill-c3">C3</div>
            <div class="pill-c4">C4</div>
            <div class="pill-cam">CAM</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_input, col_display = st.columns([1, 2.5], gap="large")

    with col_input:
        st.subheader("📸 Tải Ảnh Tiêu Bản Lá")
        input_type = st.radio("Nguồn hình ảnh:", ["Tải ảnh lên từ thiết bị", "Chụp bằng Webcam"], horizontal=True)
        
        uploaded_image = None
        if input_type == "Tải ảnh lên từ thiết bị":
            file = st.file_uploader("Chọn hình ảnh (JPG, PNG, WEBP):", type=["jpg", "jpeg", "png", "webp"])
            if file is not None:
                uploaded_image = Image.open(file)
        else:
            camera_file = st.camera_input("Chụp ảnh tiêu bản:")
            if camera_file is not None:
                uploaded_image = Image.open(camera_file)

        if uploaded_image is not None:
            st.image(uploaded_image, caption="Hình ảnh tiêu bản đầu vào", use_container_width=True)
            with st.spinner("🤖 AI đang phân tích vi cấu trúc mô học lá..."):
                pred_result = predict_plant_image(uploaded_image, model=model)
                st.session_state["last_prediction"] = pred_result
                st.session_state["pred_timestamp"] = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        else:
            st.info("👋 Hãy tải lên ảnh lát cắt ngang mô lá C3, C4 hoặc CAM để xem kết quả nhận diện!")

    with col_display:
        if "last_prediction" in st.session_state and st.session_state["last_prediction"] is not None:
            pred = st.session_state["last_prediction"]
            plant_key = pred["plant_key"]
            conf_pct = pred["confidence_percentage"]
            timestamp_str = st.session_state.get("pred_timestamp", datetime.now().strftime("%d/%m/%Y - %H:%M:%S"))

            plant_info = get_plant_details(plant_key)
            sample = plant_info.get("sample_info", {})
            form_url = get_google_form_url(plant_key)

            # Header Banner
            st.markdown(f"""
            <div class="result-header-container">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div class="result-title">{plant_info['display_name']}</div>
                        <div class="result-badge">🛡️ Độ tin cậy AI: {conf_pct}%</div>
                        <div class="result-subtext">{plant_info.get('badge_text', '')}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.write("")

            # ---------------------------------------------------------
            # ROW 1: Section 1 (Left) & Section 2 (Right)
            # ---------------------------------------------------------
            col_r1_left, col_r1_right = st.columns([1, 1], gap="medium")

            with col_r1_left:
                # 1. THÔNG TIN MẪU
                st.markdown(f"""
                <div class="card-box">
                    <div class="card-title">1. THÔNG TIN MẪU</div>
                    <table class="info-table">
                        <tr><td class="label-col">🌱 Nhóm thực vật:</td><td class="val-col">{plant_key}</td></tr>
                        <tr><td class="label-col">📅 Ngày nhận diện:</td><td class="val-col">{timestamp_str}</td></tr>
                        <tr><td class="label-col">🔬 Loại tiêu bản:</td><td class="val-col">{sample.get('sample_type', 'Lá (lát cắt ngang)')}</td></tr>
                        <tr><td class="label-col">🔬 Phương pháp:</td><td class="val-col">{sample.get('method', 'Ảnh hiển vi')}</td></tr>
                        <tr><td class="label-col">🔍 Độ phóng đại:</td><td class="val-col">{sample.get('magnification', '100x')}</td></tr>
                    </table>
                    <div style="margin-top: 1rem;">
                        <div style="font-weight: 700; font-size: 0.85rem; color: #475569; margin-bottom: 0.4rem; text-transform: uppercase;">HÌNH THÁI BÊN NGOÀI (THAM KHẢO)</div>
                        <img src="{sample.get('morphology_img', '')}" style="width: 100%; height: 160px; object-fit: cover; border-radius: 10px;">
                        <p style="font-size: 0.82rem; color: #64748b; margin-top: 0.4rem; line-height: 1.3;">{sample.get('morphology_desc', '')}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_r1_right:
                # 2. HÌNH ÁNH TIÊU BẢN VÀ CHÚ THÍCH CẤU TRÚC
                st.markdown("""
                <div class="card-box" style="margin-bottom: 0.8rem;">
                    <div class="card-title">2. HÌNH ÁNH TIÊU BẢN VÀ CHÚ THÍCH CẤU TRÚC</div>
                </div>
                """, unsafe_allow_html=True)
                
                struct_img = plant_info.get('structure_img', '')
                if struct_img:
                    st.image(struct_img, use_container_width=True)

            # ---------------------------------------------------------
            # ROW 2: Section 3 & 4 (Left) & Section 5 (Right)
            # ---------------------------------------------------------
            col_r2_left, col_r2_right = st.columns([1, 1], gap="medium")

            with col_r2_left:
                # 3. NỘI DUNG TÓM TẮT CỦA LOÀI
                st.markdown(f"""
                <div class="card-box">
                    <div class="card-title">3. NỘI DUNG TÓM TẮT CỦA LOÀI</div>
                    <p style="color: #334155; line-height: 1.6; font-size: 0.95rem; margin: 0;">
                        {plant_info.get('summary', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # 4. SO SÁNH VỚI CÁC NHÓM THỰC VẬT KHÁC
                st.markdown("""
                <div class="card-box">
                    <div class="card-title">4. SO SÁNH VỚI CÁC NHÓM THỰC VẬT KHÁC</div>
                    <div style="overflow-x: auto;">
                        <table class="comp-table">
                            <thead>
                                <tr>
                                    <th>Đặc điểm</th>
                                    <th class="highlight-c3">C3</th>
                                    <th class="highlight-c4">C4</th>
                                    <th class="highlight-cam">CAM</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><b>Cấu tạo Kranz</b></td>
                                    <td>Không</td>
                                    <td style="color: #16a34a; font-weight: 700;">Có</td>
                                    <td>Không</td>
                                </tr>
                                <tr>
                                    <td><b>Mô giậu</b></td>
                                    <td>Phát triển mạnh</td>
                                    <td>Phát triển</td>
                                    <td>Không rõ ràng</td>
                                </tr>
                                <tr>
                                    <td><b>Mô khuyết</b></td>
                                    <td>Phát triển mạnh</td>
                                    <td>Ít phát triển</td>
                                    <td>Không có</td>
                                </tr>
                                <tr>
                                    <td><b>Mô dự trữ nước</b></td>
                                    <td>Không có</td>
                                    <td>Không có</td>
                                    <td style="color: #d97706; font-weight: 700;">Phát triển rất rõ</td>
                                </tr>
                                <tr>
                                    <td><b>Bó mạch</b></td>
                                    <td>Nhỏ</td>
                                    <td>Lớn, nhiều</td>
                                    <td>Trung bình, thưa</td>
                                </tr>
                                <tr>
                                    <td><b>Khí khổng</b></td>
                                    <td>Hai mặt lá</td>
                                    <td>Hai mặt lá</td>
                                    <td style="color: #d97706; font-weight: 700;">Chủ yếu mặt dưới (mở ban đêm)</td>
                                </tr>
                                <tr>
                                    <td><b>Thích nghi</b></td>
                                    <td>Môi trường ôn hòa, ẩm</td>
                                    <td>Nhiệt độ cao, ánh sáng mạnh</td>
                                    <td>Môi trường khô hạn, thiếu nước</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_r2_right:
                # 5. KIẾN THỨC MỞ RỘNG
                highlights_html = "".join([f"<li>{h}</li>" for h in plant_info.get("highlights", [])])
                examples = plant_info.get("examples", [])
                
                ex_items = []
                for ex in examples:
                    ex_items.append(
                        f'<div style="flex: 1 1 45%; min-width: 110px; text-align: center; background: #f8fafc; padding: 0.5rem; border-radius: 8px; border: 1px solid #e2e8f0; box-sizing: border-box;">'
                        f'<img src="{ex["img"]}" style="width: 100%; height: 75px; object-fit: cover; border-radius: 6px;">'
                        f'<div style="font-size: 0.78rem; font-weight: 700; color: #334155; margin-top: 0.3rem;">{ex["name"]}</div>'
                        f'</div>'
                    )
                ex_grid_html = f'<div style="display: flex; flex-wrap: wrap; gap: 8px;">{"".join(ex_items)}</div>'

                st.markdown(f"""
                <div class="card-box">
                    <div class="card-title">5. KIẾN THỨC MỞ RỘNG</div>
                    <div style="font-weight: 700; color: #065f46; margin-bottom: 0.4rem;">Đặc điểm nổi bật của {plant_info['display_name']}</div>
                    <ul style="padding-left: 1.2rem; color: #334155; font-size: 0.9rem; line-height: 1.5; margin-bottom: 1rem;">
                        {highlights_html}
                    </ul>
                    <div style="font-weight: 700; color: #065f46; margin-bottom: 0.5rem;">Ví dụ điển hình:</div>
                    {ex_grid_html}
                </div>
                """, unsafe_allow_html=True)

            # ---------------------------------------------------------
            # 🎯 GOOGLE FORM CALL-TO-ACTION BANNER
            # ---------------------------------------------------------
            st.markdown(f"""
            <div class="gf-banner">
                <div class="gf-title">📝 ĐÁNH GIÁ KIẾN THỨC BÀI HỌC ({plant_info['display_name']})</div>
                <div class="gf-subtitle">Học sinh vui lòng bấm vào nút bên dưới để hoàn thành bài tập trắc nghiệm trên Google Form!</div>
                <a href="{form_url}" target="_blank" class="gf-button">
                    🚀 MỞ BÀI KIỂM TRA GOOGLE FORM ↗
                </a>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.warning("Vui lòng tải ảnh tiêu bản ở cột bên trái để hiển thị kết quả nhận diện.")


# ---------------------------------------------------------
# 6. TAB 3: TRANG QUẢN TRỊ ADMIN (ADMIN MANAGEMENT)
# ---------------------------------------------------------
elif menu == "🔑 Quản Trị Admin":
    st.title("🔑 Trang Quản Trị Hệ Thống (Admin Portal)")
    st.caption("Quản lý cấu hình liên kết Google Form cho các bài tập nhận diện")

    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if not st.session_state["admin_logged_in"]:
        st.subheader("🔒 Đăng Nhập Quản Trị")
        pwd = st.text_input("Nhập mật khẩu Admin:", type="password", key="input_admin_pwd")
        if st.button("Đăng Nhập 🔑", type="primary"):
            if verify_admin_password(pwd):
                st.session_state["admin_logged_in"] = True
                st.success("✅ Đăng nhập Admin thành công!")
                st.rerun()
            else:
                st.error("❌ Mật khẩu Admin không chính xác!")
    else:
        st.success("🔑 Bạn đang đăng nhập với quyền Quản trị viên (Admin).")
        
        if st.button("Đăng Xuất 🚪"):
            st.session_state["admin_logged_in"] = False
            st.rerun()

        st.divider()
        st.subheader("📝 1. Cấu Hình Liên Kết Google Form Cho Từng Nhóm Cây")
        st.write("Dán liên kết (URL) bài tập Google Form tương ứng với từng loài cây sau khi nhận diện xong:")

        config = load_config()
        forms = config.get("google_forms", {})

        with st.form("admin_form_config"):
            c3_link = st.text_input("🔗 Đường dẫn Google Form cho THỰC VẬT C3:", value=forms.get("C3", ""))
            c4_link = st.text_input("🔗 Đường dẫn Google Form cho THỰC VẬT C4:", value=forms.get("C4", ""))
            cam_link = st.text_input("🔗 Đường dẫn Google Form cho THỰC VẬT CAM:", value=forms.get("CAM", ""))

            save_btn = st.form_submit_button("Lưu Cấu Hình Google Form 💾", type="primary")

        if save_btn:
            if update_google_forms(c3_link, c4_link, cam_link):
                st.success("✅ Đã lưu cấu hình liên kết Google Form thành công!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Không thể lưu cấu hình. Vui lòng kiểm tra lại quyền ghi file.")

        st.divider()
        st.subheader("🔐 2. Đổi Mật Khẩu Admin")
        with st.form("admin_change_pwd"):
            new_pwd = st.text_input("Mật khẩu mới:", type="password")
            confirm_pwd = st.text_input("Xác nhận mật khẩu mới:", type="password")
            change_pwd_btn = st.form_submit_button("Đổi Mật Khẩu 🔑")

        if change_pwd_btn:
            if not new_pwd.strip():
                st.error("⚠️ Mật khẩu mới không được để trống!")
            elif new_pwd.strip() != confirm_pwd.strip():
                st.error("⚠️ Mật khẩu mới và xác nhận mật khẩu không khớp!")
            else:
                if update_admin_password(new_pwd):
                    st.success("✅ Đã đổi mật khẩu Admin thành công!")
                else:
                    st.error("❌ Đổi mật khẩu thất bại.")
