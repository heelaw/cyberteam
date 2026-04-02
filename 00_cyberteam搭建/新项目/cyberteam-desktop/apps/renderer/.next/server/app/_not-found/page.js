(()=>{var a={};a.id=492,a.ids=[492],a.modules={261:a=>{"use strict";a.exports=require("next/dist/shared/lib/router/utils/app-paths")},846:a=>{"use strict";a.exports=require("next/dist/compiled/next-server/app-page.runtime.prod.js")},1025:a=>{"use strict";a.exports=require("next/dist/server/app-render/dynamic-access-async-storage.external.js")},3033:a=>{"use strict";a.exports=require("next/dist/server/app-render/work-unit-async-storage.external.js")},3295:a=>{"use strict";a.exports=require("next/dist/server/app-render/after-task-async-storage.external.js")},3873:a=>{"use strict";a.exports=require("path")},4926:(a,b,c)=>{Promise.resolve().then(c.t.bind(c,4496,23))},5211:(a,b,c)=>{Promise.resolve().then(c.t.bind(c,8365,23)),Promise.resolve().then(c.t.bind(c,4596,23)),Promise.resolve().then(c.t.bind(c,6186,23)),Promise.resolve().then(c.t.bind(c,7805,23)),Promise.resolve().then(c.t.bind(c,7561,23)),Promise.resolve().then(c.t.bind(c,7569,23)),Promise.resolve().then(c.t.bind(c,2747,23)),Promise.resolve().then(c.t.bind(c,6676,23)),Promise.resolve().then(c.bind(c,7225))},6439:a=>{"use strict";a.exports=require("next/dist/shared/lib/no-fallback-error.external")},6713:a=>{"use strict";a.exports=require("next/dist/shared/lib/router/utils/is-bot")},7570:(a,b,c)=>{"use strict";c.r(b),c.d(b,{default:()=>h});var d=c(5939),e=c(3498),f=c.n(e);let g=[{href:"/",label:"Dashboard",note:"总览"},{href:"/chat",label:"Chat",note:"会话与群聊"},{href:"/organization",label:"Organization",note:"组织结构"},{href:"/playground",label:"Playground",note:"输出与审核"},{href:"/market",label:"Market",note:"Agent / Skill / 模板"},{href:"/settings",label:"Settings",note:"本地与接入"}];function h({children:a}){return(0,d.jsx)("html",{lang:"zh-CN",children:(0,d.jsxs)("body",{children:[(0,d.jsxs)("div",{className:"shell",children:[(0,d.jsxs)("aside",{className:"sidebar",children:[(0,d.jsxs)("div",{className:"brand",children:[(0,d.jsx)("div",{className:"brandMark",children:"CT"}),(0,d.jsxs)("div",{children:[(0,d.jsx)("div",{className:"brandTitle",children:"CyberTeam"}),(0,d.jsx)("div",{className:"brandSubtitle",children:"本地 AI 军团操作系统"})]})]}),(0,d.jsxs)("div",{className:"statusCard",children:[(0,d.jsx)("div",{className:"statusLabel",children:"Runtime"}),(0,d.jsx)("div",{className:"statusValue",children:"Electron + Next.js"}),(0,d.jsx)("div",{className:"statusMeta",children:"SQLite / Claude Code / macOS"})]}),(0,d.jsx)("nav",{className:"nav",children:g.map(a=>(0,d.jsxs)(f(),{className:"navItem",href:a.href,children:[(0,d.jsx)("span",{className:"navLabel",children:a.label}),(0,d.jsx)("span",{className:"navNote",children:a.note})]},a.href))})]}),(0,d.jsxs)("div",{className:"workspace",children:[(0,d.jsxs)("header",{className:"topbar",children:[(0,d.jsxs)("div",{children:[(0,d.jsx)("p",{className:"eyebrow",children:"Socratic by default"}),(0,d.jsx)("h1",{children:"让一个人拥有一整支 AI 公司。"})]}),(0,d.jsxs)("div",{className:"topbarPills",children:[(0,d.jsx)("span",{children:"Local First"}),(0,d.jsx)("span",{children:"Playground Ready"}),(0,d.jsx)("span",{children:"CEO Review"})]})]}),(0,d.jsx)("main",{className:"content",children:a})]})]}),(0,d.jsx)("style",{dangerouslySetInnerHTML:{__html:i}})]})})}let i=`
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
`},8259:(a,b,c)=>{Promise.resolve().then(c.t.bind(c,8671,23)),Promise.resolve().then(c.t.bind(c,6542,23)),Promise.resolve().then(c.t.bind(c,8248,23)),Promise.resolve().then(c.t.bind(c,9743,23)),Promise.resolve().then(c.t.bind(c,6231,23)),Promise.resolve().then(c.t.bind(c,959,23)),Promise.resolve().then(c.t.bind(c,2041,23)),Promise.resolve().then(c.t.bind(c,5094,23)),Promise.resolve().then(c.t.bind(c,7487,23))},8354:a=>{"use strict";a.exports=require("util")},9121:a=>{"use strict";a.exports=require("next/dist/server/app-render/action-async-storage.external.js")},9294:a=>{"use strict";a.exports=require("next/dist/server/app-render/work-async-storage.external.js")},9654:(a,b,c)=>{Promise.resolve().then(c.t.bind(c,3498,23))},9975:(a,b,c)=>{"use strict";c.r(b),c.d(b,{GlobalError:()=>D.a,__next_app__:()=>J,handler:()=>L,pages:()=>I,routeModule:()=>K,tree:()=>H});var d=c(3653),e=c(7714),f=c(5250),g=c(7587),h=c(2369),i=c(1889),j=c(6232),k=c(2841),l=c(6537),m=c(6027),n=c(8559),o=c(5928),p=c(9374),q=c(5971),r=c(261),s=c(9898),t=c(2967),u=c(6713),v=c(139),w=c(4248),x=c(9580),y=c(7749),z=c(3123),A=c(9745),B=c(6439),C=c(8671),D=c.n(C),E=c(8283),F=c(9818),G={};for(let a in E)0>["default","tree","pages","GlobalError","__next_app__","routeModule","handler"].indexOf(a)&&(G[a]=()=>E[a]);c.d(b,G);let H={children:["",{children:["/_not-found",{children:["__PAGE__",{},{page:[()=>Promise.resolve().then(c.t.bind(c,7983,23)),"next/dist/client/components/builtin/not-found.js"]}]},{}]},{layout:[()=>Promise.resolve().then(c.bind(c,7570)),"/Users/cyberwiz/Documents/01_Project/00_cyberteam搭建/新项目/cyberteam-desktop/apps/renderer/src/app/layout.tsx"],"global-error":[()=>Promise.resolve().then(c.t.bind(c,8671,23)),"next/dist/client/components/builtin/global-error.js"],forbidden:[()=>Promise.resolve().then(c.t.bind(c,5034,23)),"next/dist/client/components/builtin/forbidden.js"],unauthorized:[()=>Promise.resolve().then(c.t.bind(c,4693,23)),"next/dist/client/components/builtin/unauthorized.js"]}]}.children,I=[],J={require:c,loadChunk:()=>Promise.resolve()},K=new d.AppPageRouteModule({definition:{kind:e.RouteKind.APP_PAGE,page:"/_not-found/page",pathname:"/_not-found",bundlePath:"",filename:"",appPaths:[]},userland:{loaderTree:H},distDir:".next",relativeProjectDir:""});async function L(a,b,d){var C;let G="/_not-found/page";"/index"===G&&(G="/");let M=(0,h.getRequestMeta)(a,"postponed"),N=(0,h.getRequestMeta)(a,"minimalMode"),O=await K.prepare(a,b,{srcPage:G,multiZoneDraftMode:!1});if(!O)return b.statusCode=400,b.end("Bad Request"),null==d.waitUntil||d.waitUntil.call(d,Promise.resolve()),null;let{buildId:P,query:Q,params:R,parsedUrl:S,pageIsDynamic:T,buildManifest:U,nextFontManifest:V,reactLoadableManifest:W,serverActionsManifest:X,clientReferenceManifest:Y,subresourceIntegrityManifest:Z,prerenderManifest:$,isDraftMode:_,resolvedPathname:aa,revalidateOnlyGenerated:ab,routerServerContext:ac,nextConfig:ad,interceptionRoutePatterns:ae}=O,af=S.pathname||"/",ag=(0,r.normalizeAppPath)(G),{isOnDemandRevalidate:ah}=O,ai=K.match(af,$),aj=!!$.routes[aa],ak=!!(ai||aj||$.routes[ag]),al=a.headers["user-agent"]||"",am=(0,u.getBotType)(al),an=(0,p.isHtmlBotRequest)(a),ao=(0,h.getRequestMeta)(a,"isPrefetchRSCRequest")??"1"===a.headers[t.NEXT_ROUTER_PREFETCH_HEADER],ap=(0,h.getRequestMeta)(a,"isRSCRequest")??!!a.headers[t.RSC_HEADER],aq=(0,s.getIsPossibleServerAction)(a),ar=(0,m.checkIsAppPPREnabled)(ad.experimental.ppr)&&(null==(C=$.routes[ag]??$.dynamicRoutes[ag])?void 0:C.renderingMode)==="PARTIALLY_STATIC",as=!1,at=!1,au=ar?M:void 0,av=ar&&ap&&!ao,aw=(0,h.getRequestMeta)(a,"segmentPrefetchRSCRequest"),ax=!al||(0,p.shouldServeStreamingMetadata)(al,ad.htmlLimitedBots);an&&ar&&(ak=!1,ax=!1);let ay=!0===K.isDev||!ak||"string"==typeof M||av,az=an&&ar,aA=null;_||!ak||ay||aq||au||av||(aA=aa);let aB=aA;!aB&&K.isDev&&(aB=aa),K.isDev||_||!ak||!ap||av||(0,k.d)(a.headers);let aC={...E,tree:H,pages:I,GlobalError:D(),handler:L,routeModule:K,__next_app__:J};X&&Y&&(0,o.setReferenceManifestsSingleton)({page:G,clientReferenceManifest:Y,serverActionsManifest:X,serverModuleMap:(0,q.createServerModuleMap)({serverActionsManifest:X})});let aD=a.method||"GET",aE=(0,g.getTracer)(),aF=aE.getActiveScopeSpan();try{let f=K.getVaryHeader(aa,ae);b.setHeader("Vary",f);let k=async(c,d)=>{let e=new l.NodeNextRequest(a),f=new l.NodeNextResponse(b);return K.render(e,f,d).finally(()=>{if(!c)return;c.setAttributes({"http.status_code":b.statusCode,"next.rsc":!1});let d=aE.getRootSpanAttributes();if(!d)return;if(d.get("next.span_type")!==i.BaseServerSpan.handleRequest)return void console.warn(`Unexpected root span type '${d.get("next.span_type")}'. Please report this Next.js issue https://github.com/vercel/next.js`);let e=d.get("next.route");if(e){let a=`${aD} ${e}`;c.setAttributes({"next.route":e,"http.route":e,"next.span_name":a}),c.updateName(a)}else c.updateName(`${aD} ${a.url}`)})},m=async({span:e,postponed:f,fallbackRouteParams:g})=>{let i={query:Q,params:R,page:ag,sharedContext:{buildId:P},serverComponentsHmrCache:(0,h.getRequestMeta)(a,"serverComponentsHmrCache"),fallbackRouteParams:g,renderOpts:{App:()=>null,Document:()=>null,pageConfig:{},ComponentMod:aC,Component:(0,j.T)(aC),params:R,routeModule:K,page:G,postponed:f,shouldWaitOnAllReady:az,serveStreamingMetadata:ax,supportsDynamicResponse:"string"==typeof f||ay,buildManifest:U,nextFontManifest:V,reactLoadableManifest:W,subresourceIntegrityManifest:Z,serverActionsManifest:X,clientReferenceManifest:Y,setIsrStatus:null==ac?void 0:ac.setIsrStatus,dir:c(3873).join(process.cwd(),K.relativeProjectDir),isDraftMode:_,isRevalidate:ak&&!f&&!av,botType:am,isOnDemandRevalidate:ah,isPossibleServerAction:aq,assetPrefix:ad.assetPrefix,nextConfigOutput:ad.output,crossOrigin:ad.crossOrigin,trailingSlash:ad.trailingSlash,previewProps:$.preview,deploymentId:ad.deploymentId,enableTainting:ad.experimental.taint,htmlLimitedBots:ad.htmlLimitedBots,devtoolSegmentExplorer:ad.experimental.devtoolSegmentExplorer,reactMaxHeadersLength:ad.reactMaxHeadersLength,multiZoneDraftMode:!1,incrementalCache:(0,h.getRequestMeta)(a,"incrementalCache"),cacheLifeProfiles:ad.experimental.cacheLife,basePath:ad.basePath,serverActions:ad.experimental.serverActions,...as?{nextExport:!0,supportsDynamicResponse:!1,isStaticGeneration:!0,isRevalidate:!0,isDebugDynamicAccesses:as}:{},experimental:{isRoutePPREnabled:ar,expireTime:ad.expireTime,staleTimes:ad.experimental.staleTimes,cacheComponents:!!ad.experimental.cacheComponents,clientSegmentCache:!!ad.experimental.clientSegmentCache,clientParamParsing:!!ad.experimental.clientParamParsing,dynamicOnHover:!!ad.experimental.dynamicOnHover,inlineCss:!!ad.experimental.inlineCss,authInterrupts:!!ad.experimental.authInterrupts,clientTraceMetadata:ad.experimental.clientTraceMetadata||[]},waitUntil:d.waitUntil,onClose:a=>{b.on("close",a)},onAfterTaskError:()=>{},onInstrumentationRequestError:(b,c,d)=>K.onRequestError(a,b,d,ac),err:(0,h.getRequestMeta)(a,"invokeError"),dev:K.isDev}},l=await k(e,i),{metadata:m}=l,{cacheControl:n,headers:o={},fetchTags:p}=m;if(p&&(o[y.NEXT_CACHE_TAGS_HEADER]=p),a.fetchMetrics=m.fetchMetrics,ak&&(null==n?void 0:n.revalidate)===0&&!K.isDev&&!ar){let a=m.staticBailoutInfo,b=Object.defineProperty(Error(`Page changed from static to dynamic at runtime ${aa}${(null==a?void 0:a.description)?`, reason: ${a.description}`:""}
see more here https://nextjs.org/docs/messages/app-static-to-dynamic-error`),"__NEXT_ERROR_CODE",{value:"E132",enumerable:!1,configurable:!0});if(null==a?void 0:a.stack){let c=a.stack;b.stack=b.message+c.substring(c.indexOf("\n"))}throw b}return{value:{kind:v.CachedRouteKind.APP_PAGE,html:l,headers:o,rscData:m.flightData,postponed:m.postponed,status:m.statusCode,segmentData:m.segmentData},cacheControl:n}},o=async({hasResolved:c,previousCacheEntry:f,isRevalidating:g,span:i})=>{let j,k=!1===K.isDev,l=c||b.writableEnded;if(ah&&ab&&!f&&!N)return(null==ac?void 0:ac.render404)?await ac.render404(a,b):(b.statusCode=404,b.end("This page could not be found")),null;if(ai&&(j=(0,w.parseFallbackField)(ai.fallback)),j===w.FallbackMode.PRERENDER&&(0,u.isBot)(al)&&(!ar||an)&&(j=w.FallbackMode.BLOCKING_STATIC_RENDER),(null==f?void 0:f.isStale)===-1&&(ah=!0),ah&&(j!==w.FallbackMode.NOT_FOUND||f)&&(j=w.FallbackMode.BLOCKING_STATIC_RENDER),!N&&j!==w.FallbackMode.BLOCKING_STATIC_RENDER&&aB&&!l&&!_&&T&&(k||!aj)){let b;if((k||ai)&&j===w.FallbackMode.NOT_FOUND)throw new B.NoFallbackError;if(ar&&!ap){let c="string"==typeof(null==ai?void 0:ai.fallback)?ai.fallback:k?ag:null;if(b=await K.handleResponse({cacheKey:c,req:a,nextConfig:ad,routeKind:e.RouteKind.APP_PAGE,isFallback:!0,prerenderManifest:$,isRoutePPREnabled:ar,responseGenerator:async()=>m({span:i,postponed:void 0,fallbackRouteParams:k||at?(0,n.u)(ag):null}),waitUntil:d.waitUntil}),null===b)return null;if(b)return delete b.cacheControl,b}}let o=ah||g||!au?void 0:au;if(as&&void 0!==o)return{cacheControl:{revalidate:1,expire:void 0},value:{kind:v.CachedRouteKind.PAGES,html:x.default.EMPTY,pageData:{},headers:void 0,status:void 0}};let p=T&&ar&&((0,h.getRequestMeta)(a,"renderFallbackShell")||at)?(0,n.u)(af):null;return m({span:i,postponed:o,fallbackRouteParams:p})},p=async c=>{var f,g,i,j,k;let l,n=await K.handleResponse({cacheKey:aA,responseGenerator:a=>o({span:c,...a}),routeKind:e.RouteKind.APP_PAGE,isOnDemandRevalidate:ah,isRoutePPREnabled:ar,req:a,nextConfig:ad,prerenderManifest:$,waitUntil:d.waitUntil});if(_&&b.setHeader("Cache-Control","private, no-cache, no-store, max-age=0, must-revalidate"),K.isDev&&b.setHeader("Cache-Control","no-store, must-revalidate"),!n){if(aA)throw Object.defineProperty(Error("invariant: cache entry required but not generated"),"__NEXT_ERROR_CODE",{value:"E62",enumerable:!1,configurable:!0});return null}if((null==(f=n.value)?void 0:f.kind)!==v.CachedRouteKind.APP_PAGE)throw Object.defineProperty(Error(`Invariant app-page handler received invalid cache entry ${null==(i=n.value)?void 0:i.kind}`),"__NEXT_ERROR_CODE",{value:"E707",enumerable:!1,configurable:!0});let p="string"==typeof n.value.postponed;ak&&!av&&(!p||ao)&&(N||b.setHeader("x-nextjs-cache",ah?"REVALIDATED":n.isMiss?"MISS":n.isStale?"STALE":"HIT"),b.setHeader(t.NEXT_IS_PRERENDER_HEADER,"1"));let{value:q}=n;if(au)l={revalidate:0,expire:void 0};else if(N&&ap&&!ao&&ar)l={revalidate:0,expire:void 0};else if(!K.isDev)if(_)l={revalidate:0,expire:void 0};else if(ak){if(n.cacheControl)if("number"==typeof n.cacheControl.revalidate){if(n.cacheControl.revalidate<1)throw Object.defineProperty(Error(`Invalid revalidate configuration provided: ${n.cacheControl.revalidate} < 1`),"__NEXT_ERROR_CODE",{value:"E22",enumerable:!1,configurable:!0});l={revalidate:n.cacheControl.revalidate,expire:(null==(j=n.cacheControl)?void 0:j.expire)??ad.expireTime}}else l={revalidate:y.CACHE_ONE_YEAR,expire:void 0}}else b.getHeader("Cache-Control")||(l={revalidate:0,expire:void 0});if(n.cacheControl=l,"string"==typeof aw&&(null==q?void 0:q.kind)===v.CachedRouteKind.APP_PAGE&&q.segmentData){b.setHeader(t.NEXT_DID_POSTPONE_HEADER,"2");let c=null==(k=q.headers)?void 0:k[y.NEXT_CACHE_TAGS_HEADER];N&&ak&&c&&"string"==typeof c&&b.setHeader(y.NEXT_CACHE_TAGS_HEADER,c);let d=q.segmentData.get(aw);return void 0!==d?(0,A.sendRenderResult)({req:a,res:b,generateEtags:ad.generateEtags,poweredByHeader:ad.poweredByHeader,result:x.default.fromStatic(d,t.RSC_CONTENT_TYPE_HEADER),cacheControl:n.cacheControl}):(b.statusCode=204,(0,A.sendRenderResult)({req:a,res:b,generateEtags:ad.generateEtags,poweredByHeader:ad.poweredByHeader,result:x.default.EMPTY,cacheControl:n.cacheControl}))}let r=(0,h.getRequestMeta)(a,"onCacheEntry");if(r&&await r({...n,value:{...n.value,kind:"PAGE"}},{url:(0,h.getRequestMeta)(a,"initURL")}))return null;if(p&&au)throw Object.defineProperty(Error("Invariant: postponed state should not be present on a resume request"),"__NEXT_ERROR_CODE",{value:"E396",enumerable:!1,configurable:!0});if(q.headers){let a={...q.headers};for(let[c,d]of(N&&ak||delete a[y.NEXT_CACHE_TAGS_HEADER],Object.entries(a)))if(void 0!==d)if(Array.isArray(d))for(let a of d)b.appendHeader(c,a);else"number"==typeof d&&(d=d.toString()),b.appendHeader(c,d)}let s=null==(g=q.headers)?void 0:g[y.NEXT_CACHE_TAGS_HEADER];if(N&&ak&&s&&"string"==typeof s&&b.setHeader(y.NEXT_CACHE_TAGS_HEADER,s),!q.status||ap&&ar||(b.statusCode=q.status),!N&&q.status&&F.RedirectStatusCode[q.status]&&ap&&(b.statusCode=200),p&&b.setHeader(t.NEXT_DID_POSTPONE_HEADER,"1"),ap&&!_){if(void 0===q.rscData){if(q.postponed)throw Object.defineProperty(Error("Invariant: Expected postponed to be undefined"),"__NEXT_ERROR_CODE",{value:"E372",enumerable:!1,configurable:!0});return(0,A.sendRenderResult)({req:a,res:b,generateEtags:ad.generateEtags,poweredByHeader:ad.poweredByHeader,result:q.html,cacheControl:av?{revalidate:0,expire:void 0}:n.cacheControl})}return(0,A.sendRenderResult)({req:a,res:b,generateEtags:ad.generateEtags,poweredByHeader:ad.poweredByHeader,result:x.default.fromStatic(q.rscData,t.RSC_CONTENT_TYPE_HEADER),cacheControl:n.cacheControl})}let u=q.html;if(!p||N||ap)return(0,A.sendRenderResult)({req:a,res:b,generateEtags:ad.generateEtags,poweredByHeader:ad.poweredByHeader,result:u,cacheControl:n.cacheControl});if(as)return u.push(new ReadableStream({start(a){a.enqueue(z.ENCODED_TAGS.CLOSED.BODY_AND_HTML),a.close()}})),(0,A.sendRenderResult)({req:a,res:b,generateEtags:ad.generateEtags,poweredByHeader:ad.poweredByHeader,result:u,cacheControl:{revalidate:0,expire:void 0}});let w=new TransformStream;return u.push(w.readable),m({span:c,postponed:q.postponed,fallbackRouteParams:null}).then(async a=>{var b,c;if(!a)throw Object.defineProperty(Error("Invariant: expected a result to be returned"),"__NEXT_ERROR_CODE",{value:"E463",enumerable:!1,configurable:!0});if((null==(b=a.value)?void 0:b.kind)!==v.CachedRouteKind.APP_PAGE)throw Object.defineProperty(Error(`Invariant: expected a page response, got ${null==(c=a.value)?void 0:c.kind}`),"__NEXT_ERROR_CODE",{value:"E305",enumerable:!1,configurable:!0});await a.value.html.pipeTo(w.writable)}).catch(a=>{w.writable.abort(a).catch(a=>{console.error("couldn't abort transformer",a)})}),(0,A.sendRenderResult)({req:a,res:b,generateEtags:ad.generateEtags,poweredByHeader:ad.poweredByHeader,result:u,cacheControl:{revalidate:0,expire:void 0}})};if(!aF)return await aE.withPropagatedContext(a.headers,()=>aE.trace(i.BaseServerSpan.handleRequest,{spanName:`${aD} ${a.url}`,kind:g.SpanKind.SERVER,attributes:{"http.method":aD,"http.target":a.url}},p));await p(aF)}catch(b){throw b instanceof B.NoFallbackError||await K.onRequestError(a,b,{routerKind:"App Router",routePath:G,routeType:"render",revalidateReason:(0,f.c)({isRevalidate:ak,isOnDemandRevalidate:ah})},ac),b}}}};var b=require("../../webpack-runtime.js");b.C(a);var c=b.X(0,[270],()=>b(b.s=9975));module.exports=c})();