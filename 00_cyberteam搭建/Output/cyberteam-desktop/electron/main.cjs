var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));

// electron/main.ts
var electron2 = __toESM(require("electron"), 1);
var import_path3 = __toESM(require("path"), 1);
var import_fs3 = __toESM(require("fs"), 1);

// electron/database.ts
var import_path = __toESM(require("path"), 1);
var import_fs = __toESM(require("fs"), 1);
var import_electron = __toESM(require("electron"), 1);
var app = import_electron.default.app;
var JsonDatabase = class {
  dbPath;
  data;
  constructor(dbPath) {
    this.dbPath = dbPath;
    this.data = this.load();
  }
  load() {
    try {
      if (import_fs.default.existsSync(this.dbPath)) {
        const content = import_fs.default.readFileSync(this.dbPath, "utf-8");
        return JSON.parse(content);
      }
    } catch (err) {
      console.error("[DB] Load error:", err);
    }
    return this.getDefaultData();
  }
  save() {
    try {
      const dir = import_path.default.dirname(this.dbPath);
      if (!import_fs.default.existsSync(dir)) {
        import_fs.default.mkdirSync(dir, { recursive: true });
      }
      import_fs.default.writeFileSync(this.dbPath, JSON.stringify(this.data, null, 2));
    } catch (err) {
      console.error("[DB] Save error:", err);
    }
  }
  getDefaultData() {
    const now = (/* @__PURE__ */ new Date()).toISOString();
    return {
      providers: [
        {
          id: "provider_anthropic",
          name: "Anthropic",
          provider_type: "anthropic",
          protocol: "anthropic",
          base_url: "https://api.anthropic.com",
          api_key: "",
          is_active: 1,
          sort_order: 0,
          extra_env: "{}",
          headers_json: "{}",
          role_models_json: "{}",
          notes: "",
          created_at: now,
          updated_at: now
        },
        {
          id: "provider_minimax",
          name: "MiniMax",
          provider_type: "minimax",
          protocol: "openai-compatible",
          base_url: "https://api.minimax.chat/v",
          api_key: "",
          is_active: 0,
          sort_order: 1,
          extra_env: "{}",
          headers_json: "{}",
          role_models_json: "{}",
          notes: "",
          created_at: now,
          updated_at: now
        },
        {
          id: "provider_openrouter",
          name: "OpenRouter",
          provider_type: "openrouter",
          protocol: "openrouter",
          base_url: "https://openrouter.ai/api/v1",
          api_key: "",
          is_active: 0,
          sort_order: 2,
          extra_env: "{}",
          headers_json: "{}",
          role_models_json: "{}",
          notes: "",
          created_at: now,
          updated_at: now
        }
      ],
      sessions: [],
      messages: [],
      projects: [],
      departments: [
        { id: "dept_ceo", name: "CEO", icon: "\u{1F451}", parent_id: null, description: "", sort_order: 0, created_at: now },
        { id: "dept_coo", name: "COO", icon: "\u{1F3AF}", parent_id: null, description: "", sort_order: 1, created_at: now },
        { id: "dept_strategy", name: "\u6218\u7565\u90E8", icon: "\u{1F4CA}", parent_id: null, description: "", sort_order: 2, created_at: now },
        { id: "dept_product", name: "\u4EA7\u54C1\u90E8", icon: "\u{1F4BC}", parent_id: null, description: "", sort_order: 3, created_at: now },
        { id: "dept_eng", name: "\u7814\u53D1\u90E8", icon: "\u2699\uFE0F", parent_id: null, description: "", sort_order: 4, created_at: now },
        { id: "dept_design", name: "\u8BBE\u8BA1\u90E8", icon: "\u{1F3A8}", parent_id: null, description: "", sort_order: 5, created_at: now },
        { id: "dept_ops", name: "\u8FD0\u8425\u90E8", icon: "\u{1F680}", parent_id: null, description: "", sort_order: 6, created_at: now },
        { id: "dept_finance", name: "\u8D22\u52A1\u90E8", icon: "\u{1F4B0}", parent_id: null, description: "", sort_order: 7, created_at: now },
        { id: "dept_hr", name: "\u4EBA\u529B\u8D44\u6E90\u90E8", icon: "\u{1F465}", parent_id: null, description: "", sort_order: 8, created_at: now },
        { id: "dept_marketing", name: "\u5E02\u573A\u90E8", icon: "\u{1F4E2}", parent_id: null, description: "", sort_order: 9, created_at: now }
      ],
      agents: [
        {
          id: "agent_ceo",
          name: "CEO",
          avatar: "\u{1F451}",
          role: "ceo",
          department_id: "dept_ceo",
          description: "CyberTeam CEO\uFF0C\u8D1F\u8D23\u6218\u7565\u51B3\u7B56\u548C\u6574\u4F53\u534F\u8C03",
          soul_content: "",
          status: "online",
          capabilities: "[]",
          config: "{}",
          created_at: now
        }
      ],
      meetingMinutes: [],
      crewTemplates: [],
      skills: [
        {
          id: "skill_content_creation",
          name: "\u5185\u5BB9\u521B\u4F5C\u6CD5",
          icon: "\u270D\uFE0F",
          category: "content",
          description: "\u5C0F\u7EA2\u4E66/\u6296\u97F3\u591A\u5E73\u53F0\u5185\u5BB9\u521B\u4F5C\u6280\u80FD\uFF0C\u5305\u542B\u9009\u9898\u3001\u6587\u6848\u3001\u6392\u7248\u5168\u6D41\u7A0B",
          trigger: "\u5185\u5BB9\u521B\u4F5C / \u6587\u6848 / \u79CD\u8349\u7B14\u8BB0 / \u811A\u672C",
          workflow: "1.\u5206\u6790\u76EE\u6807\u7528\u6237\u753B\u50CF\n2.\u786E\u5B9A\u5185\u5BB9\u9009\u9898\u65B9\u5411\n3.\u64B0\u5199\u521D\u7A3F\n4.\u4F18\u5316\u6807\u9898\u548C\u5C01\u9762\n5.\u9002\u914D\u5E73\u53F0\u683C\u5F0F",
          agent_id: null,
          department_id: "dept_ops",
          is_preset: 1,
          config: "{}",
          created_at: now,
          updated_at: now
        },
        {
          id: "skill_data_analysis",
          name: "\u6570\u636E\u5206\u6790\u6CD5",
          icon: "\u{1F4CA}",
          category: "analytics",
          description: "\u7528\u6237\u884C\u4E3A\u5206\u6790\u3001AB\u6D4B\u8BD5\u3001\u8F6C\u5316\u6F0F\u6597\u7B49\u6570\u636E\u9A71\u52A8\u51B3\u7B56\u6280\u80FD",
          trigger: "\u6570\u636E\u5206\u6790 / AB\u6D4B\u8BD5 / \u8F6C\u5316\u7387 / \u7528\u6237\u884C\u4E3A",
          workflow: "1.\u660E\u786E\u5206\u6790\u76EE\u6807\n2.\u6570\u636E\u91C7\u96C6\u548C\u6E05\u6D17\n3.\u6784\u5EFA\u5206\u6790\u6A21\u578B\n4.\u53EF\u89C6\u5316\u5448\u73B0\n5.\u8F93\u51FA\u51B3\u7B56\u5EFA\u8BAE",
          agent_id: null,
          department_id: "dept_ops",
          is_preset: 1,
          config: "{}",
          created_at: now,
          updated_at: now
        },
        {
          id: "skill_seo_optimization",
          name: "SEO\u4F18\u5316\u6CD5",
          icon: "\u{1F50D}",
          category: "marketing",
          description: "\u641C\u7D22\u5F15\u64CE\u4F18\u5316\uFF0C\u5305\u542B\u5173\u952E\u8BCD\u7814\u7A76\u3001\u6280\u672FSEO\u3001\u5916\u94FE\u5EFA\u8BBE\u5168\u6D41\u7A0B",
          trigger: "SEO / \u5173\u952E\u8BCD / \u641C\u7D22\u6392\u540D / \u81EA\u7136\u6D41\u91CF",
          workflow: "1.\u5173\u952E\u8BCD\u7814\u7A76\u548C\u5206\u6790\n2.\u7AD9\u5185\u4F18\u5316\uFF08\u6807\u9898/\u63CF\u8FF0/\u7ED3\u6784\uFF09\n3.\u6280\u672FSEO\u68C0\u67E5\n4.\u5185\u5BB9\u4F18\u5316\n5.\u5916\u94FE\u5EFA\u8BBE\u7B56\u7565",
          agent_id: null,
          department_id: "dept_ops",
          is_preset: 1,
          config: "{}",
          created_at: now,
          updated_at: now
        },
        {
          id: "skill_strategy_planning",
          name: "\u6218\u7565\u89C4\u5212\u6CD5",
          icon: "\u{1F3AF}",
          category: "strategy",
          description: "SWOT\u5206\u6790\u3001OKR\u8BBE\u5B9A\u3001\u8DEF\u7EBF\u56FE\u89C4\u5212\u7B49\u6218\u7565\u89C4\u5212\u6280\u80FD",
          trigger: "\u6218\u7565\u89C4\u5212 / SWOT / OKR / \u8DEF\u7EBF\u56FE",
          workflow: "1.\u73B0\u72B6\u5206\u6790\uFF08SWOT\uFF09\n2.\u8BBE\u5B9A\u76EE\u6807\uFF08OKR\uFF09\n3.\u5236\u5B9A\u8DEF\u7EBF\u56FE\n4.\u8D44\u6E90\u914D\u7F6E\u8BA1\u5212\n5.\u98CE\u9669\u8BC4\u4F30\u548C\u9884\u6848",
          agent_id: null,
          department_id: "dept_ceo",
          is_preset: 1,
          config: "{}",
          created_at: now,
          updated_at: now
        },
        {
          id: "skill_product_design",
          name: "\u4EA7\u54C1\u8BBE\u8BA1\u6CD5",
          icon: "\u{1F4A1}",
          category: "product",
          description: "\u9700\u6C42\u5206\u6790\u3001PRD\u64B0\u5199\u3001\u539F\u578B\u8BBE\u8BA1\u7B49\u4EA7\u54C1\u6280\u80FD",
          trigger: "\u4EA7\u54C1 / PRD / \u9700\u6C42\u5206\u6790 / \u539F\u578B / \u7528\u6237\u4F53\u9A8C",
          workflow: "1.\u9700\u6C42\u6536\u96C6\u548C\u5206\u6790\n2.\u7528\u6237\u6545\u4E8B\u7F16\u5199\n3.PRD\u6587\u6863\u64B0\u5199\n4.\u539F\u578B\u8BBE\u8BA1\n5.\u8BC4\u5BA1\u548C\u8FED\u4EE3",
          agent_id: null,
          department_id: "dept_product",
          is_preset: 1,
          config: "{}",
          created_at: now,
          updated_at: now
        },
        {
          id: "skill_project_management",
          name: "\u9879\u76EE\u7BA1\u7406\u6CD5",
          icon: "\u{1F4CB}",
          category: "management",
          description: "\u9879\u76EE\u8FDB\u5EA6\u7BA1\u7406\u3001\u98CE\u9669\u8BC4\u4F30\u3001\u56E2\u961F\u534F\u8C03\u7B49\u9879\u76EE\u7BA1\u7406\u6280\u80FD",
          trigger: "\u9879\u76EE\u7BA1\u7406 / \u8FDB\u5EA6 / \u91CC\u7A0B\u7891 / \u98CE\u9669",
          workflow: "1.\u9879\u76EE\u8303\u56F4\u5B9A\u4E49\n2.\u4EFB\u52A1\u5206\u89E3\uFF08WBS\uFF09\n3.\u8FDB\u5EA6\u6392\u671F\n4.\u98CE\u9669\u8BC6\u522B\u548C\u7BA1\u7406\n5.\u590D\u76D8\u548C\u603B\u7ED3",
          agent_id: null,
          department_id: "dept_ceo",
          is_preset: 1,
          config: "{}",
          created_at: now,
          updated_at: now
        }
      ]
    };
  }
  // ==================== Provider ====================
  getProviders() {
    return this.data.providers.sort((a, b) => a.sort_order - b.sort_order);
  }
  getProvider(id) {
    return this.data.providers.find((p) => p.id === id);
  }
  createProvider(provider) {
    this.data.providers.push(provider);
    this.save();
    return provider;
  }
  updateProvider(id, data) {
    const index = this.data.providers.findIndex((p) => p.id === id);
    if (index !== -1) {
      this.data.providers[index] = { ...this.data.providers[index], ...data };
      this.save();
      return this.data.providers[index];
    }
    return void 0;
  }
  deleteProvider(id) {
    const index = this.data.providers.findIndex((p) => p.id === id);
    if (index !== -1) {
      this.data.providers.splice(index, 1);
      this.save();
      return true;
    }
    return false;
  }
  // ==================== Sessions ====================
  getSessions() {
    return this.data.sessions.sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    );
  }
  getSession(id) {
    return this.data.sessions.find((s) => s.id === id);
  }
  createSession(session) {
    this.data.sessions.push(session);
    this.save();
    return session;
  }
  updateSession(id, data) {
    const index = this.data.sessions.findIndex((s) => s.id === id);
    if (index !== -1) {
      this.data.sessions[index] = { ...this.data.sessions[index], ...data };
      this.save();
      return this.data.sessions[index];
    }
    return void 0;
  }
  deleteSession(id) {
    const index = this.data.sessions.findIndex((s) => s.id === id);
    if (index !== -1) {
      this.data.sessions.splice(index, 1);
      this.data.messages = this.data.messages.filter((m) => m.session_id !== id);
      this.save();
      return true;
    }
    return false;
  }
  // ==================== Messages ====================
  getMessages(sessionId) {
    return this.data.messages.filter((m) => m.session_id === sessionId).sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
  }
  createMessage(message) {
    this.data.messages.push(message);
    this.save();
    return message;
  }
  // ==================== Projects ====================
  getProjects() {
    return this.data.projects.sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    );
  }
  getProject(id) {
    return this.data.projects.find((p) => p.id === id);
  }
  createProject(project) {
    this.data.projects.push(project);
    this.save();
    return project;
  }
  updateProject(id, data) {
    const index = this.data.projects.findIndex((p) => p.id === id);
    if (index !== -1) {
      this.data.projects[index] = { ...this.data.projects[index], ...data };
      this.save();
      return this.data.projects[index];
    }
    return void 0;
  }
  deleteProject(id) {
    const index = this.data.projects.findIndex((p) => p.id === id);
    if (index !== -1) {
      this.data.projects.splice(index, 1);
      this.save();
      return true;
    }
    return false;
  }
  // ==================== Departments ====================
  getDepartments() {
    return this.data.departments.sort((a, b) => a.sort_order - b.sort_order);
  }
  getDepartment(id) {
    return this.data.departments.find((d) => d.id === id);
  }
  createDepartment(department) {
    this.data.departments.push(department);
    this.save();
    return department;
  }
  updateDepartment(id, data) {
    const index = this.data.departments.findIndex((d) => d.id === id);
    if (index !== -1) {
      this.data.departments[index] = { ...this.data.departments[index], ...data };
      this.save();
      return this.data.departments[index];
    }
    return void 0;
  }
  deleteDepartment(id) {
    const index = this.data.departments.findIndex((d) => d.id === id);
    if (index !== -1) {
      this.data.departments.splice(index, 1);
      this.save();
      return true;
    }
    return false;
  }
  // ==================== Agents ====================
  getAgents() {
    return this.data.agents.sort((a, b) => a.department_id.localeCompare(b.department_id));
  }
  getAgent(id) {
    return this.data.agents.find((a) => a.id === id);
  }
  createAgent(agent) {
    this.data.agents.push(agent);
    this.save();
    return agent;
  }
  updateAgent(id, data) {
    const index = this.data.agents.findIndex((a) => a.id === id);
    if (index !== -1) {
      this.data.agents[index] = { ...this.data.agents[index], ...data };
      this.save();
      return this.data.agents[index];
    }
    return void 0;
  }
  deleteAgent(id) {
    const index = this.data.agents.findIndex((a) => a.id === id);
    if (index !== -1) {
      this.data.agents.splice(index, 1);
      this.save();
      return true;
    }
    return false;
  }
  // ==================== Meeting Minutes ====================
  getMeetingMinutes(projectId) {
    let minutes = this.data.meetingMinutes;
    if (projectId) {
      minutes = minutes.filter((m) => m.project_id === projectId);
    }
    return minutes.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  }
  createMeetingMinutes(minutes) {
    this.data.meetingMinutes.push(minutes);
    this.save();
    return minutes;
  }
  updateMeetingMinutes(id, data) {
    const index = this.data.meetingMinutes.findIndex((m) => m.id === id);
    if (index !== -1) {
      this.data.meetingMinutes[index] = { ...this.data.meetingMinutes[index], ...data };
      this.save();
      return this.data.meetingMinutes[index];
    }
    return void 0;
  }
  // ==================== Crew Templates ====================
  getCrewTemplates() {
    return this.data.crewTemplates.sort((a, b) => b.is_preset - a.is_preset);
  }
  createCrewTemplate(template) {
    this.data.crewTemplates.push(template);
    this.save();
    return template;
  }
  deleteCrewTemplate(id) {
    const index = this.data.crewTemplates.findIndex((t) => t.id === id);
    if (index !== -1) {
      this.data.crewTemplates.splice(index, 1);
      this.save();
      return true;
    }
    return false;
  }
  // ==================== Skills ====================
  getSkills() {
    return this.data.skills || [];
  }
  getSkill(id) {
    return (this.data.skills || []).find((s) => s.id === id);
  }
  getSkillsByAgent(agentId) {
    return (this.data.skills || []).filter((s) => s.agent_id === agentId);
  }
  getSkillsByDepartment(deptId) {
    return (this.data.skills || []).filter((s) => s.department_id === deptId);
  }
  createSkill(skill) {
    if (!this.data.skills) this.data.skills = [];
    this.data.skills.push(skill);
    this.save();
    return skill;
  }
  updateSkill(id, data) {
    if (!this.data.skills) return void 0;
    const index = this.data.skills.findIndex((s) => s.id === id);
    if (index !== -1) {
      this.data.skills[index] = { ...this.data.skills[index], ...data };
      this.save();
      return this.data.skills[index];
    }
    return void 0;
  }
  deleteSkill(id) {
    if (!this.data.skills) return false;
    const index = this.data.skills.findIndex((s) => s.id === id);
    if (index !== -1) {
      this.data.skills.splice(index, 1);
      this.save();
      return true;
    }
    return false;
  }
};
var dbInstance = null;
function initDatabase() {
  const userDataPath = app.getPath("userData");
  const dbPath = import_path.default.join(userDataPath, "cyberteam-data.json");
  dbInstance = new JsonDatabase(dbPath);
  console.log("[DB] Database initialized:", dbPath);
  return dbInstance;
}
function getDb() {
  if (!dbInstance) {
    throw new Error("Database not initialized. Call initDatabase first.");
  }
  return dbInstance;
}

// electron/init-database.ts
var DEFAULT_DEPARTMENTS = [
  {
    id: "dept-management",
    name: "\u7BA1\u7406\u5C42",
    icon: "\u{1F451}",
    description: "\u516C\u53F8\u6700\u9AD8\u51B3\u7B56\u5C42\uFF0C\u8D1F\u8D23\u6218\u7565\u89C4\u5212\u548C\u8D44\u6E90\u5206\u914D",
    sort_order: 0
  },
  {
    id: "dept-growth",
    name: "\u589E\u957F\u90E8",
    icon: "\u{1F4C8}",
    description: "\u8D1F\u8D23\u7528\u6237\u589E\u957F\u3001\u5185\u5BB9\u8FD0\u8425\u3001SEO \u4F18\u5316",
    sort_order: 1
  },
  {
    id: "dept-product",
    name: "\u4EA7\u54C1\u90E8",
    icon: "\u{1F3AF}",
    description: "\u8D1F\u8D23\u4EA7\u54C1\u8BBE\u8BA1\u3001\u9700\u6C42\u5206\u6790\u3001\u7528\u6237\u4F53\u9A8C\u4F18\u5316",
    sort_order: 2
  },
  {
    id: "dept-tech",
    name: "\u6280\u672F\u90E8",
    icon: "\u{1F4BB}",
    description: "\u8D1F\u8D23\u6280\u672F\u67B6\u6784\u3001\u4EE3\u7801\u5F00\u53D1\u3001\u7CFB\u7EDF\u7A33\u5B9A\u6027",
    sort_order: 3
  },
  {
    id: "dept-ops",
    name: "\u8FD0\u8425\u90E8",
    icon: "\u{1F680}",
    description: "\u8D1F\u8D23\u65E5\u5E38\u8FD0\u8425\u3001\u7528\u6237\u7BA1\u7406\u3001\u6D3B\u52A8\u7B56\u5212",
    sort_order: 4
  },
  {
    id: "dept-qa",
    name: "\u8D28\u91CF\u90E8",
    icon: "\u{1F6E1}\uFE0F",
    description: "\u8D1F\u8D23\u8D28\u91CF\u4FDD\u969C\u3001\u6D4B\u8BD5\u7B56\u7565\u3001\u6D41\u7A0B\u6539\u8FDB",
    sort_order: 5
  }
];
var DEFAULT_AGENTS = [
  // 管理层
  {
    id: "agent-ceo",
    name: "CEO",
    avatar: "\u{1F451}",
    role: "ceo",
    department_id: "dept-management",
    description: "\u9996\u5E2D\u6267\u884C\u5B98\uFF0C\u8D1F\u8D23\u516C\u53F8\u6574\u4F53\u6218\u7565\u65B9\u5411\u548C\u91CD\u5927\u51B3\u7B56\u5BA1\u6279",
    soul_content: `\u4F60\u662F CyberTeam \u7684 CEO\u3002

## \u6838\u5FC3\u804C\u8D23
- \u6218\u7565\u89C4\u5212\uFF1A\u5236\u5B9A\u516C\u53F8\u957F\u671F\u6218\u7565\u65B9\u5411
- \u51B3\u7B56\u5BA1\u6279\uFF1A\u5BA1\u6279 COO \u63D0\u4EA4\u7684\u65B9\u6848
- \u98CE\u9669\u628A\u63A7\uFF1A\u8BC6\u522B\u91CD\u5927\u98CE\u9669\u5E76\u5236\u5B9A\u5E94\u5BF9\u63AA\u65BD
- \u8D44\u6E90\u5206\u914D\uFF1A\u5206\u914D\u6838\u5FC3\u8D44\u6E90\uFF08\u9884\u7B97\u3001\u4EBA\u529B\uFF09

## \u884C\u4E8B\u98CE\u683C
- \u7B80\u6D01\u76F4\u63A5\uFF0C\u4E0D\u5E9F\u8BDD
- \u6570\u636E\u9A71\u52A8\uFF0C\u51B3\u7B56\u679C\u65AD
- \u5173\u6CE8\u5168\u5C40\uFF0C\u4E0D\u9677\u5165\u7EC6\u8282

## CEO \u601D\u7EF4\u6A21\u578B
\u9047\u5230\u4EFB\u4F55\u95EE\u9898\uFF0C\u5148\u95EE\uFF1A
1. \u8FD9\u4E2A\u95EE\u9898\u5F71\u54CD\u7684\u662F\u5C40\u90E8\u8FD8\u662F\u5168\u5C40\uFF1F
2. \u6700\u574F\u60C5\u51B5\u662F\u4EC0\u4E48\uFF1F
3. \u6211\u4EEC\u6709\u591A\u5C11\u65F6\u95F4\uFF1F`,
    capabilities: JSON.stringify(["\u6218\u7565\u89C4\u5212", "\u51B3\u7B56\u5BA1\u6279", "\u98CE\u9669\u628A\u63A7", "\u8D44\u6E90\u5206\u914D"])
  },
  {
    id: "agent-coo",
    name: "COO",
    avatar: "\u26A1",
    role: "manager",
    department_id: "dept-management",
    description: "\u9996\u5E2D\u8FD0\u8425\u5B98\uFF0C\u8D1F\u8D23\u516C\u53F8\u65E5\u5E38\u8FD0\u8425\u548C\u8DE8\u90E8\u95E8\u534F\u8C03",
    soul_content: `\u4F60\u662F CyberTeam \u7684 COO\u3002

## \u6838\u5FC3\u804C\u8D23
- \u8FD0\u8425\u7BA1\u7406\uFF1A\u534F\u8C03\u5404\u90E8\u95E8\u65E5\u5E38\u8FD0\u4F5C
- \u7B56\u7565\u534F\u8C03\uFF1A\u5236\u5B9A\u8DE8\u90E8\u95E8\u534F\u4F5C\u7B56\u7565
- \u6D41\u7A0B\u4F18\u5316\uFF1A\u8BC6\u522B\u5E76\u6D88\u9664\u6548\u7387\u74F6\u9888
- \u6267\u884C\u76D1\u63A7\uFF1A\u786E\u4FDD\u6218\u7565\u843D\u5730

## \u884C\u4E8B\u98CE\u683C
- \u9AD8\u6548\u6267\u884C\uFF0C\u4F7F\u547D\u5FC5\u8FBE
- \u534F\u8C03\u5404\u65B9\uFF0C\u5316\u89E3\u51B2\u7A81
- \u5173\u6CE8\u7EC6\u8282\uFF0C\u6267\u884C\u5230\u4F4D

## COO \u5DE5\u4F5C\u6D41
1. \u63A5\u6536 CEO \u6218\u7565\u76EE\u6807
2. \u62C6\u89E3\u4E3A\u53EF\u6267\u884C\u4EFB\u52A1
3. \u5206\u914D\u7ED9\u5BF9\u5E94\u90E8\u95E8/Agent
4. \u76D1\u63A7\u6267\u884C\u8FDB\u5EA6\u548C\u8D28\u91CF
5. \u6C47\u603B\u7ED3\u679C\u5411 CEO \u6C47\u62A5`,
    capabilities: JSON.stringify(["\u8FD0\u8425\u7BA1\u7406", "\u7B56\u7565\u534F\u8C03", "\u8DE8\u90E8\u95E8\u534F\u4F5C", "\u6D41\u7A0B\u4F18\u5316"])
  },
  // 增长部
  {
    id: "agent-growth-director",
    name: "\u589E\u957F\u603B\u76D1",
    avatar: "\u{1F4C8}",
    role: "manager",
    department_id: "dept-growth",
    description: "\u589E\u957F\u90E8\u95E8\u8D1F\u8D23\u4EBA\uFF0C\u8D1F\u8D23\u7528\u6237\u589E\u957F\u548C\u5185\u5BB9\u8FD0\u8425\u7B56\u7565",
    soul_content: `\u4F60\u662F\u589E\u957F\u603B\u76D1\u3002

## \u6838\u5FC3\u804C\u8D23
- \u5236\u5B9A\u589E\u957F\u7B56\u7565\uFF1A\u5C0F\u7EA2\u4E66\u3001\u6296\u97F3\u3001SEO \u7B49\u6E20\u9053
- \u7528\u6237\u589E\u957F\uFF1A\u901A\u8FC7\u5185\u5BB9\u548C\u6D3B\u52A8\u5B9E\u73B0\u7528\u6237\u589E\u957F
- \u6570\u636E\u5206\u6790\uFF1A\u76D1\u6D4B\u589E\u957F\u6307\u6807\uFF0C\u4F18\u5316\u589E\u957F\u8DEF\u5F84
- \u56E2\u961F\u7BA1\u7406\uFF1A\u5E26\u9886\u589E\u957F\u56E2\u961F\u5B8C\u6210\u76EE\u6807

## \u4E13\u957F
- \u5C0F\u7EA2\u4E66\u8FD0\u8425\uFF1A\u7206\u6B3E\u5185\u5BB9\u7B56\u5212\u3001\u8FBE\u4EBA\u5408\u4F5C
- \u6296\u97F3\u8FD0\u8425\uFF1A\u77ED\u89C6\u9891\u811A\u672C\u3001\u76F4\u64AD\u5E26\u8D27
- SEO\uFF1A\u5173\u952E\u8BCD\u7814\u7A76\u3001\u6280\u672F\u4F18\u5316\u3001\u5916\u94FE\u5EFA\u8BBE

## \u589E\u957F\u601D\u7EF4
\u589E\u957F\u7684\u6838\u5FC3\u662F\u627E\u5230"\u589E\u957F\u98DE\u8F6E"\uFF1A
\u7528\u6237\u83B7\u53D6 \u2192 \u5185\u5BB9\u6D88\u8D39 \u2192 \u53E3\u7891\u4F20\u64AD \u2192 \u66F4\u591A\u7528\u6237`,
    capabilities: JSON.stringify(["\u5C0F\u7EA2\u4E66\u8FD0\u8425", "\u6296\u97F3\u8FD0\u8425", "SEO", "\u7528\u6237\u589E\u957F", "\u6570\u636E\u5206\u6790"])
  },
  {
    id: "agent-seo-specialist",
    name: "SEO \u4E13\u5458",
    avatar: "\u{1F50D}",
    role: "expert",
    department_id: "dept-growth",
    description: "\u589E\u957F\u90E8 SEO \u4E13\u5BB6\uFF0C\u8D1F\u8D23\u641C\u7D22\u5F15\u64CE\u4F18\u5316",
    soul_content: `\u4F60\u662F SEO \u4E13\u5BB6\u3002

## \u6838\u5FC3\u804C\u8D23
- \u5173\u952E\u8BCD\u7814\u7A76\uFF1A\u627E\u5230\u9AD8\u4EF7\u503C\u3001\u4F4E\u7ADE\u4E89\u5173\u952E\u8BCD
- \u6280\u672F SEO\uFF1A\u7F51\u7AD9\u7ED3\u6784\u3001\u901F\u5EA6\u3001\u79FB\u52A8\u7AEF\u4F18\u5316
- \u5185\u5BB9\u4F18\u5316\uFF1A\u6807\u9898\u3001\u63CF\u8FF0\u3001\u5185\u5BB9\u67B6\u6784
- \u5916\u94FE\u5EFA\u8BBE\uFF1A\u9AD8\u8D28\u91CF\u5916\u94FE\u83B7\u53D6\u7B56\u7565

## SEO \u601D\u7EF4
\u641C\u7D22\u5F15\u64CE\u4F18\u5316\u7684\u672C\u8D28\u662F"\u8BA9\u4F18\u8D28\u5185\u5BB9\u88AB\u6B63\u786E\u7406\u89E3"\uFF1A
1. \u6280\u672F\u5C42\u9762\uFF1A\u8BA9\u641C\u7D22\u5F15\u64CE\u80FD\u6293\u53D6\u548C\u7406\u89E3
2. \u5185\u5BB9\u5C42\u9762\uFF1A\u63D0\u4F9B\u641C\u7D22\u8005\u9700\u8981\u7684\u5185\u5BB9
3. \u4F53\u9A8C\u5C42\u9762\uFF1A\u63D0\u4F9B\u826F\u597D\u7684\u8BBF\u95EE\u4F53\u9A8C`,
    capabilities: JSON.stringify(["\u5173\u952E\u8BCD\u7814\u7A76", "\u6280\u672FSEO", "\u5916\u94FE\u5EFA\u8BBE", "\u6570\u636E\u5206\u6790"])
  },
  {
    id: "agent-content-creator",
    name: "\u5185\u5BB9\u8FD0\u8425",
    avatar: "\u270D\uFE0F",
    role: "expert",
    department_id: "dept-growth",
    description: "\u589E\u957F\u90E8\u5185\u5BB9\u4E13\u5BB6\uFF0C\u8D1F\u8D23\u5404\u5E73\u53F0\u5185\u5BB9\u7B56\u5212",
    soul_content: `\u4F60\u662F\u5185\u5BB9\u8FD0\u8425\u4E13\u5BB6\u3002

## \u6838\u5FC3\u804C\u8D23
- \u5185\u5BB9\u7B56\u5212\uFF1A\u5404\u5E73\u53F0\u5185\u5BB9\u9009\u9898\u548C\u89C4\u5212
- \u6587\u6848\u64B0\u5199\uFF1A\u8425\u9500\u6587\u6848\u3001\u79CD\u8349\u7B14\u8BB0\u3001\u4EA7\u54C1\u4ECB\u7ECD
- \u70ED\u70B9\u8FFD\u8E2A\uFF1A\u53CA\u65F6\u6355\u6349\u5E73\u53F0\u70ED\u70B9\u501F\u52BF
- \u6570\u636E\u590D\u76D8\uFF1A\u5206\u6790\u5185\u5BB9\u6570\u636E\u4F18\u5316\u7B56\u7565

## \u5185\u5BB9\u65B9\u6CD5\u8BBA
\u597D\u5185\u5BB9 = \u4EF7\u503C \xD7 \u8868\u8FBE \xD7 \u65F6\u673A
- \u4EF7\u503C\uFF1A\u89E3\u51B3\u7528\u6237\u5B9E\u9645\u95EE\u9898
- \u8868\u8FBE\uFF1A\u8BA9\u7528\u6237\u613F\u610F\u8BFB\u3001\u8BFB\u5F97\u61C2
- \u65F6\u673A\uFF1A\u5728\u7528\u6237\u9700\u8981\u7684\u65F6\u5019\u51FA\u73B0`,
    capabilities: JSON.stringify(["\u5C0F\u7EA2\u4E66\u5185\u5BB9", "\u6296\u97F3\u811A\u672C", "\u6587\u6848\u64B0\u5199", "\u70ED\u70B9\u8FFD\u8E2A"])
  },
  // 产品部
  {
    id: "agent-product-director",
    name: "\u4EA7\u54C1\u603B\u76D1",
    avatar: "\u{1F3AF}",
    role: "manager",
    department_id: "dept-product",
    description: "\u4EA7\u54C1\u90E8\u95E8\u8D1F\u8D23\u4EBA\uFF0C\u8D1F\u8D23\u4EA7\u54C1\u89C4\u5212\u8BBE\u8BA1\u548C\u9700\u6C42\u7BA1\u7406",
    soul_content: `\u4F60\u662F\u4EA7\u54C1\u603B\u76D1\u3002

## \u6838\u5FC3\u804C\u8D23
- \u4EA7\u54C1\u89C4\u5212\uFF1A\u5236\u5B9A\u4EA7\u54C1\u8DEF\u7EBF\u56FE\u548C\u8FED\u4EE3\u8BA1\u5212
- \u9700\u6C42\u5206\u6790\uFF1A\u4ECE\u7528\u6237\u9700\u6C42\u5230\u4EA7\u54C1\u65B9\u6848
- \u4F53\u9A8C\u4F18\u5316\uFF1A\u6301\u7EED\u6539\u5584\u7528\u6237\u4F53\u9A8C
- \u8DE8\u90E8\u95E8\u534F\u4F5C\uFF1A\u534F\u8C03\u8BBE\u8BA1\u3001\u6280\u672F\u3001\u8FD0\u8425

## \u4EA7\u54C1\u601D\u7EF4
\u4EA7\u54C1\u8BBE\u8BA1\u7684\u6838\u5FC3\u662F"\u53D6\u820D"\uFF1A
- \u505A\u4EC0\u4E48\uFF1A\u805A\u7126\u6838\u5FC3\u4EF7\u503C\uFF0C\u4E0D\u8D2A\u591A
- \u4E0D\u505A\u4EC0\u4E48\uFF1A\u62D2\u7EDD\u975E\u6838\u5FC3\u9700\u6C42\uFF0C\u4FDD\u6301\u4E13\u6CE8
- \u600E\u4E48\u505A\uFF1A\u7B80\u5355\u53EF\u6267\u884C\uFF0C\u907F\u514D\u8FC7\u5EA6\u8BBE\u8BA1

## PRD \u6A21\u677F
1. \u80CC\u666F\uFF1A\u4E3A\u4EC0\u4E48\u505A\u8FD9\u4E2A\u95EE\u9898
2. \u76EE\u6807\uFF1A\u89E3\u51B3\u4EC0\u4E48\u95EE\u9898/\u8FBE\u5230\u4EC0\u4E48\u6548\u679C
3. \u65B9\u6848\uFF1A\u5177\u4F53\u600E\u4E48\u8BBE\u8BA1
4. \u6307\u6807\uFF1A\u5982\u4F55\u8861\u91CF\u6210\u529F
5. \u98CE\u9669\uFF1A\u53EF\u80FD\u7684\u98CE\u9669\u548C\u5E94\u5BF9`,
    capabilities: JSON.stringify(["\u4EA7\u54C1\u8BBE\u8BA1", "\u9700\u6C42\u5206\u6790", "\u7528\u6237\u4F53\u9A8C", "\u7ADE\u54C1\u5206\u6790", "PRD\u64B0\u5199"])
  },
  {
    id: "agent-ux-researcher",
    name: "UX \u7814\u7A76\u5458",
    avatar: "\u{1F52C}",
    role: "expert",
    department_id: "dept-product",
    description: "\u4EA7\u54C1\u90E8\u7528\u6237\u4F53\u9A8C\u4E13\u5BB6\uFF0C\u8D1F\u8D23\u7528\u6237\u7814\u7A76\u548C\u4F53\u9A8C\u4F18\u5316",
    soul_content: `\u4F60\u662F UX \u7814\u7A76\u4E13\u5BB6\u3002

## \u6838\u5FC3\u804C\u8D23
- \u7528\u6237\u8C03\u7814\uFF1A\u95EE\u5377\u3001\u8BBF\u8C08\u3001\u53EF\u7528\u6027\u6D4B\u8BD5
- \u6570\u636E\u5206\u6790\uFF1A\u7528\u6237\u884C\u4E3A\u6570\u636E\u6316\u6398
- \u4F53\u9A8C\u4F18\u5316\uFF1A\u57FA\u4E8E\u7814\u7A76\u7ED3\u679C\u7684\u4F18\u5316\u5EFA\u8BAE
- \u7ADE\u54C1\u5206\u6790\uFF1A\u7814\u7A76\u7ADE\u54C1\u7528\u6237\u4F53\u9A8C

## \u7814\u7A76\u65B9\u6CD5
- \u5B9A\u91CF\uFF1A\u6570\u636E\u5206\u6790\u3001A/B \u6D4B\u8BD5
- \u5B9A\u6027\uFF1A\u7528\u6237\u8BBF\u8C08\u3001\u53EF\u7528\u6027\u6D4B\u8BD5
- \u4E8C\u624B\u7814\u7A76\uFF1A\u884C\u4E1A\u62A5\u544A\u3001\u5B66\u672F\u8BBA\u6587`,
    capabilities: JSON.stringify(["\u7528\u6237\u8C03\u7814", "\u53EF\u7528\u6027\u6D4B\u8BD5", "\u6570\u636E\u5206\u6790", "\u7528\u6237\u753B\u50CF"])
  },
  // 技术部
  {
    id: "agent-cto",
    name: "CTO",
    avatar: "\u{1F4BB}",
    role: "ceo",
    department_id: "dept-tech",
    description: "\u9996\u5E2D\u6280\u672F\u5B98\uFF0C\u8D1F\u8D23\u6280\u672F\u65B9\u5411\u548C\u6280\u672F\u56E2\u961F\u7BA1\u7406",
    soul_content: `\u4F60\u662F CyberTeam \u7684 CTO\u3002

## \u6838\u5FC3\u804C\u8D23
- \u6280\u672F\u6218\u7565\uFF1A\u5236\u5B9A\u6280\u672F\u53D1\u5C55\u65B9\u5411
- \u67B6\u6784\u8BBE\u8BA1\uFF1A\u6838\u5FC3\u7CFB\u7EDF\u7684\u67B6\u6784\u51B3\u7B56
- \u6280\u672F\u9009\u578B\uFF1A\u8BC4\u4F30\u548C\u9009\u62E9\u6280\u672F\u6808
- \u56E2\u961F\u7BA1\u7406\uFF1A\u6280\u672F\u4EBA\u624D\u57F9\u517B\u548C\u56E2\u961F\u5EFA\u8BBE

## \u6280\u672F\u601D\u7EF4
\u6280\u672F\u670D\u52A1\u4E8E\u4E1A\u52A1\uFF0C\u4F46\u4E5F\u8981\u6709\u6280\u672F\u613F\u666F\uFF1A
- \u77ED\u671F\uFF1A\u5FEB\u901F\u4EA4\u4ED8\uFF0C\u89E3\u51B3\u5F53\u524D\u95EE\u9898
- \u4E2D\u671F\uFF1A\u67B6\u6784\u4F18\u5316\uFF0C\u63D0\u5347\u7814\u53D1\u6548\u7387
- \u957F\u671F\uFF1A\u6280\u672F\u50A8\u5907\uFF0C\u5EFA\u7ACB\u7ADE\u4E89\u58C1\u5792

## \u4EE3\u7801\u5BA1\u67E5\u6807\u51C6
1. \u6B63\u786E\u6027\uFF1A\u903B\u8F91\u6B63\u786E\uFF0C\u8FB9\u754C\u5904\u7406
2. \u53EF\u8BFB\u6027\uFF1A\u4EE3\u7801\u5373\u6587\u6863
3. \u6027\u80FD\uFF1A\u907F\u514D\u660E\u663E\u6027\u80FD\u95EE\u9898
4. \u5B89\u5168\uFF1A\u6CA1\u6709\u5B89\u5168\u6F0F\u6D1E`,
    capabilities: JSON.stringify(["\u67B6\u6784\u8BBE\u8BA1", "\u6280\u672F\u9009\u578B", "\u4EE3\u7801\u5BA1\u67E5", "\u6027\u80FD\u4F18\u5316"])
  },
  {
    id: "agent-frontend-dev",
    name: "\u524D\u7AEF\u5DE5\u7A0B\u5E08",
    avatar: "\u269B\uFE0F",
    role: "expert",
    department_id: "dept-tech",
    description: "\u6280\u672F\u90E8\u524D\u7AEF\u4E13\u5BB6\uFF0C\u8D1F\u8D23\u524D\u7AEF\u5F00\u53D1\u548C\u754C\u9762\u5B9E\u73B0",
    soul_content: `\u4F60\u662F\u524D\u7AEF\u5DE5\u7A0B\u5E08\u3002

## \u6838\u5FC3\u804C\u8D23
- \u754C\u9762\u5F00\u53D1\uFF1A\u9AD8\u8D28\u91CF\u7684 UI \u5B9E\u73B0
- \u6027\u80FD\u4F18\u5316\uFF1A\u9996\u5C4F\u901F\u5EA6\u3001\u4EA4\u4E92\u6D41\u7545\u5EA6
- \u7EC4\u4EF6\u590D\u7528\uFF1A\u5EFA\u7ACB\u53EF\u590D\u7528\u7EC4\u4EF6\u5E93
- \u6280\u672F\u8C03\u7814\uFF1A\u524D\u7AEF\u65B0\u6280\u672F\u8BC4\u4F30\u548C\u5E94\u7528

## \u524D\u7AEF\u539F\u5219
- \u6027\u80FD\u7B2C\u4E00\uFF1A\u9996\u5C4F\u52A0\u8F7D < 2s\uFF0C\u4EA4\u4E92\u54CD\u5E94 < 100ms
- \u4F53\u9A8C\u4F18\u5148\uFF1A\u6D41\u7545\u52A8\u753B\uFF0C\u81EA\u7136\u4EA4\u4E92
- \u4EE3\u7801\u8D28\u91CF\uFF1A\u7EC4\u4EF6\u5316\uFF0C\u6D4B\u8BD5\u8986\u76D6`,
    capabilities: JSON.stringify(["React", "TypeScript", "CSS", "\u6027\u80FD\u4F18\u5316", "\u54CD\u5E94\u5F0F\u8BBE\u8BA1"])
  },
  {
    id: "agent-backend-dev",
    name: "\u540E\u7AEF\u5DE5\u7A0B\u5E08",
    avatar: "\u{1F527}",
    role: "expert",
    department_id: "dept-tech",
    description: "\u6280\u672F\u90E8\u540E\u7AEF\u4E13\u5BB6\uFF0C\u8D1F\u8D23\u540E\u7AEF\u670D\u52A1\u548C\u6570\u636E\u67B6\u6784",
    soul_content: `\u4F60\u662F\u540E\u7AEF\u5DE5\u7A0B\u5E08\u3002

## \u6838\u5FC3\u804C\u8D23
- API \u5F00\u53D1\uFF1A\u6E05\u6670\u3001\u9AD8\u6548\u7684\u63A5\u53E3\u8BBE\u8BA1
- \u6570\u636E\u67B6\u6784\uFF1A\u6570\u636E\u5E93\u8BBE\u8BA1\u548C\u4F18\u5316
- \u7CFB\u7EDF\u7A33\u5B9A\u6027\uFF1A\u76D1\u63A7\u3001\u544A\u8B66\u3001\u5BB9\u707E
- \u6027\u80FD\u4F18\u5316\uFF1A\u63A5\u53E3\u54CD\u5E94\u3001\u541E\u5410\u91CF

## \u540E\u7AEF\u539F\u5219
- \u6570\u636E\u4E00\u81F4\u6027\uFF1A\u4E8B\u52A1\u3001\u5E42\u7B49\u6027
- \u53EF\u6269\u5C55\u6027\uFF1A\u6C34\u5E73\u6269\u5C55\u80FD\u529B
- \u53EF\u89C2\u6D4B\u6027\uFF1A\u65E5\u5FD7\u3001\u76D1\u63A7\u3001\u8FFD\u8E2A
- \u5B89\u5168\u6027\uFF1A\u8BA4\u8BC1\u3001\u6388\u6743\u3001\u9632\u62A4`,
    capabilities: JSON.stringify(["Node.js", "Python", "\u6570\u636E\u5E93\u8BBE\u8BA1", "API\u5F00\u53D1", "\u5FAE\u670D\u52A1"])
  },
  // 运营部
  {
    id: "agent-ops-director",
    name: "\u8FD0\u8425\u603B\u76D1",
    avatar: "\u{1F680}",
    role: "manager",
    department_id: "dept-ops",
    description: "\u8FD0\u8425\u90E8\u95E8\u8D1F\u8D23\u4EBA\uFF0C\u8D1F\u8D23\u7528\u6237\u8FD0\u8425\u548C\u6D3B\u52A8\u7B56\u5212",
    soul_content: `\u4F60\u662F\u8FD0\u8425\u603B\u76D1\u3002

## \u6838\u5FC3\u804C\u8D23
- \u6D3B\u52A8\u7B56\u5212\uFF1A\u5927\u578B\u8FD0\u8425\u6D3B\u52A8\u7684\u7B56\u5212\u548C\u6267\u884C
- \u7528\u6237\u8FD0\u8425\uFF1A\u7528\u6237\u5206\u5C42\u3001\u751F\u547D\u5468\u671F\u7684\u8FD0\u8425\u7B56\u7565
- \u6E20\u9053\u7BA1\u7406\uFF1A\u5404\u6E20\u9053\u8FD0\u8425\u7B56\u7565\u5236\u5B9A
- \u6570\u636E\u9A71\u52A8\uFF1A\u901A\u8FC7\u6570\u636E\u6307\u5BFC\u8FD0\u8425\u51B3\u7B56

## \u8FD0\u8425\u6307\u6807
- \u62C9\u65B0\uFF1ACAC\uFF08\u83B7\u5BA2\u6210\u672C\uFF09
- \u4FC3\u6D3B\uFF1ADAU/MAU\u3001\u7559\u5B58\u7387
- \u8F6C\u5316\uFF1A\u4ED8\u8D39\u7387\u3001GMV
- \u7559\u5B58\uFF1A\u6B21\u65E5/7\u65E5/30\u65E5\u7559\u5B58

## \u6D3B\u52A8\u7B56\u5212\u6D41\u7A0B
1. \u76EE\u6807\u8BBE\u5B9A\uFF08SMART\uFF09
2. \u65B9\u6848\u8BBE\u8BA1\uFF08\u9884\u7B97\u3001\u5956\u54C1\u3001\u89C4\u5219\uFF09
3. \u9884\u70ED\u63A8\u5E7F\uFF08\u9020\u52BF\uFF09
4. \u6267\u884C\u76D1\u63A7\uFF08\u5B9E\u65F6\u8C03\u6574\uFF09
5. \u590D\u76D8\u603B\u7ED3\uFF08\u6570\u636E\u5F52\u6863\uFF09`,
    capabilities: JSON.stringify(["\u6D3B\u52A8\u7B56\u5212", "\u7528\u6237\u8FD0\u8425", "\u6570\u636E\u5206\u6790", "\u6E20\u9053\u7BA1\u7406"])
  },
  {
    id: "agent-user-ops",
    name: "\u7528\u6237\u8FD0\u8425",
    avatar: "\u{1F465}",
    role: "expert",
    department_id: "dept-ops",
    description: "\u8FD0\u8425\u90E8\u7528\u6237\u8FD0\u8425\u4E13\u5BB6\uFF0C\u8D1F\u8D23\u7528\u6237\u5206\u5C42\u548C\u751F\u547D\u5468\u671F\u7BA1\u7406",
    soul_content: `\u4F60\u662F\u7528\u6237\u8FD0\u8425\u4E13\u5BB6\u3002

## \u6838\u5FC3\u804C\u8D23
- \u7528\u6237\u5206\u5C42\uFF1ARFM\u3001\u4EF7\u503C\u5206\u5C42\u3001\u884C\u4E3A\u5206\u5C42
- \u751F\u547D\u5468\u671F\u7BA1\u7406\uFF1A\u65B0\u7528\u6237\u2192\u6210\u957F\u2192\u6210\u719F\u2192\u6C89\u9ED8\u2192\u6D41\u5931
- \u793E\u7FA4\u8FD0\u8425\uFF1A\u5FAE\u4FE1\u7FA4\u3001QQ \u7FA4\u7B49\u79C1\u57DF\u8FD0\u8425
- \u8F6C\u5316\u4F18\u5316\uFF1AAARRR \u5404\u73AF\u8282\u8F6C\u5316\u7387\u63D0\u5347

## \u7528\u6237\u5206\u5C42\u6A21\u578B
| \u5C42\u7EA7 | \u5B9A\u4E49 | \u8FD0\u8425\u7B56\u7565 |
|------|------|---------|
| \u9AD8\u4EF7\u503C | GMV/\u4E92\u52A8\u9AD8 | VIP \u670D\u52A1\u3001\u4E13\u5C5E\u6743\u76CA |
| \u6210\u957F\u578B | \u6709\u6F5C\u529B | \u57F9\u517B\u3001\u6FC0\u52B1\u3001\u5347\u7EA7 |
| \u666E\u901A\u7528\u6237 | \u4E00\u822C\u6D3B\u8DC3 | \u4FDD\u6301\u6D3B\u8DC3\u3001\u63A8\u9001\u5185\u5BB9 |
| \u6C89\u9ED8\u7528\u6237 | \u4E45\u672A\u6D3B\u8DC3 | \u53EC\u56DE\u3001\u6D41\u5931\u9884\u8B66 |`,
    capabilities: JSON.stringify(["\u7528\u6237\u5206\u5C42", "\u751F\u547D\u5468\u671F\u7BA1\u7406", "\u793E\u7FA4\u8FD0\u8425", "\u8F6C\u5316\u4F18\u5316"])
  },
  // 质量部
  {
    id: "agent-qa-director",
    name: "\u8D28\u91CF\u603B\u76D1",
    avatar: "\u{1F6E1}\uFE0F",
    role: "manager",
    department_id: "dept-qa",
    description: "\u8D28\u91CF\u90E8\u95E8\u8D1F\u8D23\u4EBA\uFF0C\u8D1F\u8D23\u8D28\u91CF\u4FDD\u969C\u548C\u6D4B\u8BD5\u7B56\u7565",
    soul_content: `\u4F60\u662F\u8D28\u91CF\u603B\u76D1\u3002

## \u6838\u5FC3\u804C\u8D23
- \u8D28\u91CF\u4F53\u7CFB\uFF1A\u5EFA\u7ACB\u548C\u7EF4\u62A4\u8D28\u91CF\u6807\u51C6
- \u6D4B\u8BD5\u7B56\u7565\uFF1A\u5236\u5B9A\u6D4B\u8BD5\u8BA1\u5212\u548C\u8D28\u91CF\u95E8\u7981
- \u98CE\u9669\u8BC4\u4F30\uFF1A\u8BC6\u522B\u548C\u63A7\u5236\u9879\u76EE\u98CE\u9669
- \u6D41\u7A0B\u6539\u8FDB\uFF1A\u6301\u7EED\u4F18\u5316\u7814\u53D1\u6D41\u7A0B

## \u8D28\u91CF\u601D\u7EF4
\u8D28\u91CF\u662F"\u6784\u5EFA\u51FA\u6765\u7684"\uFF0C\u4E0D\u662F"\u6D4B\u8BD5\u51FA\u6765\u7684"\uFF1A
- \u6E90\u5934\u628A\u63A7\uFF1A\u9700\u6C42\u8BC4\u5BA1\u3001\u8BBE\u8BA1\u8BC4\u5BA1
- \u8FC7\u7A0B\u4FDD\u969C\uFF1A\u4EE3\u7801\u5BA1\u67E5\u3001\u81EA\u52A8\u5316\u6D4B\u8BD5
- \u7ED3\u679C\u9A8C\u8BC1\uFF1A\u591A\u8F6E\u6D4B\u8BD5\u3001\u7070\u5EA6\u53D1\u5E03

## \u6D4B\u8BD5\u91D1\u5B57\u5854
- \u5355\u5143\u6D4B\u8BD5\uFF1A\u8986\u76D6\u6838\u5FC3\u903B\u8F91\uFF0870%\uFF09
- \u96C6\u6210\u6D4B\u8BD5\uFF1A\u9A8C\u8BC1\u6A21\u5757\u95F4\u534F\u4F5C\uFF0820%\uFF09
- E2E \u6D4B\u8BD5\uFF1A\u9A8C\u8BC1\u6838\u5FC3\u6D41\u7A0B\uFF0810%\uFF09`,
    capabilities: JSON.stringify(["\u8D28\u91CF\u4F53\u7CFB", "\u6D4B\u8BD5\u7B56\u7565", "\u98CE\u9669\u8BC4\u4F30", "\u6D41\u7A0B\u6539\u8FDB"])
  }
];
var DEFAULT_CREW_TEMPLATES = [
  {
    id: "crew-growth",
    name: "\u{1F680} \u589E\u957F\u56E2\u961F",
    description: "\u4E13\u6CE8\u7528\u6237\u589E\u957F\uFF0C\u5305\u542B\u589E\u957F\u7B56\u7565\u3001\u5185\u5BB9\u8FD0\u8425\u3001SEO \u4F18\u5316\u5168\u94FE\u8DEF\u80FD\u529B",
    members: JSON.stringify([
      { agent_id: "agent-growth-director", role: "\u7EC4\u957F" },
      { agent_id: "agent-content-creator", role: "\u5185\u5BB9\u4E13\u5BB6" },
      { agent_id: "agent-seo-specialist", role: "SEO\u4E13\u5BB6" }
    ]),
    departments: JSON.stringify([{ department_id: "dept-growth" }]),
    is_preset: 1
  },
  {
    id: "crew-product",
    name: "\u{1F3AF} \u4EA7\u54C1\u56E2\u961F",
    description: "\u4EA7\u54C1\u8BBE\u8BA1\u56E2\u961F\uFF0C\u5305\u542B\u9700\u6C42\u5206\u6790\u3001\u7528\u6237\u4F53\u9A8C\u8BBE\u8BA1\u5168\u94FE\u8DEF",
    members: JSON.stringify([
      { agent_id: "agent-product-director", role: "\u4EA7\u54C1\u8D1F\u8D23\u4EBA" },
      { agent_id: "agent-ux-researcher", role: "UX\u4E13\u5BB6" }
    ]),
    departments: JSON.stringify([{ department_id: "dept-product" }]),
    is_preset: 1
  },
  {
    id: "crew-tech",
    name: "\u{1F4BB} \u6280\u672F\u56E2\u961F",
    description: "\u6280\u672F\u5F00\u53D1\u56E2\u961F\uFF0C\u5305\u542B\u524D\u7AEF\u3001\u540E\u7AEF\u3001\u67B6\u6784\u8BBE\u8BA1\u80FD\u529B",
    members: JSON.stringify([
      { agent_id: "agent-cto", role: "\u6280\u672F\u8D1F\u8D23\u4EBA" },
      { agent_id: "agent-frontend-dev", role: "\u524D\u7AEF\u4E13\u5BB6" },
      { agent_id: "agent-backend-dev", role: "\u540E\u7AEF\u4E13\u5BB6" }
    ]),
    departments: JSON.stringify([{ department_id: "dept-tech" }]),
    is_preset: 1
  },
  {
    id: "crew-ops",
    name: "\u{1F680} \u8FD0\u8425\u56E2\u961F",
    description: "\u8FD0\u8425\u6267\u884C\u56E2\u961F\uFF0C\u5305\u542B\u6D3B\u52A8\u7B56\u5212\u3001\u7528\u6237\u8FD0\u8425\u80FD\u529B",
    members: JSON.stringify([
      { agent_id: "agent-ops-director", role: "\u8FD0\u8425\u8D1F\u8D23\u4EBA" },
      { agent_id: "agent-user-ops", role: "\u7528\u6237\u8FD0\u8425\u4E13\u5BB6" }
    ]),
    departments: JSON.stringify([{ department_id: "dept-ops" }]),
    is_preset: 1
  },
  {
    id: "crew-full",
    name: "\u{1F3E2} \u5B8C\u6574\u516C\u53F8",
    description: "\u5B8C\u6574\u516C\u53F8\u67B6\u6784\uFF0C\u5305\u542B\u7BA1\u7406\u5C42 + \u6240\u6709\u90E8\u95E8\u6838\u5FC3\u6210\u5458",
    members: JSON.stringify([
      { agent_id: "agent-ceo", role: "CEO" },
      { agent_id: "agent-coo", role: "COO" },
      { agent_id: "agent-growth-director", role: "\u589E\u957F\u603B\u76D1" },
      { agent_id: "agent-product-director", role: "\u4EA7\u54C1\u603B\u76D1" },
      { agent_id: "agent-cto", role: "CTO" },
      { agent_id: "agent-ops-director", role: "\u8FD0\u8425\u603B\u76D1" },
      { agent_id: "agent-qa-director", role: "\u8D28\u91CF\u603B\u76D1" }
    ]),
    departments: JSON.stringify([
      { department_id: "dept-management" },
      { department_id: "dept-growth" },
      { department_id: "dept-product" },
      { department_id: "dept-tech" },
      { department_id: "dept-ops" },
      { department_id: "dept-qa" }
    ]),
    is_preset: 1
  }
];
function initDefaultData() {
  const db2 = getDb();
  if (!db2) {
    console.warn("[Init] Database not ready yet, skipping init");
    return;
  }
  try {
    const existingDepts = db2.getDepartments();
    if (existingDepts.length > 0) {
      console.log(`[Init] Database already has ${existingDepts.length} departments, skipping init`);
      return;
    }
    console.log("[Init] Seeding default data...");
    for (const dept of DEFAULT_DEPARTMENTS) {
      try {
        db2.createDepartment({
          ...dept,
          parent_id: null,
          created_at: (/* @__PURE__ */ new Date()).toISOString()
        });
      } catch (e) {
        console.warn(`[Init] Failed to create department ${dept.id}:`, e);
      }
    }
    console.log(`[Init] Created ${DEFAULT_DEPARTMENTS.length} departments`);
    for (const agent of DEFAULT_AGENTS) {
      try {
        db2.createAgent({
          ...agent,
          status: "online",
          config: "{}",
          created_at: (/* @__PURE__ */ new Date()).toISOString()
        });
      } catch (e) {
        console.warn(`[Init] Failed to create agent ${agent.id}:`, e);
      }
    }
    console.log(`[Init] Created ${DEFAULT_AGENTS.length} agents`);
    for (const crew of DEFAULT_CREW_TEMPLATES) {
      try {
        db2.createCrewTemplate({
          ...crew,
          created_at: (/* @__PURE__ */ new Date()).toISOString()
        });
      } catch (e) {
        console.warn(`[Init] Failed to create crew ${crew.id}:`, e);
      }
    }
    console.log(`[Init] Created ${DEFAULT_CREW_TEMPLATES.length} crew templates`);
    console.log("[Init] Default data seeded successfully!");
  } catch (err) {
    console.error("[Init] Failed to seed default data:", err);
  }
}

// electron/claude-client.ts
var import_child_process = require("child_process");
var import_path2 = __toESM(require("path"), 1);
var import_fs2 = __toESM(require("fs"), 1);
var import_os = __toESM(require("os"), 1);
var ClaudeClient = class {
  sessionProcess = null;
  sessionId = "";
  buffer = "";
  pendingRequests = /* @__PURE__ */ new Map();
  constructor() {
  }
  /**
   * Claude Code CLI 使用 --output-format stream-json
   * 输出格式：每行一个 JSON 对象
   * {"type":"version","version":1}
   * {"type":"assistant","text":"..."}
   * {"type":"result","result":{"type":"success","...","text":"..."}}
   * {"type":"error","error":{"type":"...","message":"..."}}
   */
  async sendMessageStream(message, options = {}, onChunk) {
    const { cwd = import_os.default.homedir(), sessionId: optSessionId, systemPrompt } = options;
    return new Promise(async (resolve, reject) => {
      try {
        const { process: proc, sessionId: newSessionId } = await this.spawnClaudeProcess(cwd, systemPrompt);
        this.sessionProcess = proc;
        this.sessionId = newSessionId;
        const requestId = `req_${Date.now()}`;
        let fullContent = "";
        this.pendingRequests.set(requestId, {
          resolve: (content) => resolve(content),
          reject,
          onChunk
        });
        proc.stdout.on("data", (data) => {
          this.buffer += data.toString();
          const lines = this.buffer.split("\n");
          this.buffer = lines.pop() || "";
          for (const line of lines) {
            if (!line.trim()) continue;
            try {
              const event = JSON.parse(line);
              this.handleStreamEvent(event, requestId, (text) => {
                fullContent += text;
                onChunk?.(text);
              });
            } catch {
              console.log("[ClaudeClient raw]", line);
            }
          }
        });
        proc.stderr.on("data", (data) => {
          console.log("[ClaudeClient stderr]", data.toString().trim());
        });
        proc.on("close", (code) => {
          console.log("[ClaudeClient closed]", code);
          if (code !== 0 && code !== null) {
            const pending = this.pendingRequests.get(requestId);
            if (pending) {
              pending.reject(new Error(`Claude CLI exited with code ${code}`));
              this.pendingRequests.delete(requestId);
            }
          }
        });
        proc.on("error", (err) => {
          console.error("[ClaudeClient error]", err);
          const pending = this.pendingRequests.get(requestId);
          if (pending) {
            pending.reject(err);
            this.pendingRequests.delete(requestId);
          }
        });
        setTimeout(() => {
          if (this.sessionProcess) {
            this.sessionProcess.stdin.write(message + "\n");
          }
        }, 2e3);
        setTimeout(() => {
          if (this.pendingRequests.has(requestId)) {
            this.pendingRequests.delete(requestId);
            this.close();
            reject(new Error("Claude request timeout (5 minutes)"));
          }
        }, 3e5);
      } catch (err) {
        reject(err);
      }
    });
  }
  async spawnClaudeProcess(cwd, systemPrompt) {
    const claudePath = this.findClaudeCLI();
    if (!claudePath) {
      throw new Error(
        "Claude Code CLI not found. Please install it:\n  npm install -g @anthropic-ai/claude-code\n  or: curl -sL https://claude.ai | sh"
      );
    }
    const sessionId = `ct_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const env = {
      ...process.env,
      CLAUDE_SESSION_ID: sessionId
    };
    if (systemPrompt) {
      env.CLAUDE_SYSTEM_PROMPT = systemPrompt;
    }
    const args = [
      "--dangerously-skip-permissions",
      "--output-format",
      "stream-json",
      "--print"
    ];
    const proc = (0, import_child_process.spawn)(claudePath, args, {
      cwd,
      env,
      stdio: ["pipe", "pipe", "pipe"]
    });
    return { process: proc, sessionId };
  }
  handleStreamEvent(event, requestId, onText) {
    const pending = this.pendingRequests.get(requestId);
    if (!pending) return;
    switch (event.type) {
      case "version":
        break;
      case "assistant":
        if (event.text) {
          onText(event.text);
        }
        break;
      case "result": {
        let content = "";
        const result = event.result;
        if (result && typeof result === "object") {
          if ("text" in result && typeof result.text === "string") {
            content = result.text;
          } else {
            content = JSON.stringify(result);
          }
        }
        pending.resolve(content);
        this.pendingRequests.delete(requestId);
        break;
      }
      case "error": {
        const errorMsg = typeof event.error === "string" ? event.error : event.error?.message || "Unknown error";
        pending.reject(new Error(errorMsg));
        this.pendingRequests.delete(requestId);
        break;
      }
      case "ping":
      case "ready":
        break;
      default:
        break;
    }
  }
  findClaudeCLI() {
    const possiblePaths = [
      "/opt/homebrew/bin/claude",
      "/usr/local/bin/claude",
      import_path2.default.join(import_os.default.homedir(), ".local/bin/claude"),
      import_path2.default.join(import_os.default.homedir(), ".claude", "bin", "claude"),
      "claude"
      // PATH 中
    ];
    for (const p of possiblePaths) {
      try {
        if (p === "claude") {
          const which = (0, import_child_process.spawn)("which", ["claude"], { shell: true });
          const output = which.stdout.read() || "";
          const status = which.exitCode;
          if (status === 0 && output.toString().trim()) {
            return output.toString().trim();
          }
        } else if (import_fs2.default.existsSync(p)) {
          return p;
        }
      } catch {
      }
    }
    return null;
  }
  close() {
    if (this.sessionProcess) {
      try {
        this.sessionProcess.stdin.write("");
        this.sessionProcess.kill("SIGTERM");
      } catch {
      }
      this.sessionProcess = null;
    }
    this.pendingRequests.clear();
    this.buffer = "";
  }
};

// electron/main.ts
var {
  app: app2,
  ipcMain,
  dialog,
  shell,
  Menu,
  nativeImage,
  BrowserWindow,
  Tray
} = electron2;
console.log("[PATH] __dirname =", __dirname);
console.log("[PATH] app.getAppPath() =", app2.getAppPath());
console.log("[PATH] process.cwd() =", process.cwd());
var isDev = process.env.NODE_ENV === "development" || !app2.isPackaged && !process.env.FORCE_DIST;
var mainWindow = null;
var tray = null;
var claudeClient = null;
var db = null;
async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1e3,
    minHeight: 700,
    title: "CyberTeam Desktop",
    backgroundColor: "#0a0a0f",
    show: false,
    webPreferences: {
      preload: import_path3.default.join(__dirname, "preload.cjs"),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false
    }
  });
  createMenu();
  createTray();
  if (process.env.FORCE_DIST) {
    const http = await import("http");
    const distPath = app2.getAppPath() + "/dist";
    const fsAsync = await import("fs/promises");
    try {
      await fsAsync.access(distPath + "/index.html");
    } catch {
      console.error("[Load] ERROR: dist/index.html not found at", distPath);
      console.error("[Load] Run: npm run build");
      app2.quit();
      return;
    }
    const mimeTypes = {
      ".html": "text/html; charset=utf-8",
      ".js": "text/javascript",
      ".css": "text/css",
      ".json": "application/json",
      ".png": "image/png",
      ".svg": "image/svg+xml",
      ".ico": "image/x-icon",
      ".woff2": "font/woff2"
    };
    const server = http.createServer(async (req, res) => {
      try {
        const urlPath = req.url?.split("?")[0] ?? "/index.html";
        const filePath2 = import_path3.default.join(distPath, urlPath === "/" ? "/index.html" : urlPath);
        const ext = import_path3.default.extname(filePath2);
        const content = await import_fs3.default.promises.readFile(filePath2);
        res.writeHead(200, { "Content-Type": mimeTypes[ext] || "application/octet-stream", "Cache-Control": "no-cache" });
        res.end(content);
      } catch {
        res.writeHead(404);
        res.end("Not found: " + req.url);
      }
    });
    await new Promise((resolve) => {
      server.listen(9999, "127.0.0.1", () => {
        console.log("[Load] \u2192 loadFile dist/ via HTTP server (port 9999)");
        resolve();
      });
    });
    await mainWindow.loadURL("http://127.0.0.1:9999/index.html");
  } else {
    console.log("[Load] \u2192 loadURL http://localhost:8888 (HTTP server mode)");
    await mainWindow.loadURL("http://localhost:8888");
  }
  mainWindow.webContents.openDevTools();
  mainWindow.on("ready-to-show", () => {
    mainWindow?.show();
  });
  mainWindow.on("closed", () => {
    mainWindow = null;
  });
  mainWindow.on("close", (e) => {
    if (process.platform === "darwin") {
      e.preventDefault();
      mainWindow?.hide();
    }
  });
}
function createMenu() {
  const template = [
    {
      label: "CyberTeam",
      submenu: [
        { label: "\u5173\u4E8E CyberTeam", role: "about" },
        { type: "separator" },
        { label: "\u504F\u597D\u8BBE\u7F6E...", accelerator: "Cmd+,", click: () => mainWindow?.webContents.send("open-settings") },
        { type: "separator" },
        { label: "\u9690\u85CF CyberTeam", accelerator: "Cmd+H", role: "hide" },
        { label: "\u9690\u85CF\u5176\u4ED6", accelerator: "Cmd+Alt+H", role: "hideOthers" },
        { label: "\u663E\u793A\u5168\u90E8", role: "unhide" },
        { type: "separator" },
        { label: "\u9000\u51FA CyberTeam", accelerator: "Cmd+Q", role: "quit" }
      ]
    },
    {
      label: "\u7F16\u8F91",
      submenu: [
        { label: "\u64A4\u9500", accelerator: "Cmd+Z", role: "undo" },
        { label: "\u91CD\u505A", accelerator: "Cmd+Shift+Z", role: "redo" },
        { type: "separator" },
        { label: "\u526A\u5207", accelerator: "Cmd+X", role: "cut" },
        { label: "\u590D\u5236", accelerator: "Cmd+C", role: "copy" },
        { label: "\u7C98\u8D34", accelerator: "Cmd+V", role: "paste" },
        { label: "\u5168\u9009", accelerator: "Cmd+A", role: "selectAll" }
      ]
    },
    {
      label: "\u89C6\u56FE",
      submenu: [
        { label: "\u91CD\u65B0\u52A0\u8F7D", accelerator: "Cmd+R", role: "reload" },
        { label: "\u5F3A\u5236\u91CD\u65B0\u52A0\u8F7D", accelerator: "Cmd+Shift+R", role: "forceReload" },
        { label: "\u5F00\u53D1\u8005\u5DE5\u5177", accelerator: "Alt+Cmd+I", role: "toggleDevTools" },
        { type: "separator" },
        { label: "\u653E\u5927", accelerator: "Cmd+Plus", role: "zoomIn" },
        { label: "\u7F29\u5C0F", accelerator: "Cmd+-", role: "zoomOut" },
        { label: "\u5B9E\u9645\u5927\u5C0F", accelerator: "Cmd+0", role: "resetZoom" },
        { type: "separator" },
        { label: "\u5207\u6362\u5168\u5C4F", accelerator: "Ctrl+Cmd+F", role: "togglefullscreen" }
      ]
    },
    {
      label: "\u7A97\u53E3",
      submenu: [
        { label: "\u6700\u5C0F\u5316", accelerator: "Cmd+M", role: "minimize" },
        { label: "\u7F29\u653E", role: "zoom" },
        { type: "separator" },
        { label: "\u5168\u90E8\u7F6E\u4E8E\u9876\u5C42", role: "front" }
      ]
    },
    {
      label: "\u5E2E\u52A9",
      submenu: [
        {
          label: "\u6587\u6863",
          click: () => shell.openExternal("https://github.com/heelaw/cyberteam-desktop")
        }
      ]
    }
  ];
  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}
function createTray() {
  let icon;
  try {
    const iconPath = import_path3.default.join(__dirname, "../src-tauri.tauri.bak/icons/32x32.png");
    if (import_fs3.default.existsSync(iconPath)) {
      icon = nativeImage.createFromPath(iconPath);
    } else {
      icon = nativeImage.createEmpty();
    }
  } catch {
    icon = nativeImage.createEmpty();
  }
  tray = new Tray(icon);
  tray.setToolTip("CyberTeam Desktop");
  const contextMenu = Menu.buildFromTemplate([
    { label: "\u663E\u793A CyberTeam", click: () => mainWindow?.show() },
    { type: "separator" },
    { label: "\u65B0\u5EFA\u5BF9\u8BDD", click: () => mainWindow?.webContents.send("new-session") },
    { label: "\u8BBE\u7F6E", click: () => mainWindow?.webContents.send("open-settings") },
    { type: "separator" },
    { label: "\u9000\u51FA", click: () => app2.quit() }
  ]);
  tray.setContextMenu(contextMenu);
  tray.on("click", () => mainWindow?.show());
}
function registerIpcHandlers() {
  ipcMain.handle("chat:sessions:list", async () => {
    return db?.getSessions() || [];
  });
  ipcMain.handle("chat:sessions:get", async (_, id) => {
    return db?.getSession(id) || null;
  });
  ipcMain.handle("chat:sessions:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    const now = (/* @__PURE__ */ new Date()).toISOString();
    const session = {
      id: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      title: data.title || "\u65B0\u4F1A\u8BDD",
      working_directory: data.working_directory || "",
      provider_id: data.provider_id || "",
      model: data.model || "",
      system_prompt: data.system_prompt || "",
      conversation_type: data.conversation_type || "single",
      department_id: data.department_id || null,
      project_id: data.project_id || null,
      review_status: "pending",
      review_notes: "",
      created_at: now,
      updated_at: now
    };
    return db.createSession(session);
  });
  ipcMain.handle("chat:sessions:update", async (_, id, data) => {
    if (!db) return null;
    return db.updateSession(id, data) || null;
  });
  ipcMain.handle("chat:sessions:delete", async (_, id) => {
    if (!db) return false;
    return db.deleteSession(id);
  });
  ipcMain.handle("chat:messages:list", async (_, sessionId) => {
    if (!db) return [];
    return db.getMessages(sessionId);
  });
  ipcMain.handle("chat:messages:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    const now = (/* @__PURE__ */ new Date()).toISOString();
    const message = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      session_id: data.session_id,
      role: data.role,
      content: data.content,
      sender_id: data.sender_id || "",
      sender_name: data.sender_name || "",
      sender_avatar: data.sender_avatar || "",
      metadata: data.metadata || "{}",
      token_usage: null,
      created_at: now
    };
    db.updateSession(data.session_id, { updated_at: now });
    return db.createMessage(message);
  });
  ipcMain.handle("claude:send", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    if (!claudeClient) {
      claudeClient = new ClaudeClient();
    }
    const now = (/* @__PURE__ */ new Date()).toISOString();
    db.createMessage({
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      session_id: data.session_id,
      role: "user",
      content: data.message,
      sender_id: "",
      sender_name: "",
      sender_avatar: "",
      metadata: "{}",
      token_usage: null,
      created_at: now
    });
    db.updateSession(data.session_id, { updated_at: now });
    const response = await claudeClient.sendMessage(data.message, {
      cwd: data.working_directory,
      providerId: data.provider_id,
      model: data.model,
      systemPrompt: data.system_prompt
    });
    const aiMsgId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    db.createMessage({
      id: aiMsgId,
      session_id: data.session_id,
      role: "assistant",
      content: response,
      sender_id: "",
      sender_name: "",
      sender_avatar: "",
      metadata: "{}",
      token_usage: null,
      created_at: (/* @__PURE__ */ new Date()).toISOString()
    });
    return { content: response, messageId: aiMsgId };
  });
  ipcMain.handle("claude:stream", async (event, data) => {
    if (!db) throw new Error("Database not initialized");
    const now = (/* @__PURE__ */ new Date()).toISOString();
    db.createMessage({
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      session_id: data.session_id,
      role: "user",
      content: data.message,
      sender_id: "",
      sender_name: "",
      sender_avatar: "",
      metadata: "{}",
      token_usage: null,
      created_at: now
    });
    db.updateSession(data.session_id, { updated_at: now });
    if (!claudeClient) {
      claudeClient = new ClaudeClient();
    }
    const aiMsgId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    let fullContent = "";
    await claudeClient.sendMessageStream(data.message, {
      cwd: data.working_directory,
      providerId: data.provider_id,
      model: data.model,
      systemPrompt: data.system_prompt
    }, (chunk) => {
      fullContent += chunk;
      event.sender.send("claude:stream:chunk", {
        messageId: aiMsgId,
        chunk,
        fullContent
      });
    });
    db.createMessage({
      id: aiMsgId,
      session_id: data.session_id,
      role: "assistant",
      content: fullContent,
      sender_id: "",
      sender_name: "",
      sender_avatar: "",
      metadata: "{}",
      token_usage: null,
      created_at: (/* @__PURE__ */ new Date()).toISOString()
    });
    return { messageId: aiMsgId };
  });
  const ALLOWED_ROOT = process.env.HOME || "/Users/cyberwiz";
  ipcMain.handle("files:browse", async (_, dirPath) => {
    try {
      const targetPath = import_path3.default.resolve(dirPath || ALLOWED_ROOT);
      if (!targetPath.startsWith(ALLOWED_ROOT)) {
        return { current: targetPath, parent: null, directories: [], error: "\u8BBF\u95EE\u88AB\u62D2\u7EDD\uFF1A\u53EA\u80FD\u5728\u4E3B\u76EE\u5F55\u5185\u6D4F\u89C8" };
      }
      if (!import_fs3.default.existsSync(targetPath)) {
        return { current: targetPath, parent: null, directories: [], error: "\u8DEF\u5F84\u4E0D\u5B58\u5728" };
      }
      const stat = import_fs3.default.statSync(targetPath);
      if (!stat.isDirectory()) {
        return { current: targetPath, parent: import_path3.default.dirname(targetPath), directories: [], error: "\u4E0D\u662F\u76EE\u5F55" };
      }
      const parent = import_path3.default.dirname(targetPath);
      const entries = import_fs3.default.readdirSync(targetPath, { withFileTypes: true });
      const directories = entries.filter((entry) => entry.isDirectory() && !entry.name.startsWith(".")).map((entry) => ({
        name: entry.name,
        path: import_path3.default.join(targetPath, entry.name)
      })).sort((a, b) => a.name.localeCompare(b.name));
      return { current: targetPath, parent, directories, error: null };
    } catch (err) {
      return { current: dirPath, parent: null, directories: [], error: String(err) };
    }
  });
  ipcMain.handle("files:validate-directory", async (_, dirPath) => {
    try {
      if (!dirPath || !import_fs3.default.existsSync(dirPath)) {
        return false;
      }
      return import_fs3.default.statSync(dirPath).isDirectory();
    } catch {
      return false;
    }
  });
  ipcMain.handle("files:select-directory", async () => {
    if (!mainWindow) return null;
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ["openDirectory"],
      title: "\u9009\u62E9\u5DE5\u4F5C\u76EE\u5F55"
    });
    if (result.canceled || result.filePaths.length === 0) {
      return null;
    }
    return result.filePaths[0];
  });
  ipcMain.handle("providers:list", async () => {
    return db?.getProviders() || [];
  });
  ipcMain.handle("providers:get", async (_, id) => {
    return db?.getProvider(id) || null;
  });
  ipcMain.handle("providers:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    const now = (/* @__PURE__ */ new Date()).toISOString();
    const provider = {
      id: `provider_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: data.name,
      provider_type: data.provider_type || "anthropic",
      protocol: data.protocol || "",
      base_url: data.base_url || "",
      api_key: data.api_key || "",
      is_active: data.is_active ?? 0,
      sort_order: data.sort_order ?? 0,
      extra_env: "{}",
      headers_json: "{}",
      role_models_json: "{}",
      notes: data.notes || "",
      created_at: now,
      updated_at: now
    };
    return db.createProvider(provider);
  });
  ipcMain.handle("providers:update", async (_, id, data) => {
    if (!db) return null;
    return db.updateProvider(id, data) || null;
  });
  ipcMain.handle("providers:delete", async (_, id) => {
    if (!db) return false;
    return db.deleteProvider(id);
  });
  ipcMain.handle("providers:test", async (_, id) => {
    if (!db) return { success: false, error: "Database not initialized" };
    const provider = db.getProvider(id);
    if (!provider) {
      return { success: false, error: "Provider not found" };
    }
    try {
      const response = await fetch(provider.base_url + "/v1/models", {
        headers: {
          "Authorization": `Bearer ${provider.api_key}`,
          "Content-Type": "application/json"
        }
      });
      if (response.ok) {
        return { success: true };
      } else {
        const error = await response.text();
        return { success: false, error: `HTTP ${response.status}: ${error}` };
      }
    } catch (err) {
      return { success: false, error: String(err) };
    }
  });
  ipcMain.handle("projects:list", async () => {
    return db?.getProjects() || [];
  });
  ipcMain.handle("projects:get", async (_, id) => {
    return db?.getProject(id) || null;
  });
  ipcMain.handle("projects:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    const now = (/* @__PURE__ */ new Date()).toISOString();
    return db.createProject({
      id: `project_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: data.name,
      description: data.description || "",
      working_directory: data.working_directory || "",
      department_id: data.department_id || null,
      status: "active",
      created_at: now,
      updated_at: now
    });
  });
  ipcMain.handle("projects:update", async (_, id, data) => {
    if (!db) return null;
    return db.updateProject(id, data) || null;
  });
  ipcMain.handle("projects:delete", async (_, id) => {
    if (!db) return false;
    return db.deleteProject(id);
  });
  ipcMain.handle("departments:list", async () => {
    return db?.getDepartments() || [];
  });
  ipcMain.handle("departments:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    return db.createDepartment({
      id: `dept_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: data.name,
      icon: data.icon || "",
      parent_id: data.parent_id || null,
      description: data.description || "",
      sort_order: data.sort_order ?? 0,
      created_at: (/* @__PURE__ */ new Date()).toISOString()
    });
  });
  ipcMain.handle("departments:update", async (_, id, data) => {
    if (!db) return null;
    return db.updateDepartment(id, data) || null;
  });
  ipcMain.handle("departments:delete", async (_, id) => {
    if (!db) return false;
    return db.deleteDepartment(id);
  });
  ipcMain.handle("agents:list", async () => {
    return db?.getAgents() || [];
  });
  ipcMain.handle("agents:get", async (_, id) => {
    return db?.getAgent(id) || null;
  });
  ipcMain.handle("agents:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    return db.createAgent({
      id: `agent_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: data.name,
      avatar: data.avatar || "",
      role: data.role || "expert",
      department_id: data.department_id,
      description: data.description || "",
      soul_content: data.soul_content || "",
      status: "offline",
      capabilities: data.capabilities || "[]",
      config: data.config || "{}",
      created_at: (/* @__PURE__ */ new Date()).toISOString()
    });
  });
  ipcMain.handle("agents:update", async (_, id, data) => {
    if (!db) return null;
    return db.updateAgent(id, data) || null;
  });
  ipcMain.handle("agents:delete", async (_, id) => {
    if (!db) return false;
    return db.deleteAgent(id);
  });
  ipcMain.handle("meeting-minutes:list", async (_, projectId) => {
    return db?.getMeetingMinutes(projectId) || [];
  });
  ipcMain.handle("meeting-minutes:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    return db.createMeetingMinutes({
      id: `minutes_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      project_id: data.project_id,
      meeting_type: data.meeting_type,
      title: data.title,
      content: data.content || "",
      review_status: "pending",
      attachments: data.attachments || "[]",
      created_at: (/* @__PURE__ */ new Date()).toISOString()
    });
  });
  ipcMain.handle("meeting-minutes:update", async (_, id, data) => {
    if (!db) return null;
    return db.updateMeetingMinutes(id, data) || null;
  });
  ipcMain.handle("crew-templates:list", async () => {
    return db?.getCrewTemplates() || [];
  });
  ipcMain.handle("crew-templates:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    return db.createCrewTemplate({
      id: `crew_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: data.name,
      description: data.description || "",
      members: data.members || "[]",
      departments: data.departments || "[]",
      is_preset: data.is_preset ?? 0,
      created_at: (/* @__PURE__ */ new Date()).toISOString()
    });
  });
  ipcMain.handle("crew-templates:delete", async (_, id) => {
    if (!db) return false;
    return db.deleteCrewTemplate(id);
  });
  ipcMain.handle("system:get-home-directory", async () => {
    return process.env.HOME || "/Users/cyberwiz";
  });
  ipcMain.handle("system:open-external", async (_, url) => {
    try {
      const parsed = new URL(url);
      if (!["http:", "https:"].includes(parsed.protocol)) {
        return false;
      }
      await shell.openExternal(url);
      return true;
    } catch {
      return false;
    }
  });
  ipcMain.handle("system:show-item-in-folder", async (_, filePath) => {
    const resolvedPath = import_path3.default.resolve(filePath);
    if (!resolvedPath.startsWith(ALLOWED_ROOT)) {
      return false;
    }
    shell.showItemInFolder(filePath);
    return true;
  });
  ipcMain.handle("skills:list", async () => {
    return db?.getSkills() || [];
  });
  ipcMain.handle("skills:get", async (_, id) => {
    return db?.getSkill(id) || null;
  });
  ipcMain.handle("skills:by-agent", async (_, agentId) => {
    return db?.getSkillsByAgent(agentId) || [];
  });
  ipcMain.handle("skills:by-department", async (_, deptId) => {
    return db?.getSkillsByDepartment(deptId) || [];
  });
  ipcMain.handle("skills:create", async (_, data) => {
    if (!db) throw new Error("Database not initialized");
    const now = (/* @__PURE__ */ new Date()).toISOString();
    return db.createSkill({
      id: `skill_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: data.name,
      icon: data.icon || "\u26A1",
      category: data.category || "custom",
      description: data.description || "",
      trigger: data.trigger || "",
      workflow: data.workflow || "",
      agent_id: data.agent_id || null,
      department_id: data.department_id || null,
      is_preset: data.is_preset ?? 0,
      config: data.config || "{}",
      created_at: now,
      updated_at: now
    });
  });
  ipcMain.handle("skills:update", async (_, id, data) => {
    if (!db) return null;
    return db.updateSkill(id, { ...data, updated_at: (/* @__PURE__ */ new Date()).toISOString() }) || null;
  });
  ipcMain.handle("skills:delete", async (_, id) => {
    if (!db) return false;
    return db.deleteSkill(id);
  });
}
app2.whenReady().then(async () => {
  console.log("[Main] CyberTeam Desktop starting...");
  db = initDatabase();
  initDefaultData();
  registerIpcHandlers();
  await createWindow();
  console.log("[Main] CyberTeam Desktop ready");
});
app2.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app2.quit();
  }
});
app2.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  } else {
    mainWindow?.show();
  }
});
app2.on("before-quit", () => {
  if (claudeClient) {
    claudeClient.close();
  }
});
