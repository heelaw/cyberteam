1:"$Sreact.fragment"
2:I[9664,["177","static/chunks/app/layout-23c4d3791a1858be.js"],""]
3:I[5341,[],""]
4:I[25,[],""]
9:I[4431,[],""]
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
0:{"P":null,"b":"2V5OXcQO_79G2TOuAwnwy","p":"","c":["","_not-found",""],"i":false,"f":[[["",{"children":["/_not-found",{"children":["__PAGE__",{}]}]},"$undefined","$undefined",true],["",["$","$1","c",{"children":[null,["$","html",null,{"lang":"zh-CN","children":["$","body",null,{"children":[["$","div",null,{"className":"shell","children":[["$","aside",null,{"className":"sidebar","children":[["$","div",null,{"className":"brand","children":[["$","div",null,{"className":"brandMark","children":"CT"}],["$","div",null,{"children":[["$","div",null,{"className":"brandTitle","children":"CyberTeam"}],["$","div",null,{"className":"brandSubtitle","children":"本地 AI 军团操作系统"}]]}]]}],["$","div",null,{"className":"statusCard","children":[["$","div",null,{"className":"statusLabel","children":"Runtime"}],["$","div",null,{"className":"statusValue","children":"Electron + Next.js"}],["$","div",null,{"className":"statusMeta","children":"SQLite / Claude Code / macOS"}]]}],["$","nav",null,{"className":"nav","children":[["$","$L2","/",{"className":"navItem","href":"/","children":[["$","span",null,{"className":"navLabel","children":"Dashboard"}],["$","span",null,{"className":"navNote","children":"总览"}]]}],["$","$L2","/chat",{"className":"navItem","href":"/chat","children":[["$","span",null,{"className":"navLabel","children":"Chat"}],["$","span",null,{"className":"navNote","children":"会话与群聊"}]]}],["$","$L2","/organization",{"className":"navItem","href":"/organization","children":[["$","span",null,{"className":"navLabel","children":"Organization"}],["$","span",null,{"className":"navNote","children":"组织结构"}]]}],["$","$L2","/playground",{"className":"navItem","href":"/playground","children":[["$","span",null,{"className":"navLabel","children":"Playground"}],["$","span",null,{"className":"navNote","children":"输出与审核"}]]}],["$","$L2","/market",{"className":"navItem","href":"/market","children":[["$","span",null,{"className":"navLabel","children":"Market"}],["$","span",null,{"className":"navNote","children":"Agent / Skill / 模板"}]]}],["$","$L2","/settings",{"className":"navItem","href":"/settings","children":[["$","span",null,{"className":"navLabel","children":"Settings"}],["$","span",null,{"className":"navNote","children":"本地与接入"}]]}]]}]]}],["$","div",null,{"className":"workspace","children":[["$","header",null,{"className":"topbar","children":[["$","div",null,{"children":[["$","p",null,{"className":"eyebrow","children":"Socratic by default"}],["$","h1",null,{"children":"让一个人拥有一整支 AI 公司。"}]]}],["$","div",null,{"className":"topbarPills","children":[["$","span",null,{"children":"Local First"}],["$","span",null,{"children":"Playground Ready"}],["$","span",null,{"children":"CEO Review"}]]}]]}],["$","main",null,{"className":"content","children":["$","$L3",null,{"parallelRouterKey":"children","error":"$undefined","errorStyles":"$undefined","errorScripts":"$undefined","template":["$","$L4",null,{}],"templateStyles":"$undefined","templateScripts":"$undefined","notFound":"$undefined","forbidden":"$undefined","unauthorized":"$undefined"}]}]]}]]}],["$","style",null,{"dangerouslySetInnerHTML":{"__html":"$5"}}]]}]}]]}],{"children":["/_not-found","$L6",{"children":["__PAGE__","$L7",{},null,false]},null,false]},null,false],"$L8",false]],"m":"$undefined","G":["$9",[]],"s":false,"S":true}
a:I[5104,[],"OutletBoundary"]
c:I[7158,[],"AsyncMetadataOutlet"]
e:I[5104,[],"ViewportBoundary"]
10:I[5104,[],"MetadataBoundary"]
11:"$Sreact.suspense"
6:["$","$1","c",{"children":[null,["$","$L3",null,{"parallelRouterKey":"children","error":"$undefined","errorStyles":"$undefined","errorScripts":"$undefined","template":["$","$L4",null,{}],"templateStyles":"$undefined","templateScripts":"$undefined","notFound":"$undefined","forbidden":"$undefined","unauthorized":"$undefined"}]]}]
7:["$","$1","c",{"children":[[["$","title",null,{"children":"404: This page could not be found."}],["$","div",null,{"style":{"fontFamily":"system-ui,\"Segoe UI\",Roboto,Helvetica,Arial,sans-serif,\"Apple Color Emoji\",\"Segoe UI Emoji\"","height":"100vh","textAlign":"center","display":"flex","flexDirection":"column","alignItems":"center","justifyContent":"center"},"children":["$","div",null,{"children":[["$","style",null,{"dangerouslySetInnerHTML":{"__html":"body{color:#000;background:#fff;margin:0}.next-error-h1{border-right:1px solid rgba(0,0,0,.3)}@media (prefers-color-scheme:dark){body{color:#fff;background:#000}.next-error-h1{border-right:1px solid rgba(255,255,255,.3)}}"}}],["$","h1",null,{"className":"next-error-h1","style":{"display":"inline-block","margin":"0 20px 0 0","padding":"0 23px 0 0","fontSize":24,"fontWeight":500,"verticalAlign":"top","lineHeight":"49px"},"children":404}],["$","div",null,{"style":{"display":"inline-block"},"children":["$","h2",null,{"style":{"fontSize":14,"fontWeight":400,"lineHeight":"49px","margin":0},"children":"This page could not be found."}]}]]}]}]],null,["$","$La",null,{"children":["$Lb",["$","$Lc",null,{"promise":"$@d"}]]}]]}]
8:["$","$1","h",{"children":[["$","meta",null,{"name":"robots","content":"noindex"}],[["$","$Le",null,{"children":"$Lf"}],null],["$","$L10",null,{"children":["$","div",null,{"hidden":true,"children":["$","$11",null,{"fallback":null,"children":"$L12"}]}]}]]}]
f:[["$","meta","0",{"charSet":"utf-8"}],["$","meta","1",{"name":"viewport","content":"width=device-width, initial-scale=1"}]]
b:null
d:{"metadata":[],"error":null,"digest":"$undefined"}
12:"$d:metadata"
