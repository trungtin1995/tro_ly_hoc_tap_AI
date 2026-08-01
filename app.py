import os
import pickle
import streamlit as st
from PIL import Image

from src.predictor import predict_plant_image
from src.quiz_engine import (
    load_quiz_data,
    get_plant_quiz,
    evaluate_quiz,
    load_submissions,
    has_student_submitted,
    save_submission,
    reset_submissions
)

# ---------------------------------------------------------
# 1. Page Configuration & Custom CSS Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Sinh Học THCS - AI Nhận Diện Thực Vật",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Main Hero Banner */
    .hero-header {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 2.2rem 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(17, 153, 142, 0.25);
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        opacity: 0.95;
        margin-top: 0.5rem;
        font-weight: 500;
    }

    /* Cards */
    .info-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        margin-bottom: 1.2rem;
    }
    .result-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 30px;
        background: #e6fffa;
        color: #047857;
        font-weight: 700;
        font-size: 0.95rem;
        border: 1px solid #a7f3d0;
    }
    .submitted-banner {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-left: 5px solid #3b82f6;
        padding: 1.2rem;
        border-radius: 12px;
        color: #1e3a8a;
        margin-bottom: 1.2rem;
    }
    .explanation-box {
        background: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-top: 0.6rem;
        font-size: 0.95rem;
        color: #065f46;
    }
    .wrong-box {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-top: 0.6rem;
        font-size: 0.95rem;
        color: #991b1b;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. Resource Loading & Model Cache
# ---------------------------------------------------------
@st.cache_resource
def load_trained_model():
    model_path = os.path.join("models", "plant_classifier.pkl")
    if os.path.exists(model_path):
        try:
            with open(model_path, "rb") as f:
                return pickle.load(f)
        except Exception:
            return None
    return None

model = load_trained_model()
all_quizzes = load_quiz_data()


# ---------------------------------------------------------
# 3. Sidebar Navigation
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/illustrations/200/leaf.png", width=120)
    st.title("🌿 Sinh Học THCS AI")
    st.caption("Ứng dụng học tập thông minh cho học sinh THCS")
    
    menu = st.radio(
        "Chuyển trang:",
        [
            "🔬 Nhận Diện & Trắc Nghiệm",
            "📚 Ngân Hàng Kiến Thức",
            "🏆 Bảng Thành Tích & Lịch Sử"
        ]
    )
    
    st.divider()
    st.markdown("### 📌 Danh mục Thực vật")
    st.markdown("• 🪷 **Cây Sen** *(Hạt kín - 2 lá mầm)*")
    st.markdown("• 🎋 **Cây Tre** *(Hạt kín - 1 lá mầm)*")
    st.markdown("• 🌲 **Cây Thông** *(Hạt trần)*")


# ---------------------------------------------------------
# 4. Tab 1: Nhận Diện & Trắc Nghiệm (Main Page)
# ---------------------------------------------------------
if menu == "🔬 Nhận Diện & Trắc Nghiệm":
    st.markdown("""
    <div class="hero-header">
        <div class="hero-title">🌿 Nhận Diện Thực Vật & Thử Thách Trắc Nghiệm</div>
        <div class="hero-subtitle">Nhập thông tin học sinh, tải ảnh thực vật để AI nhận diện và nộp bài làm (Mỗi học sinh nộp bài 1 lần duy nhất)!</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("👤 1. Thông Tin Học Sinh Bắt Buộc")
        student_name = st.text_input("Họ và Tên học sinh:", placeholder="Ví dụ: Nguyễn Văn A", key="input_student_name")
        student_id = st.text_input("Mã số Học sinh / Lớp:", placeholder="Ví dụ: HS001 - Lớp 7A1", key="input_student_id")
        
        if not student_name.strip() or not student_id.strip():
            st.warning("⚠️ Học sinh vui lòng điền đầy đủ **Họ tên** và **Mã số học sinh** trước khi làm bài trắc nghiệm.")
        else:
            st.success(f"👤 Xin chào: **{student_name.strip()}** (Mã số: **{student_id.strip()}**)")

        st.divider()
        st.subheader("📸 2. Tải ảnh hoặc Chụp ảnh thực vật")
        input_type = st.radio("Lựa chọn nguồn ảnh:", ["Tải ảnh lên từ thiết bị", "Chụp bằng Webcam"], horizontal=True)
        
        uploaded_image = None
        if input_type == "Tải ảnh lên từ thiết bị":
            file = st.file_uploader("Chọn hình ảnh thực vật (JPG, PNG, JPEG):", type=["jpg", "jpeg", "png"])
            if file is not None:
                uploaded_image = Image.open(file)
        else:
            camera_file = st.camera_input("Chụp hình cây thực tế:")
            if camera_file is not None:
                uploaded_image = Image.open(camera_file)

        if uploaded_image is not None:
            st.image(uploaded_image, caption="Hình ảnh thực vật đầu vào", width="stretch")
            
            with st.spinner("🤖 AI đang phân tích đường nét và đặc điểm loài cây..."):
                pred_result = predict_plant_image(uploaded_image, model=model)
                st.session_state["last_prediction"] = pred_result
        else:
            st.info("👋 Hãy tải lên một tấm ảnh Cây Sen, Cây Tre hoặc Cây Thông để bắt đầu!")

    with col2:
        st.subheader("🔍 3. Kết quả Phân loại AI")
        
        if "last_prediction" in st.session_state and st.session_state["last_prediction"] is not None:
            pred = st.session_state["last_prediction"]
            plant_key = pred["plant_key"]
            conf_pct = pred["confidence_percentage"]
            
            plant_info = get_plant_quiz(plant_key)
            
            st.markdown(f"""
            <div class="info-card">
                <span class="result-badge">Độ tin cậy AI: {conf_pct}%</span>
                <h2 style="color: #065f46; margin-top: 0.8rem; font-weight: 800;">{plant_info['display_name']}</h2>
                <p><b>Tên khoa học:</b> <i>{plant_info['scientific_name']}</i></p>
                <p><b>Phân nhóm Sinh học:</b> {plant_info.get('group', 'Chưa rõ')}</p>
                <p><b>Môi trường sống:</b> {plant_info.get('habitat', 'Chưa rõ')}</p>
                <p style="color: #475569; margin-top: 0.5rem;">{plant_info.get('description', '')}</p>
            </div>
            """, unsafe_allow_html=True)

            # Check if student has already submitted for this plant_key
            already_submitted, existing_sub = has_student_submitted(student_id, plant_key)

            st.subheader("📝 4. Bài Kiểm Tra Kiến Thức Tương Tác")

            if not student_name.strip() or not student_id.strip():
                st.error("🔒 Hãy nhập thông tin Họ tên & Mã số học sinh ở cột bên trái để mở bài làm trắc nghiệm!")
            
            elif already_submitted and existing_sub is not None:
                # Màn hình review cho học sinh đã nộp bài trước đó
                st.markdown(f"""
                <div class="submitted-banner">
                    <b>🔒 BÀI LÀM ĐÃ ĐƯỢC NỘP VÀ KHÓA (LƯU VĨNH VIỄN)</b><br>
                    • Học sinh: <b>{existing_sub['student_name']}</b> (Mã số: {existing_sub['student_id']})<br>
                    • Thời gian nộp bài: <b>{existing_sub['submitted_at']}</b><br>
                    • Kết quả đạt được: <b>{existing_sub['correct_count']} / {existing_sub['total_count']} câu ({existing_sub['percentage']:.0f}%)</b><br>
                    • Danh hiệu: <b>{existing_sub['badge']}</b>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 📖 Xem lại đáp án bài làm đã nộp:")
                for item in existing_sub.get("details", []):
                    if item["is_correct"]:
                        st.markdown(f"""
                        <div class="explanation-box">
                            <b>✅ Câu {item['id']}: Đúng!</b><br>
                            • Câu hỏi: {item['question']}<br>
                            • Lựa chọn của bạn: <b>{item['user_answer']}</b><br>
                            • <i>Giải thích:</i> {item['explanation']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="wrong-box">
                            <b>❌ Câu {item['id']}: Chưa chính xác</b><br>
                            • Câu hỏi: {item['question']}<br>
                            • Lựa chọn của bạn: {item['user_answer']}<br>
                            • Đáp án đúng: <b>{item['correct_answer']}</b><br>
                            • <i>Giải thích:</i> {item['explanation']}
                        </div>
                        """, unsafe_allow_html=True)

            else:
                # Form làm bài mới cho học sinh chưa nộp
                st.caption(f"Dưới đây là các câu hỏi trắc nghiệm Sinh học dành cho **{plant_info['display_name']}**:")
                questions = plant_info.get("questions", [])
                
                with st.form(key=f"quiz_form_{plant_key}_{student_id}"):
                    user_answers = {}
                    for q in questions:
                        st.markdown(f"**Câu {q['id']}: {q['question']}**")
                        choice = st.radio(
                            label=f"Lựa chọn cho câu {q['id']}",
                            options=q["options"],
                            key=f"q_{plant_key}_{student_id}_{q['id']}",
                            label_visibility="collapsed"
                        )
                        user_answers[q["id"]] = choice
                        st.write("")

                    submit_btn = st.form_submit_button("Nộp Bài & Lưu Kết Quả Vĩnh Viễn 🎯", width="stretch")

                if submit_btn:
                    correct_cnt, total_cnt, pct, details, badge = evaluate_quiz(user_answers, questions)
                    # Save to persistent storage data/submissions.json
                    saved_record = save_submission(
                        student_name=student_name,
                        student_id=student_id,
                        plant_key=plant_key,
                        plant_name=plant_info['display_name'],
                        correct_count=correct_cnt,
                        total_count=total_cnt,
                        percentage=pct,
                        details=details,
                        badge=badge
                    )
                    st.success("✅ Nộp bài thành công! Dữ liệu bài làm đã được ghi nhận vào hệ thống.")
                    st.rerun()

        else:
            st.warning("Vui lòng tải ảnh lên ở cột bên trái để hiển thị bài trắc nghiệm.")


# ---------------------------------------------------------
# 5. Tab 2: Ngân Hàng Kiến Thức
# ---------------------------------------------------------
elif menu == "📚 Ngân Hàng Kiến Thức":
    st.title("📚 Ngân Hàng Kiến Thức Thực Vật THCS")
    st.write("Khám phá đặc điểm sinh học chi tiết của các loài thực vật tiêu biểu trong chương trình môn Sinh học:")

    for p_key, p_data in all_quizzes.items():
        with st.expander(f"🌿 {p_data['display_name']} ({p_data['scientific_name']})", expanded=True):
            col_a, col_b = st.columns([1, 2])
            with col_a:
                st.markdown(f"**Phân nhóm:** {p_data.get('group', 'N/A')}")
                st.markdown(f"**Môi trường sống:** {p_data.get('habitat', 'N/A')}")
            with col_b:
                st.write(p_data.get("description", ""))
            
            st.markdown("**Các câu hỏi ôn tập kiến thức:**")
            for q in p_data.get("questions", []):
                st.markdown(f"- **Câu {q['id']}:** {q['question']}")
                st.markdown(f"  *Đáp án đúng:* `{q['answer']}` - *{q['explanation']}*")


# ---------------------------------------------------------
# 6. Tab 3: Bảng Thành Tích & Lịch Sử Nộp Bài
# ---------------------------------------------------------
elif menu == "🏆 Bảng Thành Tích & Lịch Sử":
    st.title("🏆 Bảng Thành Tích & Danh Sách Học Sinh Đã Nộp Bài")
    st.write("Danh sách tổng hợp kết quả và lịch sử làm bài trắc nghiệm của học sinh:")

    submissions = load_submissions()
    
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.markdown(f"### 📊 Tổng số lượt đã nộp: **{len(submissions)}** bài làm")
    with header_col2:
        with st.popover("🗑️ Reset Bảng Kết Quả"):
            st.warning("⚠️ Bạn có chắc chắn muốn xóa toàn bộ danh sách nộp bài không?")
            if st.button("Xác nhận xóa toàn bộ", type="primary", use_container_width=True):
                reset_submissions()
                st.success("✅ Đã reset bảng kết quả thành công!")
                st.rerun()

    if not submissions:
        st.info("Chưa có học sinh nào nộp bài làm. Hãy là người đầu tiên hoàn thành thử thách!")
    else:
        # Display as structured data table
        table_data = []
        for s in submissions:
            table_data.append({
                "Họ và Tên": s.get("student_name", "N/A"),
                "Mã Số HS / Lớp": s.get("student_id", "N/A"),
                "Loài Thực Vật": s.get("plant_name", "N/A"),
                "Kết Quả": f"{s.get('correct_count', 0)}/{s.get('total_count', 0)} ({s.get('percentage', 0):.0f}%)",
                "Danh Hiệu": s.get("badge", "N/A"),
                "Thời Gian Nộp": s.get("submitted_at", "N/A")
            })
            
        st.dataframe(table_data, width="stretch")

        st.divider()
        st.markdown("### 🏅 Các Hạng Mục Danh Hiệu Khen Thưởng:")
        b1, b2, b3 = st.columns(3)
        with b1:
            st.success("🏆 **Nhà Thực Vật Học Nhí Xuất Sắc**\n\nĐạt điểm tuyệt đối 100% trong bài kiểm tra.")
        with b2:
            st.info("🌟 **Nhà Khám Phá Thiên Nhiên Giỏi**\n\nĐạt từ 66% điểm số trở lên.")
        with b3:
            st.warning("🌱 **Học Viên Chăm Chỉ**\n\nHoàn thành bài test và ghi nhận kết quả.")
