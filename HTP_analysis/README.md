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

### 데이터 수집
- 다양한 연령대(7-13)와 성별의 아동 7,000명으로부터 수집한 4개 HTP 분류 그림(JPG)과 그림 내 주요 객체에 대한 바운딩박스 라벨링을 시행한 데이터(JSON) 각 56,000건  
- 각 HTP 분류 별 Train(11200개), Validation(1400개) 데이터를 포함하고 있고, Test 셋은 정책 상 다운로드 불가능했습니다.  

| 클래스     | 수량       | 비율  |
|------------|------------|-------|
| 집         | 14,000건   | 25%   |
| 나무       | 14,000건   | 25%   |
| 여자사람   | 14,000건   | 25%   |
| 남자사람   | 14,000건   | 25%   |

### YOLO모델 학습을 위한 데이터 구성
- Test 데이터셋 구축을 위해 각 클래스(`House`, `Tree`, `Male`, `Female`)는 Train(9800개), Validation(1400개), Test(1400개)로 재구성하였습니다.
- 각 세트는 `images`, `jsons`, `labels`로 세분화 하였고 이 구조는 YOLOv11에서 요구하는 `data.yaml` 설정에 맞추어 설계되었습니다.
```
data/
├── House/
│   ├── test/
│   │   ├── images/
│   │   ├── jsons/
│   │   └── labels/
│   ├── train/
│   │   ├── images/
│   │   ├── jsons/
│   │   └── labels/
│   └── valid/
│       ├── images/
│       ├── jsons/
│       └── labels/
│
....
```

### HTP 검사를 위한 **Pytorch**를 이용해 모델 학습 및 평가, 최적화
- HTP(집-나무-사람) 검사를 위한 객체 감지 모델은 YOLOv11을 기반으로 커스터마이징하여 개발하였습니다.  
- HTP 전용 데이터셋을 구축하고, imgsz, epochs, batch_size 등의 하이퍼파라미터를 조정하면서 모델 성능을 최적화했습니다.
  - epochs(학습 횟수) : 50
  - imgsz(이미지사이즈) : 640
  - batch_size(1회 학습당 데이터 수) : 8
- 객체 감지 성능은 일반적으로 많이 사용되는 mAP50 지표를 활용해 평가하였습니다.

### 심리적 해석 룰 기반 분석 로직 구현
- 모델이 감지한 결과를 바탕으로는 심리적 해석을 위한 룰 기반 분석 로직을 설계하였습니다.
- 객체의 크기, 위치, 비율, 순서 등을 기준으로 해석 규칙을 정의하고, 이를 JSON 형태로 평가하여 해석 결과를 자동으로 텍스트로 출력하는 구조를 구현하였습니다.

---

## 4. 시스템 아키텍처 요약

- 입력 이미지 업로드 → YOLOv11 객체 감지 → 감지 결과를 JSON으로 변환 → 룰 기반 분석 수행    
- 분석 결과를 LLM에게 전달 → 해석 문장 출력

---
## 5. 이슈 발생 및 해결 과정

### 1. Rule기반 채점 방식
[자세히 보기](https://velog.io/@wotlr6894/Rule%EA%B8%B0%EB%B0%98-%EC%B1%84%EC%A0%90-%EB%B0%A9%EC%8B%9D) 
### 2. Object Detection 성능 개선을 위한 노력
[자세히 보기](https://velog.io/@wotlr6894/Object-Detection-%EC%84%B1%EB%8A%A5-%EA%B0%9C%EC%84%A0%EC%9D%84-%EC%9C%84%ED%95%9C-%EB%85%B8%EB%A0%A5) 

---
## 6. 프로젝트 회고

### **한계점**
해당 시스템은 HTP 그림에 대한 자동 분석을 목표로 개발되었지만, 몇 가지 한계도 존재합니다.  

먼저, 사용자마다 그림체나 표현 방식에 뚜렷한 개성이 있기 때문에,같은 대상을 그리더라도 선의 길이나 위치, 구성 방식이 크게 달라질 수 있습니다.
이러한 개인차는 해석 로직이 정해진 규칙에 기반하고 있다는 점에서 오차를 유발할 가능성이 있습니다.  

또한, 현재 시스템은 주로 객체의 유무와 위치, 비율 등 구조적 정보에 초점을 맞추고 있지만, 실제 심리 해석에서는 선의 굵기, 채색의 밀도, 필압의 세기와 같은 스타일적 요소도 중요한 해석 기준이 됩니다.
이러한 비정형적 요소를 정량화하고 분석하는 데에는 현재 기술적 한계가 있으며, 이를 정교하게 반영하기 위해서는 추가적인 이미지 처리 기술 또는 별도의 스타일 분석 모델이 필요할 것으로 판단됩니다.

### **개선 방향**  
향후에는 본 시스템을 HTP 검사에 국한하지 않고, **KFD(가족화 그림 검사)**나 BGT(벤더 형태 검사) 등 다양한 심리 검사 유형으로 확장하는 것을 고려하고 있습니다.
이를 통해 보다 폭넓은 심리적 정보를 자동으로 해석할 수 있는 기반을 마련하고자 합니다.  

또한, 감지된 결과를 **대형 언어 모델(LLM)**에 입력하여 해석 정확도를 높이는 실험도 진행할 계획입니다.
기존의 룰 기반 해석을 보완하거나 대체할 수 있는 방향으로 활용 가능성을 탐색 중입니다.  

마지막으로, 단순히 객체를 분석하는 것을 넘어 그림을 통해 사용자의 감정 상태나 행동 패턴을 추론할 수 있는 기능도 장기적으로 도입하고자 합니다.  
이러한 기능은 실제 임상적 활용 가능성을 높이는 데 기여할 수 있을 것으로 기대됩니다.
  
---

## 🌐 설치 및 실행 방법

### 요구사항
- Python 3.8 이상
- 필요한 Python 패키지 (requirements.txt 참조)
