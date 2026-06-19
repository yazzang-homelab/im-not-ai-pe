# MCP 도구 — doc_humanize

im-not-ai v2.0 + PE 규칙을 Claude Code MCP로 호출하는 도구입니다.

## 파일 구성

| 파일 | 역할 |
|------|------|
| `humanize.py` | 기계 규칙 엔진 + Claude guidance 생성기 |
| `README.md` | 이 문서 |

## 설치 방법

### cng-ui MCP 서버에 통합하는 경우 (권장)

```bash
# 1. humanize.py 복사
cp humanize.py /root/projects/cng-ui-mcp/

# 2. server.py 수정
```

**server.py 상단** — import 추가:
```python
import humanize as HZ
```

**server.py 하단** — 도구 등록 (`if __name__ == "__main__":` 바로 위):
```python
@mcp.tool()
def doc_humanize(content: str, mode: str = "v20pe", file_path: str = "") -> str:
    """im-not-ai v2.0 + 공정엔지니어(PE) 스타일로 문서를 윤문한다.

    file_path: 파일 경로를 주면 content 대신 파일을 읽는다 (절대 경로).
    content: 윤문할 원문 (HTML 또는 텍스트). file_path가 있으면 무시.
    mode: 'v20pe'(기본) | 'v20'(윤문만) | 'pe'(PE 압축만)

    반환(JSON):
      applied   — 기계 규칙 적용 목록 (이모지·쉼표·번역투·결산피벗)
      content   — 기계 규칙 적용 후 텍스트 (Claude가 guidance 규칙 추가 적용)
      guidance  — Claude가 적용해야 할 판단 규칙 전문
      modes     — 사용 가능한 mode 설명
    """
    import json
    from pathlib import Path

    if file_path:
        p = Path(file_path)
        if not p.exists():
            return json.dumps({"error": f"파일 없음: {file_path}"}, ensure_ascii=False)
        content = p.read_text(encoding="utf-8")

    if not content.strip():
        return json.dumps({"error": "content 또는 file_path 필요"}, ensure_ascii=False)

    result = HZ.humanize(content, mode=mode)
    result["modes"] = HZ.MODES
    return json.dumps(result, ensure_ascii=False, indent=2)
```

```bash
# 3. MCP 서버 재시작 (Claude Code 재시작으로 자동 반영)
```

### 독립 MCP 서버로 구성하는 경우

```bash
pip install mcp fastmcp
python humanize.py  # stdio MCP 서버로 실행
```

`~/.claude.json` 또는 `claude_desktop_config.json`에 추가:
```json
{
  "mcpServers": {
    "humanize-pe": {
      "command": "python",
      "args": ["/path/to/mcp/humanize_server.py"]
    }
  }
}
```

## 사용법

```python
# 파일 경로로 직접 처리
result = mcp__cng-ui__doc_humanize(
    file_path="/var/www/reports/my_report.html",
    mode="v20pe"
)

# 텍스트로 처리
result = mcp__cng-ui__doc_humanize(
    content="결론적으로, 본 절에서 발생함. ⭐핵심.",
    mode="v20"
)
```

## 반환값 구조

```json
{
  "applied": [
    "C-5 이모지 제거/변환: 27건",
    "D-1 결산피벗 삭제: 2건",
    "번역투 교정(본→이): 1건"
  ],
  "content": "<!-- 기계 규칙 적용 후 HTML/텍스트 -->",
  "guidance": "## im-not-ai v2.0 판단 규칙\n...\n## PE 규칙\n...",
  "modes": {
    "v20": "im-not-ai v2.0 윤문만",
    "pe": "공정엔지니어 압축만",
    "v20pe": "v2.0 윤문 + PE 압축 통합 (기본 권장)"
  }
}
```

## 동작 원리

### 기계 적용 (humanize.py 내부, 즉시 변환)

| 규칙 | 방법 |
|------|------|
| C-5 이모지 | 정규식으로 텍스트 치환 (⭐→[핵심]) 후 나머지 제거 |
| D-1 결산피벗 | "결론적으로·따라서·요약하면" 정규식 삭제 |
| C-11 쉼표 | 연결어미 뒤 쉼표 정규식 제거 |
| 번역투 | "본 절→이 절" 등 정규식 치환 |

### Claude 판단 (guidance로 반환, Claude가 적용)

| 규칙 | 이유 |
|------|------|
| 서술어 완성 | 문맥 파악 필요 (테이블 셀 제외 등) |
| A-15 추정→단언 | 가설 섹션 여부 판단 필요 |
| PE 배경 압축 | 어떤 내용이 "배경 지식"인지 AI 판단 필요 |
| PE 가설→표 | 문서 구조 파악 필요 |
