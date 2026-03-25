#检查点명령어

关闭检查站。

## 사용법

`/checkpoint [创建|验证|列表|清除] [名称]`

## 检查点设置

检查点设置：

1. `/verify fast`를 실행하여 현재 상태і 깨끗한지 확인합니다
2. 检查点 git stash 또는 commit을 생성합니다
3. `.claude/checkpoints.log`에 checkpoint를 기록합니다:```bash
echo "$(date +%Y-%m-%d-%H:%M) | $CHECKPOINT_NAME | $(git rev-parse --short HEAD)" >> .claude/checkpoints.log
```4. 检查站 생성 완료를 보고합니다

## 检查站 검증

检查点设置：

1. 로그에서 检查点를 읽습니다
2. 检查点设置：
   - 检查站 ה후 추า된 파일
   - 检查站 수정된 파일
   - 현재와 당시의 테스트 통과율
   - 현재와 당시의 커버리지

3.注意事项：```
CHECKPOINT COMPARISON: $NAME
============================
Files changed: X
Tests: +Y passed / -Z failed
Coverage: +X% / -Y%
Build: [PASS/FAIL]
```## 检查站목록

检查站位置：
- 름
- 타임스탬프
-Git SHA
- 상태（当前、后面、前面）

## 워크플로우

일반적인 检查站 흐름:```
[시작] --> /checkpoint create "feature-start"
   |
[구현] --> /checkpoint create "core-done"
   |
[테스트] --> /checkpoint verify "core-done"
   |
[리팩토링] --> /checkpoint create "refactor-done"
   |
[PR] --> /checkpoint verify "feature-start"
```## 인자

$参数：
- `create <name>` - 建立检查点
- `verify <name>` - 完成检查点设置
- `list` - 모든 检查点를 표시합니다
- `clear` - 제거합니다 (최근 5개만 유지)