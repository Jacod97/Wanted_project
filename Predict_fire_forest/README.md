# 머신러닝 기반 산불 발생 예측 시스템: Predict_fire_forest(2025.01 ~ 2025.02)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-008000?style=flat-square)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)

---

## 1. 프로젝트 소개

**Predict_fire_forest**는 전국 산불 발생 데이터를 기반으로 머신러닝을 활용해 산불 발생 여부를 사전에 예측하여   
재해 예방을 위한 모델 개발을 목표로 한 프로젝트입니다.  
산불은 빠르게 확산되어 막대한 피해를 초래할 수 있으므로, 데이터 기반 예측 시스템 구축을 통해 빠르고 정확한 대응이 가능하도록 지원합니다.

---

## 2. 수행 역할

### 데이터 수집 및 분석   
산불 발생에 영향을 미치는 데이터 조사

![alt text](<./asset/산불원인.png>)
| 산불 원인 유형             | 관련 데이터                            | 데이터 출처 |
|-----------------------------|------------------------------------------|----------------|
| 입산자실화 관련 데이터       | 인구 데이터, 토지 데이터(묘지)           | [행정안전부](https://jumin.mois.go.kr), [KOSIS](https://kosis.kr/statHtml/statHtml.do?sso=ok&returnurl=https%3A%2F%2Fkosis.kr%3A443%2FstatHtml%2FstatHtml.do%3F...%3D%26) |
| 기타 관련 데이터            | 기상 데이터                              | [기상청 AP](https://apihub.kma.go.kr) |
| 농산부산물 소각 데이터       | 토지 데이터(농지)                        | [KOSIS](https://kosis.kr/statHtml/statHtml.do?sso=ok&returnurl=https%3A%2F%2Fkosis.kr%3A443%2FstatHtml%2FstatHtml.do%3F...%3D%26) |
