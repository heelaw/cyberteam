name: Bug Report
description: 报告一个 Bug 帮助我们改进
title: "[Bug] "
labels: ["bug"]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        ## 🐛 Bug 描述
        请简洁清晰地描述这个问题。

  - type: textarea
    id: description
    attributes:
      label: 问题描述
      placeholder: 清晰描述问题，包括你尝试做什么，发生了什么
    validations:
      required: true

  - type: textarea
    id: reproduction
    attributes:
      label: 复现步骤
      placeholder: |
        1. 打开 '...'
        2. 点击 '...'
        3. 滚动到 '...'
        4. 看到错误
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: 预期行为
      placeholder: 你期望发生的事情
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: 实际行为
      placeholder: 实际发生的事情
    validations:
      required: true

  - type: dropdown
    id: severity
    attributes:
      label: 严重程度
      options:
        - Low (轻微问题，不影响使用)
        - Medium (中等问题，部分功能受影响)
        - High (严重问题，主要功能无法使用)
        - Critical (崩溃，无法使用)
    validations:
      required: true

  - type: input
    id: version
    attributes:
      label: 版本号
      placeholder: 例如：0.1.0

  - type: textarea
    id: logs
    attributes:
      label: 日志/错误信息
      placeholder: 如果有错误日志，请粘贴在这里

  - type: checkboxes
    id: environment
    attributes:
      label: 环境信息
      options:
        - label: macOS
          required: false
        - label: Windows
          required: false
        - label: Linux
          required: false
