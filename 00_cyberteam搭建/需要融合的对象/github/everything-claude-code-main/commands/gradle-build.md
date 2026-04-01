# Gradle 构建修复

逐步修复 Android 和 Kotlin 多平台项目的 Gradle 构建和编译错误。

## 步骤 1：检测构建配置

确定项目类型并运行适当的构建：

|指标|构建命令|
|------------|--------------|
| `build.gradle.kts` + `composeApp/` (KMP) | `./gradlew composeApp:compileKotlinMetadata 2>&1` |
| `build.gradle.kts` + `app/` (Android) | `./gradlew app:compileDebugKotlin 2>&1` |
|带有模块的“settings.gradle.kts” | `./gradlew assemble 2>&1` |
|检测配置| `./gradlew 检测 2>&1` |

另请检查“gradle.properties”和“local.properties”的配置。

## 步骤 2：解析和分组错误

1. 运行构建命令并捕获输出
2. 将 Kotlin 编译错误与 Gradle 配置错误分开
3. 按模块和文件路径分组
4.排序：按依赖顺序先配置错误，再编译错误

## 步骤 3：修复循环

对于每个错误：

1. **阅读文件** — 错误行的完整上下文
2. **诊断**——常见类别：
   - 缺少导入或未解析的参考
   - 类型不匹配或不兼容的类型
   -“build.gradle.kts”中缺少依赖项
   - 预期/实际不匹配（KMP）
   - Compose编译器错误
3. **最小化修复** — 解决错误的最小更改
4. **重新运行构建** — 验证修复并检查新错误
5. **继续** — 移至下一个错误

## 步骤 4：护栏

停下来询问用户是否：
- 修复引入的错误多于解决的错误
- 3次尝试后仍然存在相同的错误
- 错误需要添加新的依赖项或更改模块结构
- Gradle 同步本身失败（配置阶段错误）
- 生成的代码中存在错误（Room、SQLDelight、KSP）

## 步骤 5：总结

报告：
- 修复错误（模块、文件、描述）
- 剩余错误
- 引入了新的错误（应该为零）
- 建议的后续步骤

## 常见 Gradle/KMP 修复

|错误|修复 |
|--------|-----|
| `commonMain` 中未解析的引用 |检查依赖项是否在 `commonMain.dependencies {}` 中 |
|期望声明没有实际 |在每个平台源集中添加“实际”实现 |
| Compose 编译器版本不匹配 |在 `libs.versions.toml` 中对齐 Kotlin 和 Compose 编译器版本 |
|重复类 |检查与 `./gradlew dependency` 是否存在冲突的依赖项 |
| KSP 错误 |运行 `./gradlew kspCommonMainKotlinMetadata` 重新生成 |
|配置缓存问题 |检查不可序列化的任务输入 |