# 변경 이력

## v1.0.0 (2026-06-19)

### 신규
- **PE 규칙 5가지** 추가 (PE-1~5): 배경 지식 압축, 설명문→명령형 불릿, 가설 소절→요약표, 서술어 명령화, 분량 목표
- **MCP 도구** `doc_humanize`: im-not-ai v2.0 기계 규칙을 자동 적용하고 Claude 판단 규칙(guidance)을 반환
  - mode: `v20pe`(기본) / `v20` / `pe`
  - file_path 파라미터로 HTML 파일 직접 처리
- **Claude Code 스킬** `humanize-pe`: MCP→v2.0→PE 순서로 자동화된 3단계 적용
- **가상 예시**: 페로브스카이트 박막 스핀코팅 균일도 개선 시나리오 (PSC-A 모듈, 가상)
  - `examples/before.html`: AI 초안 (이모지, D-1 피벗, 번역투, 명사형 종결)
  - `examples/after_pe.html`: v2.0 + PE 변환 결과 (분량 ~55% 압축)
  - `examples/diff_v20_vs_original.html`: 원본 vs v2.0 vs v2.0+PE 3단 나란히 비교

### 기반
- [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai) v2.0 (MIT)
- [dreamworker0/urimal-for-socialworker](https://github.com/dreamworker0/urimal-for-socialworker) (MIT)
