import { useState } from 'react'
import './App.css'

// 模拟逐字稿数据
const sampleTranscript = `
标题：1.1 你的产品，是否已准备好做大规模增长？

我们今天要聊的话题是：你的产品是否已经准备好做大规模增长。

在开始之前，我想先问大家一个问题：你们觉得增长是越早越好吗？

很多人可能会说，当然是越早越好了，越早增长就能越早获取用户，越早获取用户就能建立壁垒。

这个想法本身没有问题，但是如果你在产品还没有准备好的时候就开始大规模增长，可能会带来灾难性的后果。

让我给你讲一个真实的案例：某社交产品，在DAU只有1000的时候就开始做大规模推广，每天投入10万的广告费。

结果是什么呢？用户来了，但是留存率只有5%，为什么？因为产品本身的使用体验有问题，用户来了之后很快就流失了。

这10万的广告费，换来的不是增长，而是大量的负面口碑。

所以，在做增长之前，我们首先要问一个问题：我的产品，是否已经准备好做大规模增长？

那么，怎么判断产品是否准备好呢？我总结了四个核心指标：

第一，复购率。如果一个产品的复购率低于20%，说明用户并不觉得你的产品有价值。

第二，自然推荐率。如果用户不愿意主动推荐你的产品，说明产品体验没有达到用户的预期。

第三，NPS净推荐值。NPS低于30，说明产品有很大的改进空间。

第四，单位经济模型跑通。也就是用户生命周期价值LTV要大于获客成本CAC。

只有这四个指标都达到标准，才说明产品准备好了做大规模增长。

好，今天的课程就到这里，我们下节课再见。
`

// 模拟解析结果
const parseResult = {
  methodologys: [
    {
      name: '产品增长准备度评估',
      steps: [
        '复购率检查（<20%为不合格）',
        '自然推荐率检查',
        'NPS净推荐值检查（<30为不合格）',
        '单位经济模型验证（LTV > CAC）'
      ],
      output: '产品是否准备好做大规模增长的评估报告'
    }
  ],
  metrics: [
    { name: '复购率', threshold: '>20%', type: '准入指标' },
    { name: '自然推荐率', threshold: '>10%', type: '准入指标' },
    { name: 'NPS', threshold: '>30', type: '准入指标' },
    { name: 'LTV/CAC', threshold: '>1', type: '准入指标' }
  ],
  cases: [
    { title: '某社交产品失败案例', reason: 'DAU 1000时投放10万/天，留存仅5%' }
  ]
}

function App() {
  const [activeTab, setActiveTab] = useState('parser')
  const [transcript, setTranscript] = useState(sampleTranscript)
  const [isParsing, setIsParsing] = useState(false)
  const [parseResult2, setParseResult2] = useState<typeof parseResult | null>(null)

  // 北极星指标计算器状态
  const [metrics, setMetrics] = useState({
    dau: 10000,
    conversion: 5,
    revenue: 50,
    retention: 30,
    cac: 100,
    ltv: 300
  })
  const [northStarResult, setNorthStarResult] = useState<any>(null)

  const handleParse = () => {
    setIsParsing(true)
    setTimeout(() => {
      setParseResult2(parseResult)
      setIsParsing(false)
    }, 1500)
  }

  const calculateNorthStar = () => {
    const { dau, conversion, revenue, retention, cac, ltv } = metrics
    const totalRevenue = dau * (conversion / 100) * revenue * (retention / 100)
    const unitEconomics = ltv / cac
    const monthlyGrowth = (conversion / 100) * (retention / 100)

    let recommendation = ''
    if (unitEconomics < 1) {
      recommendation = '❌ 单位经济模型未跑通，建议先优化产品'
    } else if (monthlyGrowth < 0.1) {
      recommendation = '⚠️ 增长效率较低，建议优化转化率和留存'
    } else {
      recommendation = '✅ 产品已准备好做大规模增长'
    }

    setNorthStarResult({
      totalRevenue,
      unitEconomics,
      monthlyGrowth,
      recommendation,
      northStarMetric: monthlyGrowth > 0.15 ? '月度活跃用户价值' : 'DAU'
    })
  }

  return (
    <div className="playground-container">
      {/* Header */}
      <header className="playground-header">
        <div className="logo-section">
          <span className="logo-icon">🧬</span>
          <h1>Skill Playground</h1>
        </div>
        <p className="subtitle">运营技能工具集 - 增长黑客系列</p>
      </header>

      {/* Tab Navigation */}
      <nav className="tab-nav">
        <button
          className={`tab-btn ${activeTab === 'parser' ? 'active' : ''}`}
          onClick={() => setActiveTab('parser')}
        >
          📝 课程解析器
        </button>
        <button
          className={`tab-btn ${activeTab === 'workflow' ? 'active' : ''}`}
          onClick={() => setActiveTab('workflow')}
        >
          🔗 Skill协作流
        </button>
        <button
          className={`tab-btn ${activeTab === 'calculator' ? 'active' : ''}`}
          onClick={() => setActiveTab('calculator')}
        >
          🧮 北极星指标
        </button>
      </nav>

      {/* Content */}
      <main className="playground-content">

        {/* 课程解析器 Tab */}
        {activeTab === 'parser' && (
          <div className="parser-section">
            <div className="panel input-panel">
              <h3>📄 输入：课程逐字稿</h3>
              <textarea
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                placeholder="粘贴课程逐字稿内容..."
                className="transcript-input"
              />
              <button
                className="action-btn parse-btn"
                onClick={handleParse}
                disabled={isParsing}
              >
                {isParsing ? '🔄 解析中...' : '▶️ 开始解析'}
              </button>
            </div>

            <div className="panel output-panel">
              <h3>📋 输出：解析结果</h3>
              {parseResult2 ? (
                <div className="result-content">
                  <div className="result-section">
                    <h4>🎯 提取的方法论</h4>
                    {parseResult2.methodologys.map((m: any, i: number) => (
                      <div key={i} className="methodology-card">
                        <h5>{m.name}</h5>
                        <ol>
                          {m.steps.map((s: string, j: number) => (
                            <li key={j}>{s}</li>
                          ))}
                        </ol>
                        <p className="output-label">📤 输出：{m.output}</p>
                      </div>
                    ))}
                  </div>
                  <div className="result-section">
                    <h4>📊 核心指标</h4>
                    <div className="metrics-grid">
                      {parseResult2.metrics.map((m: any, i: number) => (
                        <div key={i} className="metric-badge">
                          <span className="metric-name">{m.name}</span>
                          <span className="metric-threshold">{m.threshold}</span>
                          <span className="metric-type">{m.type}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="result-section">
                    <h4>💡 案例参考</h4>
                    {parseResult2.cases.map((c: any, i: number) => (
                      <div key={i} className="case-card">
                        <p className="case-title">{c.title}</p>
                        <p className="case-reason">{c.reason}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="empty-state">
                  <span className="empty-icon">📭</span>
                  <p>点击"开始解析"查看结果</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Skill协作流 Tab */}
        {activeTab === 'workflow' && (
          <div className="workflow-section">
            <h3>🔗 三个基础Skill的协作流程</h3>

            <div className="workflow-diagram">
              <div className="workflow-step step-1">
                <div className="step-icon">📥</div>
                <h4>Phase 1: 课程解析</h4>
                <p>输入：原始逐字稿</p>
                <p>输出：结构化文本</p>
                <div className="step-status">✅ 已完成</div>
              </div>

              <div className="workflow-arrow">→</div>

              <div className="workflow-step step-2">
                <div className="step-icon">🔍</div>
                <h4>Phase 2: 知识提取</h4>
                <p>输入：结构化文本</p>
                <p>输出：知识点清单</p>
                <div className="step-status">⏳ 待执行</div>
              </div>

              <div className="workflow-arrow">→</div>

              <div className="workflow-step step-3">
                <div className="step-icon">🏗️</div>
                <h4>Phase 3: 方法论结构化</h4>
                <p>输入：知识点清单</p>
                <p>输出：Skill规格文档</p>
                <div className="step-status">⏳ 待执行</div>
              </div>
            </div>

            <div className="dependency-graph">
              <h4>📊 Skill依赖关系图</h4>
              <div className="graph-content">
                <pre>{`
Layer 0: 基础能力
├─ course-parser (课程解析)
│   输入: 逐字稿文本
│   输出: {sections, key_points, concepts}
│
├─ knowledge-extractor (知识提取)
│   输入: {sections, key_points, concepts}
│   输出: [{name, definition, steps, output}]
│   依赖: course-parser
│
└─ methodology-structurer (方法论结构化)
    输入: [{name, definition, steps, output}]
    输出: Skill规格文档
    依赖: knowledge-extractor

Layer 1: 工具型Skill (依赖Layer 0)
├─ north-star-calculator
├─ funnel-analyzer
├─ ice-scorer
└─ ...
                `}</pre>
              </div>
            </div>
          </div>
        )}

        {/* 北极星指标计算器 Tab */}
        {activeTab === 'calculator' && (
          <div className="calculator-section">
            <h3>🧮 北极星指标计算器</h3>

            <div className="calculator-grid">
              <div className="input-group">
                <label>DAU（日活跃用户）</label>
                <input
                  type="number"
                  value={metrics.dau}
                  onChange={(e) => setMetrics({...metrics, dau: Number(e.target.value)})}
                />
              </div>
              <div className="input-group">
                <label>转化率 (%)</label>
                <input
                  type="number"
                  value={metrics.conversion}
                  onChange={(e) => setMetrics({...metrics, conversion: Number(e.target.value)})}
                />
              </div>
              <div className="input-group">
                <label>单用户收入 (元)</label>
                <input
                  type="number"
                  value={metrics.revenue}
                  onChange={(e) => setMetrics({...metrics, revenue: Number(e.target.value)})}
                />
              </div>
              <div className="input-group">
                <label>次留率 (%)</label>
                <input
                  type="number"
                  value={metrics.retention}
                  onChange={(e) => setMetrics({...metrics, retention: Number(e.target.value)})}
                />
              </div>
              <div className="input-group">
                <label>获客成本 CAC (元)</label>
                <input
                  type="number"
                  value={metrics.cac}
                  onChange={(e) => setMetrics({...metrics, cac: Number(e.target.value)})}
                />
              </div>
              <div className="input-group">
                <label>用户生命周期价值 LTV (元)</label>
                <input
                  type="number"
                  value={metrics.ltv}
                  onChange={(e) => setMetrics({...metrics, ltv: Number(e.target.value)})}
                />
              </div>
            </div>

            <button className="action-btn calculate-btn" onClick={calculateNorthStar}>
              🧮 计算北极星指标
            </button>

            {northStarResult && (
              <div className="result-cards">
                <div className="result-card">
                  <span className="result-label">月度总收入</span>
                  <span className="result-value">¥{northStarResult.totalRevenue.toLocaleString()}</span>
                </div>
                <div className="result-card">
                  <span className="result-label">单位经济 (LTV/CAC)</span>
                  <span className="result-value">{northStarResult.unitEconomics.toFixed(2)}</span>
                </div>
                <div className="result-card">
                  <span className="result-label">月增长率</span>
                  <span className="result-value">{(northStarResult.monthlyGrowth * 100).toFixed(1)}%</span>
                </div>
                <div className="result-card highlight">
                  <span className="result-label">推荐指标</span>
                  <span className="result-value">{northStarResult.northStarMetric}</span>
                </div>
              </div>
            )}

            {northStarResult && (
              <div className="recommendation-box">
                <h4>📋 分析结论</h4>
                <p className="recommendation">{northStarResult.recommendation}</p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="playground-footer">
        <p>Skill Playground v0.1 | 课程到Skill转化原型</p>
        <p>基于增长黑客高阶+入门课程</p>
      </footer>
    </div>
  )
}

export default App
