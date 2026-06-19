# im-not-ai-pe

**im-not-ai v2.0 + 공정엔지니어(PE) 스타일 확장판**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 원작: [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai) (MIT)  
> 확장: [dreamworker0/urimal-for-socialworker](https://github.com/dreamworker0/urimal-for-socialworker) (MIT)

---

## 이게 뭔가요?

기술 보고서·분석 문서를 **AI 냄새 없이, 공정엔지니어 스타일로** 다듬는 도구입니다.

| 변환 전 | 변환 후 |
|---------|---------|
| "⭐ 결론적으로, 본 절에서 확인 가능합니다." | "[핵심] 이 절에서 확인합니다." |
| H1~H5 각 소절 설명문 (6개, 1200자) | 가설 비교표 1개 + 2-진단 원칙 2줄 |
| "~이 발생함", "~이 필수적" | "~이 발생합니다", "~이 필수적입니다" |
| 설명적 산문 중심 | 명령형 불릿 (`▶`) + 테이블 중심 |

---

## 원본 im-not-ai v2.0 대비 추가한 것

### PE(공정엔지니어) 규칙 5가지

| 규칙 | 내용 | 효과 |
|------|------|------|
| PE-1 배경 지식 압축 | 엔지니어가 이미 아는 설명 → 삭제 또는 1줄 요약 | 분량 20~30%↓ |
| PE-2 설명문 → 명령형 | "~합니다 이유는" → `▶` 불릿 | 가독성↑ |
| PE-3 가설 소절 → 요약표 | H1~H5 개별 서술 → 가설 비교표 1개 | 분량 40%↓ |
| PE-4 서술어 명령화 | "확인합니다" → "확인한다" | 엔지니어 문체 |
| PE-5 분량 목표 | 원본 대비 40~50% 압축 | 핵심 집중 |

### 유지 항목 (PE 규칙에서도 절대 삭제 금지)
- 수치·스펙·기준값 (PCE 18.2%, n=12 등)
- 테이블 전체
- Decision Gate 규칙
- 리스크 대응 방안
- 측정 항목 목록

---

## MCP 도구

Claude Code에 연결해 `mcp__cng-ui__doc_humanize`로 바로 호출할 수 있습니다.

### 설치 (cng-ui MCP 기준)

```bash
# 1. humanize.py를 cng-ui MCP 디렉토리에 복사
cp mcp/humanize.py /root/projects/cng-ui-mcp/

# 2. server.py에 import 및 도구 등록 (mcp/server_patch.py 참조)
# 또는 README의 "server.py 패치" 섹션 참조
```

### server.py 패치

```python
# server.py 상단 import에 추가
import humanize as HZ

# 하단 @mcp.tool() 블록 추가
@mcp.tool()
def doc_humanize(content: str, mode: str = "v20pe", file_path: str = "") -> str:
    """im-not-ai v2.0 + 공정엔지니어(PE) 스타일로 문서를 윤문한다.

    file_path: 파일 경로를 주면 content 대신 파일을 읽는다.
    mode: 'v20pe'(기본) | 'v20'(윤문만) | 'pe'(PE 압축만)

    반환(JSON):
      applied   — 기계 규칙 적용 목록
      content   — 기계 규칙 적용 후 텍스트
      guidance  — Claude가 추가로 적용해야 할 판단 규칙
    """
    if file_path:
        from pathlib import Path
        p = Path(file_path)
        if not p.exists():
            import json
            return json.dumps({"error": f"파일 없음: {file_path}"}, ensure_ascii=False)
        content = p.read_text(encoding="utf-8")

    if not content.strip():
        import json
        return json.dumps({"error": "content 또는 file_path 필요"}, ensure_ascii=False)

    import json
    result = HZ.humanize(content, mode=mode)
    result["modes"] = HZ.MODES
    return json.dumps(result, ensure_ascii=False, indent=2)
```

### 사용법

```python
# Claude Code에서
mcp__cng-ui__doc_humanize(
    file_path="/var/www/reports/my_report.html",
    mode="v20pe"   # v20 | pe | v20pe
)
```

반환값의 `content`에 기계 규칙이 적용된 텍스트, `guidance`에 Claude가 추가로 적용할 규칙이 담겨 옵니다.

---

## Claude Code 스킬 설치

```bash
# Claude Code 스킬 디렉토리에 복사
cp -r .claude/skills/humanize-pe ~/.claude/skills/
```

이후 대화에서 `/humanize-pe` 또는 관련 프롬프트로 활성화됩니다.

---

## 예시

가상 시나리오: 페로브스카이트 박막 스핀코팅 균일도 개선 (PSC-A 소형 모듈)

- **원본 AI 초안**: 이모지, 피벗어, 번역투, 명사 종결, H1~H3 상세 서술
- **v2.0 윤문 후**: S1·S2 패턴 제거, 합쇼체 전환, 대명사 수정
- **PE 개조 후**: 분량 ~55%로 압축, 가설 비교표 통합, 명령형 불릿 전환

| 예시 | 링크 |
|------|------|
| 변환 전 (AI 초안) | [before.html](https://yazzang-homelab.github.io/im-not-ai-pe/examples/before.html) |
| 변환 후 (v2.0 + PE) | [after\_pe.html](https://yazzang-homelab.github.io/im-not-ai-pe/examples/after_pe.html) |
| 원본·v2.0·v2.0+PE 3단 비교 | [diff\_v20\_vs\_original.html](https://yazzang-homelab.github.io/im-not-ai-pe/examples/diff_v20_vs_original.html) |

---

## 규칙 요약 (v2.0 + PE 통합)

전체 규칙은 [`rules/pe-rules.md`](rules/pe-rules.md)를 참조하세요.

### 기계 자동 적용 (humanize.py)
| 규칙 | 내용 | 심각도 |
|------|------|--------|
| C-5 | 이모지 제거 및 텍스트 변환 | S1 |
| D-1 | 결산피벗 삭제 (결론적으로·따라서·요약하면) | S1 |
| C-11 | 연결어미 뒤 쉼표 제거 | S1 |
| 번역투 | 본 절→이 절, 본 케이스→이 사례 등 | S1 |
| 강조기호 | ⭐→[핵심], ★→[1순위] | S1 |

### Claude 판단 적용 (guidance로 전달)
| 규칙 | 내용 | 심각도 |
|------|------|--------|
| 서술어 완성 | 명사 종결 → 합쇼체 (~20건) | S1 |
| A-15 | 추정→단언 ("~일 것" → "~이다") | S2 |
| A-16 | 대명사 직역 수정 (그→구체명사) | S1 |
| PE-1~5 | 설명문 압축·명령형·가설 표 통합 | PE |

---

## 등급 기준 (v2.0)

| 등급 | 조건 |
|------|------|
| **A** | S1=0건, S2≤2건, 변경률 10~25% |
| B | S1≤2건, S2≤5건, 변경률 10~30% |
| C | S1≤5건 또는 변경률 30~50% |
| D | S1 6건+, 변경률 50%+ |

---

## 라이선스

MIT License — 원저작자 표시 의무:
- epoko77-ai (im-not-ai)
- dreamworker0 (urimal-for-socialworker)

자세한 내용은 [LICENSE](LICENSE) 참조.
