# 판독문 번역 시스템
## Medical Imaging Report Korean Translation System

> 영어 의료영상 판독문을 한국어로 번역하고 환자 친화적 설명을 자동 생성합니다.
> 모든 처리는 오픈소스 모델을 사용하여 온프레미스(자체 서버)에서 이루어집니다.

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| 영→한 번역 | 의료 용어·수치·단위·해부학적 방향을 보존하며 번역 |
| 환자 설명 생성 | 요약 + 소견 목록 + 상세 설명을 쉬운 한국어로 자동 생성 |
| 2단계 번역 검증 | 규칙 기반(수치·단위·부정 표현) + LLM 기반(의미 왜곡) 이중 검사 |
| 신뢰도 점수 | 위험도·이슈 수 기반 0~1 신뢰도 자동 산출 |
| 위험 소견 감지 | 폐색전증·출혈·경색 등 위험 표현 자동 플래그 |
| RAG 의료 용어집 | 57개 방사선 용어 + 71개 위험 표현 벡터 검색 |
| 완전 오프라인 | 외부 API 호출 없음, 모든 모델 로컬 실행 |

---

## 아키텍처

```
브라우저 (Next.js :3000)
        │ HTTP / REST
        ▼
FastAPI 백엔드 (:8000)
   ├── MedicalTranslator
   │     ├── Helsinki-NLP/opus-mt-en-ko  (1차 기계 번역, CPU)
   │     └── qwen2.5:14b via Ollama      (의료 용어 정제 + 완전 한국어 변환)
   ├── MedicalRAG
   │     ├── BAAI/bge-m3                 (다국어 임베딩)
   │     └── ChromaDB                   (로컬 벡터 저장소)
   └── MedicalValidator
         ├── 규칙 기반                   (수치·단위·부정 표현 보존 검사)
         └── qwen2.5:14b via Ollama      (의미 왜곡 LLM 검증)
        │
        ▼
Ollama 서버 (:11434)
   └── qwen2.5:14b
```

**번역 파이프라인 (요청당):**

```
영문 판독문
    │
    ▼
Helsinki-NLP/opus-mt-en-ko   ← 1차 기계 번역 (CPU, ~100-300ms)
    │
    ▼
RAG 문맥 검색 (BGE-M3)        ← 관련 의료 용어 top-5 조회
    │
    ▼
qwen2.5:14b (Ollama)          ← 의료 용어 정제 + 완전 한국어 번역
    │
    ├→ 한국어 번역문
    ├→ 환자용 설명 (선택)
    └→ 번역 품질 검증 (선택)
         ├→ Tier 1: 규칙 기반 (수치·단위·부정 표현)
         └→ Tier 2: LLM 기반 (의미 왜곡) — 규칙 기반 통과 시 negation 오탐 필터링
```

---

## 오픈소스 모델

| 모델 | 역할 | 라이선스 |
|------|------|----------|
| **qwen2.5:14b** (Alibaba, Ollama) | 번역 정제 · 환자 설명 · LLM 검증 | Apache 2.0 |
| **Helsinki-NLP/opus-mt-en-ko** (HuggingFace) | 영→한 1차 기계 번역 초안 | CC-BY 4.0 |
| **BAAI/bge-m3** (HuggingFace) | 의료 용어 RAG 임베딩 | MIT |
| **ChromaDB** | 로컬 벡터 저장소 | Apache 2.0 |

모든 모델은 로컬에서 실행되며 데이터가 외부로 전송되지 않습니다.

---

## 시스템 요구사항

| 항목 | 최소 | 권장 |
|------|------|------|
| Python | 3.10+ | 3.11+ |
| Node.js | 18+ | 20 LTS |
| Ollama | latest | latest |
| RAM | 16 GB | 32 GB |
| 디스크 여유 공간 | 15 GB | 20 GB |
| GPU (선택) | 10 GB VRAM | 16 GB VRAM |

> GPU 없이 CPU만으로도 동작하지만 응답 속도가 느립니다 (번역 1회 약 30-90초).

---

## 빠른 시작

### 1. 사전 설치

```bash
# Ollama 설치 (macOS)
brew install ollama

# 모델 다운로드 (~9 GB)
ollama pull qwen2.5:14b
```

### 2. 백엔드

```bash
cd medical-translation

# 가상환경 생성 (최초 1회)
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 서버 시작
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 프론트엔드 (새 터미널)

```bash
cd medical-translation/frontend
npm install
npm run dev
```

### 4. 접속

| 서비스 | URL |
|--------|-----|
| 프론트엔드 | http://localhost:3000 |
| API 문서 (Swagger) | http://localhost:8000/docs |
| API 문서 (ReDoc) | http://localhost:8000/redoc |

---

## API 문서

### `POST /api/translate`

판독문을 번역하고 선택적으로 환자 설명과 검증을 수행합니다.

**요청:**
```json
{
  "text": "No acute cardiopulmonary findings. The lungs are clear.",
  "source_lang": "auto",
  "mode": "full"
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `text` | string | 원문 판독문 (최대 10,000자) |
| `source_lang` | `"auto"` \| `"en"` \| `"ko"` | 원문 언어 (기본값: auto) |
| `mode` | `"translation_only"` \| `"with_explanation"` \| `"full"` | 처리 수준 |

**응답:**
```json
{
  "original": "No acute cardiopulmonary findings. The lungs are clear.",
  "translated": "급성 심폐 이상 소견 없음. 폐는 명료합니다.",
  "patient_explanation": {
    "summary": "폐와 심장을 검사한 결과 급성 이상 소견이 없습니다. 폐는 명료하며 특별한 문제가 관찰되지 않았습니다.",
    "key_findings": [
      "폐에는 특별한 이상 소견이 관찰되지 않았으며, 이는 폐가 건강한 상태임을 의미합니다.",
      "심장 관련 급성 문제도 확인되지 않았습니다.",
      "전반적으로 정상 범위의 검사 결과입니다."
    ],
    "patient_text": "검사 결과 폐와 심장에 급성 이상 소견이 없습니다. 폐는 명료하며 특별한 문제가 발견되지 않았습니다. 정확한 진단과 치료 계획은 담당 의사 선생님과 상담하시기 바랍니다."
  },
  "validation": {
    "is_valid": true,
    "issues": [],
    "risk_level": "low",
    "confidence_score": 0.95
  },
  "critical_findings": [],
  "processing_time_ms": 28500
}
```

---

### `POST /api/validate`

기존 번역의 품질을 검증합니다 (재번역 없음).

**요청:**
```json
{
  "original": "Pulmonary embolism identified in the right lower lobe.",
  "translated": "우측 하엽에 폐색전증이 확인되었습니다."
}
```

---

### `GET /api/terms/search?q=nodule&limit=5`

의료 용어 사전을 의미 기반으로 검색합니다.

---

### `GET /api/health`

서비스 상태를 확인합니다.

```json
{
  "status": "ok",
  "models": {
    "ollama": "connected",
    "translator": "loaded",
    "rag": "loaded",
    "validator": "loaded"
  }
}
```

---

## 번역 모드별 성능

| 모드 | 예상 시간 | 용도 |
|------|-----------|------|
| `translation_only` | ~20-40초 | 빠른 번역만 필요할 때 |
| `with_explanation` | ~40-70초 | 환자 설명 포함 일반 사용 |
| `full` | ~60-90초 | QA 검토, 위험 판독문 |

> 첫 번째 요청은 모델 로딩으로 추가 시간이 소요됩니다.

---

## 검증 시스템

### 2단계 검증 구조

| 단계 | 방식 | 검사 항목 |
|------|------|-----------|
| Tier 1 | 규칙 기반 | 수치·단위 보존, 부정 표현 보존 |
| Tier 2 | LLM 기반 | 의미 왜곡, 임상적 오류 |

### 위험도 분류

| 위험도 | 트리거 조건 |
|--------|------------|
| 높음 (high) | LLM이 `meaning_distortion` 감지 |
| 중간 (medium) | 수치·단위 불일치, 부정 표현 불일치, 용어 오류 |
| 낮음 (low) | 이슈 없음 |

> 규칙 기반 부정 표현 검사를 통과한 경우 LLM의 negation_error 판단은 무시됩니다 (혼합 언어 오탐 방지).

### 신뢰도 점수 산출

| 위험도 | 기본 점수 | 이슈 1개당 감점 |
|--------|-----------|----------------|
| 낮음 | 0.95 | -0.05 |
| 중간 | 0.65 | -0.05 |
| 높음 | 0.35 | -0.05 |

---

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama 서버 주소 |
| `OLLAMA_MODEL` | `qwen2.5:14b` | 기본 LLM 모델 |
| `OLLAMA_FALLBACK_MODEL` | `qwen2.5:14b` | 폴백 LLM 모델 |
| `OLLAMA_TIMEOUT` | `120` | API 타임아웃 (초) |
| `TRANSLATION_MODEL` | `Helsinki-NLP/opus-mt-en-ko` | 1차 번역 모델 |
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | RAG 임베딩 모델 |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB 저장 경로 |
| `MAX_TEXT_LENGTH` | `10000` | 최대 입력 길이 |
| `LOG_LEVEL` | `INFO` | 로그 레벨 |

---

## 프로젝트 구조

```
medical-translation/
├── venv/                          # Python 가상환경
├── docker-compose.yml
├── setup.sh
├── start.sh
├── README.md
│
├── backend/
│   ├── main.py                    # FastAPI 앱 엔트리포인트
│   ├── config.py                  # 환경 변수 기반 설정
│   ├── schemas.py                 # Pydantic 요청/응답 모델
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── models/
│   │   ├── translator.py          # 번역 파이프라인 (Helsinki-NLP + Ollama)
│   │   ├── validator.py           # 2단계 검증기 (규칙 기반 + LLM)
│   │   └── prompts.py             # 의료 특화 프롬프트 템플릿
│   ├── rag/
│   │   ├── medical_terms.py       # 의료 용어 사전
│   │   └── vectorstore.py         # ChromaDB + BGE-M3 래퍼
│   └── data/
│       └── sample_reports.json    # 샘플 판독문
│
└── frontend/
    ├── app/
    │   ├── layout.tsx
    │   └── page.tsx
    ├── components/
    │   ├── TranslationForm.tsx     # 판독문 입력 폼
    │   ├── ResultPanel.tsx         # 번역·설명·검증 탭 패널
    │   └── CriticalFindingAlert.tsx
    ├── lib/
    │   ├── api.ts                  # API 클라이언트 + TypeScript 타입
    │   └── sampleReports.ts        # 샘플 판독문
    └── package.json
```

---

## 향후 개선 예정

### 권고사항 규칙 기반 전환
현재 권고사항은 LLM이 판독 소견을 읽고 자동 생성하는 방식입니다.
추후 아래 조건을 확정하면 규칙 기반으로 전환할 예정입니다.

- 특정 소견(결절 크기, 위험도 등) 감지 시 → 미리 정의된 권고 멘트 출력
- 모든 판독문에 routine으로 추가할 공통 멘트

> **TODO**: 조건 및 권고 멘트 확정 후 `backend/models/translator.py` 또는 별도 규칙 엔진으로 구현

---

## 라이선스

| 컴포넌트 | 라이선스 |
|----------|----------|
| qwen2.5 | Apache 2.0 |
| Helsinki-NLP opus-mt | CC-BY 4.0 |
| BGE-M3 | MIT |
| ChromaDB | Apache 2.0 |
| FastAPI | MIT |
| Next.js | MIT |
