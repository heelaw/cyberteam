import { useState, useEffect, useRef, useCallback } from "react"

interface UseTypingEffectOptions {
  /** 完整文本 */
  text: string
  /** 每个字符的延迟，ms，默认 15 */
  speed?: number
  /** 是否启用，默认 true */
  enabled?: boolean
  /** 完成回调 */
  onComplete?: () => void
  /** 是否追加模式（不重置已有内容）*/
  append?: boolean
}

interface UseTypingEffectResult {
  /** 当前显示的文本 */
  displayedText: string
  /** 是否正在打字 */
  isTyping: boolean
  /** 进度百分比 0-100 */
  progress: number
  /** 重置到开头 */
  reset: () => void
}

/**
 * 打字机效果 Hook
 *
 * @example
 * const { displayedText, isTyping, progress } = useTypingEffect({
 *   text: fullResponse,
 *   speed: 15,
 *   enabled: isStreaming,
 *   onComplete: () => setIsStreaming(false)
 * })
 */
export const useTypingEffect = ({
  text,
  speed = 15,
  enabled = true,
  onComplete,
  append = false,
}: UseTypingEffectOptions): UseTypingEffectResult => {
  const [displayedText, setDisplayedText] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [progress, setProgress] = useState(0)
  const indexRef = useRef(0)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const targetTextRef = useRef(text)
  const onCompleteRef = useRef(onComplete)

  // 更新 onComplete ref
  useEffect(() => {
    onCompleteRef.current = onComplete
  }, [onComplete])

  // 更新目标文本
  useEffect(() => {
    if (!enabled) {
      setDisplayedText(text)
      setProgress(100)
      setIsTyping(false)
      return
    }

    targetTextRef.current = text

    // 如果追加模式，检查是否需要追加
    if (append && text.startsWith(displayedText)) {
      // 追加新文本
      const startIndex = displayedText.length
      indexRef.current = startIndex

      setIsTyping(true)

      intervalRef.current = setInterval(() => {
        setDisplayedText(prev => {
          const nextIndex = prev.length + 1
          const newText = text.slice(0, nextIndex)
          const pct = text.length > 0 ? Math.round((nextIndex / text.length) * 100) : 100
          setProgress(pct)

          if (nextIndex >= text.length) {
            clearInterval(intervalRef.current!)
            setIsTyping(false)
            onCompleteRef.current?.()
            return text
          }
          return newText
        })
      }, speed)
    } else {
      // 非追加模式，重置并从头开始
      if (text.length <= displayedText.length && !append) {
        // 新文本比当前的短，重置
        indexRef.current = 0
        setDisplayedText("")
      }

      // 如果已经显示完了，不需要重新打字
      if (indexRef.current >= text.length) {
        setDisplayedText(text)
        setProgress(100)
        setIsTyping(false)
        return
      }

      setIsTyping(true)

      intervalRef.current = setInterval(() => {
        indexRef.current += 1
        const newText = text.slice(0, indexRef.current)
        setDisplayedText(newText)

        const pct = text.length > 0 ? Math.round((indexRef.current / text.length) * 100) : 100
        setProgress(pct)

        if (indexRef.current >= text.length) {
          if (intervalRef.current) clearInterval(intervalRef.current)
          setIsTyping(false)
          onCompleteRef.current?.()
        }
      }, speed)
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [text, enabled, speed, append])

  const reset = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    indexRef.current = 0
    setDisplayedText("")
    setProgress(0)
    setIsTyping(false)
  }, [])

  return { displayedText, isTyping, progress, reset }
}
