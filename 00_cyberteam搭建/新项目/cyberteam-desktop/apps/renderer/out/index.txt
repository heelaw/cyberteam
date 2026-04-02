1:"$Sreact.fragment"
2:I[9664,["177","static/chunks/app/layout-23c4d3791a1858be.js"],""]
3:I[5341,[],""]
4:I[25,[],""]
8:I[4431,[],""]
5:T1c5c,
  :root {
    color-scheme: dark;
    --bg: #07111f;
    --bg-soft: #0d1728;
    --bg-panel: rgba(15, 23, 42, 0.88);
    --line: rgba(148, 163, 184, 0.18);
    --line-strong: rgba(148, 163, 184, 0.3);
    --text: #e5eefb;
    --muted: #93a4c3;
    --accent: #77c6ff;
    --accent-2: #7cf0c8;
    --warm: #f7b267;
    --shadow: 0 28px 80px rgba(0, 0, 0, 0.34);
  }

  * {
    box-sizing: border-box;
  }

  html, body {
    margin: 0;
    min-height: 100%;
    background:
      radial-gradient(circle at top left, rgba(72, 135, 255, 0.22), transparent 30%),
      radial-gradient(circle at top right, rgba(124, 240, 200, 0.18), transparent 26%),
      linear-gradient(145deg, #050b16 0%, #091121 50%, #06101c 100%);
    color: var(--text);
    font-family: Avenir Next, "PingFang SC", "Hiragino Sans GB", "Segoe UI", sans-serif;
  }

  a {
    color: inherit;
    text-decoration: none;
  }

  .shell {
    display: grid;
    grid-template-columns: 280px minmax(0, 1fr);
    min-height: 100vh;
  }

  .sidebar {
    padding: 28px 22px;
    border-right: 1px solid var(--line);
    background: rgba(6, 11, 20, 0.72);
    backdrop-filter: blur(18px);
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 22px;
  }

  .brandMark {
    width: 48px;
    height: 48px;
    border-radius: 16px;
    display: grid;
    place-items: center;
    background: linear-gradient(135deg, rgba(119, 198, 255, 0.3), rgba(124, 240, 200, 0.3));
    border: 1px solid var(--line-strong);
    font-weight: 800;
    letter-spacing: 0.08em;
  }

  .brandTitle {
    font-size: 18px;
    font-weight: 700;
  }

  .brandSubtitle {
    color: var(--muted);
    font-size: 12px;
    margin-top: 2px;
  }

  .statusCard, .panel, .hero, .metric, .threadCard, .docCard, .marketCard, .settingsCard, .nodeCard {
    background: var(--bg-panel);
    border: 1px solid var(--line);
    box-shadow: var(--shadow);
    backdrop-filter: blur(16px);
  }

  .statusCard {
    border-radius: 22px;
    padding: 18px;
    margin-bottom: 20px;
  }

  .statusLabel, .eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.18em;
    font-size: 11px;
    color: var(--muted);
  }

  .statusValue {
    margin-top: 10px;
    font-size: 18px;
    font-weight: 700;
  }

  .statusMeta {
    margin-top: 6px;
    color: var(--muted);
    font-size: 13px;
    line-height: 1.5;
  }

  .nav {
    display: grid;
    gap: 10px;
  }

  .navItem {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 14px 16px;
    border-radius: 18px;
    border: 1px solid transparent;
    background: rgba(255, 255, 255, 0.02);
    transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
  }

  .navItem:hover {
    transform: translateX(2px);
    border-color: var(--line-strong);
    background: rgba(255, 255, 255, 0.05);
  }

  .navLabel {
    font-weight: 650;
  }

  .navNote {
    color: var(--muted);
    font-size: 12px;
  }

  .workspace {
    min-width: 0;
    padding: 28px;
  }

  .topbar {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 24px;
    margin-bottom: 24px;
  }

  .topbar h1 {
    margin: 8px 0 0;
    font-size: clamp(30px, 4vw, 56px);
    line-height: 1.02;
    letter-spacing: -0.05em;
    max-width: 900px;
  }

  .topbarPills {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 10px;
  }

  .topbarPills span, .chip, .tag, .pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    border-radius: 999px;
    border: 1px solid var(--line);
    background: rgba(255, 255, 255, 0.04);
    color: var(--text);
    font-size: 12px;
  }

  .content {
    display: grid;
    gap: 18px;
  }

  .hero, .panel, .threadCard, .docCard, .marketCard, .settingsCard, .nodeCard, .metric {
    border-radius: 24px;
    padding: 20px;
  }

  .hero {
    display: grid;
    gap: 18px;
  }

  .heroHeader {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 18px;
  }

  .heroTitle {
    margin: 6px 0 0;
    font-size: 28px;
    line-height: 1.08;
    letter-spacing: -0.04em;
  }

  .heroLead {
    color: var(--muted);
    line-height: 1.75;
    max-width: 70ch;
  }

  .grid {
    display: grid;
    gap: 16px;
  }

  .grid.metrics {
    grid-template-columns: repeat(6, minmax(0, 1fr));
  }

  .grid.two {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .grid.three {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .metricValue {
    font-size: 30px;
    font-weight: 800;
    margin-top: 14px;
  }

  .metricNote, .panelNote, .cardNote, .miniNote, .subtle {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.7;
  }

  .sectionTitle {
    margin: 0 0 10px;
    font-size: 18px;
  }

  .sectionStack {
    display: grid;
    gap: 16px;
  }

  .timeline {
    display: grid;
    gap: 10px;
  }

  .timelineItem {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 12px 14px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--line);
  }

  .conversationList, .messageList, .nodeList, .skillList, .marketList, .settingsList {
    display: grid;
    gap: 12px;
  }

  .conversationItem, .messageCard, .skillCard, .marketCardItem, .settingsCardItem {
    padding: 14px 16px;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--line);
  }

  .conversationItem.active {
    border-color: rgba(119, 198, 255, 0.45);
    background: linear-gradient(135deg, rgba(119, 198, 255, 0.12), rgba(124, 240, 200, 0.1));
  }

  .messageHeader, .cardHeader, .nodeHeader, .rowHeader {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }

  .messageAuthor, .conversationTitle, .nodeTitle, .marketTitle, .settingsTitle {
    font-weight: 700;
  }

  .messageMeta, .conversationMeta, .nodeMeta, .cardMeta {
    color: var(--muted);
    font-size: 12px;
  }

  .messageBody {
    margin-top: 10px;
    line-height: 1.8;
  }

  .messageMentions, .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
  }

  .orgTree {
    display: grid;
    gap: 14px;
  }

  .orgBranch {
    padding-left: 18px;
    border-left: 1px solid var(--line-strong);
    display: grid;
    gap: 12px;
  }

  .docPreview {
    padding: 16px;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--line);
    white-space: pre-wrap;
    line-height: 1.7;
  }

  .footerGrid {
    display: grid;
    gap: 14px;
  }

  @media (max-width: 1200px) {
    .shell {
      grid-template-columns: 1fr;
    }

    .sidebar {
      border-right: 0;
      border-bottom: 1px solid var(--line);
    }

    .grid.metrics, .grid.two, .grid.three {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 720px) {
    .workspace {
      padding: 18px;
    }

    .topbar {
      flex-direction: column;
      align-items: flex-start;
    }

    .grid.metrics, .grid.two, .grid.three {
      grid-template-columns: 1fr;
    }

    .topbarPills {
      justify-content: flex-start;
    }
  }
0:{"P":null,"b":"2V5OXcQO_79G2TOuAwnwy","p":"","c":["",""],"i":false,"f":[[["",{"children":["__PAGE__",{}]},"$undefined","$undefined",true],["",["$","$1","c",{"children":[null,["$","html",null,{"lang":"zh-CN","children":["$","body",null,{"children":[["$","div",null,{"className":"shell","children":[["$","aside",null,{"className":"sidebar","children":[["$","div",null,{"className":"brand","children":[["$","div",null,{"className":"brandMark","children":"CT"}],["$","div",null,{"children":[["$","div",null,{"className":"brandTitle","children":"CyberTeam"}],["$","div",null,{"className":"brandSubtitle","children":"本地 AI 军团操作系统"}]]}]]}],["$","div",null,{"className":"statusCard","children":[["$","div",null,{"className":"statusLabel","children":"Runtime"}],["$","div",null,{"className":"statusValue","children":"Electron + Next.js"}],["$","div",null,{"className":"statusMeta","children":"SQLite / Claude Code / macOS"}]]}],["$","nav",null,{"className":"nav","children":[["$","$L2","/",{"className":"navItem","href":"/","children":[["$","span",null,{"className":"navLabel","children":"Dashboard"}],["$","span",null,{"className":"navNote","children":"总览"}]]}],["$","$L2","/chat",{"className":"navItem","href":"/chat","children":[["$","span",null,{"className":"navLabel","children":"Chat"}],["$","span",null,{"className":"navNote","children":"会话与群聊"}]]}],["$","$L2","/organization",{"className":"navItem","href":"/organization","children":[["$","span",null,{"className":"navLabel","children":"Organization"}],["$","span",null,{"className":"navNote","children":"组织结构"}]]}],["$","$L2","/playground",{"className":"navItem","href":"/playground","children":[["$","span",null,{"className":"navLabel","children":"Playground"}],["$","span",null,{"className":"navNote","children":"输出与审核"}]]}],["$","$L2","/market",{"className":"navItem","href":"/market","children":[["$","span",null,{"className":"navLabel","children":"Market"}],["$","span",null,{"className":"navNote","children":"Agent / Skill / 模板"}]]}],["$","$L2","/settings",{"className":"navItem","href":"/settings","children":[["$","span",null,{"className":"navLabel","children":"Settings"}],["$","span",null,{"className":"navNote","children":"本地与接入"}]]}]]}]]}],["$","div",null,{"className":"workspace","children":[["$","header",null,{"className":"topbar","children":[["$","div",null,{"children":[["$","p",null,{"className":"eyebrow","children":"Socratic by default"}],["$","h1",null,{"children":"让一个人拥有一整支 AI 公司。"}]]}],["$","div",null,{"className":"topbarPills","children":[["$","span",null,{"children":"Local First"}],["$","span",null,{"children":"Playground Ready"}],["$","span",null,{"children":"CEO Review"}]]}]]}],["$","main",null,{"className":"content","children":["$","$L3",null,{"parallelRouterKey":"children","error":"$undefined","errorStyles":"$undefined","errorScripts":"$undefined","template":["$","$L4",null,{}],"templateStyles":"$undefined","templateScripts":"$undefined","notFound":[[["$","title",null,{"children":"404: This page could not be found."}],["$","div",null,{"style":{"fontFamily":"system-ui,\"Segoe UI\",Roboto,Helvetica,Arial,sans-serif,\"Apple Color Emoji\",\"Segoe UI Emoji\"","height":"100vh","textAlign":"center","display":"flex","flexDirection":"column","alignItems":"center","justifyContent":"center"},"children":["$","div",null,{"children":[["$","style",null,{"dangerouslySetInnerHTML":{"__html":"body{color:#000;background:#fff;margin:0}.next-error-h1{border-right:1px solid rgba(0,0,0,.3)}@media (prefers-color-scheme:dark){body{color:#fff;background:#000}.next-error-h1{border-right:1px solid rgba(255,255,255,.3)}}"}}],["$","h1",null,{"className":"next-error-h1","style":{"display":"inline-block","margin":"0 20px 0 0","padding":"0 23px 0 0","fontSize":24,"fontWeight":500,"verticalAlign":"top","lineHeight":"49px"},"children":404}],["$","div",null,{"style":{"display":"inline-block"},"children":["$","h2",null,{"style":{"fontSize":14,"fontWeight":400,"lineHeight":"49px","margin":0},"children":"This page could not be found."}]}]]}]}]],[]],"forbidden":"$undefined","unauthorized":"$undefined"}]}]]}]]}],["$","style",null,{"dangerouslySetInnerHTML":{"__html":"$5"}}]]}]}]]}],{"children":["__PAGE__","$L6",{},null,false]},null,false],"$L7",false]],"m":"$undefined","G":["$8",[]],"s":false,"S":true}
9:I[5262,["262","static/chunks/262-8c2a285229f9e01d.js","974","static/chunks/app/page-306fb7468159cf12.js"],"DashboardView"]
b:I[5104,[],"ViewportBoundary"]
d:I[5104,[],"MetadataBoundary"]
e:"$Sreact.suspense"
6:["$","$1","c",{"children":[["$","$L9",null,{"seed":{"company":{"id":"company_1","name":"CyberTeam","avatar":"CT","description":"本地 Claude Code 驱动的 AI 军团操作系统","theme":"midnight","version":"0.1.0","createdAt":"2026-04-01T13:31:21.956Z","updatedAt":"2026-04-01T13:31:21.956Z"},"organization":{"company":"$6:props:children:0:props:seed:company","departments":[{"id":"dept_1","companyId":"company_1","name":"CEO","parentId":"$undefined","type":"review","color":"#f59e0b","description":"最终审核与决策中心","createdAt":"2026-04-01T13:31:21.957Z","updatedAt":"2026-04-01T13:31:21.957Z"},{"id":"dept_2","companyId":"company_1","name":"讨论层","parentId":"dept_1","type":"discussion","color":"#3b82f6","description":"用于发起讨论、汇总观点和形成方案","createdAt":"2026-04-01T13:31:21.957Z","updatedAt":"2026-04-01T13:31:21.957Z"},{"id":"dept_3","companyId":"company_1","name":"执行层","parentId":"dept_1","type":"execution","color":"#10b981","description":"用于拆解任务、推进执行和交付结果","createdAt":"2026-04-01T13:31:21.957Z","updatedAt":"2026-04-01T13:31:21.957Z"}],"agents":[{"id":"agent_1","companyId":"company_1","name":"CEO","title":"CEO","avatar":"$undefined","bio":"","personality":"calm, precise, helpful","status":"online","isCEO":true,"isActive":true,"createdAt":"2026-04-01T13:31:21.957Z","updatedAt":"2026-04-01T13:31:21.957Z","departmentId":"dept_1"},{"id":"agent_2","companyId":"company_1","name":"讨论主管","title":"Discussion Lead","avatar":"$undefined","bio":"负责把模糊需求拆成可以讨论的问题","personality":"calm, precise, helpful","status":"offline","isCEO":false,"isActive":true,"createdAt":"2026-04-01T13:31:21.958Z","updatedAt":"2026-04-01T13:31:21.958Z","departmentId":"dept_2"},{"id":"agent_3","companyId":"company_1","name":"执行主管","title":"Delivery Lead","avatar":"$undefined","bio":"负责把结论推进成可交付成果","personality":"calm, precise, helpful","status":"offline","isCEO":false,"isActive":true,"createdAt":"2026-04-01T13:31:21.958Z","updatedAt":"2026-04-01T13:31:21.958Z","departmentId":"dept_3"}]},"conversations":[{"id":"conv_1","title":"CEO 私聊","type":"private","participantIds":["agent_1"],"createdAt":"2026-04-01T13:31:21.958Z","updatedAt":"2026-04-01T13:31:21.958Z"},{"id":"conv_2","title":"产品增长讨论群","type":"group","participantIds":["agent_1","agent_2","agent_3"],"createdAt":"2026-04-01T13:31:21.958Z","updatedAt":"2026-04-01T13:31:21.958Z"},{"id":"conv_3","title":"执行层部门群","type":"department","participantIds":["agent_3"],"createdAt":"2026-04-01T13:31:21.958Z","updatedAt":"2026-04-01T13:31:21.958Z"}],"messagesByConversation":{"conv_1":[{"id":"msg_1","conversationId":"conv_1","content":"先判断问题的本质，再决定要不要拆给团队。","senderId":"agent_1","mentions":[],"status":"sent","createdAt":"2026-04-01T13:31:21.958Z"},{"id":"msg_2","conversationId":"conv_1","content":"确认 MVP 只保留最小闭环。","senderId":"agent_1","mentions":[],"status":"sent","createdAt":"2026-04-01T13:31:21.958Z"}],"conv_2":[{"id":"msg_3","conversationId":"conv_2","content":"请围绕首屏、组织页、聊天页、设置页做一次苏格拉底式拆解。","senderId":"agent_1","mentions":[{"agentId":"agent_2","agentName":"讨论主管","agentTitle":"Discussion Lead"}],"status":"sent","createdAt":"2026-04-01T13:31:21.958Z"},{"id":"msg_4","conversationId":"conv_2","content":"先把信息流、组织感、交付感三件事做出来。","senderId":"agent_2","mentions":[],"status":"sent","createdAt":"2026-04-01T13:31:21.958Z"},{"id":"msg_5","conversationId":"conv_2","content":"执行上优先打通页面和种子数据，再补 IPC 与状态同步。","senderId":"agent_3","mentions":[],"status":"sent","createdAt":"2026-04-01T13:31:21.958Z"}],"conv_3":[{"id":"msg_6","conversationId":"conv_3","content":"把占位符替换成能看见的页面与数据。","senderId":"agent_3","mentions":[],"status":"sent","createdAt":"2026-04-01T13:31:21.958Z"}]},"privateConversation":"$6:props:children:0:props:seed:conversations:0","groupConversation":"$6:props:children:0:props:seed:conversations:1","departmentConversation":"$6:props:children:0:props:seed:conversations:2","playgroundDocument":{"id":"playground_1","title":"CyberTeam MVP 讨论纪要","content":"# CyberTeam MVP 讨论纪要\n\n首屏已经对齐公司、组织、聊天、Playground、设置与市场六个关键入口，正在收口为可运行桌面骨架。","type":"meeting notes","reviewStatus":"pending","version":"v1"},"playgroundReview":{"status":"approved","notes":[]},"playgroundExport":"# CyberTeam MVP 讨论纪要\n\n# CyberTeam MVP 讨论纪要\n\n首屏已经对齐公司、组织、聊天、Playground、设置与市场六个关键入口，正在收口为可运行桌面骨架。","roadmap":[{"id":"phase-0","sortOrder":0,"name":"本地桌面骨架","status":"done","goal":"Electron + Next.js + SQLite 跑通","proof":"可以启动、浏览页面、读取种子态。","question":"如果没有桌面壳，这个系统还剩什么？"},{"id":"phase-1","sortOrder":1,"name":"运行时闭环","status":"done","goal":"IPC / preload / runtime snapshot 打通","proof":"前端已能读写 SQLite，页面能刷新实时状态。","question":"系统的单一事实源在哪里？"},{"id":"phase-2","sortOrder":2,"name":"组织与对话协作","status":"in-progress","goal":"把组织、聊天、Playground 串成工作流","proof":"组织页、聊天页、Playground 页已存在并写回数据库。","question":"任务从输入到审核，是否形成了闭环？"},{"id":"phase-3","sortOrder":3,"name":"质量门控","status":"next","goal":"把验证、审核、回滚和日志变成默认路径","proof":"当前已有构建验证，但还缺产品内质量仪表盘。","question":"当结果不可信时，系统如何自动拦下？"},{"id":"phase-4","sortOrder":4,"name":"能力扩展","status":"planned","goal":"把更多 Agent、Skill、模板接到市场层","proof":"市场页已显示种子资源，后续可继续增长。","question":"新能力是怎么被发现、分发和复用的？"}],"skills":[{"id":"ceo-review","name":"CEO Review","description":"Output review and decision gate","category":"governance","prompt":"Review outputs with CEO-level scrutiny.","tools":["review","export"],"version":"v1"},{"id":"socratic-questioning","name":"Socratic Questioning","description":"Ask structured questions to clarify the problem","category":"reasoning","prompt":"Question assumptions and sharpen the problem definition.","tools":["reason","reflect"],"version":"v1"}],"market":{"agents":[{"id":"agent-ceo","name":"CEO","description":"最终审核与方向决策","kind":"agent"},{"id":"agent-discussion","name":"讨论主管","description":"把问题推到可讨论的粒度","kind":"agent"},{"id":"agent-execution","name":"执行主管","description":"推动结论落地","kind":"agent"}],"skills":[{"id":"skill-ceo-review","name":"CEO Review"},{"id":"skill-socratic","name":"Socratic Questioning"}],"templates":[{"id":"template-default","name":"Default Company"},{"id":"template-sprint","name":"MVP Sprint"}]},"claudeInstalled":true,"metrics":[{"label":"公司","value":"1","note":"已创建 CyberTeam 核心公司"},{"label":"部门","value":"3","note":"CEO / 讨论层 / 执行层"},{"label":"Agent","value":"3","note":"最小可协作阵列已就绪"},{"label":"会话","value":"3","note":"私聊 / 群聊 / 部门群"},{"label":"Skill","value":"2","note":"基础能力插件已加载"},{"label":"Claude Code","value":"已检测","note":"本地执行引擎状态"}],"timeline":["公司初始化","CEO 节点生成","讨论层与执行层展开","群聊与 Playground 已串联"]}}],null,"$La"]}]
7:["$","$1","h",{"children":[null,[["$","$Lb",null,{"children":"$Lc"}],null],["$","$Ld",null,{"children":["$","div",null,{"hidden":true,"children":["$","$e",null,{"fallback":null,"children":"$Lf"}]}]}]]}]
10:I[5104,[],"OutletBoundary"]
12:I[7158,[],"AsyncMetadataOutlet"]
a:["$","$L10",null,{"children":["$L11",["$","$L12",null,{"promise":"$@13"}]]}]
c:[["$","meta","0",{"charSet":"utf-8"}],["$","meta","1",{"name":"viewport","content":"width=device-width, initial-scale=1"}]]
11:null
13:{"metadata":[],"error":null,"digest":"$undefined"}
f:"$13:metadata"
