exports.id=594,exports.ids=[594],exports.modules={3269:(a,b,c)=>{"use strict";c.d(b,{ChatView:()=>m,DashboardView:()=>l,MarketView:()=>p,OrganizationView:()=>n,PlaygroundView:()=>o,SettingsView:()=>q});var d=c(8157),e=c(1768);function f(){}async function g(){let a=f();if(!a?.app?.getState)return null;try{return await a.app.getState()}catch(a){return console.warn("[CyberTeam] Failed to load runtime state",a),null}}let h=["done","in-progress","next","planned"];function i(a){return{status:a.status,goal:a.goal,proof:a.proof,question:a.question,sortOrder:a.sortOrder??0}}function j(){let[a,b]=(0,e.useState)(null),c=(0,e.useRef)(0),d=(0,e.useRef)(!0);return{state:a,refresh:async function(){let a=++c.current,e=await g();return d.current&&a===c.current&&b(e),e}}}function k(a){return a?.database?.counts??{}}function l({seed:a}){let{state:b,refresh:c}=j(),g=k(b),l=b?b.database?.company:a.company,m=b?b.database?.departments??[]:a.organization.departments,n=b?b.database?.agents??[]:a.organization.agents,o=function(a,b){let c=b?.database?.roadmapPhases;return b&&c?.length?[...c].sort((a,b)=>(a.sortOrder??0)-(b.sortOrder??0)):a.roadmap}(a,b),p=new Map(o.map(a=>[a.id,a])),[q,r]=(0,e.useState)(()=>Object.fromEntries(o.map(a=>[a.id,i(a)]))),[s,t]=(0,e.useState)(""),[u,v]=(0,e.useState)(""),w=(0,e.useRef)(new Set),x=b?.database?.playgroundDocuments?.[0]?{...b.database.playgroundDocuments[0],content:b.database.playgroundDocuments[0].content??""}:a.playgroundDocument,y=b?.database?.playgroundDocuments?.[0]?b.database.playgroundDocuments[0].content??"运行态尚无导出内容。":a.playgroundExport,z=b?.database?.reviewRecords?.[0]?{status:b.database.reviewRecords[0].decision??"pending",notes:function(a){if(Array.isArray(a))return a.map(a=>String(a));if("string"!=typeof a||!a)return[];try{let b=JSON.parse(a);return Array.isArray(b)?b.map(a=>String(a)):[a]}catch{return[a]}}(b.database.reviewRecords[0].comments)}:a.playgroundReview,A=l?.name??(b?"公司未初始化":a.company.name),B=l?.version??(b?"—":a.company.version),C=l?.description??(b?"运行态尚未写入公司信息":a.company.description),D=b?[{label:"公司",value:String(g.companies??0),note:A},{label:"部门",value:String(g.departments??m.length),note:"数据库中的组织结构"},{label:"Agent",value:String(g.agents??n.length),note:"可协作节点已加载"},{label:"会话",value:String(g.conversations??a.conversations.length),note:"对话线程已持久化"},{label:"Skill",value:String(g.skills??a.skills.length),note:"能力仓库已入库"},{label:"Claude Code",value:b.claude.installed?"已检测":"未检测",note:b.claude.command??"本地执行引擎"}]:a.metrics;function E(a,b){w.current.add(a),r(c=>{let d=p.get(a),e=c[a]??(d?i(d):void 0);return e?{...c,[a]:{...e,...b}}:c})}async function F(d){let e=f(),g=q[d],h=o.find(a=>a.id===d);if(e?.roadmap?.upsertPhase&&g&&h){t(d);try{await e.roadmap.upsertPhase({id:h.id,companyId:b?.database?.company?.id??a.company.id,name:h.name,status:g.status,goal:g.goal,proof:g.proof,question:g.question,sortOrder:g.sortOrder,createdAt:h.createdAt,updatedAt:new Date().toISOString()}),await c(),w.current.delete(d),v("路线图已写入 SQLite 并刷新运行态")}catch(a){console.error("[CyberTeam] Failed to save roadmap phase",a),v("路线图保存失败，请检查运行态是否可写")}finally{t("")}}}return(0,d.jsxs)("article",{className:"sectionStack",children:[(0,d.jsxs)("section",{className:"hero",children:[(0,d.jsxs)("div",{className:"heroHeader",children:[(0,d.jsxs)("div",{children:[(0,d.jsx)("p",{className:"eyebrow",children:"Dashboard"}),(0,d.jsx)("h2",{className:"heroTitle",children:"CyberTeam 已经从设想进入最小闭环。"})]}),(0,d.jsx)("div",{className:"chip",children:b?"Live runtime":"Bootstrap preview"})]}),(0,d.jsx)("p",{className:"heroLead",children:"这个版本先验证四件事：公司能否组织起来，Agent 能否协作，聊天能否承载任务，Playground 能否把讨论沉淀成交付物。"}),(0,d.jsx)("div",{className:"grid metrics",children:D.map(a=>(0,d.jsxs)("div",{className:"metric",children:[(0,d.jsx)("div",{className:"statusLabel",children:a.label}),(0,d.jsx)("div",{className:"metricValue",children:a.value}),(0,d.jsx)("div",{className:"metricNote",children:a.note})]},a.label))})]}),(0,d.jsxs)("section",{className:"panel",children:[(0,d.jsx)("h3",{className:"sectionTitle",children:"第一性原理路线图"}),(0,d.jsx)("div",{className:"subtle",style:{marginBottom:12},children:u||"编辑后会直接写回 SQLite，并在保存后刷新运行态。"}),(0,d.jsx)("div",{className:"sectionStack",children:o.map(a=>{let b=q[a.id];return(0,d.jsxs)("div",{className:"panelNote",style:{display:"grid",gap:12},children:[(0,d.jsxs)("div",{className:"cardHeader",children:[(0,d.jsxs)("div",{style:{display:"grid",gap:4},children:[(0,d.jsx)("strong",{children:a.name}),(0,d.jsx)("span",{className:"subtle",children:a.question})]}),(0,d.jsx)("span",{className:"chip",children:b?.status??a.status})]}),(0,d.jsxs)("div",{className:"grid two",style:{gap:12},children:[(0,d.jsxs)("label",{className:"settingsTitle",style:{display:"grid",gap:6},children:["Status",(0,d.jsx)("select",{value:q[a.id]?.status??a.status,onChange:b=>E(a.id,{status:b.target.value}),style:{borderRadius:14,padding:10,background:"rgba(255,255,255,0.04)",color:"inherit",border:"1px solid rgba(148,163,184,0.2)"},children:h.map(a=>(0,d.jsx)("option",{value:a,children:a},a))})]}),(0,d.jsxs)("label",{className:"settingsTitle",style:{display:"grid",gap:6},children:["Sort Order",(0,d.jsx)("input",{type:"number",value:q[a.id]?.sortOrder??a.sortOrder??0,onChange:b=>E(a.id,{sortOrder:Number(b.target.value)}),style:{borderRadius:14,padding:10,background:"rgba(255,255,255,0.04)",color:"inherit",border:"1px solid rgba(148,163,184,0.2)"}})]})]}),(0,d.jsxs)("label",{className:"settingsTitle",style:{display:"grid",gap:6},children:["Goal",(0,d.jsx)("input",{value:q[a.id]?.goal??a.goal,onChange:b=>E(a.id,{goal:b.target.value}),style:{borderRadius:14,padding:10,background:"rgba(255,255,255,0.04)",color:"inherit",border:"1px solid rgba(148,163,184,0.2)"}})]}),(0,d.jsxs)("label",{className:"settingsTitle",style:{display:"grid",gap:6},children:["Proof",(0,d.jsx)("textarea",{value:q[a.id]?.proof??a.proof,onChange:b=>E(a.id,{proof:b.target.value}),rows:2,style:{borderRadius:14,padding:10,background:"rgba(255,255,255,0.04)",color:"inherit",border:"1px solid rgba(148,163,184,0.2)"}})]}),(0,d.jsx)("div",{style:{display:"flex",justifyContent:"flex-end"},children:(0,d.jsx)("button",{type:"button",onClick:()=>void F(a.id),disabled:s===a.id,style:{borderRadius:999,padding:"10px 16px",background:"linear-gradient(135deg, #77c6ff, #7cf0c8)",border:0,color:"#06101c",fontWeight:700},children:s===a.id?"Saving...":"Save Phase"})})]},a.id)})})]}),(0,d.jsxs)("section",{className:"panel",children:[(0,d.jsx)("h3",{className:"sectionTitle",children:"运行时状态"}),(0,d.jsxs)("div",{className:"timeline",children:[(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"Company"}),(0,d.jsxs)("span",{className:"subtle",children:[A," \xb7 ",B]})]}),(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"Database"}),(0,d.jsx)("span",{className:"subtle",children:b?.database?.path??"SQLite 未加载"})]}),(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"Departments"}),(0,d.jsx)("span",{className:"subtle",children:m.length})]}),(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"Agents"}),(0,d.jsx)("span",{className:"subtle",children:n.length})]})]})]}),(0,d.jsxs)("section",{className:"grid two",children:[(0,d.jsxs)("div",{className:"panel",children:[(0,d.jsx)("h3",{className:"sectionTitle",children:"当前组织"}),(0,d.jsxs)("div",{className:"sectionStack",children:[(0,d.jsxs)("div",{children:[(0,d.jsxs)("div",{className:"cardHeader",children:[(0,d.jsx)("strong",{children:A}),(0,d.jsx)("span",{className:"pill",children:B})]}),(0,d.jsx)("div",{className:"cardMeta",children:C})]}),(0,d.jsx)("div",{className:"timeline",children:m.length?m.map(a=>(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:a.name}),(0,d.jsx)("span",{className:"subtle",children:a.type??"custom"})]},a.id)):(0,d.jsx)("div",{className:"panelNote",children:"运行态还没有部门数据。"})})]})]}),(0,d.jsxs)("div",{className:"panel",children:[(0,d.jsx)("h3",{className:"sectionTitle",children:"核心 Agent"}),(0,d.jsx)("div",{className:"nodeList",children:n.length?n.map(a=>(0,d.jsxs)("div",{className:"nodeCard",children:[(0,d.jsxs)("div",{className:"nodeHeader",children:[(0,d.jsx)("strong",{children:a.name}),(0,d.jsx)("span",{className:"tag",children:a.title})]}),(0,d.jsx)("div",{className:"nodeMeta",children:a.bio||a.personality||"已接入数据库"})]},a.id)):(0,d.jsx)("div",{className:"panelNote",children:"运行态还没有 Agent 数据。"})})]})]}),(0,d.jsxs)("section",{className:"grid two",children:[(0,d.jsxs)("div",{className:"panel",children:[(0,d.jsx)("h3",{className:"sectionTitle",children:"协作路线"}),(0,d.jsx)("div",{className:"timeline",children:(b?["数据库启动","组织同步","会话持久化","实时桥接"]:a.timeline).map((a,b)=>(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsxs)("span",{children:[String(b+1).padStart(2,"0")," \xb7 ",a]}),(0,d.jsx)("span",{className:"subtle",children:"ready"})]},a))})]}),(0,d.jsxs)("div",{className:"panel",children:[(0,d.jsx)("h3",{className:"sectionTitle",children:"交付预览"}),(0,d.jsxs)("div",{className:"footerGrid",children:[(0,d.jsxs)("div",{children:[(0,d.jsx)("div",{className:"cardMeta",children:"Playground Review"}),(0,d.jsxs)("div",{className:"cardHeader",children:[(0,d.jsx)("strong",{children:x.title}),(0,d.jsx)("span",{className:"chip",children:z.status})]}),(0,d.jsx)("div",{className:"panelNote",children:x.content})]}),(0,d.jsx)("div",{className:"docPreview",children:y})]})]})]})]})}function m({seed:a}){let{state:b,refresh:c}=j(),[g,h]=(0,e.useState)(""),[i,k]=(0,e.useState)(!1),[l,m]=(0,e.useState)(""),n=function(a,b){let c=b?.database?.conversations;return c?.length?c.find(a=>"private"!==a.type)??c[0]:a.conversations.find(a=>"private"!==a.type)??a.conversations[0]}(a,b),o=n?.id,p=b?b.database?.conversations??[]:a.conversations,q=o&&(!b||p.length>0)?function(a,b,c){let d=b?.database?.messagesByConversation?.[c];return b&&d?.length?d.map(a=>({id:a.id,content:a.content,senderId:a.senderId,createdAt:a.createdAt??"",mentions:function(a){if(Array.isArray(a))return a;if("string"!=typeof a||!a)return[];try{let b=JSON.parse(a);return Array.isArray(b)?b:[]}catch{return[]}}(a.mentions)})):a.messagesByConversation[c]??[]}(a,b,o):[],r=!!(b&&(!o||0===p.length));async function s(){let d=g.trim();if(!d)return;let e=f();if(e?.chat?.sendMessage){if(!o||b&&0===p.length)return void m("当前运行态没有可写入的会话");k(!0);try{await e.chat.sendMessage(o,{content:d,senderId:a.organization.agents[0]?.id,mentions:[]}),h(""),m("消息已写入 SQLite"),await c()}finally{k(!1)}}}return(0,d.jsxs)("section",{className:"grid two",children:[(0,d.jsxs)("div",{className:"panel",children:[(0,d.jsx)("h3",{className:"sectionTitle",children:"会话列表"}),(0,d.jsx)("div",{className:"conversationList",children:p.map(c=>(0,d.jsxs)("div",{className:`conversationItem ${o===c.id?"active":""}`,children:[(0,d.jsx)("div",{className:"conversationTitle",children:c.title}),(0,d.jsxs)("div",{className:"conversationMeta",children:[c.type," \xb7 ",b?"live":`${a.conversations.find(a=>a.id===c.id)?.participantIds?.length??0} participants`]})]},c.id))})]}),r?(0,d.jsxs)("div",{className:"panel",children:[(0,d.jsx)("h3",{className:"sectionTitle",children:"Active Thread"}),(0,d.jsx)("div",{className:"panelNote",children:"当前运行态没有会话记录，先检查 SQLite 是否已完成 bootstrap。"})]}):n?(0,d.jsxs)("div",{className:"sectionStack",children:[(0,d.jsxs)("div",{className:"threadCard",children:[(0,d.jsxs)("div",{className:"cardHeader",children:[(0,d.jsxs)("div",{children:[(0,d.jsx)("div",{className:"statusLabel",children:"Active Thread"}),(0,d.jsx)("h3",{className:"sectionTitle",style:{marginTop:8},children:n.title})]}),(0,d.jsx)("span",{className:"chip",children:n.type})]}),(0,d.jsx)("div",{className:"messageList",children:q.map(c=>{var e;let f=(e=c.senderId)?b?.database?.agents.find(a=>a.id===e)?.name??a.organization.agents.find(a=>a.id===e)?.name??"System":"System";return(0,d.jsxs)("div",{className:"messageCard",children:[(0,d.jsxs)("div",{className:"messageHeader",children:[(0,d.jsx)("div",{className:"messageAuthor",children:f}),(0,d.jsx)("div",{className:"messageMeta",children:c.createdAt||"live"})]}),(0,d.jsx)("div",{className:"messageBody",children:c.content}),!!c.mentions?.length&&(0,d.jsx)("div",{className:"messageMentions",children:c.mentions?.map(a=>(0,d.jsxs)("span",{className:"tag",children:["@",a.agentName]},a.agentId))})]},c.id)})}),(0,d.jsxs)("div",{className:"messageComposer",style:{marginTop:16},children:[(0,d.jsx)("textarea",{value:g,onChange:a=>h(a.target.value),onKeyDown:a=>{"Enter"!==a.key||a.shiftKey||(a.preventDefault(),s())},placeholder:"输入一条新消息，写入 SQLite",rows:3,style:{width:"100%",borderRadius:16,padding:12,background:"rgba(255,255,255,0.04)",color:"inherit",border:"1px solid rgba(148,163,184,0.2)"}}),(0,d.jsxs)("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",marginTop:10,gap:12},children:[(0,d.jsx)("div",{className:"subtle",children:l||"Enter 发送，Shift+Enter 换行"}),(0,d.jsx)("button",{type:"button",onClick:s,disabled:i,style:{borderRadius:999,padding:"10px 16px",background:"linear-gradient(135deg, #77c6ff, #7cf0c8)",border:0,color:"#06101c",fontWeight:700},children:i?"Sending...":"Send to DB"})]})]})]}),(0,d.jsxs)("div",{className:"panel",children:[(0,d.jsx)("h3",{className:"sectionTitle",children:"群聊规则"}),(0,d.jsxs)("div",{className:"timeline",children:[(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"@Agent 触发上下文"}),(0,d.jsx)("span",{className:"subtle",children:"mention"})]}),(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"讨论层负责拆解问题"}),(0,d.jsx)("span",{className:"subtle",children:"discussion"})]}),(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"执行层负责落地结果"}),(0,d.jsx)("span",{className:"subtle",children:"delivery"})]}),(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"CEO 负责最后审核"}),(0,d.jsx)("span",{className:"subtle",children:"review"})]})]})]})]}):null]})}function n({seed:a}){let{state:b}=j(),c=b?.database?.company??a.company,e=b?.database?.departments??a.organization.departments,f=b?.database?.agents??a.organization.agents;return(0,d.jsxs)("section",{className:"sectionStack",children:[(0,d.jsxs)("div",{className:"panel",children:[(0,d.jsxs)("div",{className:"cardHeader",children:[(0,d.jsxs)("div",{children:[(0,d.jsx)("p",{className:"eyebrow",children:"Organization"}),(0,d.jsx)("h3",{className:"sectionTitle",style:{marginTop:8},children:c.name})]}),(0,d.jsxs)("span",{className:"chip",children:[f.length," agents"]})]}),(0,d.jsx)("div",{className:"orgTree",children:e.map(a=>(0,d.jsxs)("div",{className:"nodeCard",children:[(0,d.jsxs)("div",{className:"nodeHeader",children:[(0,d.jsx)("strong",{children:a.name}),(0,d.jsx)("span",{className:"pill",style:{borderColor:a.color},children:a.type})]}),(0,d.jsx)("div",{className:"nodeMeta",children:a.description}),(0,d.jsx)("div",{className:"orgBranch",children:f.filter(b=>b.departmentId===a.id).map(a=>(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsxs)("div",{children:[(0,d.jsx)("div",{className:"conversationTitle",children:a.name}),(0,d.jsxs)("div",{className:"conversationMeta",children:[a.title," \xb7 ",a.status]})]}),(0,d.jsx)("span",{className:"subtle",children:1===a.isCEO?"CEO":"Member"})]},a.id))})]},a.id))})]}),(0,d.jsx)("div",{className:"grid three",children:f.map(a=>(0,d.jsxs)("div",{className:"panel",children:[(0,d.jsxs)("div",{className:"cardHeader",children:[(0,d.jsx)("strong",{children:a.name}),(0,d.jsx)("span",{className:"chip",children:a.title})]}),(0,d.jsx)("div",{className:"panelNote",children:a.bio||a.personality})]},a.id))})]})}function o({seed:a}){let{state:b,refresh:c}=j(),[g,h]=(0,e.useState)(()=>{var b;return{decision:(b=a.playgroundReview).status,comments:b.notes.join("；")}}),[i,k]=(0,e.useState)(!1),[l,m]=(0,e.useState)(""),n=(0,e.useRef)(!1),o=b?.database?.playgroundDocuments?.[0],p=o?.sourceConversationId??a.groupConversation.id,q=o?{...o,sourceConversationId:p}:a.playgroundDocument;function r(a){n.current=!0,h(b=>({...b,...a}))}async function s(){let a=f();if(a?.playground?.updateReview){k(!0);try{await a.playground.updateReview(q.id,{decision:g.decision,comments:g.comments}),await c(),n.current=!1,m("审核结果已同步到 SQLite 并刷新运行态")}catch(a){console.error("[CyberTeam] Failed to save playground review",a),m("审核结果保存失败，请检查运行态是否可写")}finally{k(!1)}}}return b?.database?.reviewRecords?.[0]?b.database.reviewRecords[0]:(a.playgroundReview.status,JSON.stringify(a.playgroundReview.notes)),(0,d.jsxs)("section",{className:"grid two",children:[(0,d.jsxs)("div",{className:"docCard",children:[(0,d.jsxs)("div",{className:"cardHeader",children:[(0,d.jsxs)("div",{children:[(0,d.jsx)("p",{className:"eyebrow",children:"Playground"}),(0,d.jsx)("h3",{className:"sectionTitle",style:{marginTop:8},children:q.title})]}),(0,d.jsx)("span",{className:"chip",children:q.version})]}),(0,d.jsxs)("div",{className:"tags",children:[(0,d.jsx)("span",{className:"tag",children:g.decision}),(0,d.jsx)("span",{className:"tag",children:q.type??"meeting notes"})]}),(0,d.jsx)("div",{className:"docPreview",style:{marginTop:16},children:q.content})]}),(0,d.jsxs)("div",{className:"sectionStack",children:[(0,d.jsxs)("div",{className:"panel",children:[(0,d.jsx)("h3",{className:"sectionTitle",children:"审核结果"}),(0,d.jsxs)("div",{className:"timeline",children:[(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"Review Status"}),(0,d.jsx)("span",{className:"subtle",children:g.decision})]}),(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"Notes"}),(0,d.jsx)("span",{className:"subtle",children:g.comments||"none"})]}),(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"Source Conversation"}),(0,d.jsx)("span",{className:"subtle",children:(p&&b?.database?.conversations?b.database.conversations.find(a=>a.id===p)??b.database.conversations[0]:!p?a.conversations[0]:a.conversations.find(a=>a.id===p)??a.conversations[0])?.title??"unknown"})]})]}),(0,d.jsxs)("div",{className:"sectionStack",style:{marginTop:16},children:[(0,d.jsx)("label",{className:"settingsTitle",children:"Decision"}),(0,d.jsx)("input",{value:g.decision,onChange:a=>r({decision:a.target.value}),style:{borderRadius:14,padding:10,background:"rgba(255,255,255,0.04)",color:"inherit",border:"1px solid rgba(148,163,184,0.2)"}}),(0,d.jsx)("label",{className:"settingsTitle",children:"Comments"}),(0,d.jsx)("textarea",{value:g.comments,onChange:a=>r({comments:a.target.value}),rows:4,style:{borderRadius:14,padding:10,background:"rgba(255,255,255,0.04)",color:"inherit",border:"1px solid rgba(148,163,184,0.2)"}}),(0,d.jsx)("div",{style:{display:"flex",justifyContent:"flex-end"},children:(0,d.jsx)("button",{type:"button",onClick:s,disabled:i,style:{borderRadius:999,padding:"10px 16px",background:"linear-gradient(135deg, #f7b267, #77c6ff)",border:0,color:"#06101c",fontWeight:700},children:i?"Saving...":"Save Review"})}),(0,d.jsx)("div",{className:"subtle",children:l||"保存后会自动刷新上方状态"})]})]}),(0,d.jsxs)("div",{className:"panel",children:[(0,d.jsx)("h3",{className:"sectionTitle",children:"输出历史"}),(0,d.jsxs)("div",{className:"timeline",children:[(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"v1 \xb7 draft"}),(0,d.jsx)("span",{className:"subtle",children:"生成纪要"})]}),(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"v1 \xb7 review"}),(0,d.jsx)("span",{className:"subtle",children:"CEO 审核"})]}),(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"v1 \xb7 export"}),(0,d.jsx)("span",{className:"subtle",children:"Markdown 导出"})]})]})]})]})]})}function p({seed:a}){let{state:b}=j(),c=b?.database?.skills??[],e=b?.database?.templates??[],f=b?.database?.agents?.length?b.database.agents:a.market.agents,g=c.length?c:a.market.skills,h=e.length?e:a.market.templates,i=f.map(a=>({id:a.id,name:a.name,description:"description"in a&&a.description?String(a.description):String("bio"in a&&a.bio?a.bio:"已写入运行态。")})),k=g.map(a=>({id:a.id,name:a.name,description:"description"in a&&a.description?String(a.description):"基础技能入口已预置。"})),l=h.map(a=>({id:a.id,name:a.name,description:"description"in a&&a.description?String(a.description):"模板系统的初始槽位。"}));return(0,d.jsxs)("section",{className:"sectionStack",children:[(0,d.jsxs)("div",{className:"panel",children:[(0,d.jsxs)("div",{className:"cardHeader",children:[(0,d.jsxs)("div",{children:[(0,d.jsx)("p",{className:"eyebrow",children:"Market"}),(0,d.jsx)("h3",{className:"sectionTitle",style:{marginTop:8},children:"Agent / Skill / Template"})]}),(0,d.jsx)("span",{className:"chip",children:b?"live":"bootstrap"})]}),(0,d.jsxs)("div",{className:"grid three",children:[i.map(a=>(0,d.jsxs)("div",{className:"marketCardItem",children:[(0,d.jsx)("div",{className:"marketTitle",children:a.name}),(0,d.jsx)("div",{className:"cardNote",children:a.description})]},a.id)),k.map(a=>(0,d.jsxs)("div",{className:"marketCardItem",children:[(0,d.jsx)("div",{className:"marketTitle",children:a.name}),(0,d.jsx)("div",{className:"cardNote",children:a.description})]},a.id)),l.map(a=>(0,d.jsxs)("div",{className:"marketCardItem",children:[(0,d.jsx)("div",{className:"marketTitle",children:a.name}),(0,d.jsx)("div",{className:"cardNote",children:a.description})]},a.id))]})]}),(0,d.jsxs)("div",{className:"panel",children:[(0,d.jsx)("h3",{className:"sectionTitle",children:"已加载 Skill"}),(0,d.jsx)("div",{className:"skillList",children:(c.length?c:a.skills).map(a=>(0,d.jsxs)("div",{className:"skillCard",children:[(0,d.jsxs)("div",{className:"cardHeader",children:[(0,d.jsx)("strong",{children:a.name}),(0,d.jsx)("span",{className:"tag",children:a.category??"loaded"})]}),(0,d.jsx)("div",{className:"cardNote",children:a.description??"技能已入库"})]},a.id))})]})]})}function q({seed:a}){let{state:b}=j(),c=k(b);return(0,d.jsxs)("section",{className:"sectionStack",children:[(0,d.jsxs)("div",{className:"panel",children:[(0,d.jsxs)("div",{className:"cardHeader",children:[(0,d.jsxs)("div",{children:[(0,d.jsx)("p",{className:"eyebrow",children:"Settings"}),(0,d.jsx)("h3",{className:"sectionTitle",style:{marginTop:8},children:"Local Runtime"})]}),(0,d.jsx)("span",{className:"chip",children:b?.claude.installed?"Claude detected":"Claude missing"})]}),(0,d.jsxs)("div",{className:"grid three",children:[(0,d.jsxs)("div",{className:"settingsCardItem",children:[(0,d.jsx)("div",{className:"settingsTitle",children:"Claude Code"}),(0,d.jsx)("div",{className:"cardNote",children:b?.claude.installed?"已检测到本地 Claude Code 可执行文件。":"当前机器还未检测到 Claude Code。"})]}),(0,d.jsxs)("div",{className:"settingsCardItem",children:[(0,d.jsx)("div",{className:"settingsTitle",children:"User Data"}),(0,d.jsx)("div",{className:"cardNote",children:b?.userData??"Electron 侧将使用本地 userData 目录作为未来持久化入口。"})]}),(0,d.jsxs)("div",{className:"settingsCardItem",children:[(0,d.jsx)("div",{className:"settingsTitle",children:"Theme"}),(0,d.jsx)("div",{className:"cardNote",children:"默认采用深色、玻璃质感与高对比信息面板。"})]})]})]}),(0,d.jsxs)("div",{className:"grid two",children:[(0,d.jsxs)("div",{className:"panel",children:[(0,d.jsx)("h3",{className:"sectionTitle",children:"系统信息"}),(0,d.jsxs)("div",{className:"timeline",children:[(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"Company"}),(0,d.jsx)("span",{className:"subtle",children:b?.database?.company?.name??a.company.name})]}),(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"Agents"}),(0,d.jsx)("span",{className:"subtle",children:c.agents??a.organization.agents.length})]}),(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"Conversations"}),(0,d.jsx)("span",{className:"subtle",children:c.conversations??a.conversations.length})]}),(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"Database"}),(0,d.jsx)("span",{className:"subtle",children:b?.database?.path??"SQLite 未加载"})]})]})]}),(0,d.jsxs)("div",{className:"panel",children:[(0,d.jsx)("h3",{className:"sectionTitle",children:"接入建议"}),(0,d.jsxs)("div",{className:"timeline",children:[(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"本地 Claude Code"}),(0,d.jsx)("span",{className:"subtle",children:"优先"})]}),(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"SQLite 持久化"}),(0,d.jsx)("span",{className:"subtle",children:"已启用"})]}),(0,d.jsxs)("div",{className:"timelineItem",children:[(0,d.jsx)("span",{children:"正式账号体系"}),(0,d.jsx)("span",{className:"subtle",children:"暂缓"})]})]})]})]})]})}},4926:(a,b,c)=>{Promise.resolve().then(c.t.bind(c,4496,23))},5211:(a,b,c)=>{Promise.resolve().then(c.t.bind(c,8365,23)),Promise.resolve().then(c.t.bind(c,4596,23)),Promise.resolve().then(c.t.bind(c,6186,23)),Promise.resolve().then(c.t.bind(c,7805,23)),Promise.resolve().then(c.t.bind(c,7561,23)),Promise.resolve().then(c.t.bind(c,7569,23)),Promise.resolve().then(c.t.bind(c,2747,23)),Promise.resolve().then(c.t.bind(c,6676,23)),Promise.resolve().then(c.bind(c,7225))},7498:(a,b,c)=>{"use strict";c.d(b,{$:()=>F});let d=0,e=0,f=0,g=0;function h(a,b="Member",c,d="company_1"){let e=new Date().toISOString();return g+=1,{id:`agent_${g}`,companyId:d,name:a,title:b,avatar:c,bio:"",personality:"calm, precise, helpful",status:"offline",isCEO:"ceo"===b.toLowerCase(),isActive:!0,createdAt:e,updatedAt:e}}let i=0;function j(a,b,c="company_1"){let d=new Date().toISOString();return i+=1,{id:`dept_${i}`,companyId:c,name:a,parentId:b,type:"custom",color:"#64748b",description:"",createdAt:d,updatedAt:d}}let k=0,l=[{id:"ceo-review",name:"CEO Review",description:"Output review and decision gate",category:"governance",prompt:"Review outputs with CEO-level scrutiny.",tools:["review","export"],version:"v1"},{id:"socratic-questioning",name:"Socratic Questioning",description:"Ask structured questions to clarify the problem",category:"reasoning",prompt:"Question assumptions and sharpen the problem definition.",tools:["reason","reflect"],version:"v1"}];function m(a,b,c=""){return{id:a,name:b,description:c,kind:"agent"}}var n,o=c(1421);let p=["claude","claude-code"];function q(){return null!==function(){for(let a of p)if(function(a){let b=(0,o.spawnSync)("which",[a],{encoding:"utf8"});return 0===b.status&&!!b.stdout.trim()}(a))return a;return null}()}let r=function(a,b,c){let d=new Date().toISOString();return f+=1,{id:`company_${f}`,name:a,avatar:"CT",description:c,theme:"midnight",version:"0.1.0",createdAt:d,updatedAt:d}}("CyberTeam",0,"本地 Claude Code 驱动的 AI 军团操作系统"),s=function(a){let b=j("CEO",void 0,a.id);b.type="review",b.color="#f59e0b",b.description="最终审核与决策中心";let c=j("讨论层",b.id,a.id);c.type="discussion",c.color="#3b82f6",c.description="用于发起讨论、汇总观点和形成方案";let d=j("执行层",b.id,a.id);d.type="execution",d.color="#10b981",d.description="用于拆解任务、推进执行和交付结果";let e=h("CEO","CEO",void 0,a.id);e.departmentId=b.id,e.status="online";let f=h("讨论主管","Discussion Lead",void 0,a.id);f.departmentId=c.id,f.bio="负责把模糊需求拆成可以讨论的问题";let g=h("执行主管","Delivery Lead",void 0,a.id);return g.departmentId=d.id,g.bio="负责把结论推进成可交付成果",{company:a,departments:[b,c,d],agents:[e,f,g]}}(r),t=function(){let a=[],b=new Map;return{createConversation(c,e,f=[]){let g=function(a,b,c=[]){let e=new Date().toISOString();return d+=1,{id:`conv_${d}`,title:a,type:b,participantIds:c,createdAt:e,updatedAt:e}}(c,e,f);return a.push(g),b.set(g.id,[]),g},listConversations:()=>a,sendMessage(a,c,d,f=[]){let g=function(a,b,c,d=[]){let f=new Date().toISOString();return e+=1,{id:`msg_${e}`,conversationId:a,content:b,senderId:c,mentions:d,status:"sent",createdAt:f}}(a,c,d,f??[]),h=b.get(a)??[];return h.push(g),b.set(a,h),g},getMessages:a=>b.get(a)??[],getConversation:b=>a.find(a=>a.id===b)}}(),[u,v,w]=s.agents,x=t.createConversation("CEO 私聊","private",[u.id]);t.sendMessage(x.id,"先判断问题的本质，再决定要不要拆给团队。",u.id),t.sendMessage(x.id,"确认 MVP 只保留最小闭环。",u.id);let y=t.createConversation("产品增长讨论群","group",[u.id,v.id,w.id]);t.sendMessage(y.id,"请围绕首屏、组织页、聊天页、设置页做一次苏格拉底式拆解。",u.id,[(n=v.id,{agentId:n,agentName:v.name,agentTitle:v.title})]),t.sendMessage(y.id,"先把信息流、组织感、交付感三件事做出来。",v.id),t.sendMessage(y.id,"执行上优先打通页面和种子数据，再补 IPC 与状态同步。",w.id);let z=t.createConversation("执行层部门群","department",[w.id]);t.sendMessage(z.id,"把占位符替换成能看见的页面与数据。",w.id);let A=function(a,b){return k+=1,{id:`playground_${k}`,title:a,content:`# ${a}

${b}`,type:"meeting notes",reviewStatus:"pending",version:"v1"}}("CyberTeam MVP 讨论纪要","首屏已经对齐公司、组织、聊天、Playground、设置与市场六个关键入口，正在收口为可运行桌面骨架。"),B=function(a){let b=!!a.content?.trim();return{status:b?"approved":"pending",notes:b?[]:["Document is empty"]}}(A),C=function(a){return`# ${a.title}

${a.content}`}(A),D=function(){let a=new Map;for(let b of l.slice())a.set(b.id,b);return a}(),E={agents:[m("agent-ceo","CEO","最终审核与方向决策"),m("agent-discussion","讨论主管","把问题推到可讨论的粒度"),m("agent-execution","执行主管","推动结论落地")],skills:[{id:"skill-ceo-review",name:"CEO Review"},{id:"skill-socratic",name:"Socratic Questioning"}],templates:[{id:"template-default",name:"Default Company"},{id:"template-sprint",name:"MVP Sprint"}]};function F(){let a=t.listConversations(),b=Object.fromEntries(a.map(a=>[a.id,t.getMessages(a.id)]));return{company:r,organization:s,conversations:a,messagesByConversation:b,privateConversation:x,groupConversation:y,departmentConversation:z,playgroundDocument:A,playgroundReview:B,playgroundExport:C,roadmap:[{id:"phase-0",sortOrder:0,name:"本地桌面骨架",status:"done",goal:"Electron + Next.js + SQLite 跑通",proof:"可以启动、浏览页面、读取种子态。",question:"如果没有桌面壳，这个系统还剩什么？"},{id:"phase-1",sortOrder:1,name:"运行时闭环",status:"done",goal:"IPC / preload / runtime snapshot 打通",proof:"前端已能读写 SQLite，页面能刷新实时状态。",question:"系统的单一事实源在哪里？"},{id:"phase-2",sortOrder:2,name:"组织与对话协作",status:"in-progress",goal:"把组织、聊天、Playground 串成工作流",proof:"组织页、聊天页、Playground 页已存在并写回数据库。",question:"任务从输入到审核，是否形成了闭环？"},{id:"phase-3",sortOrder:3,name:"质量门控",status:"next",goal:"把验证、审核、回滚和日志变成默认路径",proof:"当前已有构建验证，但还缺产品内质量仪表盘。",question:"当结果不可信时，系统如何自动拦下？"},{id:"phase-4",sortOrder:4,name:"能力扩展",status:"planned",goal:"把更多 Agent、Skill、模板接到市场层",proof:"市场页已显示种子资源，后续可继续增长。",question:"新能力是怎么被发现、分发和复用的？"}],skills:Array.from(D.values()),market:E,claudeInstalled:q(),metrics:[{label:"公司",value:"1",note:"已创建 CyberTeam 核心公司"},{label:"部门",value:String(s.departments.length),note:"CEO / 讨论层 / 执行层"},{label:"Agent",value:String(s.agents.length),note:"最小可协作阵列已就绪"},{label:"会话",value:String(a.length),note:"私聊 / 群聊 / 部门群"},{label:"Skill",value:String(D.size),note:"基础能力插件已加载"},{label:"Claude Code",value:q()?"已检测":"未检测",note:"本地执行引擎状态"}],timeline:["公司初始化","CEO 节点生成","讨论层与执行层展开","群聊与 Playground 已串联"]}}},7570:(a,b,c)=>{"use strict";c.r(b),c.d(b,{default:()=>h});var d=c(5939),e=c(3498),f=c.n(e);let g=[{href:"/",label:"Dashboard",note:"总览"},{href:"/chat",label:"Chat",note:"会话与群聊"},{href:"/organization",label:"Organization",note:"组织结构"},{href:"/playground",label:"Playground",note:"输出与审核"},{href:"/market",label:"Market",note:"Agent / Skill / 模板"},{href:"/settings",label:"Settings",note:"本地与接入"}];function h({children:a}){return(0,d.jsx)("html",{lang:"zh-CN",children:(0,d.jsxs)("body",{children:[(0,d.jsxs)("div",{className:"shell",children:[(0,d.jsxs)("aside",{className:"sidebar",children:[(0,d.jsxs)("div",{className:"brand",children:[(0,d.jsx)("div",{className:"brandMark",children:"CT"}),(0,d.jsxs)("div",{children:[(0,d.jsx)("div",{className:"brandTitle",children:"CyberTeam"}),(0,d.jsx)("div",{className:"brandSubtitle",children:"本地 AI 军团操作系统"})]})]}),(0,d.jsxs)("div",{className:"statusCard",children:[(0,d.jsx)("div",{className:"statusLabel",children:"Runtime"}),(0,d.jsx)("div",{className:"statusValue",children:"Electron + Next.js"}),(0,d.jsx)("div",{className:"statusMeta",children:"SQLite / Claude Code / macOS"})]}),(0,d.jsx)("nav",{className:"nav",children:g.map(a=>(0,d.jsxs)(f(),{className:"navItem",href:a.href,children:[(0,d.jsx)("span",{className:"navLabel",children:a.label}),(0,d.jsx)("span",{className:"navNote",children:a.note})]},a.href))})]}),(0,d.jsxs)("div",{className:"workspace",children:[(0,d.jsxs)("header",{className:"topbar",children:[(0,d.jsxs)("div",{children:[(0,d.jsx)("p",{className:"eyebrow",children:"Socratic by default"}),(0,d.jsx)("h1",{children:"让一个人拥有一整支 AI 公司。"})]}),(0,d.jsxs)("div",{className:"topbarPills",children:[(0,d.jsx)("span",{children:"Local First"}),(0,d.jsx)("span",{children:"Playground Ready"}),(0,d.jsx)("span",{children:"CEO Review"})]})]}),(0,d.jsx)("main",{className:"content",children:a})]})]}),(0,d.jsx)("style",{dangerouslySetInnerHTML:{__html:i}})]})})}let i=`
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
`},8259:(a,b,c)=>{Promise.resolve().then(c.t.bind(c,8671,23)),Promise.resolve().then(c.t.bind(c,6542,23)),Promise.resolve().then(c.t.bind(c,8248,23)),Promise.resolve().then(c.t.bind(c,9743,23)),Promise.resolve().then(c.t.bind(c,6231,23)),Promise.resolve().then(c.t.bind(c,959,23)),Promise.resolve().then(c.t.bind(c,2041,23)),Promise.resolve().then(c.t.bind(c,5094,23)),Promise.resolve().then(c.t.bind(c,7487,23))},8988:(a,b,c)=>{"use strict";c.d(b,{ChatView:()=>f,DashboardView:()=>e,MarketView:()=>i,OrganizationView:()=>g,PlaygroundView:()=>h,SettingsView:()=>j});var d=c(5459);let e=(0,d.registerClientReference)(function(){throw Error("Attempted to call DashboardView() from the server but DashboardView is on the client. It's not possible to invoke a client function from the server, it can only be rendered as a Component or passed to props of a Client Component.")},"/Users/cyberwiz/Documents/01_Project/00_cyberteam搭建/新项目/cyberteam-desktop/apps/renderer/src/components/hybrid-pages.tsx","DashboardView"),f=(0,d.registerClientReference)(function(){throw Error("Attempted to call ChatView() from the server but ChatView is on the client. It's not possible to invoke a client function from the server, it can only be rendered as a Component or passed to props of a Client Component.")},"/Users/cyberwiz/Documents/01_Project/00_cyberteam搭建/新项目/cyberteam-desktop/apps/renderer/src/components/hybrid-pages.tsx","ChatView"),g=(0,d.registerClientReference)(function(){throw Error("Attempted to call OrganizationView() from the server but OrganizationView is on the client. It's not possible to invoke a client function from the server, it can only be rendered as a Component or passed to props of a Client Component.")},"/Users/cyberwiz/Documents/01_Project/00_cyberteam搭建/新项目/cyberteam-desktop/apps/renderer/src/components/hybrid-pages.tsx","OrganizationView"),h=(0,d.registerClientReference)(function(){throw Error("Attempted to call PlaygroundView() from the server but PlaygroundView is on the client. It's not possible to invoke a client function from the server, it can only be rendered as a Component or passed to props of a Client Component.")},"/Users/cyberwiz/Documents/01_Project/00_cyberteam搭建/新项目/cyberteam-desktop/apps/renderer/src/components/hybrid-pages.tsx","PlaygroundView"),i=(0,d.registerClientReference)(function(){throw Error("Attempted to call MarketView() from the server but MarketView is on the client. It's not possible to invoke a client function from the server, it can only be rendered as a Component or passed to props of a Client Component.")},"/Users/cyberwiz/Documents/01_Project/00_cyberteam搭建/新项目/cyberteam-desktop/apps/renderer/src/components/hybrid-pages.tsx","MarketView"),j=(0,d.registerClientReference)(function(){throw Error("Attempted to call SettingsView() from the server but SettingsView is on the client. It's not possible to invoke a client function from the server, it can only be rendered as a Component or passed to props of a Client Component.")},"/Users/cyberwiz/Documents/01_Project/00_cyberteam搭建/新项目/cyberteam-desktop/apps/renderer/src/components/hybrid-pages.tsx","SettingsView")},9654:(a,b,c)=>{Promise.resolve().then(c.t.bind(c,3498,23))}};