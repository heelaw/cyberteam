name: Feature Request
description: 为 CyberTeam Desktop 提出新功能建议
title: "[Feature] "
labels: ["enhancement"]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        ## 💡 功能建议
        请描述你想要的功能，以及为什么你觉得这个功能有价值。

  - type: textarea
    id: problem
    attributes:
      label: 解决什么问题
      placeholder: 这个功能要解决什么问题？
    validations:
      required: true

  - type: textarea
    id: solution
    attributes:
      label: 期望的解决方案
      placeholder: 你期望这个功能如何工作？
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: 替代方案
      placeholder: 你考虑过其他替代方案吗？

  - type: textarea
    id: context
    attributes:
      label: 其他上下文
      placeholder: 其他信息、截图、设计稿等

  - type: checkboxes
    id: type
    attributes:
      label: 功能类型
      options:
        - label: 新功能 (feat)
          required: false
        - label: 功能改进 (improvement)
          required: false
        - label: UI 改进 (ui)
          required: false
