# 技能健康仪表板

显示组合中所有技能的综合运行状况仪表板，包括成功率迷你图、失败模式聚类、待修改和版本历史记录。

## 实施

在仪表板模式下运行技能运行状况 CLI：```bash
ECC_ROOT="${CLAUDE_PLUGIN_ROOT:-$(node -e "var p=require('path'),f=require('fs'),h=require('os').homedir(),d=p.join(h,'.claude'),q=p.join('scripts','lib','utils.js');if(!f.existsSync(p.join(d,q))){try{var b=p.join(d,'plugins','cache','everything-claude-code');for(var o of f.readdirSync(b))for(var v of f.readdirSync(p.join(b,o))){var c=p.join(b,o,v);if(f.existsSync(p.join(c,q))){d=c;break}}}catch(x){}}console.log(d)")}"
node "$ECC_ROOT/scripts/skills-health.js" --dashboard
```仅适用于特定面板：```bash
ECC_ROOT="${CLAUDE_PLUGIN_ROOT:-$(node -e "var p=require('path'),f=require('fs'),h=require('os').homedir(),d=p.join(h,'.claude'),q=p.join('scripts','lib','utils.js');if(!f.existsSync(p.join(d,q))){try{var b=p.join(d,'plugins','cache','everything-claude-code');for(var o of f.readdirSync(b))for(var v of f.readdirSync(p.join(b,o))){var c=p.join(b,o,v);if(f.existsSync(p.join(c,q))){d=c;break}}}catch(x){}}console.log(d)")}"
node "$ECC_ROOT/scripts/skills-health.js" --dashboard --panel failures
```对于机器可读的输出：```bash
ECC_ROOT="${CLAUDE_PLUGIN_ROOT:-$(node -e "var p=require('path'),f=require('fs'),h=require('os').homedir(),d=p.join(h,'.claude'),q=p.join('scripts','lib','utils.js');if(!f.existsSync(p.join(d,q))){try{var b=p.join(d,'plugins','cache','everything-claude-code');for(var o of f.readdirSync(b))for(var v of f.readdirSync(p.join(b,o))){var c=p.join(b,o,v);if(f.existsSync(p.join(c,q))){d=c;break}}}catch(x){}}console.log(d)")}"
node "$ECC_ROOT/scripts/skills-health.js" --dashboard --json
```＃＃ 用法```
/skill-health                    # Full dashboard view
/skill-health --panel failures   # Only failure clustering panel
/skill-health --json             # Machine-readable JSON output
```## 做什么

1. 使用 --dashboard 标志运行 Skills-health.js 脚本
2.向用户显示输出
3. 如果有任何技能正在下降，请突出显示它们并建议运行 /evolve
4. 如果有待修改的内容，建议进行审查

## 面板

- **成功率 (30d)** — 迷你图显示每项技能的每日成功率
- **故障模式** — 使用水平条形图聚类故障原因
- **待定修正案** — 等待审查的修正案提案
- **版本历史记录** — 每个技能的版本快照时间线