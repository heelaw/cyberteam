# CyberTeam 代码目录与文件清单

## 1. 根目录

```bash
cyberteam/
├── package.json
├── README.md
├── apps/
├── packages/
├── resources/
├── docs/
├── tests/
└── .gitignore
```

## 2. apps/desktop

```bash
apps/desktop/
├── src/
│   ├── main.ts
│   ├── preload.ts
│   ├── window.ts
│   ├── ipc/
│   │   └── handlers.ts
│   ├── app/
│   │   ├── lifecycle.ts
│   │   └── updater.ts
│   └── claude/
│       ├── detector.ts
│       └── bridge.ts
└── package.json
```

## 3. apps/renderer

```bash
apps/renderer/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── chat/
│   │   ├── organization/
│   │   ├── playground/
│   │   ├── market/
│   │   └── settings/
│   ├── components/
│   ├── hooks/
│   ├── stores/
│   └── styles/
└── package.json
```

## 4. packages/core

```bash
packages/core/
├── src/
│   ├── team/
│   │   ├── manager.ts
│   │   ├── lifecycle.ts
│   │   └── models.ts
│   ├── router/
│   │   └── message-router.ts
│   ├── session/
│   │   └── session-manager.ts
│   ├── review/
│   │   └── review-engine.ts
│   └── index.ts
└── package.json
```

## 5. packages/claude

```bash
packages/claude/
├── src/
│   ├── client.ts
│   ├── session.ts
│   ├── stream.ts
│   ├── detector.ts
│   └── index.ts
└── package.json
```

## 6. packages/team

```bash
packages/team/
├── src/
│   ├── company.ts
│   ├── department.ts
│   ├── agent.ts
│   ├── organization.ts
│   └── index.ts
└── package.json
```

## 7. packages/chat

```bash
packages/chat/
├── src/
│   ├── conversation.ts
│   ├── message.ts
│   ├── mention.ts
│   ├── group-chat.ts
│   └── index.ts
└── package.json
```

## 8. packages/skill

```bash
packages/skill/
├── src/
│   ├── skill.ts
│   ├── loader.ts
│   ├── registry.ts
│   ├── market.ts
│   └── index.ts
└── package.json
```

## 9. packages/playground

```bash
packages/playground/
├── src/
│   ├── generator.ts
│   ├── review.ts
│   ├── exporter.ts
│   └── index.ts
└── package.json
```

## 10. packages/market

```bash
packages/market/
├── src/
│   ├── agent-market.ts
│   ├── skill-market.ts
│   ├── template-market.ts
│   └── index.ts
└── package.json
```

## 11. packages/db

```bash
packages/db/
├── src/
│   ├── schema.ts
│   ├── client.ts
│   ├── repositories/
│   └── index.ts
└── package.json
```

## 12. packages/ui

```bash
packages/ui/
├── src/
│   ├── components/
│   ├── styles/
│   ├── theme/
│   └── index.ts
└── package.json
```

## 13. resources

```bash
resources/
├── templates/
├── avatars/
├── prompts/
└── icons/
```

## 14. docs

```bash
docs/
├── architecture.md
├── product.md
├── roadmap.md
└── decisions/
```

## 15. 第一版必须出现的文件

- apps/desktop/src/main.ts
- apps/desktop/src/preload.ts
- apps/renderer/src/app/layout.tsx
- packages/claude/src/client.ts
- packages/db/src/schema.ts
- packages/team/src/company.ts
- packages/chat/src/conversation.ts
- packages/playground/src/generator.ts
