var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
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
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// electron/database.ts
var database_exports = {};
__export(database_exports, {
  getDb: () => getDb,
  initDatabase: () => initDatabase
});
module.exports = __toCommonJS(database_exports);
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
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  getDb,
  initDatabase
});
