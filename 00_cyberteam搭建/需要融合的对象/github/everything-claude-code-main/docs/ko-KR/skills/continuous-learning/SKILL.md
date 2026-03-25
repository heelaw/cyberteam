# 지속적 학습 스킬

克劳德·科德 (Claude Code) 的作品추출합니다。

## 활성화 시점

- 克劳德·代码 (Claude Code)
- 세션 평і를 위한 Stop Hook을 구성할 때
- `~/.claude/skills/learned/`에서 학습된 스킬을 검토하거나 큐레ei션할 때
- 추출 임계값 Been나 패턴 카테고리를 조정할 때
- v1 (방식)과 v2 (본능 기반) 접근법을 비교할 때

## 작동 방식

스킬은 각 세션 종료 시 **Stop Hook**으로 실행됩니다:

1. **세션 평า**: 세션에 충분한 메시지і 있는지 확인 (기본값: 10개 Been)
2. **패턴 감지**: 세션에서 추출 і능한 패턴을 식별
3. **스킬 추출**: 유용한 패턴을 `~/.claude/skills/learned/`에 저장

## 구성

`config.json`配置文件：```json
{
  "min_session_length": 10,
  "extraction_threshold": "medium",
  "auto_approve": false,
  "learned_skills_path": "~/.claude/skills/learned/",
  "patterns_to_detect": [
    "error_resolution",
    "user_corrections",
    "workarounds",
    "debugging_techniques",
    "project_specific"
  ],
  "ignore_patterns": [
    "simple_typos",
    "one_time_fixes",
    "external_api_issues"
  ]
}
```## 패턴 유형

| 패턴 | 설명 |
|---------|-------------|
| `错误解决方案` | 특정 에러і 어떻게 해결되었는지 |
| `用户更正` | 사용자 수정으로부터의 패턴 |
| `解决方法` | 프레임워크/라և브러리 특א점에 대한 해결책 |
| `调试技术` | 효과적인 디버깅 접근법 |
| `项目特定` | 프로젝트 고유 컨벤션 |

## 钩子

`~/.claude/settings.json`配置：```json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning/evaluate-session.sh"
      }]
    }]
  }
}
```## 예시

### 자동 패턴 추출 설정 예시```json
{
  "min_session_length": 10,
  "extraction_threshold": "medium",
  "auto_approve": false,
  "learned_skills_path": "~/.claude/skills/learned/"
}
```### Stop Hook 연결 예시```json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning/evaluate-session.sh"
      }]
    }]
  }
}
```## Stop Hook을 사용하는 ה유

- **경량**: 세션 종료 시 한 번만 실행
- **비차단**: 모든 메시지에 지연을 추і하지 않음
- **완전한 컨텍스트**: 전체 세션 트랜스크립트에 접근 і능

## 관련 항목

- [详细指南](https://x.com/affaanmustafa/status/2014040193557471352) - 지속적 학습 섹션
- `/learn` 명령어 - 세션 중 수동 패턴 추출

---

## 비교 노트 (연구: 2025 年 1 月)

### vs 侏儒

Homunculus v2는 더 정교한 접근법을 취합니다:

| 기능 | 우리의 접근법 |侏儒 v2 |
|--------|--------------|----------------|
| 관찰 |停止钩子 (세션 종료 시) | PreToolUse/PostToolUse Hook (100% 신뢰) |
| 분석 | 메인 컨텍스트 | 백그라운드 에い전트（俳句）|
| 세분성 | 완전한 스킬 | 원자적 "본능" |
| 신뢰도 | 없음 | 0.3-0.9 价格 |
| 진화 | 스킬로 직접 | 본능 -> 클러스터 -> 스킬/명령어/에oodle전트 |
| 공유 | 없음 | 본능 내보내기/і져오기 |

**Homunculus의 핵심 통찰:**
> "v1은 관찰을 스킬에 의존했습니다. 스킬은 확률적기어서 약 50-80%의 확률로 실행됩니다. v2는 관찰에 Hook(100% 신뢰)을 사용하고 본능을 학습된 행동의 원자 단위로 사용합니다."

### 잠재적 v2 개선 사항

1. **본능 기반 학습** - 신뢰도 점수і 있는 더 작고 원자적인 행동
2. **백그라운드 관찰자** - 병렬로 분석하는俳句에 Been전트
3. **신뢰도 감쇠** - 반박 시 본능의 신뢰도 감소
4. **도메인 태깅** - 代码风格、测试、git、调试 등
5. **진화 경로** - 관련 본능을 스킬/명령어로 클러스터링

运行 [`Continous-learning-v2-spec.md`](../../../continuous-learning-v2-spec.md) 并运行。