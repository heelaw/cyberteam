import React, { useEffect, useState } from "react"

interface StreamingCursorProps {
  /** 是否显示 */
  visible: boolean
  /** 自定义颜色 */
  color?: string
  /** 闪烁频率 ms */
  blinkRate?: number
}

export const StreamingCursor: React.FC<StreamingCursorProps> = ({
  visible,
  color = "#3b82f6",
  blinkRate = 530,
}) => {
  const [show, setShow] = useState(true)

  useEffect(() => {
    if (!visible) {
      setShow(false)
      return
    }

    setShow(true)

    const interval = setInterval(() => {
      setShow(prev => !prev)
    }, blinkRate)

    return () => clearInterval(interval)
  }, [visible, blinkRate])

  if (!visible) return null

  return (
    <span
      className="streaming-cursor inline-block align-middle"
      style={{
        display: "inline-block",
        width: "2px",
        height: "1.1em",
        backgroundColor: color,
        marginLeft: "2px",
        marginRight: "2px",
        verticalAlign: "text-bottom",
        opacity: show ? 1 : 0,
        transition: "opacity 0.08s",
        borderRadius: "1px",
      }}
    />
  )
}
