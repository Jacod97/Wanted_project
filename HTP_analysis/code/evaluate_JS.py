import json

class Main_Box:
    """
    객체 감지 결과를 저장하고 바운딩 박스 정보를 처리하는 클래스.
    - 결과 데이터를 bbox() 메서드를 통해 바운딩 박스 좌표와 크기 정보로 변환.
    - JSON 데이터를 활용할 경로를 지정하여 초기화함.
    """
    def __init__(self, result):
        self.result = result
        self.json_path = "./htp_evaluate.json"  # JSON 파일 경로 설정
        self.boxes = self.bbox()  # 바운딩 박스 정보 생성
        self.boxes_dict = {key: value for d in self.boxes for key, value in d.items()}  # 객체별 바운딩 박스 딕셔너리 생성

    def bbox(self):
        """
        감지된 객체의 바운딩 박스 정보를 리스트 형태로 변환하여 저장하는 메서드.
        - 각 객체의 이름(name)을 키로 사용하여, 해당 객체의 바운딩 박스 좌표(x, y, w, h)와 크기(size)를 저장.
        """
        bbox_list = []
        for name, xyxy in self.result.items():
            bbox_dict = next((item for item in bbox_list if name in item), None)
            if not bbox_dict:
                new_entry = {name: {"bbox": {"x": [], "y": [], "w": [], "h": []}, "size": []}}
                bbox_list.append(new_entry)
                bbox_dict = new_entry

            for val in xyxy:
                x, y, w, h, size = val
                bbox_dict[name]["bbox"]["x"].append(x)
                bbox_dict[name]["bbox"]["y"].append(y)
                bbox_dict[name]["bbox"]["w"].append(w)
                bbox_dict[name]["bbox"]["h"].append(h)
                bbox_dict[name]["size"].append(size)

        return bbox_list


class Analysis(Main_Box):
    """
    객체 감지 결과를 기반으로 HTP(집-나무-사람 검사) 심리 분석을 수행하는 클래스.
    - 크기 비율, 위치 정보, 존재 여부, 개수를 분석하여 JSON 데이터와 비교.
    - 모든 좌표와 크기를 정규화하여 일관성을 유지.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def size_ratio(self, entry):
        """
        객체 크기(class_label)와 목표 크기(target_label)의 비율을 계산하여 특정 임계값(threshold)과 비교.
        - 비율이 임계값을 초과하면 'big', 미만이면 'small'로 판단하여 JSON 감정 점수를 반환.
        """
        target_label = entry["target"]
        class_label = entry["class_label"]
        threshold = float(entry["threshold"])
        item = entry["item"]
        score = []
        text = []

        if class_label not in self.boxes_dict:
            return [], []

        class_sizes = self.boxes_dict.get(class_label, {}).get('size', [])
        target_exists = target_label in self.boxes_dict

        if target_label != "paper" and not target_exists and target_label != 'person': 
            return [], []

        num_iterations = len(class_sizes)

        if target_label != "paper" and target_exists:
            target_sizes = self.boxes_dict[target_label].get('size', [])
            num_iterations = min(num_iterations, len(target_sizes))

        for i in range(num_iterations):
            if target_label == "paper":
                target_area = 1.0
            elif target_label == "person":
                # "person"인 경우, "Male" 크기를 찾아야 함
                target_area = next((bbox['Male']['size'][0] for bbox in self.boxes if 'Male' in bbox), 0)
            else:
                target_area = self.boxes_dict[target_label]['size'][i]

            class_area = self.boxes_dict[class_label]['size'][i]
            ratio = class_area / target_area

            # 비율이 임계값을 초과/미만하는 경우 감정 점수 반환
            if (ratio >= threshold and item == "big") or (ratio <= threshold and item == "small"):
                score.append([int(entry[key]) for key in 
                            ["aggression", "social_anxiety", "depression", "avoidance",
                            "self_esteem", "emotional_instability", "affection_deficit",
                            "inferiority", "regression"]])
                text.append(item)

        return score, text if score else ([], [])

    def locate(self, bbox, entry):
        """
        객체의 위치를 분석하여 특정 감정을 평가하는 메서드.
        - 객체의 중심 좌표를 기반으로 'left', 'right', 'bottom' 중 하나로 분류.
        """
        score = []
        text = []

        for i in range(len(bbox['x'])):
            item = entry["item"]
            box_x, box_y, box_w, box_h = bbox['x'][i], bbox['y'][i], bbox['w'][i], bbox['h'][i]
            box_center_x = box_x + box_w / 2
            box_center_y = box_y + box_h / 2

            if box_center_y > 0.5:
                position = 'bottom'
            else:
                position = 'right' if box_center_x > 0.5 else 'left'

            if item == position:
                score.append([int(entry[key]) for key in
                              ["aggression", "social_anxiety", "depression", "avoidance",
                               "self_esteem", "emotional_instability", "affection_deficit",
                               "inferiority", "regression"]])
                text.append(item)

        return score, text

    def counting(self, bbox, entry):
        """
        객체 개수를 세고, 설정된 임계값과 비교하여 감정 점수를 반환.
        """
        threshold = float(entry["threshold"])
        item = entry["item"]
        count = len(bbox['x'])

        if (count >= threshold and item == 'many') or (count <= threshold and item == 'few'):
            return [[int(entry[key]) for key in 
                     ["aggression", "social_anxiety", "depression", "avoidance", "self_esteem",
                      "emotional_instability", "affection_deficit", "inferiority", "regression"]]], item
        else:
            return [[]], []

    def exist(self, entry):
        """
        객체 존재 여부를 확인하여 감정 점수를 반환하는 메서드.
        """
        item = entry["item"]
        return [[int(entry[key]) for key in 
                ["aggression", "social_anxiety", "depression", "avoidance", "self_esteem",
                 "emotional_instability", "affection_deficit", "inferiority", "regression"]]], item


class Base_evaluate(Main_Box):
    """
    HTP 데이터를 불러와 감지된 객체 정보를 분석하는 클래스.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.htp = self.htp_data()
        self.analysis = Analysis(result=self.result)  # 감정 분석 객체 생성
        self.key_list = list(self.result.keys())  # 분석할 객체 리스트
        self.private_dict = {}

        self.process_data()

    def htp_data(self):
        """
        JSON 파일에서 HTP 데이터를 불러오는 메서드.
        """
        with open(self.json_path, 'r', encoding="UTF-8") as f:
            return json.load(f)

    def process_data(self):
        for class_nm in self.key_list:
            matched_entries = [entry for entry in self.htp if class_nm in entry["class_label"].replace(",", " ").split()]

            if class_nm not in self.private_dict:
                self.private_dict[class_nm] = {}

            for entry in matched_entries:
                category = entry["category"]
                score, text = None, None

                try:
                    if category == "size":
                        score, text = self.analysis.size_ratio(entry)
                    elif category == "place":
                        score, text = self.analysis.locate(self.boxes_dict[class_nm]["bbox"], entry)
                    elif category == 'count':
                        score, text = self.analysis.counting(self.boxes_dict[class_nm]["bbox"], entry)
                    elif category == 'exist':
                        if (not self.result[class_nm] and entry['item'] == 'FALSE') or \
                        (self.result[class_nm] and entry['item'] == 'TRUE'):
                            score, text = self.analysis.exist(entry)

                    if score and text:
                        if category not in self.private_dict[class_nm]:
                            self.private_dict[class_nm][category] = {'score': [], 'text': []}
                        self.private_dict[class_nm][category]['score'].extend(score)
                        # 변경된 부분: text를 항상 리스트로 처리
                        self.private_dict[class_nm][category]['text'].extend([text] if isinstance(text, str) else text)

                except Exception as e:
                    print(f"Error processing {class_nm}, {category}: {str(e)}")