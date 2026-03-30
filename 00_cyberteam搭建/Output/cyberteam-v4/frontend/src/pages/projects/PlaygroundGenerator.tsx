/**
 * Playground 生成器页面
 *
 * 功能：
 * - 输入项目数据（漏斗、渠道、预算）
 * - POST 到后端 /api/playground/generate
 * - SSE 订阅生成进度
 * - iframe 实时预览 HTML
 * - 下载 HTML 文件
 * - 模拟器滑块实时更新预览
 */
import { useState, useCallback, useRef, useEffect } from 'react'
import {
  Card, Form, Input, InputNumber, Button, Progress, Space,
  Typography, Row, Col, Slider, Tag, Alert, Divider, message,
} from 'antd'
import {
  PlayCircleOutlined, DownloadOutlined, ReloadOutlined,
  CheckCircleOutlined, LoadingOutlined, WarningOutlined,
} from '@ant-design/icons'
import {
  generatePlayground,
  fetchPlaygroundHTML,
  subscribePlaygroundSSE,
  type PlaygroundRequest,
} from '@/apis/modules/playground'

const { Title, Text, Paragraph } = Typography
const { TextArea } = Input

// 漏斗默认值
const DEFAULT_FUNNEL = {
  曝光: 100000,
  点击: 5000,
  注册: 500,
  成交: 100,
}

// 渠道默认值
const DEFAULT_CHANNELS = {
  小红书: { 曝光: 40000, 成本: 5000, ROI: 3.2 },
  抖音: { 曝光: 60000, 成本: 8000, ROI: 2.8 },
  微信: { 曝光: 10000, 成本: 3000, ROI: 4.5 },
}

type GenStatus = 'idle' | 'generating' | 'success' | 'error'

export default function PlaygroundGenerator() {
  const [form] = Form.useForm()
  const [status, setStatus] = useState<GenStatus>('idle')
  const [progress, setProgress] = useState(0)
  const [progressStep, setProgressStep] = useState('')
  const [generatedHTML, setGeneratedHTML] = useState('')
  const [taskId, setTaskId] = useState('')
  const [errorMsg, setErrorMsg] = useState('')
  const iframeRef = useRef<HTMLIFrameElement>(null)

  // 模拟器状态（漏斗数据）
  const [funnelValues, setFunnelValues] = useState(DEFAULT_FUNNEL)
  const [budget, setBudget] = useState(16000)
  const [riskLevel, setRiskLevel] = useState('中等')

  // 生成 Playground
  const handleGenerate = useCallback(async () => {
    try {
      const values = await form.validateFields()

      setStatus('generating')
      setProgress(0)
      setProgressStep('正在提交...')
      setErrorMsg('')
      setGeneratedHTML('')

      // 1. 触发生成
      const { task_id } = await generatePlayground({
        projectName: values.projectName,
        projectDate: values.projectDate,
        funnel: funnelValues,
        channels: DEFAULT_CHANNELS,
        budget: budget,
        riskLevel: riskLevel,
        notes: values.notes || '',
      })

      setTaskId(task_id)
      setProgressStep('生成中...')

      // 2. 订阅 SSE 进度
      const unsubscribe = subscribePlaygroundSSE(task_id, {
        onProgress: (step, percent) => {
          setProgressStep(step)
          setProgress(percent)
        },
        onComplete: async (html) => {
          setProgress(100)
          setProgressStep('生成完成')
          if (html) {
            setGeneratedHTML(html)
          } else {
            // SSE 没带 HTML，走 HTTP 获取
            try {
              const htmlContent = await fetchPlaygroundHTML(taskId)
              setGeneratedHTML(htmlContent)
            } catch {
              // 可能还在生成中，稍后刷新
              setTimeout(async () => {
                try {
                  const htmlContent = await fetchPlaygroundHTML(taskId)
                  setGeneratedHTML(htmlContent)
                } catch (e) {
                  setErrorMsg('HTML 获取超时，请稍后刷新重试')
                }
              }, 2000)
            }
          }
          setStatus('success')
          unsubscribe()
        },
        onError: (err) => {
          setErrorMsg(err)
          setStatus('error')
          unsubscribe()
        },
      })

      // 备用：30s 超时
      setTimeout(() => {
        if (status === 'generating') {
          unsubscribe()
          setErrorMsg('生成超时，请稍后刷新重试')
          setStatus('error')
        }
      }, 30000)
    } catch (err: any) {
      setErrorMsg(err?.message || '提交失败')
      setStatus('error')
    }
  }, [form, funnelValues, budget, riskLevel, taskId, status])

  // 下载 HTML
  const handleDownload = useCallback(() => {
    if (!generatedHTML) return
    const blob = new Blob([generatedHTML], { type: 'text/html;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const projectName = form.getFieldValue('projectName') || 'playground'
    a.download = `活动看板_${projectName}.html`
    a.click()
    URL.revokeObjectURL(url)
    message.success('下载成功')
  }, [generatedHTML, form])

  // 刷新预览
  const handleRefresh = useCallback(() => {
    if (iframeRef.current && generatedHTML) {
      iframeRef.current.srcdoc = generatedHTML
    }
  }, [generatedHTML])

  // 模拟器滑块变化 → 更新漏斗数据
  const handleFunnelChange = (key: keyof typeof DEFAULT_FUNNEL, value: number) => {
    setFunnelValues(prev => ({ ...prev, [key]: value }))
  }

  // 预览区域样式
  const previewStyle: React.CSSProperties = {
    width: '100%',
    height: '600px',
    border: '1px solid #d9d9d9',
    borderRadius: 8,
    background: '#fff',
  }

  return (
    <div className="p-6">
      <Title level={3}>
        Playground 生成器
      </Title>
      <Paragraph type="secondary">
        输入项目数据，生成交互式活动看板。支持漏斗模拟、进度预览和 HTML 下载。
      </Paragraph>

      <Row gutter={24}>
        {/* 左侧：输入表单 + 模拟器 */}
        <Col span={12}>
          <Card title="项目信息" style={{ marginBottom: 16 }}>
            <Form form={form} layout="vertical" initialValues={{
              projectName: '',
              projectDate: new Date().toISOString().split('T')[0],
              notes: '',
            }}>
              <Form.Item
                name="projectName"
                label="项目名称"
                rules={[{ required: true, message: '请输入项目名称' }]}
              >
                <Input placeholder="例如：西北发面包子品牌策划" />
              </Form.Item>

              <Form.Item
                name="projectDate"
                label="项目日期"
                rules={[{ required: true, message: '请选择日期' }]}
              >
                <Input type="date" />
              </Form.Item>

              <Form.Item name="notes" label="备注（可选）">
                <TextArea rows={3} placeholder="补充说明..." />
              </Form.Item>
            </Form>
          </Card>

          <Card title="漏斗模拟器" style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div>
                <Text strong>曝光: {funnelValues.曝光.toLocaleString()}</Text>
                <Slider
                  min={0}
                  max={500000}
                  value={funnelValues.曝光}
                  onChange={(v) => handleFunnelChange('曝光', v)}
                  tooltip={{ formatter: (v) => `${(v || 0).toLocaleString()}` }}
                />
              </div>
              <div>
                <Text strong>点击: {funnelValues.点击.toLocaleString()}</Text>
                <Slider
                  min={0}
                  max={funnelValues.曝光}
                  value={funnelValues.点击}
                  onChange={(v) => handleFunnelChange('点击', v)}
                  tooltip={{ formatter: (v) => `${(v || 0).toLocaleString()}` }}
                />
              </div>
              <div>
                <Text strong>注册: {funnelValues.注册.toLocaleString()}</Text>
                <Slider
                  min={0}
                  max={funnelValues.点击}
                  value={funnelValues.注册}
                  onChange={(v) => handleFunnelChange('注册', v)}
                  tooltip={{ formatter: (v) => `${(v || 0).toLocaleString()}` }}
                />
              </div>
              <div>
                <Text strong>成交: {funnelValues.成交.toLocaleString()}</Text>
                <Slider
                  min={0}
                  max={funnelValues.注册}
                  value={funnelValues.成交}
                  onChange={(v) => handleFunnelChange('成交', v)}
                  tooltip={{ formatter: (v) => `${(v || 0).toLocaleString()}` }}
                />
              </div>
            </Space>

            <Divider />

            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <div>
                <Text strong>总预算: {budget.toLocaleString()} 元</Text>
                <Slider
                  min={1000}
                  max={100000}
                  step={1000}
                  value={budget}
                  onChange={setBudget}
                  tooltip={{ formatter: (v) => `${(v || 0).toLocaleString()} 元` }}
                />
              </div>
              <div>
                <Text strong>风险等级: {riskLevel}</Text>
                <Slider
                  min={1}
                  max={3}
                  marks={{ 1: '低', 2: '中等', 3: '高' }}
                  value={riskLevel === '低' ? 1 : riskLevel === '高' ? 3 : 2}
                  onChange={(v) => setRiskLevel(v === 1 ? '低' : v === 3 ? '高' : '中等')}
                />
              </div>
            </Space>

            <Divider />

            {/* 漏斗转化率预览 */}
            <div style={{ background: '#f5f5f5', padding: 12, borderRadius: 8 }}>
              <Text type="secondary">转化率预览</Text>
              <Row gutter={8} style={{ marginTop: 8 }}>
                <Col span={12}>
                  <Text>曝光→点击</Text>
                  <br />
                  <Text strong>{funnelValues.曝光 > 0 ? ((funnelValues.点击 / funnelValues.曝光) * 100).toFixed(2) : 0}%</Text>
                </Col>
                <Col span={12}>
                  <Text>点击→注册</Text>
                  <br />
                  <Text strong>{funnelValues.点击 > 0 ? ((funnelValues.注册 / funnelValues.点击) * 100).toFixed(2) : 0}%</Text>
                </Col>
                <Col span={12} style={{ marginTop: 8 }}>
                  <Text>注册→成交</Text>
                  <br />
                  <Text strong>{funnelValues.注册 > 0 ? ((funnelValues.成交 / funnelValues.注册) * 100).toFixed(2) : 0}%</Text>
                </Col>
                <Col span={12} style={{ marginTop: 8 }}>
                  <Text>总体转化率</Text>
                  <br />
                  <Text strong>{funnelValues.曝光 > 0 ? ((funnelValues.成交 / funnelValues.曝光) * 100).toFixed(4) : 0}%</Text>
                </Col>
              </Row>
            </div>
          </Card>

          {/* 状态 + 操作 */}
          <Card>
            {status === 'idle' && (
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                size="large"
                block
                onClick={handleGenerate}
              >
                生成 Playground
              </Button>
            )}

            {status === 'generating' && (
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                <Alert
                  type="info"
                  icon={<LoadingOutlined />}
                  message={progressStep}
                  showIcon
                />
                <Progress percent={progress} status="active" />
                <Text type="secondary" style={{ textAlign: 'center', display: 'block' }}>
                  正在生成，请勿关闭页面...
                </Text>
              </Space>
            )}

            {status === 'success' && (
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                <Alert
                  type="success"
                  icon={<CheckCircleOutlined />}
                  message="生成成功"
                  showIcon
                />
                <Space>
                  <Button icon={<ReloadOutlined />} onClick={handleGenerate}>
                    重新生成
                  </Button>
                  <Button
                    type="primary"
                    icon={<DownloadOutlined />}
                    onClick={handleDownload}
                    disabled={!generatedHTML}
                  >
                    下载 HTML
                  </Button>
                </Space>
              </Space>
            )}

            {status === 'error' && (
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                <Alert
                  type="error"
                  icon={<WarningOutlined />}
                  message="生成失败"
                  description={errorMsg}
                  showIcon
                />
                <Button
                  icon={<ReloadOutlined />}
                  onClick={handleGenerate}
                >
                  重试
                </Button>
              </Space>
            )}
          </Card>
        </Col>

        {/* 右侧：预览区 */}
        <Col span={12}>
          <Card
            title="预览区"
            extra={
              generatedHTML && (
                <Space>
                  <Button size="small" icon={<ReloadOutlined />} onClick={handleRefresh}>
                    刷新
                  </Button>
                  <Button size="small" icon={<DownloadOutlined />} onClick={handleDownload}>
                    下载
                  </Button>
                </Space>
              )
            }
          >
            {generatedHTML ? (
              <iframe
                ref={iframeRef}
                srcDoc={generatedHTML}
                style={previewStyle}
                title="Playground 预览"
                sandbox="allow-scripts allow-same-origin"
              />
            ) : (
              <div
                style={{
                  ...previewStyle,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: '#fafafa',
                  color: '#bbb',
                  fontSize: 16,
                }}
              >
                <Space direction="vertical" style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 48 }}>&#128190;</div>
                  <Text type="secondary">
                    {status === 'generating' ? '生成中...' : '点击「生成 Playground」开始'}
                  </Text>
                </Space>
              </div>
            )}
          </Card>

          {/* 渠道配置预览 */}
          <Card title="渠道配置" style={{ marginTop: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              {Object.entries(DEFAULT_CHANNELS).map(([channel, data]) => (
                <div key={channel} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Tag color="blue">{channel}</Tag>
                  <Space size="middle">
                    <Text>曝光: {data.曝光.toLocaleString()}</Text>
                    <Text>成本: {data.成本.toLocaleString()}元</Text>
                    <Text type={data.ROI >= 3 ? 'success' : 'warning'}>ROI: {data.ROI}x</Text>
                  </Space>
                </div>
              ))}
              <Divider style={{ margin: '8px 0' }} />
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text strong>总成本:</Text>
                <Text strong>{Object.values(DEFAULT_CHANNELS).reduce((s, c) => s + c.成本, 0).toLocaleString()} 元</Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text strong>平均 ROI:</Text>
                <Text strong type="success">
                  {(Object.values(DEFAULT_CHANNELS).reduce((s, c) => s + c.ROI, 0) / Object.keys(DEFAULT_CHANNELS).length).toFixed(2)}x
                </Text>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  )
}
