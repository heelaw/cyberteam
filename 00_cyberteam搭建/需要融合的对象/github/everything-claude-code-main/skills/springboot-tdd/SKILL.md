# Spring Boot TDD 工作流程

Spring Boot 服务的 TDD 指导覆盖率超过 80%（单元 + 集成）。

## 何时使用

- 新功能或端点
- 错误修复或重构
- 添加数据访问逻辑或安全规则

## 工作流程

1）首先编写测试（它们应该失败）
2）实现最少的代码通过
3）重构并测试绿色
4) 强制覆盖 (JaCoCo)

## 单元测试（JUnit 5 + Mockito）```java
@ExtendWith(MockitoExtension.class)
class MarketServiceTest {
  @Mock MarketRepository repo;
  @InjectMocks MarketService service;

  @Test
  void createsMarket() {
    CreateMarketRequest req = new CreateMarketRequest("name", "desc", Instant.now(), List.of("cat"));
    when(repo.save(any())).thenAnswer(inv -> inv.getArgument(0));

    Market result = service.create(req);

    assertThat(result.name()).isEqualTo("name");
    verify(repo).save(any());
  }
}
```图案：
- 安排-行动-断言
- 避免部分模拟；更喜欢显式存根
- 对变体使用“@ParameterizedTest”

## Web 层测试 (MockMvc)```java
@WebMvcTest(MarketController.class)
class MarketControllerTest {
  @Autowired MockMvc mockMvc;
  @MockBean MarketService marketService;

  @Test
  void returnsMarkets() throws Exception {
    when(marketService.list(any())).thenReturn(Page.empty());

    mockMvc.perform(get("/api/markets"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.content").isArray());
  }
}
```## 集成测试（SpringBootTest）```java
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class MarketIntegrationTest {
  @Autowired MockMvc mockMvc;

  @Test
  void createsMarket() throws Exception {
    mockMvc.perform(post("/api/markets")
        .contentType(MediaType.APPLICATION_JSON)
        .content("""
          {"name":"Test","description":"Desc","endDate":"2030-01-01T00:00:00Z","categories":["general"]}
        """))
      .andExpect(status().isCreated());
  }
}
```## 持久性测试 (DataJpaTest)```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import(TestContainersConfig.class)
class MarketRepositoryTest {
  @Autowired MarketRepository repo;

  @Test
  void savesAndFinds() {
    MarketEntity entity = new MarketEntity();
    entity.setName("Test");
    repo.save(entity);

    Optional<MarketEntity> found = repo.findByName("Test");
    assertThat(found).isPresent();
  }
}
```## 测试容器

- 使用可重复使用的 Postgres/Redis 容器来镜像生产
- 通过“@DynamicPropertySource”连接将 JDBC URL 注入 Spring 上下文

## 覆盖范围 (JaCoCo)

Maven 片段：```xml
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
  <version>0.8.14</version>
  <executions>
    <execution>
      <goals><goal>prepare-agent</goal></goals>
    </execution>
    <execution>
      <id>report</id>
      <phase>verify</phase>
      <goals><goal>report</goal></goals>
    </execution>
  </executions>
</plugin>
```## 断言

- 出于可读性考虑，更喜欢 AssertJ (`assertThat`)
- 对于 JSON 响应，请使用 `jsonPath`
- 对于例外情况：`assertThatThrownBy(...)`

## 测试数据构建器```java
class MarketBuilder {
  private String name = "Test";
  MarketBuilder withName(String name) { this.name = name; return this; }
  Market build() { return new Market(null, name, MarketStatus.ACTIVE); }
}
```## CI 命令

- Maven：`mvn -T 4 test` 或 `mvn verify`
- Gradle：`./gradlew 测试 jacocoTestReport`

**记住**：保持测试快速、隔离和确定性。测试行为，而不是实现细节。