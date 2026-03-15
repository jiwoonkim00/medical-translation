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
