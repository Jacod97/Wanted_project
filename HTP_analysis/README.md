# AI 기반 HTP 검사 보조 프로그램: DeepPrint(2025.02 ~ 2025.03)  
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![YOLOv11](https://img.shields.io/badge/YOLOv11-black?style=flat-square)

---

## 1. 프로젝트 소개

DeepPrint는 심리 평가 도구인 HTP(집-나무-사람) 검사를 AI 기반으로 자동 분석하는 보조 시스템입니다.
YOLO 객체 감지 모델을 활용하여 그림 내의 집, 나무, 사람을 자동으로 감지하고,
이를 JSON 형식으로 정리한 후 룰 기반 분석 및 LLM 해석을 통해 심리적 특성을 자동으로 평가합니다.

---

## 2. 시연 영상 <👇클릭하세요👇>
<a href="https://youtu.be/xcK26iobhLY" target="_blank">
  <img src="./asset/demo.gif" width="600" height="300"/>
</a>

---

## 3. 수행 역할

### HTP 검사용 **YOLO11** 모델 학습 및 최적화
- YOLOv11 커스터마이징 및 HTP 객체(집, 나무, 사람) 전용 데이터셋 구축  
- 학습 파라미터 조정 (imgsz, epochs 등)으로 최적화 진행

### 심리적 해석 룰 기반 분석 로직 구현
- 감지된 객체의 크기, 위치, 비율, 순서를 기준으로 심리 해석 규칙 정의  
- JSON 기반 평가 로직 구현 및 해석 결과 텍스트 생성  

---

## 4. 시스템 아키텍처 요약

- 입력 이미지 업로드 → YOLOv11 객체 감지  
- 감지 결과를 JSON으로 변환 → 룰 기반 분석 수행  
- 분석 결과를 LLM에게 전달 → 해석 문장 출력  
![alt text](<./asset/아키텍쳐.png>)
---
## 5. 이슈 발생 및 해결 과정

---
## 6. 프로젝트 회고

**한계점:**
- 사용자별 개성/그림체 차이로 인한 해석 오차 발생 가능  
- 분석 정밀도를 높이기 위한 추가 임상데이터 확보 필요

**개선 방향**  
- 다양한 심리 검사(KFD, BGT 등)로 확장  
- 감지 결과를 기반으로 LLM의 해석 정확도 향상 실험  
- 감정/행동 패턴 추론 기능 추가
  
---

## 🌐 설치 및 실행 방법

### 요구사항
- Python 3.8 이상
- 필요한 Python 패키지 (requirements.txt 참조)

### 설치 및 실행

1. 패키지 설치:
  ```bash
   pip install -r requirements.txt
  ```
2. 프로젝트 실행:
  ```bash
  python src/main.py
  ```


**향후 개선 계획:**
- YOLO 모델 업그레이드를 통한 객체 감지 성능 향상
- 다양한 심리 검사(KFD, BGT 등)로 자동 해석 범위 확장
- 추가 데이터 수집 및 학습을 통한 심리 해석 정확도 개선
