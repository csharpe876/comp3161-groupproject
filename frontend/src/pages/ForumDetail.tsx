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
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-xs text-neutral-400 mb-5">
        <Link to="/" className="hover:text-primary no-underline transition-colors">Dashboard</Link>
        <span>/</span>
        <Link to={`/courses/${courseId}`} className="hover:text-primary no-underline transition-colors">
          Course
        </Link>
        <span>/</span>
        <span className="text-neutral-700 font-medium">{forumTitle}</span>
      </nav>

      {/* Forum header */}
      <div className="bg-secondary rounded-2xl px-6 py-5 mb-6 text-white flex items-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center text-2xl flex-shrink-0">
          💬
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">{forumTitle}</h1>
          <p className="text-white/60 text-sm mt-0.5">{threads.length} thread{threads.length !== 1 ? 's' : ''}</p>
        </div>
      </div>

      <div className="space-y-2 mb-8">
        {threads.length === 0 && (
          <p className="text-neutral-400 text-sm">No threads yet. Start one below.</p>
        )}
        {threads.map((t) => (
          <Link
            key={t.threadid}
            to={`/courses/${courseId}/forums/${forumId}/threads/${t.threadid}`}
            className="flex items-center gap-4 bg-white rounded-xl border border-neutral-100
                       shadow-card hover:shadow-card-hover transition-shadow no-underline group px-5 py-4"
          >
            {/* Author initial avatar */}
            <div className="w-9 h-9 rounded-full bg-primary-50 text-primary font-bold
                            flex items-center justify-center text-sm flex-shrink-0">
              {t.authorname.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-neutral-900 group-hover:text-primary
                            transition-colors text-sm truncate">
                {t.title}
              </p>
              <p className="text-xs text-neutral-400 mt-0.5">
                by {t.authorname} &middot; {new Date(t.createdat).toLocaleDateString()}
              </p>
            </div>
            <span className="flex-shrink-0 text-xs text-neutral-400">
              {t.replycount} {t.replycount === 1 ? 'reply' : 'replies'}
            </span>
          </Link>
        ))}
      </div>

      {msg && <p className="text-success text-sm mb-3 font-medium">{msg}</p>}

      <div className="bg-white rounded-xl border border-neutral-100 shadow-card p-5">
        <h3 className="font-semibold text-neutral-800 mb-4 text-sm">Start a new thread</h3>
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
