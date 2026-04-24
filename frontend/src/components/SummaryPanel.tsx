import { useState } from 'react'
import { apiSummarize } from '../api/client'
import type { UploadedDocument, SummarizeResult, SummaryStyle } from '../types'
import './SummaryPanel.css'

// ── Lightweight Markdown → JSX renderer ──────────────────────────────────────
function renderMarkdown(text: string): JSX.Element {
  const lines = text.split('\n')
  const elements: JSX.Element[] = []
  let ulBuffer: string[] = []
  let olBuffer: string[] = []
  let key = 0

  const flushUl = () => {
    if (ulBuffer.length) {
      elements.push(
        <ul key={key++} className="md-ul">
          {ulBuffer.map((item, i) => (
            <li key={i} dangerouslySetInnerHTML={{ __html: inlineFormat(item) }} />
          ))}
        </ul>
      )
      ulBuffer = []
    }
  }
  const flushOl = () => {
    if (olBuffer.length) {
      elements.push(
        <ol key={key++} className="md-ol">
          {olBuffer.map((item, i) => (
            <li key={i} dangerouslySetInnerHTML={{ __html: inlineFormat(item) }} />
          ))}
        </ol>
      )
      olBuffer = []
    }
  }

  for (const raw of lines) {
    const line = raw.trimEnd()

    // H2/H3 heading
    if (/^###\s/.test(line)) {
      flushUl(); flushOl()
      elements.push(<h4 key={key++} className="md-h4" dangerouslySetInnerHTML={{ __html: inlineFormat(line.replace(/^###\s/, '')) }} />)
    } else if (/^##\s/.test(line)) {
      flushUl(); flushOl()
      elements.push(<h3 key={key++} className="md-h3" dangerouslySetInnerHTML={{ __html: inlineFormat(line.replace(/^##\s/, '')) }} />)
    } else if (/^#\s/.test(line)) {
      flushUl(); flushOl()
      elements.push(<h2 key={key++} className="md-h2" dangerouslySetInnerHTML={{ __html: inlineFormat(line.replace(/^#\s/, '')) }} />)
    // Unordered list
    } else if (/^[-*]\s/.test(line)) {
      flushOl()
      ulBuffer.push(line.replace(/^[-*]\s/, ''))
    // Ordered list
    } else if (/^\d+\.\s/.test(line)) {
      flushUl()
      olBuffer.push(line.replace(/^\d+\.\s/, ''))
    // Empty line → paragraph break
    } else if (line === '') {
      flushUl(); flushOl()
      elements.push(<div key={key++} className="md-spacer" />)
    // Regular paragraph
    } else {
      flushUl(); flushOl()
      elements.push(<p key={key++} className="md-p" dangerouslySetInnerHTML={{ __html: inlineFormat(line) }} />)
    }
  }
  flushUl(); flushOl()

  return <div className="md-body">{elements}</div>
}

/** Bold, italic, inline code */
function inlineFormat(text: string): string {
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
}


interface Props {
  documents: UploadedDocument[]
  selectedDocIds: string[]
}

const STYLES: { value: SummaryStyle; label: string; hint: string }[] = [
  { value: 'short', label: 'Kısa', hint: '3-6 cümle' },
  { value: 'detailed', label: 'Detaylı', hint: 'Kapsamlı analiz' },
  { value: 'bullet', label: 'Madde madde', hint: 'Önemli noktalar' },
]

export default function SummaryPanel({ documents, selectedDocIds }: Props) {
  const [style, setStyle] = useState<SummaryStyle>('short')
  const [result, setResult] = useState<SummarizeResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const selectedDocs = documents.filter((d) => selectedDocIds.includes(d.docId))

  const handleSummarize = async () => {
    if (!selectedDocIds.length) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await apiSummarize(selectedDocIds, style)
      setResult(res)
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Özetleme başarısız'
      // 503 / 429 → kullanıcı dostu mesaj
      if (msg.includes('503') || msg.includes('UNAVAILABLE') || msg.includes('429')) {
        setError('Yapay zeka modeli şu an yoğun. Birkaç saniye bekleyip tekrar deneyin.')
      } else {
        setError(msg)
      }
    } finally {
      setLoading(false)
    }
  }

  if (documents.length === 0) {
    return (
      <div className="summary-panel summary-empty">
        <div className="summary-empty-icon">📋</div>
        <p className="summary-empty-title">Belge bulunamadı</p>
        <p className="summary-empty-hint">Özetlemek için önce belge yükleyin.</p>
      </div>
    )
  }

  return (
    <div className="summary-panel">
      {/* Config area */}
      <div className="summary-config">
        <div className="summary-config-section">
          <h3 className="summary-config-label">Seçili Belgeler</h3>
          {selectedDocs.length === 0 ? (
            <p className="summary-no-selection">
              Sol panelden özetlenecek belgeleri seçin.
            </p>
          ) : (
            <ul className="summary-doc-list">
              {selectedDocs.map((doc) => (
                <li key={doc.docId} className="summary-doc-item">
                  <span className="summary-doc-icon">
                    {/\.pdf$/i.test(doc.docName) ? '📄' : /\.docx$/i.test(doc.docName) ? '📝' : '📃'}
                  </span>
                  <span className="summary-doc-name">{doc.docName}</span>
                  <span className="summary-doc-chunks">{doc.totalChunks} parça</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="summary-config-section">
          <h3 className="summary-config-label">Özet Stili</h3>
          <div className="style-selector">
            {STYLES.map((s) => (
              <button
                key={s.value}
                className={`style-btn ${style === s.value ? 'active' : ''}`}
                onClick={() => setStyle(s.value)}
              >
                <span className="style-btn-label">{s.label}</span>
                <span className="style-btn-hint">{s.hint}</span>
              </button>
            ))}
          </div>
        </div>

        <button
          className="summarize-btn"
          onClick={handleSummarize}
          disabled={loading || selectedDocIds.length === 0}
        >
          {loading ? (
            <>
              <span className="summarize-spinner" />
              Özetleniyor...
            </>
          ) : (
            <>
              <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
              </svg>
              {selectedDocIds.length > 1
                ? `${selectedDocIds.length} Belgeyi Özetle`
                : 'Belgeyi Özetle'}
            </>
          )}
        </button>
      </div>

      {/* Result area */}
      <div className="summary-result-area">
        {error && (
          <div className="summary-error">{error}</div>
        )}

        {!result && !loading && !error && (
          <div className="summary-placeholder">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"
              width="40" height="40" style={{ color: 'var(--text-muted)' }}>
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            <p>Özetlemek istediğiniz belgeleri seçin ve "Özetle" butonuna tıklayın.</p>
          </div>
        )}

        {result && (
          <div className="summary-result">
            <div className="summary-result-header">
              <h3 className="summary-result-title">Özet</h3>
              <div className="summary-result-actions">
                <div className="summary-result-sources">
                  {result.sources.map((s) => (
                    <span key={s.docId} className="summary-source-badge">{s.docName}</span>
                  ))}
                </div>
                <button
                  className="copy-btn"
                  title="Panoya kopyala"
                  onClick={() => navigator.clipboard.writeText(result.summary)}
                >
                  <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                    <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                    <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
                  </svg>
                  Kopyala
                </button>
              </div>
            </div>
            <div className="summary-text">
              {renderMarkdown(result.summary)}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
