# 指标和赞助手册

该文件是赞助商电话会议和生态系统合作伙伴审查的实用脚本。

## 追踪什么

在每次更新中使用四个类别：

1. **分发** — npm 包和 GitHub 应用程序安装
2. **采用** — 明星、分叉、贡献者、发布节奏
3. **产品表面** — 命令/技能/代理和跨平台支持
4. **可靠性** — 测试通过计数和生产错误周转

## 拉动实时指标

### npm 下载```bash
# Weekly downloads
curl -s https://api.npmjs.org/downloads/point/last-week/ecc-universal
curl -s https://api.npmjs.org/downloads/point/last-week/ecc-agentshield

# Last 30 days
curl -s https://api.npmjs.org/downloads/point/last-month/ecc-universal
curl -s https://api.npmjs.org/downloads/point/last-month/ecc-agentshield
```### GitHub 存储库采用```bash
gh api repos/affaan-m/everything-claude-code \
  --jq '{stars:.stargazers_count,forks:.forks_count,contributors_url:.contributors_url,open_issues:.open_issues_count}'
```### GitHub 流量（需要维护者访问权限）```bash
gh api repos/affaan-m/everything-claude-code/traffic/views
gh api repos/affaan-m/everything-claude-code/traffic/clones
```### GitHub 应用程序安装

GitHub 应用程序安装计数目前在 Marketplace/App 仪表板中最可靠。
使用以下位置的最新值：

- [ECC 工具市场](https://github.com/marketplace/ecc-tools)

## 哪些内容（目前）还不能公开衡量

- Claude 插件安装/下载计数当前未通过公共 API 公开。
- 对于合作伙伴对话，使用 npm 指标 + GitHub 应用程序安装 + 存储库流量作为代理捆绑包。

## 建议的赞助商包装

使用这些作为谈判的起点：

- **试点合作伙伴：** `200 美元/月`
  - 最适合首次合作伙伴验证和简单的每月赞助商更新。
- **成长伙伴：** `500 美元/月`
  - 包括路线图检查和实施反馈循环。
- **战略合作伙伴：** `$1,000+/月`
  - 多点触控协作、启动支持和更深入的操作协调。

## 60 秒谈话曲目

在通话中使用它：

> ECC 现在定位为代理利用性能系统，而不是配置存储库。  
> 我们通过 npm 分发、GitHub 应用程序安装和存储库增长来跟踪采用情况。  
> Claude 插件安装量在结构上被公开低估，因此我们使用混合指标模型。  
> 该项目支持 Claude Code、Cursor、OpenCode 和 Codex app/CLI，具有生产级挂钩可靠性和大型通过测试套件。

有关启动就绪的社交副本片段，请参阅 [`social-launch-copy.md`](./social-launch-copy.md)。