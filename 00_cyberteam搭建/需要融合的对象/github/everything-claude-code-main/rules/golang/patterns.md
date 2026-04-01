# 围棋模式

> 此文件使用 Go 特定内容扩展了 [common/patterns.md](../common/patterns.md)。

## 功能选项```go
type Option func(*Server)

func WithPort(port int) Option {
    return func(s *Server) { s.port = port }
}

func NewServer(opts ...Option) *Server {
    s := &Server{port: 8080}
    for _, opt := range opts {
        opt(s)
    }
    return s
}
```## 小接口

在使用接口的地方定义接口，而不是在实现接口的地方定义接口。

## 依赖注入

使用构造函数注入依赖项：```go
func NewUserService(repo UserRepository, logger Logger) *UserService {
    return &UserService{repo: repo, logger: logger}
}
```## 参考

请参阅技能：“golang-patterns”，了解全面的 Go 模式，包括并发、错误处理和包组织。