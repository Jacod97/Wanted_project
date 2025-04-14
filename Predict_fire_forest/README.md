# Predict_fire_forest

AI 기반 산불 발생 예측 시스템

---

## 🔍 프로젝트 소개

**Predict_fire_forest**는 머신러닝 모델을 활용해 산불 발생 가능성을 사전에 예측함으로써,  
재해 예방 및 대응 시스템 개선에 기여하는 것을 목표로 한 프로젝트입니다.  
산불은 빠르게 확산되어 막대한 피해를 초래할 수 있으므로, 데이터 기반 예측 시스템 구축을 통해 빠르고 정확한 대응이 가능하도록 지원합니다.

---

## 👥 팀 정보

- **팀명:** 예측 "불" 가능
- **팀원:** 이승재, 박형빈, 정재식
- **프로젝트 기간:** 2025.01.03 ~ 2025.02.03

---
## 🛤️ 프로젝트 과정

1. **아이디어 도출 및 기획**
   - 산불이 확산되기 전에 조기에 예측하여 피해를 줄이기 위한 방안 고민
   - 전국 및 지역별 데이터를 기반으로 산불 발생 가능성 예측 모델 구축 목표 설정

2. **데이터 수집 및 전처리**
   - 전국 산불 발생 기록 및 관련 기상 데이터를 수집
   - 결측치 처리 및 이상치 제거
   - 모델 학습을 위한 Feature 선정 및 가공

3. **데이터 불균형 해결**
   - 산불 발생 데이터가 희소한 문제를 인식
   - SMOTE 및 RandomUnderSampler를 조합하여 클래스 불균형 개선

4. **모델 개발 및 성능 비교**
   - 다양한 머신러닝 모델 (LogisticRegression, XGBoost, LightGBM, RandomForest) 학습
   - 전국 단일 모델과 지역별 특화 모델을 각각 개발하여 성능 비교

5. **모델 최적화 및 앙상블 적용**
   - 하이퍼파라미터 튜닝을 통해 모델 성능 개선
   - StackingClassifier를 적용하여 모델 앙상블 및 성능 향상

6. **모델 평가 및 검증**
   - ROC-AUC, Precision, Recall, F1-score를 활용하여 모델 평가
   - 소수 클래스 예측 성능을 보완하기 위해 PR-AUC 지표 검토

7. **문제 해결 및 개선**
   - 데이터 불균형 문제 해결을 통해 예측 신뢰도 상승
   - 지역별 데이터 부족 문제를 인지하고 추가 데이터 확보 방안 모색

8. **성과**
   - 전국 및 지역별 산불 발생 예측 모델 구축 완료
   - 모델 앙상블을 통한 단일 모델 대비 예측 성능 개선
   - 데이터 기반 산불 예방 시스템 가능성 제시
---
## 🧑‍💻 나의 역할 (정재식)

- 데이터 전처리 및 피처 엔지니어링
- 데이터 불균형 문제 해결 (SMOTE + RandomUnderSampler)
- 전국/지역별 머신러닝 모델 개발 및 성능 비교
- 최적 모델 선정 및 하이퍼파라미터 튜닝
- 모델 앙상블(StackingClassifier) 적용 및 최적화
- 모델 성능 평가 및 개선 방안 제안

---

## 📈 프로젝트 주요 기능

- **산불 발생 예측**: 전국 및 지역별 데이터 기반 산불 발생 가능성 예측
- **데이터 불균형 해결**: SMOTE와 RandomUnderSampler 조합으로 클래스 불균형 완화
- **다중 모델 비교 및 최적화**: LogisticRegression, XGBoost, LightGBM, RandomForest를 활용하여 최적 모델 선정
- **모델 앙상블**: StackingClassifier를 통한 성능 향상
- **모델 성능 평가**: ROC-AUC, Precision-Recall AUC 등 다양한 지표를 활용한 평가

---

## 🛠️ 프로젝트 기술 스택

- **언어**: Python
- **EDA/전처리**: Pandas, Scikit-learn
- **머신러닝**: XGBoost, LightGBM, RandomForest, LogisticRegression
- **데이터 증강**: SMOTE, RandomUnderSampler
- **모델 앙상블**: StackingClassifier
- **시각화**: Matplotlib
- **개발 환경**: Jupyter Notebook

---

## 📊 프로젝트 결과 및 회고

- 전국 및 지역별로 산불 발생 예측이 가능한 머신러닝 모델 구축
- 데이터 불균형 문제를 일정 부분 해결하여 모델 신뢰도 향상
- 모델 앙상블 기법 적용을 통해 단일 모델 대비 성능 개선
- 산불 예방 및 대응 시스템 개선에 기여할 수 있는 모델 제안

**한계점:**
- 사용한 Feature만으로는 예측 성능에 한계 존재
- ROC-AUC만을 주요 지표로 사용했기에 소수 클래스(산불 발생) 대응이 완벽하지 않음
- 일부 지역 데이터가 부족하여 지역별 모델 성능 편차 발생

**향후 개선 계획:**
- 지형, 토지 이용, 인간 활동 등 다양한 Feature 추가
- Precision-Recall AUC(PR-AUC)를 주요 평가 지표로 사용
- 실시간 데이터 수집 및 적용 시스템 구축 고려

---

## 🌐 설치 및 실행 방법

### 요구사항
- Python 3.8 이상
- 필요한 Python 패키지 (requirements.txt 참조)

### 설치 사항

1. 가상환경 생성 및 패키지 설치:
   ```bash
   python -m venv venv
   source venv/bin/activate   # (Windows의 경우: .\venv\Scripts\activate)
   pip install -r requirements.txt