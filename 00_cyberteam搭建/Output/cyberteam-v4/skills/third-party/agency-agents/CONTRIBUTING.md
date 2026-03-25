# Contributing to This Agency

First, thank you for considering contributing to this agency! It's people like you that make this collection of AI agents better for everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Agent Design Guidelines](#agent-design-guidelines)
- [Pull Request Process](#pull-request-process)
- [Style Guide](#style-guide)
- [Community](#community)

---

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code:

- **Respect**: Treat everyone with respect. Healthy debate is encouraged, but personal attacks are not tolerated.
- **Inclusive**: Welcome and support people of all backgrounds and identities.
- **Collaboration**: What we create together is better than what we create alone.
- **Professional**: Keep discussions focused on improving the agents and community.

---

## How Can I Contribute?

### 1. Create a New Agent

Have an idea for a specialized agent? Great! Here's how to add one:

1. **Fork the repository**
2. **Choose the appropriate category** (or propose a new category):
   - `engineering/` - Software development specialists
   - `design/` - UX/UI and creative specialists
   - `game-development/` - Game design and development specialists
   - `marketing/` - Growth and marketing specialists
   - `paid-media/` - Paid acquisition and media specialists
   - `product/` - Product management specialists
   - `project-management/` - PM and coordination specialists
   - `testing/` - QA and testing specialists
   - `support/` - Operations and support specialists
   - `spatial-computing/` - AR/VR/XR specialists
   - `specialized/` - Unique specialists that don't fit elsewhere

3. **Create your agent file following the template below**
4. **Test your agent in real scenarios**
5. **Submit a pull request for your agent**

### 2. Improve Existing Agents

Found a way to make an agent better? Contributions are welcome:

- Add real-world examples and use cases
- Enhance code examples with modern patterns
- Update workflows based on new best practices
- Add success metrics and benchmarks
- Fix typos, improve clarity, enhance documentation

### 3. Share Success Stories

Used these agents successfully? Share your story:

- Post in [GitHub Discussions](https://github.com/msitarzewski/agency-agents/discussions)
- Add case studies in the README
- Write a blog post and link to it
- Create video tutorials

### 4. Report Issues

Found a problem? Let us know:

- Check if an issue already exists
- Provide clear reproduction steps
- Include context about your use case
- If you have ideas, propose potential solutions

---

## Agent Design Guidelines

### Agent File Structure

Each agent should follow this structure:
```markdown
---
name: Agent Name
description: One-line description of the agent's specialty and focus
color: colorname or "#hexcode"
emoji: 🎯
vibe: One-line personality hook — what makes this agent memorable
services:                              # optional — only if the agent requires external services
  - name: Service Name
    url: https://service-url.com
    tier: free                         # free, freemium, or paid
---

# Agent Name

## Your Identity & Memory
- **Role**: Clear role description
- **Personality**: Personality traits and communication style
- **Memory**: What the agent remembers and learns
- **Experience**: Domain expertise and perspective

## Your Core Mission
- Primary responsibility 1 with clear deliverables
- Primary responsibility 2 with clear deliverables
- Primary responsibility 3 with clear deliverables
- **Default requirement**: Always-on best practices

## Critical Rules You Must Follow
Domain-specific rules and constraints that define the agent's approach

## Your Technical Deliverables
Concrete examples of what the agent produces:
- Code samples
- Templates
- Frameworks
- Documents

## Your Workflow Process
Step-by-step process the agent follows:
1. Phase 1: Discovery and research
2. Phase 2: Planning and strategy
3. Phase 3: Execution and implementation
4. Phase 4: Review and optimization

## Your Communication Style
- How the agent communicates
- Example phrases and patterns
- Tone and approach

## Learning & Memory
What the agent learns from:
- Successful patterns
- Failed approaches
- User feedback
- Domain evolution

## Your Success Metrics
Measurable outcomes:
- Quantitative metrics (with numbers)
- Qualitative indicators
- Performance benchmarks

## Advanced Capabilities
Advanced techniques and approaches the agent masters
```

### Agent Structure

Agent files are organized into two semantic groups that map to OpenClaw's workspace format and help other tools parse your agent:

#### Persona (Who the Agent Is)
- **Identity & Memory** — Role, personality, background
- **Communication Style** — Tone, voice, approach
- **Critical Rules** — Boundaries and constraints

#### Operations (What the Agent Does)
- **Core Mission** — Primary responsibilities
- **Technical Deliverables** — Concrete outputs and templates
- **Workflow** — Step-by-step methodology
- **Success Metrics** — Measurable outcomes
- **Advanced Capabilities** — Specialized techniques

No special formatting is required — just keep persona-relevant sections (Identity, Communication, Rules) grouped separately from operations sections (Mission, Deliverables, Workflow, Metrics). The `convert.sh` script uses these section headers to automatically split agents into tool-specific formats.

### Agent Design Principles

1. **Strong Personality**
   - Give the agent a unique voice and character
   - Not "I am a helpful assistant" — be specific and memorable
   - Example: "I default to finding 3-5 issues and require visual evidence" (Evidence Collector)

2. **Clear Deliverables**
   - Provide concrete code examples
   - Include templates and frameworks
   - Show real outputs, not vague descriptions

3. **Success Metrics**
   - Include specific, measurable metrics
   - Example: "Page load time under 3 seconds on 3G"
   - Example: "10,000+ composite karma across accounts"

4. **Verified Workflows**
   - Step-by-step processes
   - Methods tested in practice
   - Not theoretical — battle-tested

5. **Learning Memory**
   - What patterns does the agent recognize
   - How does it improve over time
   - What does it remember between sessions

### External Services

Agents may depend on external services (APIs, platforms, SaaS tools) that are essential to the agent's function. When they do:

1. **Declare dependencies in frontmatter using the `services` field**
2. **Agents must be standalone** — strip out API calls and there
   should still be a useful role, workflow, and expertise
3. **Don't duplicate vendor documentation** - reference them, don't copy them.
   Agent files should read like an agent, not a getting-started guide
4. **Prefer services with free tiers** so contributors can test the agent

Testing: *Is this agent for users or for vendors?*
Solving user problems with services belongs here. A quickstart guide for a service wearing an agent costume does not.

### Tool-Specific Compatibility

**Qwen Code Compatibility**: Agent bodies support `${variable}` templates for dynamic context (e.g., `${project_name}`, `${task_description}`). Qwen SubAgents use minimal frontmatter: only `name` and `description` are required; `color`, `emoji`, and `version` fields are omitted because Qwen does not use them.

### What Makes a Great Agent?

**Great agents have**:
- ✅ Narrow, deep specialization
- ✅ Unique personality and voice
- ✅ Concrete code/template examples
- ✅ Measurable success metrics
- ✅ Step-by-step workflows
- ✅ Real-world testing and iteration

**Avoid**:
- ❌ Generic "helpful assistant" personality
- ❌ Vague "I will help you..." descriptions
- ❌ No code examples or deliverables
- ❌ Too broad in scope (jack of all trades)
- ❌ Untested theoretical approaches

---

## Pull Request Process

### What Belongs in a PR (and What Doesn't)

The fastest path to merging a PR is **one markdown file** - a new or improved agent, that's where the sweet spot is.

For anything beyond that, here's how we keep things moving:

#### Always Welcome as PRs
- Adding a new agent (one ".md" file)
- Improving content, examples, or personality of existing agents
- Fixing typos or clarifying documentation

#### Start with a Discussion First
- New tools, build systems, or CI workflows
- Architecture changes (new directories, new scripts, site generators)
- Changes involving many files in the repository
- New integration formats or platforms

We love ambitious ideas - [Discussions](https://github.com/msitarzewski/agency-agents/discussions) just give the community a chance to agree on an approach before code is written. It saves everyone time, especially yours.

#### What We Will Always Close
- **Committed build outputs**: Generated files (`_site/`, compiled resources, converted agent files) should never be committed. Users run `convert.sh` locally; all output is gitignored.
- **PRs that bulk-modify existing agents without prior discussion** - even well-intentioned reformatting can create merge conflicts for other contributors.

### Before Submitting

1. **Test your agent**: Use it in real scenarios, iterate based on feedback
2. **Follow the template**: Match the structure of existing agents
3. **Add examples**: Include at least 2-3 code/template examples
4. **Define metrics**: Include specific, measurable success criteria
5. **Proofread**: Check for typos, formatting issues, clarity

### Submitting Your PR

1. **Fork** the repository
2. **Create a branch**: `git checkout -b add-agent-name`
3. **Make changes**: Add your agent file
4. **Commit**: `git commit -m "feat: add [agent name] specialist"`
5. **Push**: `git push origin add-agent-name`
6. **Open a Pull Request**:
   - Clear title: "Add [Agent Name] - [Category]"
   - Description of what the agent does
   - Why this agent is needed (use cases)
   - Any testing you've done

### PR Review Process

1. **Community review**: Other contributors can provide feedback
2. **Iterate**: Address feedback and make improvements
3. **Approval**: Maintainers will approve when ready
4. **Merge**: Your contribution becomes part of the agency!

### PR Template
```markdown
## Agent Information
**Agent Name**: [Name]
**Category**: [engineering/design/marketing/etc.]
**Specialty**: [One-line description]

## Motivation
[Why is this agent needed? What gap does it fill?]

## Testing
[How have you tested this agent? Real-world use cases?]

## Checklist
- [ ] Follows agent template structure
- [ ] Includes personality and voice
- [ ] Has concrete code/template examples
- [ ] Defines success metrics
- [ ] Includes step-by-step workflow
- [ ] Proofread and formatted correctly
- [ ] Tested in real scenarios
```

---

## Style Guide

### Writing Style

- **Specific**: "Reduce page load by 60%" not "make it faster"
- **Concrete**: "Create a React component with TypeScript" not "build UI"
- **Memorable**: Give agents personality, not generic corporate speak
- **Actionable**: Include real code, not pseudocode

### Formatting

- Use **Markdown formatting** consistently
- Include **emojis** in section headers (makes scanning easier)
- Use **code blocks** for all code examples with proper syntax highlighting
- Use **tables** to compare options or show metrics
- Use **bold** for emphasis, "code" for technical terms

### Code Examples
```markdown
## Example Code Block

```typescript
// Always include:
// 1. Language specification for syntax highlighting
// 2. Comments explaining key concepts
// 3. Real, runnable code (not pseudocode)
// 4. Modern best practices

interface AgentExample {
  name: string;
  specialty: string;
  deliverables: string[];
}
```
```

### Tone

- **Professional but approachable**: Not too formal or too casual
- **Confident but not arrogant**: "This is the best approach" not "maybe you could try..."
- **Helpful, but not hand-holding**: Assume competence, provide depth
- **Personality-driven**: Every agent should have a unique voice

---

## Recognition

Contributors who make significant contributions will be:

- Listed in the acknowledgments section of the README
- Highlighted in release notes
- Featured in "Agent of the Week" showcases when applicable
- Given credit in the agent file itself

---

## Got Questions?

- **General questions**: [GitHub Discussions](https://github.com/msitarzewski/agency-agents/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/msitarzewski/agency-agents/issues)
- **Feature requests**: [GitHub Issues](https://github.com/msitarzewski/agency-agents/issues)
- **Community chat**: [Join our discussions](https://github.com/msitarzewski/agency-agents/discussions)

---

## Resources

### For New Contributors

- [README.md](README.md) - Overview and agent directory
- [Example: Frontend Developer](engineering/engineering-frontend-developer.md) - Well-structured agent example
- [Example: Reddit Community Builder](marketing/marketing-reddit-community-builder.md) - Great personality example
- [Example: Whimsy Injector](design/design-whimsy-injector.md) - Creative specialist example

### For Agent Design

- Read existing agents for inspiration
- Study patterns that work
- Test your agents in real scenarios
- Iterate based on feedback

---

## Thank You!

Your contributions make this agency better for everyone. Whether you:

- Add a new agent
- Improve documentation
- Fix bugs
- Share success stories
- Help other contributors

**You're making a difference. Thank you!**

---

<div align="center">

**Have questions? Have ideas? Feedback?**

[Open an Issue](https://github.com/msitarzewski/agency-agents/issues) • [Start a Discussion](https://github.com/msitarzewski/agency-agents/discussions) • [Submit a PR](https://github.com/msitarzewski/agency-agents/pulls)

Made with by the community

</div>
