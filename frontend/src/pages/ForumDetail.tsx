import { useEffect, useState, type FormEvent } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../services/api'

interface Thread {
  threadid: number
  title: string
  authorname: string
  createdat: string
  replycount: number
}

export default function ForumDetail() {
  const { courseId, forumId } = useParams<{ courseId: string; forumId: string }>()

  const [forumTitle, setForumTitle] = useState('')
  const [threads,    setThreads]    = useState<Thread[]>([])
  const [loading,    setLoading]    = useState(true)
  const [newThread,  setNewThread]  = useState({ title: '', content: '' })
  const [msg,        setMsg]        = useState('')

  useEffect(() => {
    async function load() {
      const { data } = await api.get(`/forums/${forumId}/threads`)
      setForumTitle(data.forum.title)
      setThreads(data.threads)
      setLoading(false)
    }
    load()
  }, [forumId])

  async function handleCreate(e: FormEvent) {
    e.preventDefault()
    await api.post(`/forums/${forumId}/threads`, newThread)
    setMsg('Thread created!')
    setNewThread({ title: '', content: '' })
    const { data } = await api.get(`/forums/${forumId}/threads`)
    setThreads(data.threads)
  }

  if (loading) return (
    <div className="flex items-center justify-center py-16 text-neutral-400 text-sm">Loading…</div>
  )

  return (
    <div>
      <Link
        to={`/courses/${courseId}`}
        className="inline-flex items-center gap-1 text-sm text-neutral-400
                   hover:text-primary transition-colors no-underline"
      >
        ← Back to course
      </Link>

      <div className="page-header mt-3">
        <h1 className="page-title">{forumTitle}</h1>
      </div>

      <div className="space-y-3 mb-8">
        {threads.map((t) => (
          <Link
            key={t.threadid}
            to={`/courses/${courseId}/forums/${forumId}/threads/${t.threadid}`}
            className="card-hover no-underline block group"
          >
            <p className="font-semibold text-neutral-900 group-hover:text-primary transition-colors">
              {t.title}
            </p>
            <p className="text-xs text-neutral-400 mt-1">
              by {t.authorname}
              {' · '}
              {new Date(t.createdat).toLocaleString()}
              {' · '}
              {t.replycount} {t.replycount === 1 ? 'reply' : 'replies'}
            </p>
          </Link>
        ))}
        {threads.length === 0 && (
          <p className="text-neutral-400 text-sm">No threads yet. Start one below.</p>
        )}
      </div>

      {msg && <p className="text-success text-sm mb-3 font-medium">{msg}</p>}

      <div className="card">
        <h3 className="font-semibold text-neutral-800 mb-4">Start a new thread</h3>
        <form onSubmit={handleCreate} className="space-y-3">
          <input
            placeholder="Title"
            value={newThread.title}
            onChange={(e) => setNewThread(t => ({ ...t, title: e.target.value }))}
            required
            className="input-field"
          />
          <textarea
            placeholder="Post content…"
            value={newThread.content}
            onChange={(e) => setNewThread(t => ({ ...t, content: e.target.value }))}
            required
            rows={4}
            className="input-field"
          />
          <button className="btn-primary">Post Thread</button>
        </form>
      </div>
    </div>
  )
}
