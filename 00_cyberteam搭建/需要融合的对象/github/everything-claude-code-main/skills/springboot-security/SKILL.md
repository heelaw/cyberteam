# Spring Boot 安全审查

在添加身份验证、处理输入、创建端点或处理机密时使用。

## 何时激活

- 添加身份验证（JWT、OAuth2、基于会话）
- 实现授权（@PreAuthorize，基于角色的访问）
- 验证用户输入（Bean 验证、自定义验证器）
- 配置 CORS、CSRF 或安全标头
- 管理秘密（Vault、环境变量）
- 添加速率限制或暴力保护
- 扫描 CVE 的依赖关系

## 身份验证

- 更喜欢无状态 JWT 或带有撤销列表的不透明令牌
- 对会话使用“httpOnly”、“Secure”、“SameSite=Strict” cookie
- 使用“OncePerRequestFilter”或资源服务器验证令牌```java
@Component
public class JwtAuthFilter extends OncePerRequestFilter {
  private final JwtService jwtService;

  public JwtAuthFilter(JwtService jwtService) {
    this.jwtService = jwtService;
  }

  @Override
  protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
      FilterChain chain) throws ServletException, IOException {
    String header = request.getHeader(HttpHeaders.AUTHORIZATION);
    if (header != null && header.startsWith("Bearer ")) {
      String token = header.substring(7);
      Authentication auth = jwtService.authenticate(token);
      SecurityContextHolder.getContext().setAuthentication(auth);
    }
    chain.doFilter(request, response);
  }
}
```## 授权

- 启用方法安全性：`@EnableMethodSecurity`
- 使用 `@PreAuthorize("hasRole('ADMIN')")` 或 `@PreAuthorize("@authz.canEdit(#id)")`
- 默认拒绝；仅公开所需的范围```java
@RestController
@RequestMapping("/api/admin")
public class AdminController {

  @PreAuthorize("hasRole('ADMIN')")
  @GetMapping("/users")
  public List<UserDto> listUsers() {
    return userService.findAll();
  }

  @PreAuthorize("@authz.isOwner(#id, authentication)")
  @DeleteMapping("/users/{id}")
  public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
    userService.delete(id);
    return ResponseEntity.noContent().build();
  }
}
```## 输入验证

- 在控制器上使用“@Valid”进行 Bean 验证
- 对 DTO 应用约束：`@NotBlank`、`@Email`、`@Size`、自定义验证器
- 在渲染之前使用白名单清理任何 HTML```java
// BAD: No validation
@PostMapping("/users")
public User createUser(@RequestBody UserDto dto) {
  return userService.create(dto);
}

// GOOD: Validated DTO
public record CreateUserDto(
    @NotBlank @Size(max = 100) String name,
    @NotBlank @Email String email,
    @NotNull @Min(0) @Max(150) Integer age
) {}

@PostMapping("/users")
public ResponseEntity<UserDto> createUser(@Valid @RequestBody CreateUserDto dto) {
  return ResponseEntity.status(HttpStatus.CREATED)
      .body(userService.create(dto));
}
```## SQL注入预防

- 使用 Spring Data 存储库或参数化查询
- 对于本机查询，使用 `:param` 绑定；从不连接字符串```java
// BAD: String concatenation in native query
@Query(value = "SELECT * FROM users WHERE name = '" + name + "'", nativeQuery = true)

// GOOD: Parameterized native query
@Query(value = "SELECT * FROM users WHERE name = :name", nativeQuery = true)
List<User> findByName(@Param("name") String name);

// GOOD: Spring Data derived query (auto-parameterized)
List<User> findByEmailAndActiveTrue(String email);
```## 密码编码

- 始终使用 BCrypt 或 Argon2 对密码进行哈希处理 — 从不存储明文
- 使用 `PasswordEncoder` bean，而不是手动散列```java
@Bean
public PasswordEncoder passwordEncoder() {
  return new BCryptPasswordEncoder(12); // cost factor 12
}

// In service
public User register(CreateUserDto dto) {
  String hashedPassword = passwordEncoder.encode(dto.password());
  return userRepository.save(new User(dto.email(), hashedPassword));
}
```## CSRF 保护

- 对于浏览器会话应用程序，请保持 CSRF 启用；在表单/标题中包含令牌
- 对于具有不记名令牌的纯 API，禁用 CSRF 并依赖无状态身份验证```java
http
  .csrf(csrf -> csrf.disable())
  .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS));
```## 秘密管理

- 来源没有秘密；从 env 或Vault加载
- 保持“application.yml”不含凭据；使用占位符
- 定期轮换令牌和数据库凭证```yaml
# BAD: Hardcoded in application.yml
spring:
  datasource:
    password: mySecretPassword123

# GOOD: Environment variable placeholder
spring:
  datasource:
    password: ${DB_PASSWORD}

# GOOD: Spring Cloud Vault integration
spring:
  cloud:
    vault:
      uri: https://vault.example.com
      token: ${VAULT_TOKEN}
```## 安全标头```java
http
  .headers(headers -> headers
    .contentSecurityPolicy(csp -> csp
      .policyDirectives("default-src 'self'"))
    .frameOptions(HeadersConfigurer.FrameOptionsConfig::sameOrigin)
    .xssProtection(Customizer.withDefaults())
    .referrerPolicy(rp -> rp.policy(ReferrerPolicyHeaderWriter.ReferrerPolicy.NO_REFERRER)));
```## CORS 配置

- 在安全过滤器级别配置 CORS，而不是每个控制器
- 限制允许的来源——切勿在生产中使用“*”```java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
  CorsConfiguration config = new CorsConfiguration();
  config.setAllowedOrigins(List.of("https://app.example.com"));
  config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE"));
  config.setAllowedHeaders(List.of("Authorization", "Content-Type"));
  config.setAllowCredentials(true);
  config.setMaxAge(3600L);

  UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
  source.registerCorsConfiguration("/api/**", config);
  return source;
}

// In SecurityFilterChain:
http.cors(cors -> cors.configurationSource(corsConfigurationSource()));
```## 速率限制

- 对昂贵的端点应用 Bucket4j 或网关级限制
- 突发事件的记录和警报；返回 429 并带有重试提示```java
// Using Bucket4j for per-endpoint rate limiting
@Component
public class RateLimitFilter extends OncePerRequestFilter {
  private final Map<String, Bucket> buckets = new ConcurrentHashMap<>();

  private Bucket createBucket() {
    return Bucket.builder()
        .addLimit(Bandwidth.classic(100, Refill.intervally(100, Duration.ofMinutes(1))))
        .build();
  }

  @Override
  protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
      FilterChain chain) throws ServletException, IOException {
    String clientIp = request.getRemoteAddr();
    Bucket bucket = buckets.computeIfAbsent(clientIp, k -> createBucket());

    if (bucket.tryConsume(1)) {
      chain.doFilter(request, response);
    } else {
      response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
      response.getWriter().write("{\"error\": \"Rate limit exceeded\"}");
    }
  }
}
```## 依赖安全

- 在 CI 中运行 OWASP 依赖项检查 / Snyk
- 将 Spring Boot 和 Spring Security 保留在受支持的版本上
- 失败建立在已知的 CVE 上

## 日志记录和 PII

- 切勿记录机密、令牌、密码或完整 PAN 数据
- 编辑敏感字段；使用结构化 JSON 日志记录

## 文件上传

- 验证大小、内容类型和扩展名
- 存储在外部网络根目录；如果需要扫描

## 发布前检查清单

- [ ] 身份验证令牌已正确验证并过期
- [ ] 每个敏感路径上的授权守护
- [ ] 所有输入均经过验证和清理
- [ ] 没有字符串连接的 SQL
- [ ] CSRF 姿势对于应用程序类型正确
- [ ] 秘密外化；没有人承诺
- [ ] 配置安全标头
- [ ] API 速率限制
- [ ] 依赖关系已扫描并已更新
- [ ] 日志不含敏感数据

**记住**：默认拒绝、验证输入、最小权限和首先配置安全。