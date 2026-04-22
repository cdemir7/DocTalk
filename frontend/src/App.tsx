import { useState, useCallback } from 'react'
import './App.css'
import DocumentUploader from './components/DocumentUploader'
import DocumentList from './components/DocumentList'
import ChatPanel from './components/ChatPanel'
import SummaryPanel from './components/SummaryPanel'
import type { UploadedDocument, ChatMessage } from './types'

type Tab = 'chat' | 'summary'

export default function App() {
  const [documents, setDocuments] = useState<UploadedDocument[]>([])
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([])
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [activeTab, setActiveTab] = useState<Tab>('chat')

  const handleUploaded = useCallback((docs: UploadedDocument[]) => {
    setDocuments((prev) => {
      const existingIds = new Set(prev.map((d) => d.docId))
      const newDocs = docs.filter((d) => !existingIds.has(d.docId))
      return [...prev, ...newDocs]
    })
    setSelectedDocIds((prev) => {
      const incoming = docs.map((d) => d.docId)
      return Array.from(new Set([...prev, ...incoming]))
    })
  }, [])

  const handleRemoveDoc = useCallback((docId: string) => {
    setDocuments((prev) => prev.filter((d) => d.docId !== docId))
    setSelectedDocIds((prev) => prev.filter((id) => id !== docId))
    setMessages((prev) =>
      prev.filter((m) => !m.sources?.every((s) => s.docId === docId))
    )
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <div className="app-header-logo">DocTalk</div>
          <div className="app-header-subtitle">Belgelerinizle konuşun</div>
        </div>
      </header>

      <div className="app-body">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="sidebar-section">
            <div className="sidebar-section-title">Belge Yükle</div>
            <DocumentUploader onUploaded={handleUploaded} />
          </div>

          <div className="sidebar-docs">
            <div className="sidebar-section-title">Yüklenen Belgeler</div>
            <DocumentList
              documents={documents}
              selectedDocIds={selectedDocIds}
              onSelectionChange={setSelectedDocIds}
              onRemove={handleRemoveDoc}
            />
          </div>
        </aside>

        {/* Main */}
        <main className="main-panel">
          <div className="tabs">
            <button
              className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              Sohbet
            </button>
            <button
              className={`tab-btn ${activeTab === 'summary' ? 'active' : ''}`}
              onClick={() => setActiveTab('summary')}
            >
              Özetleme
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'chat' ? (
              <ChatPanel
                messages={messages}
                onMessagesChange={setMessages}
                selectedDocIds={selectedDocIds}
                hasDocuments={documents.length > 0}
              />
            ) : (
              <SummaryPanel
                documents={documents}
                selectedDocIds={selectedDocIds}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
