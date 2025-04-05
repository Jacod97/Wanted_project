import streamlit as st
import requests
import fitz
from PIL import Image
import base64
from matplotlib import font_manager as fm
import os

API_URL = "http://localhost:8000"

VOICE_OPTIONS = {
    "♀️ 여성 모델": "WOMAN",
    "♂️ 남성 모델": "MAN",
}

def get_korean_font():
    font_candidates = ["NanumGothic", "Malgun Gothic", "AppleGothic", "Droid Sans Fallback"]
    for font_name in font_candidates:
        font_path = fm.findSystemFonts(fontpaths=None, fontext='ttf')
        for path in font_path:
            if font_name in path:
                return path
    return None

def convert_pdf_page_to_image(pdf_bytes, page_num):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[page_num]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

def initialize_session_state():
    defaults = {
        "app_page": "home",
        "current_page": 1,
        "current_slide": 0,
        "presentation_slide": 0,
        "pdf_file": None,
        "pdf_bytes": None,
        "full_document": "",
        "scripts": [],
        "tts_audios": [],
        "total_pages": 0,
        "presentation_completed": False,
        "keywords": [],
        "chat_history": [],
        "selected_voice": "ko-KR-Wavenet-E",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def styled_container():
    st.markdown("""
        <style>
            .stApp {
                font-family: 'NanumGothic', sans-serif;
                background-color: rgba(247, 249, 251, 0.8);
                background-blend-mode: lighten;
            }
            .page-container {
                border: 2px solid #dee2e6;
                padding: 20px;
                margin: 30px 0;
                border-radius: 15px;
                background-color: black;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            }
            .page-title {
                font-size: 1.8em;
                font-weight: bold;
                margin-bottom: 20px;
                color: #2c3e50;
                border-bottom: 2px solid #ced4da;
                padding-bottom: 12px;
            }
            .script-container {
                background-color: #f1f3f5;
                padding: 15px;
                border-radius: 10px;
                margin-top: 15px;
            }
            .audio-container {
                background-color: #e9ecef;
                padding: 10px;
                border-radius: 10px;
                margin-top: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

def set_background(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    background_style = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }}
    </style>
    """
    st.markdown(background_style, unsafe_allow_html=True)

def show_chat_interface():
    if st.session_state.app_page == "presentation" and st.session_state.current_page != 1:
        with st.sidebar:
            image_path = "assets/chatbot1.png"  # 또는 방금 업로드한 파일 경로 사용
            with open(image_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode()

            st.markdown(f"""
                <div style="text-align: left; margin-bottom: 1.5rem;">
                    <img src="data:image/png;base64,{image_base64}" style="width: 60px; margin-bottom: 0.5rem;">
                    <div style="font-size: 1.4rem; font-weight: 700;">💬 AI 오인용</div>
                    <div style="font-size: 0.85rem; color: #adb5bd;">PPT에 관련 질문을 해주세요!</div>
                </div>
                <hr style="margin-top: 1rem; margin-bottom: 1rem;">
            """, unsafe_allow_html=True)

            # 이전 질문-답변 출력
            for chat in st.session_state.chat_history:
                # 사용자 메시지 (오른쪽 정렬)
                st.markdown(f"""
                <div style="text-align: right; margin: 10px 0;">
                    <div style="
                        display: inline-block;
                        background-color: #d1e7dd;
                        color: black;
                        padding: 10px 15px;
                        border-radius: 15px;
                        border-bottom-right-radius: 0;
                        max-width: 70%;
                        font-size: 0.95rem;
                    ">
                        {chat['question']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 챗봇 메시지 (왼쪽 정렬, '챗봇' 라벨 포함)
                st.markdown(f"""
                <div style="text-align: left; margin: 10px 0;">
                    <div style="font-size: 0.90rem; color: #000000; margin-left: 5px; margin-bottom: 3px;">AI 오인용</div>
                    <div style="
                        display: inline-block;
                        background-color: #ffffff;
                        color: black;
                        padding: 10px 15px;
                        border-radius: 15px;
                        border-bottom-left-radius: 0;
                        max-width: 70%;
                        font-size: 0.95rem;
                    ">
                        {chat['answer']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # 질문 입력
            user_question = st.chat_input("질문을 입력하세요")
            if user_question:
                try:
                    with st.spinner("생각 중입니다..."):
                        response = requests.post(
                            f"{API_URL}/chat",
                            json={"question": user_question, "session_id": "streamlit_session"}
                        )
                    if response.status_code == 200:
                        st.session_state.chat_history.append({
                            "question": user_question,
                            "answer": response.json()["answer"]
                        })
                        st.rerun()
                    else:
                        st.error("답변 생성 중 오류가 발생했습니다.")
                except Exception as e:
                    st.error(f"오류 발생: {str(e)}")

def render_home_page():
    # 상단 타이틀 박스
    st.markdown(f"""
    <div style='
        display: flex;
        justify-content: center;
        margin-bottom: 30px;
    '>
        <img 
            src='data:image/png;base64,{base64.b64encode(open("assets/title_image.png", "rb").read()).decode()}'
            style='
                width: 100%;
                max-width: 860px;
                height: auto;
                border-radius: 15px;
                # box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            '
        >
    </div>
    """, unsafe_allow_html=True)

    # 사용 가이드 박스
    st.markdown(f"""
    <div style='
        padding: 25px 30px;
        border-left: 6px solid #ffc107;
        background-color: #fffbea;
        border-radius: 12px;
        margin-bottom: 30px;
    '>
        <h3 style='margin-top: 0;'>📝 사용 가이드</h3>
        <ul style='padding-left: 1.2rem; font-size: 1.05rem; color: #343a40; line-height: 1.7;'>
            <li><strong>발표자료를 <span style="color:#ff0000;">PDF 파일</span>로 업로드해주세요.</strong></li>
            <li><strong><span style="color:#ff0000;">5문단</span> 이상의 <span style="color:#ff0000;">프로젝트 스토리</span>를 작성해주세요.</strong></li>
            <li><strong>입력하시는 <span style="color:#ff0000;">프로젝트의 스토리가 구체적일수록</span> 대본의 퀄리티가 올라갑니다.</strong></li>
            <li><strong>강조하고 싶은 단어는 <span style="color:#ff0000;">쉼표(,)</span>로 구분하여 입력해주세요.</strong></li>
            <li><strong><span style="color:#ff0000;">내용이 없는 파티션 슬라이드(간지)</span>는 제거해주세요.</strong></li>
            <li><strong>스크립트 생성에는 발표자료의 길이에 따라 <span style="color:#ff0000;">다소 시간(수 분 가량)</span>이 소요될 수 있습니다.</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # 스타일 적용 (버튼 텍스트 크기, 여백, 색상 등)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📢 발표하러 가기", key="start_presentation"):
            st.session_state.app_page = "presentation"
            st.session_state.current_page = 1
            st.session_state.current_slide = 0
            st.rerun()

    # 커스터마이즈 스타일
    st.markdown("""
    <style>
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #f5d5ba, #f9e0c6);
        color: black;
        font-size: 1.3rem;
        font-weight: 600;
        padding: 16px 36px;
        border: none;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.2);
    }
    div.stButton {
        display: flex;
        justify-content: center;
        margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

def render_presentation_workflow():
    font_path = get_korean_font()
    if font_path:
        styled_container()

    st.markdown("""
    <div style='
        border: 2px solid black;
        border-radius: 15px;
        padding: 30px;
        background-color: transparent;
        margin-bottom: 2rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
    '>
        <img src='data:image/png;base64,{}' width='80' style='margin-bottom: 0;'>
        <h1 style='margin: 0;'>발표 준비 단계</h1>
    </div>
    """.format(base64.b64encode(open("assets/image6.png", "rb").read()).decode()), unsafe_allow_html=True)

    if st.session_state.current_page == 1:
        st.subheader("1단계. 발표자료 및 정보 입력")

        with st.container():
            # 🎙️ TTS 선택
            st.markdown("<div class='container-box'>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 10px; font-size: 1.2rem; font-weight: bold;'>🎙️ TTS 목소리 선택</div>", unsafe_allow_html=True)
            st.session_state.selected_voice = st.selectbox("", options=list(VOICE_OPTIONS.values()),
                                                           format_func=lambda x: [k for k, v in VOICE_OPTIONS.items() if v == x][0])
            st.markdown("</div>", unsafe_allow_html=True)

            # ✔️ 키워드
            st.markdown("<div class='container-box'>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 10px; font-size: 1.2rem; font-weight: bold;'>✔️ 강조할 키워드 (쉼표로 구분)</div>", unsafe_allow_html=True)
            keywords_input = st.text_input("", value=", ".join(st.session_state.keywords), placeholder="인공지능, 발표, 기획, 자동화")
            st.session_state.keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
            st.markdown("</div>", unsafe_allow_html=True)

            # 📜 PDF 업로드
            st.markdown("<div class='container-box'>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 10px; font-size: 1.2rem; font-weight: bold;'>📜 PDF 발표자료 업로드</div>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("", type=['pdf'])
            if uploaded_file:
                st.session_state.pdf_file = uploaded_file
                st.session_state.pdf_bytes = uploaded_file.read()
                doc = fitz.open(stream=st.session_state.pdf_bytes, filetype="pdf")
                st.session_state.total_pages = len(doc)
                st.success(f"✔️ PDF 업로드 완료 ({st.session_state.total_pages}페이지)")
            st.markdown("</div>", unsafe_allow_html=True)

            # 📖 스토리 입력
            st.markdown("<div class='container-box'>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 10px; font-size: 1.2rem; font-weight: bold;'>📖 프로젝트 스토리 입력</div>", unsafe_allow_html=True)
            st.session_state.full_document = st.text_area(
                "",
                height=200,
                placeholder=(
                    "1. 프로젝트 배경과 필요성\n"
                    "발표에 대한 두려움과 어려움을 해결하고자 누구나 쉽게 발표할 수 있는 자동화 시스템의 필요성이 대두되었습니다.\n\n"
                    "2. 프로젝트 개요와 시스템 구조\n"
                    "PDF와 요약 텍스트를 입력하면 AI가 자동으로 대본을 생성하고 음성으로 변환하여 발표와 Q&A까지 지원하는 시스템을 개발했습니다.\n\n"
                    "3. 기술 구성 및 핵심 기능\n"
                    "GPT-4o-mini, LangChain, FastAPI 기반의 시스템은 대본 생성, TTS 발표, 실시간 챗봇 기능과 다양한 발표 최적화 기술을 포함합니다.\n\n"
                    "4. 미래 확장성\n"
                    "보안 강화, 캐릭터 도입, 실시간 인터랙션 등으로 다양한 발표 환경에 확장 가능한 구조를 지향합니다.\n\n"
                    "5. 활용 계획\n"
                    "교육, 기업, 고객 응대 등 다양한 분야에서 자동 발표 시스템으로 활용될 수 있습니다."
                )
            )
            st.markdown("</div>", unsafe_allow_html=True)

            # 다음 단계 버튼
            if all([st.session_state.pdf_file, st.session_state.full_document, st.session_state.keywords]):
                col_btn = st.columns([1, 2, 1])
                with col_btn[1]:
                    if st.button(":arrow_right: 다음 단계로 이동", key="next_step_button"):
                        st.session_state.current_page = 2
                        st.rerun()
            else:
                st.info("❗ 모든 항목을 입력해야 다음 단계로 진행됩니다.")

    elif st.session_state.current_page == 2:
        st.subheader("2단계. 슬라이드별 스크립트 생성 및 확인")
        st.markdown("<script>window.scrollTo(0, 0);</script>", unsafe_allow_html=True)

        if not st.session_state.scripts:
            with st.spinner("스크립트와 음성 생성 중..."):
                try:
                    files = {"file": ("document.pdf", st.session_state.pdf_bytes, "application/pdf")}
                    data = {"full_document": st.session_state.full_document}
                    response = requests.post(f"{API_URL}/generate-script", files=files, data=data)
                    if response.status_code == 200:
                        st.session_state.scripts = response.json() 
                        
                        # 🎯 Q&A 활성화 요청
                        script_data = [{"page": i, "script": s if isinstance(s, str) else s.get("script", "")}
                                    for i, s in enumerate(st.session_state.scripts)]
                        enable_res = requests.post(f"{API_URL}/qa/enable", json={
                            "full_document": st.session_state.full_document,
                            "script_data": script_data
                        })

                        gender = st.session_state.selected_voice

                        audio_res = requests.post(f"{API_URL}/generate-audio", json={
                            "scripts": {str(i): s if isinstance(s, str) else s.get("script", "") for i, s in enumerate(st.session_state.scripts)},
                            "keywords": st.session_state.keywords,
                            "gender": gender  # 명시적으로 전달
                        })
                        if audio_res.status_code == 200:
                            st.session_state.tts_audios = audio_res.json()
                            st.markdown("""
                            <style>
                            .success-highlight {
                                background-color: #d1e7dd;
                                color: #0f5132;
                                padding: 1rem;
                                border-left: 6px solid #0f5132;
                                border-radius: 8px;
                                font-weight: bold;
                                font-size: 1.05rem;
                            }
                            </style>
                            """, unsafe_allow_html=True
                            )
                            st.markdown('<div class="success-highlight">☑️ 전체 스크립트와 음성이 생성되었습니다!</div>', unsafe_allow_html=True)
                        else:
                            st.error(f"TTS 생성 오류: {audio_res.text}")
                    else:
                        st.error(f"API 오류: {response.text}")
                except Exception as e:
                    st.error(f"스크립트 생성 실패: {str(e)}")

        if st.session_state.scripts:
            page_num = st.session_state.current_slide
            st.markdown(f"<div class='page-container' style='margin-bottom: 30px;'><div class='page-title'><strong>📜 슬라이드 {page_num + 1}</strong></div></div>", unsafe_allow_html=True)
            st.image(convert_pdf_page_to_image(st.session_state.pdf_bytes, page_num), use_container_width=True)

            current_script = st.session_state.scripts[page_num]
            if isinstance(current_script, dict):
                current_script = current_script.get("script", "")

            st.markdown("<div class='script-container'><h4>☑️ 발표 스크립트</h4></div>", unsafe_allow_html=True)
            st.markdown("**🔨 여기서 생성된 대본을 수정할 수 있습니다. 수정된 대본에 맞게 음성도 재생성할 수 있습니다.**")
            edited_script = st.text_area(label="", value=current_script, height=150, key=f"script_{page_num}")
            if edited_script != current_script:
                st.session_state.scripts[page_num] = edited_script
                st.success("❗스크립트가 수정되었습니다!")

            audio_b64 = st.session_state.tts_audios.get(str(page_num)) if isinstance(st.session_state.tts_audios, dict) else None
            if audio_b64:
                st.audio(base64.b64decode(audio_b64), format="audio/wav")

            col1, col2, col3 = st.columns([2.5, 4.5, 2.5])
            with col1:
                if page_num > 0 and st.button("이전 슬라이드 ⬅"):
                    st.session_state.current_slide -= 1
                    st.rerun()
            with col2:
                st.markdown(f"<div style='text-align:center;font-weight:bold;'>슬라이드 {page_num + 1} / {st.session_state.total_pages}</div>", unsafe_allow_html=True)
            with col3:
                if page_num < st.session_state.total_pages - 1 and st.button("다음 슬라이드 ➡"):
                    st.session_state.current_slide += 1
                    st.rerun()

            # 마지막 슬라이드일 때만 표시되는 버튼
            if page_num == st.session_state.total_pages - 1:
                col1, col_spacer, col2, col_spacer2, col3 = st.columns([1.5, 0.3, 1.7, 0.3, 1.5])

                with col1:
                    if st.button("🔁음성 재생성"):
                        try:
                            with st.spinner("음성 재생성 중..."):
                                response = requests.post(f"{API_URL}/generate-audio", json={
                                    "scripts": {
                                        str(i): s if isinstance(s, str) else s.get("script", "")
                                        for i, s in enumerate(st.session_state.scripts)
                                    },
                                    "keywords": st.session_state.keywords,
                                    "gender": st.session_state.selected_voice
                                })
                                if response.status_code == 200:
                                    st.session_state.tts_audios = response.json()
                                    st.success("수정된 음성이 생성되었습니다.")
                                    st.rerun()
                        except Exception as e:
                            st.error(f"오류 발생: {str(e)}")

                with col2:
                    if st.button("📦PDF, 음성 결합"):
                        try:
                            with st.spinner("ZIP 파일 생성 중..."):
                                files = {
                                    "file": ("presentation.pdf", st.session_state.pdf_bytes, "application/pdf")
                                }
                                data = {"wav_dir": "../data/audio"}
                                response = requests.post(f"{API_URL}/export-presentation", files=files, data=data)
                                if response.status_code == 200:
                                    st.session_state.generated_zip = response.content
                                else:
                                    st.error(f"API 오류: {response.text}")
                        except Exception as e:
                            st.error(f"다운로드 실패: {str(e)}")

                    # 정확히 수직 정렬되도록 감싸서 렌더링
                    if st.session_state.get("generated_zip"):
                        zip_button_html = """
                        <div style="margin-top: 12px; display: flex; justify-content: center;">
                            <a href="data:application/zip;base64,{b64}" download="presentation_bundle.zip">
                                <button style="
                                    background: linear-gradient(135deg, #f5d5ba, #f9e0c6);
                                    color: black;
                                    font-size: 1.1rem;
                                    font-weight: 600;
                                    padding: 12px 24px;
                                    border: none;
                                    border-radius: 10px;
                                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
                                    cursor: pointer;
                                ">
                                    📥 다운로드 (ZIP)
                                </button>
                            </a>
                        </div>
                        """.format(b64=base64.b64encode(st.session_state.generated_zip).decode())
                        st.markdown(zip_button_html, unsafe_allow_html=True)


                with col3:
                    if st.button("🎤발표 시작"):
                        st.session_state.app_page = "presentation_view"
                        st.session_state.presentation_slide = 0
                        st.rerun()
    st.markdown("""
    <style>
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #f5d5ba, #f9e0c6);
        color: black;
        font-size: 1.3rem;
        font-weight: 600;
        padding: 16px 36px;
        border: none;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.2);
    }
    div.stButton {
        display: flex;
        justify-content: center;
        margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

def render_presentation_mode():
    st.title("🎤 발표 모드")
    page_num = st.session_state.presentation_slide

    # 상단 박스 스타일 슬라이드 번호
    st.markdown(f"""
        <div style='
            border: 2px solid #dee2e6;
            padding: 15px;
            border-radius: 12px;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            text-align: center;
            margin: 20px 0;
        '>
            <span style='font-weight: bold; font-size: 1.2rem; color: #2c3e50;'>
                슬라이드 {page_num + 1} / {st.session_state.total_pages}
            </span>
        </div>
    """, unsafe_allow_html=True)

    st.image(convert_pdf_page_to_image(st.session_state.pdf_bytes, page_num), use_container_width=True)

    audio_b64 = st.session_state.tts_audios.get(str(page_num)) if isinstance(st.session_state.tts_audios, dict) else None
    if audio_b64:
        st.audio(base64.b64decode(audio_b64), format="audio/wav")

    # 버튼 영역 (div 감싸지 않음)
    col1, spacer, col2 = st.columns([1.5, 4, 1.5])
    with col1:
        if page_num > 0 and st.button("⬅ 이전 슬라이드"):
            st.session_state.presentation_slide -= 1
            st.rerun()
    with col2:
        if page_num < st.session_state.total_pages - 1 and st.button("다음 슬라이드 ➡"):
            st.session_state.presentation_slide += 1
            st.rerun()

    # 스타일 전역 적용 (모든 st.button 대상)
    st.markdown("""
    <style>
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #f5d5ba, #f9e0c6);
        color: black !important;
        font-size: 1.2rem;
        font-weight: 600;
        padding: 14px 32px;
        border: none;
        border-radius: 10px;
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
def main():
    initialize_session_state()
    set_background("assets/background.png")  # 배경 이미지
    if st.session_state.app_page == "presentation":
        render_presentation_workflow()
        show_chat_interface()
    elif st.session_state.app_page == "presentation_view":
        render_presentation_mode()
    else:
        render_home_page()

if __name__ == "__main__":
    main()