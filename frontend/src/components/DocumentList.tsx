import type { UploadedDocument } from '../types'
import './DocumentList.css'

interface Props {
  documents: UploadedDocument[]
  selectedDocIds: string[]
  onSelectionChange: (ids: string[]) => void
  onRemove: (docId: string) => void
}

function fileIcon(name: string): string {
  const ext = name.split('.').pop()?.toLowerCase()
  if (ext === 'pdf') return '📄'
  if (ext === 'docx') return '📝'
  return '📃'
}

export default function DocumentList({ documents, selectedDocIds, onSelectionChange, onRemove }: Props) {
  if (documents.length === 0) {
    return (
      <div className="doclist-empty">
        <span>Henüz belge yüklenmedi.</span>
        <span className="doclist-empty-hint">Belge yükledikten sonra burada görünür.</span>
      </div>
    )
  }

  const allSelected = documents.every((d) => selectedDocIds.includes(d.docId))

  const toggleAll = () => {
    if (allSelected) {
      onSelectionChange([])
    } else {
      onSelectionChange(documents.map((d) => d.docId))
    }
  }

  const toggleOne = (docId: string) => {
    if (selectedDocIds.includes(docId)) {
      onSelectionChange(selectedDocIds.filter((id) => id !== docId))
    } else {
      onSelectionChange([...selectedDocIds, docId])
    }
  }

  return (
    <div className="doclist">
      <div className="doclist-header">
        <label className="doclist-check-label">
          <input
            type="checkbox"
            checked={allSelected}
            onChange={toggleAll}
          />
          <span>Tümünü seç</span>
        </label>
        <span className="doclist-count">{documents.length} belge</span>
      </div>

      <ul className="doclist-items">
        {documents.map((doc) => {
          const selected = selectedDocIds.includes(doc.docId)
          return (
            <li key={doc.docId} className={`doclist-item ${selected ? 'selected' : ''}`}>
              <input
                type="checkbox"
                checked={selected}
                onChange={() => toggleOne(doc.docId)}
                className="doclist-checkbox"
              />
              <span className="doclist-icon">{fileIcon(doc.docName)}</span>
              <div className="doclist-info">
                <span className="doclist-name" title={doc.docName}>{doc.docName}</span>
                <span className="doclist-meta">{doc.totalChunks} parça</span>
              </div>
              <button
                className="doclist-remove"
                onClick={() => onRemove(doc.docId)}
                title="Kaldır"
              >
                <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                  <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </button>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
