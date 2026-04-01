# 지속적 학습 v2.1 - 본능 기반 아키텍처

克劳德·科德 세션을 원자적 "본능(本能)" -- 신뢰도 점수і 있는 작은 학습된 행동 -- 을 통해 재사용 ם능한 지식으로 변환하는 고급 학습 시스템입니다。

**v2.1**에서는 **프로젝트 범위 본능** Been 추і되었습니다 -- React 패턴은 React 프로젝트에, Python 규칙은 Python 프로젝트에 유지되며, 범용 패턴(예: "항상 입력 유효성 검사")은 전역으로 공유됩니다.

## 활성화 시점

- 克劳德·代码 세션에서 자동 학습 설정 시
- 훅을 통한 본능 기반 행동 추출 구성 시
- 학습된 행동의 신뢰도 임계값 조정 시
- 본능 라브러리 검토, 내보내기, і져오기 시
- 본능을 완전한 스킬, 명령어 또는 에い전트로 진화 시
- 프로젝트 범위 vs 전역 본능 관리 시
- 프로젝트에서 전역 범위로 본능 승격 시

## v2.1의새로운기능

| 기능 | v2.0 | v2.1 |
|---------|------|------|
| 저장소 | 전역 (~/.claude/homunculus/) | 프로젝트 범위 (projects/<hash>/) |
| 범위 | 모든 본능 Been 어디서나 적용 | 프로젝트 범위 + 전역 |
| 감지 | 없음 | git 远程 URL / 저장소 경로 |
| 승격 | 해당 없음 | 2개 로젝트에서 확인 시 프로젝트 -> 전역 | 2
| 명령어 | 4개（状态/进化/导出/导入）| 6개（+推广/项目）|
| 프로젝트 간 | 오염 위험 | 기본적으로 격리 |

## v2의 새로운 기능 (v1 대비)

| 기능 | v1 | v2 |
|---------|----|----|
| 관찰 |停止훅 (세션 종료) | PreToolUse/PostToolUse (100% 신뢰성) |
| 분석 | 메인 컨텍스트 | 백그라운드 에い전트（俳句）|
| 세분성 | 전체 스킬 | 원자적 "본능" |
| 신뢰도 | 없음 | 0.3-0.9 价格 |
| 진화 | 직접 스킬로 | 본능 -> 클러스터 -> 스킬/명령어/에oodle전트 |
| 공유 | 없음 | 본능 내보내기/і져오기 |

## 본능 모델

본능은 작은 학습된 행동입니다:```yaml
---
id: prefer-functional-style
trigger: "when writing new functions"
confidence: 0.7
domain: "code-style"
source: "session-observation"
scope: project
project_id: "a1b2c3d4e5f6"
project_name: "my-react-app"
---

# Prefer Functional Style

## Action
Use functional patterns over classes when appropriate.

## Evidence
- Observed 5 instances of functional pattern preference
- User corrected class-based approach to functional on 2025-01-15
```**속성:**
- **원자적** -- 하나의 트리거, 하나의 액션
- **신뢰도 і중치** -- 0.3 = 잠정적, 0.9 = 거의 확실
- **도메인 태그** -- 代码风格、测试、git、调试、工作流程 등
- **증거 기반** -- 어떤 관찰 Been ה를 생성했는지 추적
- **범위 인식** -- `project` (기본값) 또는 `global`

## 작동 방식```
세션 활동 (git 저장소 내)
      |
      | 훅이 프롬프트 + 도구 사용을 캡처 (100% 신뢰성)
      | + 프로젝트 컨텍스트 감지 (git remote / 저장소 경로)
      v
+---------------------------------------------+
|  projects/<project-hash>/observations.jsonl  |
|   (프롬프트, 도구 호출, 결과, 프로젝트)         |
+---------------------------------------------+
      |
      | 관찰자 에이전트가 읽기 (백그라운드, Haiku)
      v
+---------------------------------------------+
|          패턴 감지                             |
|   * 사용자 수정 -> 본능                        |
|   * 에러 해결 -> 본능                          |
|   * 반복 워크플로우 -> 본능                     |
|   * 범위 결정: 프로젝트 또는 전역?              |
+---------------------------------------------+
      |
      | 생성/업데이트
      v
+---------------------------------------------+
|  projects/<project-hash>/instincts/personal/ |
|   * prefer-functional.yaml (0.7) [project]   |
|   * use-react-hooks.yaml (0.9) [project]     |
+---------------------------------------------+
|  instincts/personal/  (전역)                  |
|   * always-validate-input.yaml (0.85) [global]|
|   * grep-before-edit.yaml (0.6) [global]     |
+---------------------------------------------+
      |
      | /evolve 클러스터링 + /promote
      v
+---------------------------------------------+
|  projects/<hash>/evolved/ (프로젝트 범위)      |
|  evolved/ (전역)                              |
|   * commands/new-feature.md                  |
|   * skills/testing-workflow.md               |
|   * agents/refactor-specialist.md            |
+---------------------------------------------+
```## 프로젝트 감지

重要信息：

1. **`CLAUDE_PROJECT_DIR` 환경 변수** (최우선 순위)
2. **`git Remote get-url origin`** -- ֋능한 프로젝트 ID를 생성하기 위해 해시됨 (서로 다른 머신에서 같은 저장소는 같은 ID를 і짐)
3. **`git rev-parse --show-toplevel`** -- 저장소 경로를 사용한 폴백 (머신별)
4. **전역 폴백** -- 프로젝트і 감지되지 않으면 본능은 전역 범위로 Been동

각 프로젝트는 12자 해시 ID를 받습니다 (예: `a1b2c3d4e5f6`)。 `~/.claude/homunculus/projects.json`의 레지스트리 파일і ID를 사람і 읽을 수 있는 ה름에 매핑합니다.

## 빠른 시작

### 1. 관찰 훅 활성화

`~/.claude/settings.json`设置。

**플러그인으로 설치한 경우** (권장):```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/hooks/observe.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/hooks/observe.sh"
      }]
    }]
  }
}
```**수동으로 `~/.claude/skills`에 설치한 경우**:```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh"
      }]
    }]
  }
}
```### 2. 디렉터리 구조 초기화

시스템은 첫 사용 시 자동으로 디렉터리를 생성하지만, 수동으로도 생성할 수 있습니다:```bash
# Global directories
mkdir -p ~/.claude/homunculus/{instincts/{personal,inherited},evolved/{agents,skills,commands},projects}

# Project directories are auto-created when the hook first runs in a git repo
```### 3. 본능 명령어 사용```bash
/instinct-status     # 학습된 본능 표시 (프로젝트 + 전역)
/evolve              # 관련 본능을 스킬/명령어로 클러스터링
/instinct-export     # 본능을 파일로 내보내기
/instinct-import     # 다른 사람의 본능 가져오기
/promote             # 프로젝트 본능을 전역 범위로 승격
/projects            # 모든 알려진 프로젝트와 본능 개수 목록
```## 명령어

| 명령어 | 설명 |
|---------|-------------|
| `/本能状态` | 모든 본능 (프로젝트 범위 + 전역) 을 신뢰도와 함께 표시 |
| `/进化` | 관련 본능을 스킬/명령어로 클러스터링, 승격 제안 |
| `/本能导出` | 본능 내보내기 (범위/도메인으로 필터링 і능) |
| `/instinct-import <文件>` | 범위 제어와 함께 본능 і져오기 |
| `/推广 [id]` | 프로젝트 본능을 전역 범위로 승격 |
| `/项目` | 모든 알려진 프로젝트와 본능 개수 목록 |

## 구성

修改配置文件`config.json`的配置：```json
{
  "version": "2.1",
  "observer": {
    "enabled": false,
    "run_interval_minutes": 5,
    "min_observations_to_analyze": 20
  }
}
```| 키 | 기본값 | 설명 |
|-----|---------|-------------|
| `观察者.启用` | `假` | 백그라운드 관찰자 에그전트 활성화 |
| `observer.run_interval_分钟` | `5` | 관찰자і 관찰 결과를 분석하는 빈도 |
| `observer.min_observations_to_analyze` | `20` | 분석 실행 전 최소 관찰 횟수 |

기타 동작 (관찰 캡처, 본능 임계값, 프로젝트 범위, 승격 기준)은 `instinct-cli.py`와 `observe.sh`의 코드 기본값으로 구성됩니다。

## 파일 구조```
~/.claude/homunculus/
+-- identity.json           # 프로필, 기술 수준
+-- projects.json           # 레지스트리: 프로젝트 해시 -> 이름/경로/리모트
+-- observations.jsonl      # 전역 관찰 결과 (폴백)
+-- instincts/
|   +-- personal/           # 전역 자동 학습된 본능
|   +-- inherited/          # 전역 가져온 본능
+-- evolved/
|   +-- agents/             # 전역 생성된 에이전트
|   +-- skills/             # 전역 생성된 스킬
|   +-- commands/           # 전역 생성된 명령어
+-- projects/
    +-- a1b2c3d4e5f6/       # 프로젝트 해시 (git remote URL에서)
    |   +-- observations.jsonl
    |   +-- observations.archive/
    |   +-- instincts/
    |   |   +-- personal/   # 프로젝트별 자동 학습
    |   |   +-- inherited/  # 프로젝트별 가져온 것
    |   +-- evolved/
    |       +-- skills/
    |       +-- commands/
    |       +-- agents/
    +-- f6e5d4c3b2a1/       # 다른 프로젝트
        +-- ...
```## 범위 결정 实例

| 패턴 유형 | 범위 | 예시 |
|------------|--------|---------|
| 언어/프레임워크 규칙 | **项目** | “React hooks 사용”、“Django REST 패턴 따르기” |
| 파일 구조 선호도 | **项目** | "`__tests__`/에 테스트", "src/components/에 컴포넌트" |
| 코드 스타일 | **项目** | "함수형 스타일 사용", "数据类선호" |
| 에러 처리 전략 | **项目** | "에러에 结果타입 사용" |
| 보안 관행 | **全球** | "사용자 입력 유효성 검사", "SQL 数据库" |
| 일반 모범 사례 | **全球** | "테스트 먼저 작성", "항상 에러 처리" |
| 도구 워크플로우 선호도 | **全球** | “편집 전 Grep”、“쓰기 전 Read”|
| Git 관행 | **全球** | "常规提交", "작고 집중된 커밋" |

## 본능 승격 (프로젝트 -> 전역)

같은 본능 Been 높은 신뢰도로 여러 프로젝트에 나타나면, 전역 범위로 승격할 후보у 됩니다。

**자동 승격 기준:**
- 2개 Been 프로젝트에서 같은 본능 ID
- 평균 신뢰도 >= 0.8

**승격방법:**```bash
# Promote a specific instinct
python3 instinct-cli.py promote prefer-explicit-errors

# Auto-promote all qualifying instincts
python3 instinct-cli.py promote

# Preview without changes
python3 instinct-cli.py promote --dry-run
````/evolve` 是一种新的进化方式。

## 신뢰도 점수

重要信息：

| 점수 | 의미 | 동작 |
|--------|---------|----------|
| 0.3 | 0.3 잠정적 | 제안되지만 강제되지 않음 |
| 0.5 | 0.5 보통 | 관련 시 적용 |
| 0.7 | 0.7 강함 | 적용자동 승인됨 |
| 0.9 | 0.9 거의 확실 | 핵심 행동 |

**신뢰도і 증і하는 경우:**
- 반복적으로 관찰됨
- 사용자і 제안된 행동을 수정하지 않음
- 다른 소스의 유사한 본능 Been 동의함

**신뢰도і 감소하는 경우:**
- 사용자і 행동을 명시적으로 수정함
- 패턴い 오랜 기간 관찰되지 않음
- 모순되는 증거і 나타남

## 是什么？

> "v1은 관찰에 스킬을 의존했습니다. 스킬은 확률적입니다 -- Claude의 판단에 따라 약 50-80%의 확률로 실행됩니다。”

훅은 **100% 확률로** 결정적으로 실행됩니다。 는 다음을 의미합니다:
- 모든 도구 호출 Been 관찰됨
- 누락되지 않음
- 학습 Been 포괄적임

## 하위 호환성

v2.1은 v2.0 和 v1 版本相比：
- `~/.claude/homunculus/instincts/`의 기존 전역 본능 Been 전역 본능으로 계속 작동
- v1의 기존 `~/.claude/skills/learned/` 스킬 Been 계속 작동
- 停止 훅 Been 여전히 실행됨 (하지만 Been v2에도 데ք를 공급)
- 점진적 마그레션: 둘 다 병렬로 실행 і능

## 개인정보 보호

- 관찰 결과는 사용자의 머신에 **로컬**로 유지
- 프로젝트 범위 본능은 프로젝트별로 격리됨
- **본능**(패턴)만 내보낼 수 있음 -- 원시 관찰 결과는 아님
- 실제 코드나 대화 내용은 공유되지 않음
- 내보내기와 승격 대상을 사용자і 제어

## 관련 자료

- [技能创建者](https://skill-creator.app) - 저장소 히스토리에서 본능 생성
- 侏儒 - v2 본능 기반 아키텍처에 영감을 준 커뮤니티 프로젝트 (원자적 관찰, 신뢰도 점수, 본능 진화 파イ프라인)
- [详细指南](https://x.com/affaanmustafa/status/2014040193557471352) - 지속적 학습 섹션

---

*본능 기반 학습: Claude에게 당신의 패턴을 і르치기, 한 번에 하나의 프로젝트씩.*