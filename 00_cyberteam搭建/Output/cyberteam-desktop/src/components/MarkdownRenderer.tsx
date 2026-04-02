import React, { useMemo } from "react"
import ReactMarkdown from "react-markdown"
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism"

interface MarkdownRendererProps {
  content: string
  className?: string
}

/**
 * Markdown 渲染器
 * 支持：
 * - 代码高亮（Prism）
 * - 表格
 * - 链接（安全打开）
 * - 任务列表
 */
export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, className = "" }) => {
  return (
    <div className={`markdown-renderer ${className}`}>
      <ReactMarkdown
        components={{
          code({ node, className: codeClassName, children, ...props }) {
            const match = /language-(\w+)/.exec(codeClassName || "")
            const codeString = String(children).replace(/\n$/, "")

            // 行内代码
            if (!match) {
              return (
                <code className="inline-code" {...props}>
                  {children}
                </code>
              )
            }

            // 代码块
            return (
              <SyntaxHighlighter
                style={oneDark}
                language={match[1]}
                PreTag="div"
                customStyle={{
                  margin: "12px 0",
                  borderRadius: "8px",
                  fontSize: "13px",
                  background: "#1e293b",
                }}
                {...props}
              >
                {codeString}
              </SyntaxHighlighter>
            )
          },

          table({ children }) {
            return (
              <div className="table-wrapper">
                <table>{children}</table>
              </div>
            )
          },

          a({ children, href }) {
            const isExternal = href?.startsWith("http://") || href?.startsWith("https://")
            return (
              <a
                href={href}
                target={isExternal ? "_blank" : undefined}
                rel={isExternal ? "noopener noreferrer" : undefined}
              >
                {children}
              </a>
            )
          },

          ul({ children }) {
            return <ul className="list-disc pl-5">{children}</ul>
          },

          ol({ children }) {
            return <ol className="list-decimal pl-5">{children}</ol>
          },

          li({ children, ...props }) {
            // 检查是否是任务列表项
            const hasCheckbox = String(children).includes("<input")
            if (hasCheckbox) {
              return <li {...props}>{children}</li>
            }
            return <li {...props}>{children}</li>
          },

          blockquote({ children }) {
            return <blockquote className="border-l-4 border-blue-500 pl-4 italic">{children}</blockquote>
          },

          h1({ children }) {
            return <h1 className="text-xl font-bold mt-4 mb-2">{children}</h1>
          },
          h2({ children }) {
            return <h2 className="text-lg font-bold mt-3 mb-2">{children}</h2>
          },
          h3({ children }) {
            return <h3 className="text-base font-bold mt-2 mb-1">{children}</h3>
          },

          p({ children }) {
            return <p className="mb-2">{children}</p>
          },

          hr() {
            return <hr className="border-gray-700 my-3" />
          },

          input({ type, checked, ...props }) {
            if (type === "checkbox") {
              return (
                <input
                  type="checkbox"
                  checked={checked}
                  readOnly
                  className="mr-2"
                  {...props}
                />
              )
            }
            return <input type={type} {...props} />
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
