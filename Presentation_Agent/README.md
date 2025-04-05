# Presentation-Agent

Presentation-Agent는 AI 기반 프레젠테이션 도우미 애플리케이션입니다. PDF 문서를 분석하고 프레젠테이션을 생성하며, 음성 합성 기능을 통해 발표를 도와주는 통합 솔루션을 제공합니다.

## 주요 기능

- PDF 문서 분석 및 시각화
- AI 기반 프레젠테이션 생성
- 음성 합성 기능 (남성/여성 음성 지원)
- 실시간 프레젠테이션 모드

## 프로젝트 구조

```
Presentation-Agent/
├── streamlit/          # Streamlit 웹 인터페이스
│   ├── app.py         # 메인 애플리케이션
│   └── assets/        # 정적 리소스
├── fastapi/           # 백엔드 API 서버
│   ├── main.py        # FastAPI 애플리케이션
│   ├── models.py      # 데이터 모델
│   ├── routes.py      # API 라우트
│   ├── utils.py       # 유틸리티 함수
│   └── prompts/       # AI 프롬프트
├── data/              # 데이터 저장소
└── code/              # 개발 코드
    ├── JK/           # 개발자 JK의 코드
    ├── JS/           # 개발자 JS의 코드
    └── data/         # 코드 관련 데이터
```

## 설치 및 실행

### 요구사항
- Python 3.8 이상
- 필요한 Python 패키지 (requirements.txt 참조)

### 설치 사항

1. 필요한 API 키 설정:
   - OpenAI API 키
   - Google Cloud API 키 (음성 합성용)

2. API 키 설정 방법:
   ```bash
   # .env 파일 생성
   touch .env
   
   # .env 파일에 다음 내용 추가
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_CLOUD_API_KEY=your_google_cloud_api_key_here
   ```

3. Python 패키지 설치:
   ```bash
   # 가상환경 생성 (선택사항)
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   
   # 필요한 패키지 설치
   pip install -r requirements.txt
   ```

### 실행 방법

1. 백엔드 서버 실행:
```bash
cd fastapi
uvicorn main:app --reload
```

2. 프론트엔드 실행:
```bash
cd streamlit
streamlit run app.py
```

## API 엔드포인트

- `http://localhost:8000` - FastAPI 백엔드 서버
- Streamlit 웹 인터페이스는 기본적으로 `http://localhost:8501`에서 실행됩니다.

## 환경 설정

`.env` 파일을 통해 환경 변수를 설정할 수 있습니다. 필요한 경우 `.env.example` 파일을 참조하세요.

## 라이선스

[라이선스 정보를 여기에 추가하세요]

## 기여

프로젝트에 기여하고 싶으시다면 다음 단계를 따르세요:
1. 이슈를 생성하여 변경사항을 논의
2. Fork 후 Pull Request 생성
3. 코드 리뷰 후 병합