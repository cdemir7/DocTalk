import { useRef, useState, useEffect } from 'react'
import { apiChat } from '../api/client'
import type { ChatMessage, Source } from '../types'
import './ChatPanel.css'

interface Props {
  messages: ChatMessage[]
  onMessagesChange: (msgs: ChatMessage[]) => void
  selectedDocIds: string[]
  hasDocuments: boolean
}

function SourcesAccordion({ sources }: { sources: Source[] }) {
  const [open, setOpen] = useState(false)
  if (!sources.length) return null
  return (
    <div className="sources">
      <button className="sources-toggle" onClick={() => setOpen((o) => !o)}>
        <svg viewBox="0 0 20 20" fill="currentColor" width="12" height="12"
          style={{ transform: open ? 'rotate(90deg)' : 'none', transition: 'transform 0.2s' }}>
          <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
        </svg>
        {sources.length} kaynak
      </button>
      {open && (
        <ul className="sources-list">
          {sources.map((s, i) => (
            <li key={i} className="source-item">
              <div className="source-header">
                <span className="source-badge">{s.docName}</span>
                <span className="source-chunk">parça {s.chunkIndex}</span>
                {s.score !== undefined && (
                  <span className="source-score">{(s.score * 100).toFixed(0)}%</span>
                )}
              </div>
              {s.snippet && <p className="source-snippet">{s.snippet}</p>}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`message ${isUser ? 'message-user' : 'message-assistant'}`}>
      <div className={`message-avatar ${isUser ? 'avatar-user' : 'avatar-bot'}`}>
        {isUser ? 'S' : 'D'}
      </div>
      <div className="message-body">
        <div className="message-bubble">{msg.content}</div>
        {!isUser && msg.sources && <SourcesAccordion sources={msg.sources} />}
        <span className="message-time">
          {msg.timestamp.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  )
}

export default function ChatPanel({ messages, onMessagesChange, selectedDocIds, hasDocuments }: Props) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const send = async () => {
    const question = input.trim()
    if (!question || loading) return

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: question,
      timestamp: new Date(),
    }
    onMessagesChange([...messages, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await apiChat(
        question,
        selectedDocIds.length ? selectedDocIds : null,
      )
      const botMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: res.answer,
        sources: res.sources,
        timestamp: new Date(),
      }
      onMessagesChange([...messages, userMsg, botMsg])
    } catch (err) {
      const errMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: err instanceof Error ? err.message : 'Bir hata oluştu.',
        timestamp: new Date(),
      }
      onMessagesChange([...messages, userMsg, errMsg])
    } finally {
      setLoading(false)
    }
  }

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <div className="chat-empty-icon">💬</div>
            <p className="chat-empty-title">Sohbete başlayın</p>
            <p className="chat-empty-hint">
              {hasDocuments
                ? 'Belgeleriniz hakkında bir soru sorun.'
                : 'Önce sol panelden belge yükleyin.'}
            </p>
          </div>
        ) : (
          messages.map((m) => <MessageBubble key={m.id} msg={m} />)
        )}
        {loading && (
          <div className="message message-assistant">
            <div className="message-avatar avatar-bot">D</div>
            <div className="message-body">
              <div className="typing-indicator">
                <span /><span /><span />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-area">
        {selectedDocIds.length > 0 && (
          <div className="chat-scope">
            {selectedDocIds.length} belge seçili — sorular bu belgelerle sınırlı
          </div>
        )}
        <div className="chat-input-row">
          <textarea
            ref={textareaRef}
            className="chat-textarea"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Sorunuzu yazın... (Enter ile gönderin)"
            rows={1}
            disabled={loading}
          />
          <button
            className="chat-send-btn"
            onClick={send}
            disabled={loading || !input.trim()}
            title="Gönder (Enter)"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="18" height="18">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
