import { useRef, useState, useCallback } from 'react'
import { apiUpload } from '../api/client'
import type { UploadedDocument } from '../types'
import './DocumentUploader.css'

interface Props {
  onUploaded: (docs: UploadedDocument[]) => void
}

const ACCEPTED = '.pdf,.docx,.txt'

export default function DocumentUploader({ onUploaded }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [pending, setPending] = useState<File[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const addFiles = useCallback((incoming: FileList | File[]) => {
    const allowed = Array.from(incoming).filter((f) =>
      /\.(pdf|docx|txt)$/i.test(f.name)
    )
    const invalid = Array.from(incoming).filter(
      (f) => !/\.(pdf|docx|txt)$/i.test(f.name)
    )
    if (invalid.length) {
      setError(`Desteklenmeyen dosya: ${invalid.map((f) => f.name).join(', ')}`)
    } else {
      setError(null)
    }
    setPending((prev) => {
      const existing = new Set(prev.map((f) => f.name))
      return [...prev, ...allowed.filter((f) => !existing.has(f.name))]
    })
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      addFiles(e.dataTransfer.files)
    },
    [addFiles]
  )

  const handleUpload = async () => {
    if (!pending.length) return
    setLoading(true)
    setError(null)
    try {
      const docs = await apiUpload(pending)
      onUploaded(docs)
      setPending([])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Yükleme başarısız')
    } finally {
      setLoading(false)
    }
  }

  const removePending = (name: string) =>
    setPending((prev) => prev.filter((f) => f.name !== name))

  return (
    <div className="uploader">
      <div
        className={`drop-zone ${isDragging ? 'dragging' : ''}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        <svg className="drop-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
        </svg>
        <span className="drop-text">
          {isDragging ? 'Bırakın...' : 'Sürükleyin veya tıklayın'}
        </span>
        <span className="drop-hint">PDF, DOCX, TXT</span>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          multiple
          style={{ display: 'none' }}
          onChange={(e) => e.target.files && addFiles(e.target.files)}
        />
      </div>

      {pending.length > 0 && (
        <ul className="pending-list">
          {pending.map((f) => (
            <li key={f.name} className="pending-item">
              <span className="pending-name" title={f.name}>{f.name}</span>
              <span className="pending-size">{(f.size / 1024).toFixed(0)} KB</span>
              <button
                className="pending-remove"
                onClick={() => removePending(f.name)}
                title="Kaldır"
              >×</button>
            </li>
          ))}
        </ul>
      )}

      {error && <div className="uploader-error">{error}</div>}

      <button
        className="upload-btn"
        onClick={handleUpload}
        disabled={loading || pending.length === 0}
      >
        {loading
          ? 'Yükleniyor...'
          : pending.length
            ? `${pending.length} dosyayı yükle`
            : 'Dosya seçin'}
      </button>
    </div>
  )
}
