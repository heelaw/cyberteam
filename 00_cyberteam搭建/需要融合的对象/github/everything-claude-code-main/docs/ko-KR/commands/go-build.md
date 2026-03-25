# 构建并修复

커맨드는 **go-build-resolver** 开发工具 Go build 开发工具수정합니다。

## 커맨드і 하는 것

1. **진단 실행**: `go build`, `go vet`, `staticcheck` 실행
2. **에러 분석**: 파일별로 그룹화하고 심각도순 정렬
3. **점진적 수정**: 한 번에 하나의 에러씩
4. **각 수정 검증**: 각 변경 후 build 재실행
5. **요약 보고**: 수정된 것과 남은 것 표시

## 사용 시점

`/go-build`配置文件：
- `去构建./...`і 에러로 실패할 때
- `去兽医吧./...`і 슈를 보고할 때
- `golangci-lint run` Been 고를 보여줄 때
- 모듈 의존성깨졌을 때
- 변경사항을 pull한 후 buildі 깨졌을 때

## 실행되는 진단 커맨드```bash
# 기본 build 확인
go build ./...

# 정적 분석
go vet ./...

# 확장 린팅 (사용 가능한 경우)
staticcheck ./...
golangci-lint run

# 모듈 이슈
go mod verify
go mod tidy -v
```## 예시 세션````text
User: /go-build

Agent:
# Go Build 해결

## 초기 진단

```巴什
$ 去构建./...
内部/service/user.go:25:15：未定义：UserRepository
Internal/handler/api.go:42:9：无法使用 x（字符串类型）作为 int 类型
Internal/handler/api.go:58:2：函数结束时缺少返回```

발견된 에러: 3개

## 수정 1: 정의되지 않은 식별자

파일: internal/service/user.go:25
에러: undefined: UserRepository
원인: import 누락

```去
// 导入추ν
导入“项目/内部/存储库”

// 변경 전
var repo 用户存储库
// 변경 후
var repo 存储库.UserRepository```

```巴什
$ 去构建./...
#2개에러남음```

## 수정 2: 타입 불일치

파일: internal/handler/api.go:42
에러: cannot use x (type string) as type int

```去
// 변경 전
计数 := params.Get("计数")
// 변경 후
countStr := params.Get("计数")
计数, _ := strconv.Atoi(countStr)```

```巴什
$ 去构建./...
# 1 에러 남음```

## 수정 3: 누락된 return

파일: internal/handler/api.go:58
에러: missing return at end of function

```去
func GetUser(id string) (*用户, 错误) {
    如果id==“”{
        返回零，ErrInvalidID
    }
    用户 := 查找用户(id)
    // 누락된 返回 추у
    返回用户，无
}```

```巴什
$ 去构建./...
# 构建성공！```

## 최종 검증

```巴什
$ 去看兽医./...
# 슈없음

$ 去测试./...
好的项目/内部/服务0.015s
好的项目/内部/处理程序 0.023s```

## 요약

| 항목 | 수량 |
|------|------|
| 수정된 Build 에러 | 3 |
| 수정된 Vet 경고 | 0 |
| 수정된 파일 | 2 |
| 남은 이슈 | 0 |

Build 상태: ✅ 성공
````

## 자주 발생하는 에러

| 에러 | 일반적인 수정 방법 |
|------|-------------------|
| `undefined: X` | import 추가 또는 오타 수정 |
| `cannot use X as Y` | 타입 변환 또는 할당 수정 |
| `missing return` | return 문 추가 |
| `X does not implement Y` | 누락된 메서드 추가 |
| `import cycle` | 패키지 구조 재구성 |
| `declared but not used` | 변수 제거 또는 사용 |
| `cannot find package` | `go get` 또는 `go mod tidy` |

## 수정 전략

1. **Build 에러 먼저** - 코드가 컴파일되어야 함
2. **Vet 경고 두 번째** - 의심스러운 구조 수정
3. **Lint 경고 세 번째** - 스타일과 모범 사례
4. **한 번에 하나씩** - 각 변경 검증
5. **최소한의 변경** - 리팩토링이 아닌 수정만

## 중단 조건

에이전트가 중단하고 보고하는 경우:
- 3번 시도 후에도 같은 에러가 지속
- 수정이 더 많은 에러를 발생시킴
- 아키텍처 변경이 필요한 경우
- 외부 의존성이 누락된 경우

## 관련 커맨드

- `/go-test` - build 성공 후 테스트 실행
- `/go-review` - 코드 품질 리뷰
- `/verify` - 전체 검증 루프

## 관련 항목

- 에이전트: `agents/go-build-resolver.md`
- 스킬: `skills/golang-patterns/`