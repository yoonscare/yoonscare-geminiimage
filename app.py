import streamlit as st
import os
import io
import base64
from PIL import Image
import google.generativeai as genai

# 페이지 설정
st.set_page_config(
    page_title="✨ Gemini 이미지 생성기",
    page_icon="🎨",
    layout="wide"
)

# 커스텀 CSS 적용
st.markdown("""
<style>
    .main {
        background-color: #f5f7ff;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    h1, h2, h3 {
        color: #1e3a8a;
        font-weight: 600;
    }
    .stTextInput, .stSlider {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stButton > button {
        background-color: #4f46e5;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #4338ca;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        transform: translateY(-2px);
    }
    .feature-box {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        color: #ffffff;
    }
    .feature-box h3 {
        color: #ffffff;
        font-weight: 600;
    }
    .feature-box p {
        color: #f1f5f9;
        font-size: 16px;
        line-height: 1.6;
    }
    .footer {
        text-align: center;
        margin-top: 30px;
        padding: 20px;
        color: #6b7280;
        font-size: 14px;
    }
    .kakao-link {
        background-color: #FEE500;
        color: #000000;
        padding: 8px 16px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        display: inline-block;
        margin-top: 10px;
    }
    .kakao-link:hover {
        background-color: #F2D900;
    }
    .image-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
    }
    .image-card {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 10px;
        background-color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: transform 0.3s;
    }
    .image-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 사이드바 - API 설정
with st.sidebar:
    st.header("🔑 API 설정")
    api_key = st.text_input("Gemini API 키를 입력하세요", type="password")
    
    st.markdown("---")
    
    st.subheader("🌟 주요 특징")
    
    with st.container():
        st.markdown("""
        <div class="feature-box">
            <h3>🇰🇷 한국어 특화 이미지 생성 솔루션!</h3>
            <p>한글이 포함된 이미지 생성에 특화된 서비스입니다. 일반 AI 도구에서 자주 발생하는 한글 깨짐이나 왜곡 없이 자연스러운 한글 텍스트가 포함된 고품질 이미지를 생성합니다.</p>
            <p>당신의 창의적인 아이디어를 한글로 표현해 보세요!</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 이미지 크기 조절 옵션
    image_size = st.radio(
        "이미지 크기 선택",
        options=["1024x1024", "1152x896", "896x1152"],
        index=0
    )
    
    st.markdown("---")
    
    st.markdown("""
    <div class="footer">
        <p>궁금한 점이 있으신가요? 카카오톡 오픈채팅방에 참여하세요!</p>
        <a href="https://open.kakao.com/o/gJJuZUgg" target="_blank" class="kakao-link">
            💬 윤스케어&도로시J의 제미나이방
        </a>
    </div>
    """, unsafe_allow_html=True)

# 헤더 섹션
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/image/default/48px.svg", width=80)
with col2:
    st.title("✨ Gemini 이미지 생성기")
    st.markdown("By **YOONSCARE**")

# API 키가 입력되지 않은 경우 경고 메시지
if not api_key:
    st.warning("⚠️ 사이드바에 Gemini API 키를 먼저 입력해주세요", icon="⚠️")

# 메인 섹션
st.markdown("### 🖌️ 이미지 생성을 위한 프롬프트를 입력하세요")

prompt = st.text_area(
    "프롬프트 입력",
    value="한글 캘리그라피로 '행복하세요'라는 문구가 쓰여진 우주 배경 이미지",
    height=100
)

# 이미지 생성 수 설정
num_images = st.slider("생성할 이미지 수", min_value=1, max_value=1, value=1)

# 생성 버튼
generate_button = st.button("🚀 생성", use_container_width=True)

# 이미지 생성 함수
def generate_images(prompt, api_key, num_images=1, image_size="1024x1024"):
    try:
        # API 키 설정
        genai.configure(api_key=api_key)
        
        # 모델 설정
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        images = []
        
        with st.spinner(f"🎨 이미지를 생성 중입니다..."):
            for i in range(num_images):
                try:
                    # 이미지 생성 요청 설정
                    generation_config = {
                        "temperature": 1.0,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 8192,
                    }
                    
                    # 이미지 생성 프롬프트 설정
                    image_prompt = f"""
                    {prompt}
                    
                    Generate only the image without any text explanations. Create a high-quality image that includes the Korean text correctly. The text should be clear and easy to read.
                    """
                    
                    # 이미지 생성 요청
                    response = model.generate_content(
                        image_prompt,
                        generation_config=generation_config
                    )
                    
                    # 이미지 데이터 추출
                    for part in response.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            image_data = base64.b64decode(part.inline_data.data)
                            image = Image.open(io.BytesIO(image_data))
                            images.append(image)
                            break
                    
                except Exception as inner_error:
                    st.error(f"이미지 생성 중 오류: {str(inner_error)}")
                    continue
        
        return images
    except Exception as e:
        st.error(f"이미지 생성 중 오류가 발생했습니다: {str(e)}")
        return []

# 이미지 생성 로직
if generate_button:
    if not api_key:
        st.error("⚠️ API 키가 필요합니다! 사이드바에 API 키를 먼저 입력해주세요")
    else:
        # 이미지 생성 실행
        images = generate_images(prompt, api_key, num_images, image_size)
        
        if images:
            st.markdown("### ✅ 생성된 이미지")
            
            # 이미지 표시
            for i, image in enumerate(images):
                st.image(image, caption=f"이미지 #{i+1}", use_column_width=True)
                
                # 이미지 다운로드 버튼
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                st.download_button(
                    label="💾 다운로드",
                    data=buf.getvalue(),
                    file_name=f"gemini_image_{i+1}.png",
                    mime="image/png"
                )
        else:
            st.error("이미지를 생성할 수 없습니다. 다른 프롬프트를 시도하거나 API 키를 확인해보세요.")
