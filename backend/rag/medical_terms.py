"""
Medical terminology dictionary for Korean radiology.
Provides structured term mappings used by the RAG vector store and rule-based validator.
"""

from typing import TypedDict


class TermEntry(TypedDict):
    korean: str
    patient_friendly: str
    category: str


# ---------------------------------------------------------------------------
# Primary radiology term dictionary
# 50+ key radiology terms: English → Korean + patient-friendly explanation
# ---------------------------------------------------------------------------

RADIOLOGY_TERMS: dict[str, TermEntry] = {
    # --- Morphological findings ---
    "nodule": {
        "korean": "결절",
        "patient_friendly": "조직에서 발견된 작은 혹 또는 덩어리 (보통 3cm 미만)",
        "category": "morphology",
    },
    "mass": {
        "korean": "종괴",
        "patient_friendly": "영상에서 확인된 덩어리 모양의 병변 (3cm 이상)",
        "category": "morphology",
    },
    "lesion": {
        "korean": "병변",
        "patient_friendly": "정상과 다른 이상 조직 또는 부위",
        "category": "morphology",
    },
    "tumor": {
        "korean": "종양",
        "patient_friendly": "비정상적으로 자라는 세포 덩어리",
        "category": "morphology",
    },
    "cyst": {
        "korean": "낭종",
        "patient_friendly": "액체가 차 있는 주머니 모양의 구조물",
        "category": "morphology",
    },
    "polyp": {
        "korean": "용종",
        "patient_friendly": "점막에서 돌출된 작은 혹",
        "category": "morphology",
    },
    "calcification": {
        "korean": "석회화",
        "patient_friendly": "조직 내에 칼슘이 침착되어 딱딱해진 부분",
        "category": "morphology",
    },
    "thickening": {
        "korean": "비후",
        "patient_friendly": "조직이 정상보다 두꺼워진 상태",
        "category": "morphology",
    },
    "atrophy": {
        "korean": "위축",
        "patient_friendly": "장기나 조직이 줄어들어 작아진 상태",
        "category": "morphology",
    },
    "hypertrophy": {
        "korean": "비대",
        "patient_friendly": "장기나 조직이 정상보다 커진 상태",
        "category": "morphology",
    },

    # --- Lung / chest ---
    "consolidation": {
        "korean": "경화",
        "patient_friendly": "폐의 공기 공간이 액체나 세포로 채워져 폐가 단단해진 상태 (폐렴 등에서 나타남)",
        "category": "lung",
    },
    "atelectasis": {
        "korean": "무기폐",
        "patient_friendly": "폐의 일부가 완전히 펴지지 않고 쭈그러든 상태",
        "category": "lung",
    },
    "pneumothorax": {
        "korean": "기흉",
        "patient_friendly": "폐와 흉벽 사이에 공기가 새어 들어간 상태",
        "category": "lung",
    },
    "pleural effusion": {
        "korean": "흉막삼출",
        "patient_friendly": "폐를 둘러싼 흉막 공간에 액체가 고인 상태",
        "category": "lung",
    },
    "pneumonia": {
        "korean": "폐렴",
        "patient_friendly": "세균이나 바이러스 등으로 인한 폐 감염",
        "category": "lung",
    },
    "emphysema": {
        "korean": "폐기종",
        "patient_friendly": "폐의 공기 주머니(폐포)가 손상되어 늘어난 상태 (주로 흡연과 관련)",
        "category": "lung",
    },
    "bronchiectasis": {
        "korean": "기관지확장증",
        "patient_friendly": "기관지가 비정상적으로 넓어지고 변형된 상태",
        "category": "lung",
    },
    "ground-glass opacity": {
        "korean": "간유리음영",
        "patient_friendly": "CT에서 폐가 반투명 유리처럼 뿌옇게 보이는 소견",
        "category": "lung",
    },
    "interstitial opacity": {
        "korean": "간질성 음영",
        "patient_friendly": "폐 조직 사이의 결합 조직에 이상 소견이 나타난 상태",
        "category": "lung",
    },
    "effusion": {
        "korean": "삼출",
        "patient_friendly": "체강 내에 액체가 고인 상태",
        "category": "general",
    },

    # --- Cardiovascular ---
    "cardiomegaly": {
        "korean": "심장비대",
        "patient_friendly": "심장이 정상보다 커진 상태",
        "category": "cardiovascular",
    },
    "pericardial effusion": {
        "korean": "심낭삼출",
        "patient_friendly": "심장을 감싸는 막(심낭) 안에 액체가 고인 상태",
        "category": "cardiovascular",
    },
    "stenosis": {
        "korean": "협착",
        "patient_friendly": "혈관이나 관강이 좁아진 상태",
        "category": "cardiovascular",
    },
    "occlusion": {
        "korean": "폐색",
        "patient_friendly": "혈관이나 관강이 완전히 막힌 상태",
        "category": "cardiovascular",
    },
    "aneurysm": {
        "korean": "동맥류",
        "patient_friendly": "혈관 벽이 약해져 풍선처럼 부풀어 오른 상태",
        "category": "cardiovascular",
    },
    "dissection": {
        "korean": "박리",
        "patient_friendly": "혈관 벽의 층이 분리되는 상태 (응급 상황일 수 있음)",
        "category": "cardiovascular",
    },
    "thrombosis": {
        "korean": "혈전증",
        "patient_friendly": "혈관 내에 혈전(핏덩어리)이 생긴 상태",
        "category": "cardiovascular",
    },
    "embolism": {
        "korean": "색전증",
        "patient_friendly": "혈전이나 이물질이 혈관을 막은 상태",
        "category": "cardiovascular",
    },

    # --- Brain / neurological ---
    "infarction": {
        "korean": "경색",
        "patient_friendly": "혈액 공급이 차단되어 조직이 손상된 상태 (뇌경색, 심근경색 등)",
        "category": "neuro",
    },
    "hemorrhage": {
        "korean": "출혈",
        "patient_friendly": "혈관이 터져 혈액이 주변 조직으로 새어 나온 상태",
        "category": "neuro",
    },
    "edema": {
        "korean": "부종",
        "patient_friendly": "조직에 액체가 고여 부어오른 상태",
        "category": "neuro",
    },
    "midline shift": {
        "korean": "정중선 편위",
        "patient_friendly": "뇌의 중심선이 한쪽으로 밀려난 상태",
        "category": "neuro",
    },
    "hydrocephalus": {
        "korean": "수두증",
        "patient_friendly": "뇌 안에 뇌척수액이 과도하게 고인 상태",
        "category": "neuro",
    },
    "white matter lesion": {
        "korean": "백질 병변",
        "patient_friendly": "뇌의 신경 섬유 다발(백질) 부위에 생긴 이상 소견",
        "category": "neuro",
    },

    # --- Abdomen / liver / GI ---
    "hepatomegaly": {
        "korean": "간비대",
        "patient_friendly": "간이 정상보다 커진 상태",
        "category": "abdomen",
    },
    "splenomegaly": {
        "korean": "비장비대",
        "patient_friendly": "지라(비장)가 정상보다 커진 상태",
        "category": "abdomen",
    },
    "ascites": {
        "korean": "복수",
        "patient_friendly": "복강(배 안)에 액체가 고인 상태",
        "category": "abdomen",
    },
    "cirrhosis": {
        "korean": "간경변",
        "patient_friendly": "간 조직이 딱딱하게 굳어 정상 기능을 잃어가는 상태",
        "category": "abdomen",
    },
    "cholelithiasis": {
        "korean": "담석증",
        "patient_friendly": "담낭(쓸개)이나 담관에 돌(담석)이 생긴 상태",
        "category": "abdomen",
    },
    "cholecystitis": {
        "korean": "담낭염",
        "patient_friendly": "담낭(쓸개)에 염증이 생긴 상태",
        "category": "abdomen",
    },
    "pancreatitis": {
        "korean": "췌장염",
        "patient_friendly": "췌장에 염증이 생긴 상태",
        "category": "abdomen",
    },
    "diverticulosis": {
        "korean": "게실증",
        "patient_friendly": "장 벽에 작은 주머니 모양의 돌출부(게실)가 생긴 상태",
        "category": "abdomen",
    },

    # --- Musculoskeletal ---
    "fracture": {
        "korean": "골절",
        "patient_friendly": "뼈가 부러지거나 금이 간 상태",
        "category": "musculoskeletal",
    },
    "dislocation": {
        "korean": "탈구",
        "patient_friendly": "관절이 제자리에서 벗어난 상태",
        "category": "musculoskeletal",
    },
    "osteoporosis": {
        "korean": "골다공증",
        "patient_friendly": "뼈의 밀도가 낮아져 부러지기 쉬운 상태",
        "category": "musculoskeletal",
    },
    "herniation": {
        "korean": "탈출증",
        "patient_friendly": "추간판(디스크)이 제자리를 벗어나 신경을 누르는 상태",
        "category": "musculoskeletal",
    },
    "spondylosis": {
        "korean": "척추증",
        "patient_friendly": "척추의 퇴행성 변화로 인한 변형",
        "category": "musculoskeletal",
    },
    "osteophyte": {
        "korean": "골극",
        "patient_friendly": "뼈 가장자리에 가시 모양으로 돌출된 뼈",
        "category": "musculoskeletal",
    },

    # --- Contrast / signal characteristics ---
    "enhancement": {
        "korean": "조영증강",
        "patient_friendly": "조영제를 투여했을 때 특정 부위가 밝게 보이는 현상 (혈관 분포 및 병변 특성 파악에 사용)",
        "category": "imaging_characteristic",
    },
    "hypodense": {
        "korean": "저음영",
        "patient_friendly": "CT에서 주변 조직보다 어둡게 보이는 부위",
        "category": "imaging_characteristic",
    },
    "hyperdense": {
        "korean": "고음영",
        "patient_friendly": "CT에서 주변 조직보다 밝게 보이는 부위 (출혈 등에서 나타남)",
        "category": "imaging_characteristic",
    },
    "hyperintense": {
        "korean": "고신호강도",
        "patient_friendly": "MRI에서 주변 조직보다 밝게 보이는 부위",
        "category": "imaging_characteristic",
    },
    "hypointense": {
        "korean": "저신호강도",
        "patient_friendly": "MRI에서 주변 조직보다 어둡게 보이는 부위",
        "category": "imaging_characteristic",
    },

    # --- Oncology ---
    "malignancy": {
        "korean": "악성 종양",
        "patient_friendly": "암으로 발전할 수 있거나 이미 암인 조직 (반드시 전문의 상담 필요)",
        "category": "oncology",
    },
    "metastasis": {
        "korean": "전이",
        "patient_friendly": "암세포가 원래 발생 부위에서 다른 장기로 퍼진 상태",
        "category": "oncology",
    },
    "lymphadenopathy": {
        "korean": "림프절병증",
        "patient_friendly": "림프절이 커지거나 비정상적으로 변한 상태",
        "category": "oncology",
    },
    "invasion": {
        "korean": "침범",
        "patient_friendly": "병변이 주변 조직이나 장기로 퍼져 들어간 상태",
        "category": "oncology",
    },

    # --- Commonly mistranslated terms ---
    "focal": {
        "korean": "국소",
        "patient_friendly": "특정 부위에 한정된 (중심성이 아님)",
        "category": "descriptor",
    },
    "focal pneumonia": {
        "korean": "국소 폐렴",
        "patient_friendly": "폐의 특정 부위에 발생한 폐렴 (국소성 폐렴)",
        "category": "lung",
    },
    "unremarkable": {
        "korean": "특이 소견 없음",
        "patient_friendly": "검사에서 이상 소견이 발견되지 않은 정상 상태",
        "category": "descriptor",
    },
    "otherwise unremarkable": {
        "korean": "그 외 특이 소견 없음",
        "patient_friendly": "나머지 부위에서는 이상 소견이 없음",
        "category": "descriptor",
    },
    "enlarged lymph nodes": {
        "korean": "비대된 림프절",
        "patient_friendly": "정상보다 커진 림프절",
        "category": "oncology",
    },
    "lymph node enlargement": {
        "korean": "림프절 비대",
        "patient_friendly": "림프절이 정상보다 커진 상태",
        "category": "oncology",
    },
    "enlarged": {
        "korean": "비대된",
        "patient_friendly": "정상보다 커진",
        "category": "descriptor",
    },
    "small nodule": {
        "korean": "소결절",
        "patient_friendly": "작은 결절 (보통 6mm 미만)",
        "category": "morphology",
    },
    "solid nodule": {
        "korean": "고형 결절",
        "patient_friendly": "내부가 고형(단단한) 성분으로 채워진 결절",
        "category": "morphology",
    },
    "ground glass nodule": {
        "korean": "간유리음영 결절",
        "patient_friendly": "반투명하게 보이는 결절",
        "category": "morphology",
    },
    "peribronchial": {
        "korean": "기관지 주위",
        "patient_friendly": "기관지 주변 부위",
        "category": "lung",
    },

    # --- Lung lobe abbreviations ---
    "RUL": {
        "korean": "우상엽",
        "patient_friendly": "오른쪽 폐의 위쪽 부분 (우측 상엽)",
        "category": "lung",
    },
    "LUL": {
        "korean": "좌상엽",
        "patient_friendly": "왼쪽 폐의 위쪽 부분 (좌측 상엽)",
        "category": "lung",
    },
    "RML": {
        "korean": "우중엽",
        "patient_friendly": "오른쪽 폐의 가운데 부분 (우측 중엽)",
        "category": "lung",
    },
    "RLL": {
        "korean": "우하엽",
        "patient_friendly": "오른쪽 폐의 아래쪽 부분 (우측 하엽)",
        "category": "lung",
    },
    "LLL": {
        "korean": "좌하엽",
        "patient_friendly": "왼쪽 폐의 아래쪽 부분 (좌측 하엽)",
        "category": "lung",
    },
    "right upper lobe": {
        "korean": "우상엽",
        "patient_friendly": "오른쪽 폐의 위쪽 부분",
        "category": "lung",
    },
    "left upper lobe": {
        "korean": "좌상엽",
        "patient_friendly": "왼쪽 폐의 위쪽 부분",
        "category": "lung",
    },
    "right middle lobe": {
        "korean": "우중엽",
        "patient_friendly": "오른쪽 폐의 가운데 부분",
        "category": "lung",
    },
    "right lower lobe": {
        "korean": "우하엽",
        "patient_friendly": "오른쪽 폐의 아래쪽 부분",
        "category": "lung",
    },
    "left lower lobe": {
        "korean": "좌하엽",
        "patient_friendly": "왼쪽 폐의 아래쪽 부분",
        "category": "lung",
    },

    # --- Imaging modality abbreviations ---
    "CT": {
        "korean": "전산화단층촬영 (CT)",
        "patient_friendly": "X선을 여러 각도에서 촬영해 신체 단면 영상을 만드는 검사",
        "category": "modality",
    },
    "MRI": {
        "korean": "자기공명영상 (MRI)",
        "patient_friendly": "자기장을 이용해 신체 내부를 자세히 촬영하는 검사",
        "category": "modality",
    },
    "PET": {
        "korean": "양전자방출단층촬영 (PET)",
        "patient_friendly": "방사성 물질을 이용해 신체 대사 활동을 영상화하는 검사",
        "category": "modality",
    },
    "CXR": {
        "korean": "흉부 X선",
        "patient_friendly": "가슴 부위를 X선으로 촬영하는 검사",
        "category": "modality",
    },
    "US": {
        "korean": "초음파",
        "patient_friendly": "초음파를 이용해 신체 내부를 실시간으로 확인하는 검사",
        "category": "modality",
    },

    # --- Brain MRI sequence abbreviations ---
    "DWI": {
        "korean": "확산강조영상",
        "patient_friendly": "물 분자의 움직임을 측정해 급성 뇌경색 등을 조기 발견하는 MRI 기법",
        "category": "neuro",
    },
    "T2WI": {
        "korean": "T2 강조영상",
        "patient_friendly": "액체가 밝게 보이도록 설정한 MRI 영상 기법",
        "category": "neuro",
    },
    "T1WI": {
        "korean": "T1 강조영상",
        "patient_friendly": "지방이 밝게 보이도록 설정한 MRI 영상 기법",
        "category": "neuro",
    },
    "FLAIR": {
        "korean": "액체감쇠역전회복영상",
        "patient_friendly": "뇌척수액 신호를 제거해 뇌 병변을 더 잘 보이게 하는 MRI 기법",
        "category": "neuro",
    },
    "ADC": {
        "korean": "겉보기확산계수",
        "patient_friendly": "조직 내 물 분자의 확산 정도를 수치화한 MRI 지표",
        "category": "neuro",
    },
    "GRE": {
        "korean": "경사에코영상",
        "patient_friendly": "출혈이나 석회화를 민감하게 감지하는 MRI 기법",
        "category": "neuro",
    },

    # --- Nuclear medicine ---
    "SUV": {
        "korean": "표준화섭취값",
        "patient_friendly": "PET 검사에서 방사성 물질이 특정 부위에 얼마나 흡수되었는지를 나타내는 수치",
        "category": "nuclear",
    },
    "FDG": {
        "korean": "불소-18 포도당",
        "patient_friendly": "PET 검사에 사용되는 방사성 포도당 추적자",
        "category": "nuclear",
    },

    # --- Cardiovascular abbreviations ---
    "LAD": {
        "korean": "좌전하행지",
        "patient_friendly": "왼쪽 심장에 혈액을 공급하는 주요 관상동맥 중 하나",
        "category": "cardiovascular",
    },
    "RCA": {
        "korean": "우관상동맥",
        "patient_friendly": "오른쪽 심장에 혈액을 공급하는 관상동맥",
        "category": "cardiovascular",
    },
    "LCX": {
        "korean": "좌회선지",
        "patient_friendly": "왼쪽 심장 측벽에 혈액을 공급하는 관상동맥",
        "category": "cardiovascular",
    },
    "IVC": {
        "korean": "하대정맥",
        "patient_friendly": "하체의 혈액을 심장으로 운반하는 큰 정맥",
        "category": "cardiovascular",
    },
    "SVC": {
        "korean": "상대정맥",
        "patient_friendly": "상체의 혈액을 심장으로 운반하는 큰 정맥",
        "category": "cardiovascular",
    },
    "AAA": {
        "korean": "복부대동맥류",
        "patient_friendly": "배 부위 대동맥이 비정상적으로 부풀어 오른 상태 (응급 상황일 수 있음)",
        "category": "cardiovascular",
    },
    "PE": {
        "korean": "폐색전증",
        "patient_friendly": "혈전이 폐혈관을 막은 응급 상태",
        "category": "cardiovascular",
    },
    "DVT": {
        "korean": "심부정맥혈전증",
        "patient_friendly": "다리 등 깊은 정맥에 혈전이 생긴 상태",
        "category": "cardiovascular",
    },

    # --- Abdominal abbreviations ---
    "CBD": {
        "korean": "총담관",
        "patient_friendly": "담낭과 간에서 만들어진 담즙이 십이지장으로 흘러가는 관",
        "category": "abdomen",
    },
    "GB": {
        "korean": "담낭",
        "patient_friendly": "담즙을 저장하는 작은 주머니 (쓸개)",
        "category": "abdomen",
    },
    "GI": {
        "korean": "위장관",
        "patient_friendly": "입에서 항문까지 이어지는 소화 기관 전체",
        "category": "abdomen",
    },

    # --- Anatomical regions ---
    "chest": {
        "korean": "흉부",
        "patient_friendly": "가슴 부위 (폐, 심장, 흉벽 포함)",
        "category": "anatomy",
    },
    "thorax": {
        "korean": "흉부",
        "patient_friendly": "가슴 부위",
        "category": "anatomy",
    },
    "thoracic": {
        "korean": "흉부",
        "patient_friendly": "가슴 부위",
        "category": "anatomy",
    },
    "abdomen": {
        "korean": "복부",
        "patient_friendly": "배 부위 (간, 신장, 장 등 포함)",
        "category": "anatomy",
    },
    "abdominal": {
        "korean": "복부",
        "patient_friendly": "배 부위",
        "category": "anatomy",
    },
    "pelvis": {
        "korean": "골반",
        "patient_friendly": "골반 부위 (방광, 자궁, 직장 등 포함)",
        "category": "anatomy",
    },
    "pelvic": {
        "korean": "골반",
        "patient_friendly": "골반 부위",
        "category": "anatomy",
    },
    "brain": {
        "korean": "뇌",
        "patient_friendly": "머리 안의 뇌",
        "category": "anatomy",
    },
    "spine": {
        "korean": "척추",
        "patient_friendly": "등뼈 (목부터 허리까지)",
        "category": "anatomy",
    },
    "cervical spine": {
        "korean": "경추",
        "patient_friendly": "목뼈 (C1-C7)",
        "category": "anatomy",
    },
    "thoracic spine": {
        "korean": "흉추",
        "patient_friendly": "등뼈 (T1-T12)",
        "category": "anatomy",
    },
    "lumbar spine": {
        "korean": "요추",
        "patient_friendly": "허리뼈 (L1-L5)",
        "category": "anatomy",
    },
    "sacrum": {
        "korean": "천골",
        "patient_friendly": "척추 아래 끝에 위치한 삼각형 모양의 뼈",
        "category": "anatomy",
    },
    "neck": {
        "korean": "경부",
        "patient_friendly": "목 부위",
        "category": "anatomy",
    },
    "liver": {
        "korean": "간",
        "patient_friendly": "오른쪽 윗배에 위치한 소화·해독 기관",
        "category": "anatomy",
    },
    "kidney": {
        "korean": "신장",
        "patient_friendly": "허리 양쪽에 위치한 콩팥",
        "category": "anatomy",
    },
    "lung": {
        "korean": "폐",
        "patient_friendly": "호흡을 담당하는 가슴 안의 장기",
        "category": "anatomy",
    },
    "heart": {
        "korean": "심장",
        "patient_friendly": "혈액을 온몸으로 순환시키는 기관",
        "category": "anatomy",
    },
    "aorta": {
        "korean": "대동맥",
        "patient_friendly": "심장에서 나오는 가장 큰 동맥",
        "category": "anatomy",
    },
    "mediastinum": {
        "korean": "종격동",
        "patient_friendly": "양쪽 폐 사이의 공간 (심장, 대혈관, 식도 포함)",
        "category": "anatomy",
    },
    "hilum": {
        "korean": "폐문부",
        "patient_friendly": "폐로 혈관과 기관지가 들어오는 부위",
        "category": "anatomy",
    },
    "adrenal": {
        "korean": "부신",
        "patient_friendly": "신장 위에 위치한 호르몬 분비 기관",
        "category": "anatomy",
    },
    "thyroid": {
        "korean": "갑상선",
        "patient_friendly": "목 앞에 위치한 호르몬 분비 기관",
        "category": "anatomy",
    },
    "prostate": {
        "korean": "전립선",
        "patient_friendly": "방광 아래 남성 생식기 일부",
        "category": "anatomy",
    },
    "uterus": {
        "korean": "자궁",
        "patient_friendly": "여성 골반 내 생식 기관",
        "category": "anatomy",
    },
    "ovary": {
        "korean": "난소",
        "patient_friendly": "여성 골반 내 난자를 생성하는 기관",
        "category": "anatomy",
    },
    "bladder": {
        "korean": "방광",
        "patient_friendly": "소변을 저장하는 기관",
        "category": "anatomy",
    },
    "pancreas": {
        "korean": "췌장",
        "patient_friendly": "소화 효소와 인슐린을 분비하는 기관",
        "category": "anatomy",
    },
    "spleen": {
        "korean": "비장",
        "patient_friendly": "면역과 혈액 여과를 담당하는 기관 (왼쪽 윗배)",
        "category": "anatomy",
    },
    "gallbladder": {
        "korean": "담낭",
        "patient_friendly": "담즙을 저장하는 기관 (쓸개)",
        "category": "anatomy",
    },

    # --- Imaging study types (modality + region) ---
    "chest CT": {
        "korean": "흉부 CT",
        "patient_friendly": "가슴 부위를 CT로 촬영한 검사",
        "category": "modality",
    },
    "chest X-ray": {
        "korean": "흉부 X선",
        "patient_friendly": "가슴 부위를 X선으로 촬영한 검사",
        "category": "modality",
    },
    "chest radiograph": {
        "korean": "흉부 X선",
        "patient_friendly": "가슴 부위를 X선으로 촬영한 검사",
        "category": "modality",
    },
    "CT pulmonary angiography": {
        "korean": "CT 폐혈관조영술",
        "patient_friendly": "폐혈관을 조영제를 이용해 CT로 촬영하는 검사 (폐색전증 진단에 사용)",
        "category": "modality",
    },
    "CTPA": {
        "korean": "CT 폐혈관조영술",
        "patient_friendly": "폐혈관을 CT로 촬영하는 검사",
        "category": "modality",
    },
    "CT angiography": {
        "korean": "CT 혈관조영술",
        "patient_friendly": "혈관에 조영제를 투여하고 CT로 촬영하는 검사",
        "category": "modality",
    },
    "brain MRI": {
        "korean": "뇌 MRI",
        "patient_friendly": "뇌를 자기공명영상으로 촬영한 검사",
        "category": "modality",
    },
    "abdominal CT": {
        "korean": "복부 CT",
        "patient_friendly": "배 부위를 CT로 촬영한 검사",
        "category": "modality",
    },
    "abdomen CT": {
        "korean": "복부 CT",
        "patient_friendly": "배 부위를 CT로 촬영한 검사",
        "category": "modality",
    },
    "abdominal ultrasound": {
        "korean": "복부 초음파",
        "patient_friendly": "배 부위를 초음파로 촬영한 검사",
        "category": "modality",
    },
    "spine MRI": {
        "korean": "척추 MRI",
        "patient_friendly": "척추를 자기공명영상으로 촬영한 검사",
        "category": "modality",
    },
    "whole body PET-CT": {
        "korean": "전신 PET-CT",
        "patient_friendly": "전신의 대사 활동을 PET-CT로 촬영한 검사",
        "category": "modality",
    },
    "intravenous contrast": {
        "korean": "정맥 내 조영제",
        "patient_friendly": "혈관으로 투여하는 조영제 (혈관 및 장기 구조를 더 잘 보이게 함)",
        "category": "modality",
    },

    # --- Report section headers ---
    "clinical indication": {
        "korean": "임상적 적응증",
        "patient_friendly": "검사를 시행한 임상적 이유",
        "category": "report_structure",
    },
    "technique": {
        "korean": "검사 방법",
        "patient_friendly": "검사가 진행된 방식",
        "category": "report_structure",
    },
    "findings": {
        "korean": "소견",
        "patient_friendly": "영상 검사에서 발견된 내용",
        "category": "report_structure",
    },
    "impression": {
        "korean": "결론",
        "patient_friendly": "판독 의사의 최종 소견 요약",
        "category": "report_structure",
    },
    "conclusion": {
        "korean": "결론",
        "patient_friendly": "판독 결과의 최종 요약",
        "category": "report_structure",
    },
    "comparison": {
        "korean": "비교 영상",
        "patient_friendly": "이전 검사와 비교한 내용",
        "category": "report_structure",
    },

    # --- Common descriptors ---
    "pulmonary": {
        "korean": "폐",
        "patient_friendly": "폐와 관련된",
        "category": "lung",
    },
    "cardiac": {
        "korean": "심장",
        "patient_friendly": "심장과 관련된",
        "category": "cardiovascular",
    },
    "vascular": {
        "korean": "혈관",
        "patient_friendly": "혈관과 관련된",
        "category": "cardiovascular",
    },
    "bilateral": {
        "korean": "양측",
        "patient_friendly": "양쪽 모두",
        "category": "direction",
    },
    "unilateral": {
        "korean": "일측",
        "patient_friendly": "한쪽",
        "category": "direction",
    },
    "diffuse": {
        "korean": "미만성",
        "patient_friendly": "넓은 범위에 걸쳐 퍼져 있는",
        "category": "descriptor",
    },
    "focal": {
        "korean": "국소",
        "patient_friendly": "특정 부위에 한정된",
        "category": "descriptor",
    },
    "acute": {
        "korean": "급성",
        "patient_friendly": "갑자기 발생한",
        "category": "descriptor",
    },
    "chronic": {
        "korean": "만성",
        "patient_friendly": "오래 지속된",
        "category": "descriptor",
    },
    "subacute": {
        "korean": "아급성",
        "patient_friendly": "급성과 만성 사이의 경과",
        "category": "descriptor",
    },
    "mild": {
        "korean": "경도",
        "patient_friendly": "가벼운 정도",
        "category": "descriptor",
    },
    "moderate": {
        "korean": "중등도",
        "patient_friendly": "중간 정도",
        "category": "descriptor",
    },
    "severe": {
        "korean": "중증",
        "patient_friendly": "심한 정도",
        "category": "descriptor",
    },
    "interval": {
        "korean": "경과 중",
        "patient_friendly": "이전 검사 이후 변화",
        "category": "descriptor",
    },
    "stable": {
        "korean": "변화 없음",
        "patient_friendly": "이전 검사 대비 변화 없는 상태",
        "category": "descriptor",
    },
    "unchanged": {
        "korean": "변화 없음",
        "patient_friendly": "이전 검사 대비 변화 없음",
        "category": "descriptor",
    },
    "increased": {
        "korean": "증가",
        "patient_friendly": "이전보다 커지거나 많아진",
        "category": "descriptor",
    },
    "decreased": {
        "korean": "감소",
        "patient_friendly": "이전보다 작아지거나 줄어든",
        "category": "descriptor",
    },

    # --- Imaging finding abbreviations ---
    "GGO": {
        "korean": "간유리음영",
        "patient_friendly": "CT에서 폐가 반투명 유리처럼 뿌옇게 보이는 소견",
        "category": "lung",
    },
    "HU": {
        "korean": "하운즈필드 단위",
        "patient_friendly": "CT에서 조직 밀도를 나타내는 수치 단위",
        "category": "imaging_characteristic",
    },
}


# ---------------------------------------------------------------------------
# Negation patterns — phrases indicating absence or normal findings
# ---------------------------------------------------------------------------

NEGATION_PATTERNS: list[str] = [
    # English patterns
    "no ",
    "no evidence",
    "no evidence of",
    "not seen",
    "not identified",
    "not detected",
    "not visualized",
    "not observed",
    "without ",
    "without evidence",
    "absence of",
    "absent",
    "unremarkable",
    "within normal limits",
    "wnl",
    "normal in size",
    "normal in appearance",
    "no acute",
    "no significant",
    "no definite",
    "no focal",
    "no suspicious",
    "negative for",
    "free of",
    "clear of",

    # Korean patterns
    "없음",
    "관찰되지 않음",
    "관찰되지 않았습니다",
    "확인되지 않음",
    "확인되지 않았습니다",
    "이상 소견 없음",
    "이상 소견이 없습니다",
    "정상 범위",
    "정상 소견",
    "특이 소견 없음",
    "특이 소견이 없습니다",
    "음성",
    "보이지 않음",
    "보이지 않습니다",
    "발견되지 않음",
    "발견되지 않았습니다",
]


# ---------------------------------------------------------------------------
# Critical terms — findings that require immediate attention / flagging
# ---------------------------------------------------------------------------

CRITICAL_TERMS: list[str] = [
    # English critical terms
    "mass",
    "malignancy",
    "malignant",
    "cancer",
    "carcinoma",
    "sarcoma",
    "lymphoma",
    "metastasis",
    "metastatic",
    "hemorrhage",
    "haemorrhage",
    "bleeding",
    "infarction",
    "infarct",
    "stroke",
    "aneurysm",
    "dissection",
    "rupture",
    "perforation",
    "obstruction",
    "occlusion",
    "embolism",
    "pulmonary embolism",
    "pneumothorax",
    "tension pneumothorax",
    "tamponade",
    "pericardial tamponade",
    "abscess",
    "septic",
    "invasion",
    "invasive",
    "necrotizing",
    "necrosis",
    "acute",
    "critical",
    "urgent",
    "emergent",
    "life-threatening",
    "midline shift",
    "herniation",
    "hydrocephalus",
    "aortic dissection",

    # Korean critical terms
    "악성",
    "악성 종양",
    "암",
    "암종",
    "출혈",
    "경색",
    "뇌경색",
    "심근경색",
    "동맥류",
    "박리",
    "파열",
    "천공",
    "폐색",
    "색전증",
    "폐색전증",
    "기흉",
    "긴장성 기흉",
    "압박",
    "심낭압박",
    "농양",
    "괴사",
    "침범",
    "전이",
    "정중선 편위",
    "탈출증",
    "수두증",
    "대동맥 박리",
    "응급",
    "위급",
]
