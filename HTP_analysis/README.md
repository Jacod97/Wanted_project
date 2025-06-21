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
  <img src="./demo.gif" width="600" height="300"/>
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

---
## 5. 이슈 발생 및 해결 과정

---
## 📊 프로젝트 과정

1. **아이디어 도출 및 기획**
   - HTP 검사의 자동화를 통한 심리 평가 효율성 향상 목표 수립
   - 객체 감지와 심리 해석을 연계하는 시스템 구상

2. **시스템 설계**
   - YOLO11 기반 개별 객체 감지 모델 설계
   - 감지 결과를 JSON 데이터로 변환하여 해석 가능한 구조 설계

3. **핵심 기능 개발**
   - 집, 나무, 사람 감지를 위한 YOLO11 모델 학습
   - 입력 이미지 크기(imgsz) 조정 및 학습 속도 최적화(epochs 조절)
   - 감지 결과를 바탕으로 크기, 위치 분석 및 심리적 해석 적용

4. **코드 구조화 및 최적화**
   - 객체 지향 프로그래밍(OOP) 방식으로 데이터 처리 로직 구조화
   - 감지된 객체 데이터를 효과적으로 다루기 위한 JSON 설계

5. **테스트 및 검증**
   - 다양한 HTP 검사 데이터를 대상으로 모델 성능 및 해석 결과 검증
   - 기존 연구 데이터와 비교하여 해석 정확도 평가

6. **성과**
   - HTP 검사 자동 분석 시스템 프로토타입 완성
   - YOLO11 기반 모델을 활용한 높은 객체 감지 정확도 확보
   - 자동화된 심리 해석 적용 가능성 검증

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
