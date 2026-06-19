"""im-not-ai v2.0 + PE 윤문 엔진.

기계적 규칙(regex): 직접 적용 후 변경 목록 반환.
판단 규칙(v2.0 A·B계열 + PE 압축): claude_guidance 문자열로 반환 → Claude 적용.
"""
from __future__ import annotations
import re

# ── 기계 적용 규칙 ────────────────────────────────────────────────────────

_EMOJI_RE = re.compile(
    r"[\U0001F300-\U0001F9FF\U00002702-\U000027B0"
    r"\U0000FE0F\U00002600-\U000026FF⭐⬆⤵⤴"
    r"\U0001FA00-\U0001FFFF]+",
    re.UNICODE,
)

_PIVOT = re.compile(
    r"(결론적으로|요약하면|정리하면|따라서|이상으로)[,\s]",
    re.UNICODE,
)

_COMMA_CONJ = re.compile(
    r"(함으로써|하므로|으로써|으로서|하여|해서|하면|하고|하니),\s",
    re.UNICODE,
)

_TRANSL = [
    (re.compile(r"\b본\s절\b"), "이 절"),
    (re.compile(r"\b본\s케이스\b"), "이 사례"),
    (re.compile(r"\b본\s연구\b"), "이 연구"),
    (re.compile(r"\b본\s과제\b"), "이 과제"),
    (re.compile(r"\b본\s방법\b"), "이 방법"),
    (re.compile(r"\b본\s문서\b"), "이 문서"),
]

_SYMBOLS = [
    (re.compile(r"⭐"), "[핵심]"),
    (re.compile(r"★"), "[1순위]"),
    (re.compile(r"☆"), "[참고]"),
    (re.compile(r"✅"), "[완료]"),
    (re.compile(r"❌"), "[제외]"),
    (re.compile(r"🚦"), "[신호]"),
    (re.compile(r"🎯"), "[목표]"),
    (re.compile(r"📐"), "[설계]"),
    (re.compile(r"📥"), "[입력]"),
    (re.compile(r"❓"), "[확인필요]"),
]


def _apply_mechanical(text: str, mode: str) -> tuple[str, list[str]]:
    """기계 규칙 적용. (변환된 텍스트, 변경 요약 목록) 반환."""
    changes: list[str] = []

    # C-5: 이모지 → 텍스트 또는 제거
    n_emoji = len(_EMOJI_RE.findall(text))
    if n_emoji:
        for pat, repl in _SYMBOLS:
            text = pat.sub(repl, text)
        text = _EMOJI_RE.sub("", text)
        changes.append(f"C-5 이모지 제거/변환: {n_emoji}건")

    # D-1: 결산피벗 어구 삭제
    n_pivot = len(_PIVOT.findall(text))
    if n_pivot:
        text = _PIVOT.sub("", text)
        changes.append(f"D-1 결산피벗 삭제(결론적으로·따라서 등): {n_pivot}건")

    # C-11: 연결어미 뒤 쉼표 제거
    n_comma = len(_COMMA_CONJ.findall(text))
    if n_comma:
        text = _COMMA_CONJ.sub(lambda m: m.group(1) + " ", text)
        changes.append(f"C-11 연결어미 뒤 쉼표 제거: {n_comma}건")

    # 번역투 교정
    n_transl = 0
    for pat, repl in _TRANSL:
        found = len(pat.findall(text))
        n_transl += found
        text = pat.sub(repl, text)
    if n_transl:
        changes.append(f"번역투 교정(본→이): {n_transl}건")

    return text, changes


# ── Claude 지침 생성 ──────────────────────────────────────────────────────

_V20_GUIDANCE = """## im-not-ai v2.0 판단 규칙 (Claude 적용)

### 서술어 완성 (S1 — 20건 내외)
- 명사 종결 → 합쇼체: "발생함" → "발생합니다", "필수적" → "필수적입니다"
- 단, 테이블 셀·제목·코드·수식은 제외

### A-15 추정→단언 (S2)
- "~일 것으로 추정됩니다" → "~입니다"
- "~빠를 것으로 추정됩니다" → "~빠릅니다"
- 단, 가설(H1~H5) 섹션 내 명시적 불확실 표현은 유지

### A-16 대명사 직역 (S1)
- "그" "그녀" 가 사람/가설 지칭 시 → 구체명사로 대체
  (예: "그가 주장" → "해당 가설이 주장")

### 강조기호 텍스트화 (S1)
- ⭐ → [핵심], ★ → [1순위 레버], ☆ → [참고]  (기계규칙 후 잔여분)

### 자체검증 체크리스트
1. S1 패턴 0건 목표
2. S2 ≤ 2건
3. 변경률 10~25%
4. 등급 A 기준: S1=0, S2≤2, 변경률 10~25%
"""

_PE_GUIDANCE = """## 공정엔지니어(PE) 압축 규칙 (추가 적용)

### 핵심 원칙
- 배경 지식 설명 → 삭제 또는 1줄 요약
- 설명 문단(~합니다 이유는/~다음과 같은 이유로) → 불릿(▶) 또는 표
- 합쇼체 설명문 → 명령형 불릿: "측정합니다" → "측정한다", "확인합니다" → "확인한다"
- 중복 표현 제거: "~에 대해 설명합니다. 내용은 다음과 같습니다." → 삭제

### 가설 섹션 압축
- 개별 가설 상세 서술(H1~H5 각 소절) → 가설 비교표 1개로 통합
- 각 가설 1줄 핵심 메커니즘만 보존

### 분량 목표
- 원본 대비 40~50% 압축
- 숫자·스펙·게이트 기준(감도비 0.95, n=12, 8주 등)은 변경 없이 유지

### 유지 항목 (삭제 금지)
- 모든 수치/기준값/임계치
- 테이블 전체
- Decision Gate 규칙
- 측정 항목 목록
- 리스크 대응 방안
"""


def build_guidance(mode: str) -> str:
    if mode == "v20":
        return _V20_GUIDANCE
    if mode == "pe":
        return _PE_GUIDANCE
    # v20pe (기본)
    return _V20_GUIDANCE + "\n" + _PE_GUIDANCE


# ── 공개 API ──────────────────────────────────────────────────────────────

def humanize(content: str, mode: str = "v20pe") -> dict:
    """
    content: 윤문할 원문(HTML 또는 텍스트)
    mode: 'v20' | 'pe' | 'v20pe'
    반환: {applied: [...], content: str, guidance: str}
    """
    text, changes = _apply_mechanical(content, mode)
    guidance = build_guidance(mode)
    return {
        "applied": changes,
        "content": text,
        "guidance": guidance,
    }


MODES = {
    "v20": "im-not-ai v2.0 윤문만 (이모지·서술어·번역투·결산피벗·쉼표 교정)",
    "pe": "공정엔지니어 압축만 (설명문→명령형 불릿, 가설→요약표, ~50% 압축)",
    "v20pe": "v2.0 윤문 + PE 압축 통합 (기본 권장)",
}
