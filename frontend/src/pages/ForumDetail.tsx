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

  if (loading) return <p className="text-gray-500">Loading…</p>

  return (
    <div>
      <Link to={`/courses/${courseId}`} className="text-indigo-500 text-sm hover:underline">
        ← Back to course
      </Link>
      <h1 className="text-2xl font-bold text-gray-800 mt-2 mb-6">{forumTitle}</h1>

      <div className="space-y-3 mb-8">
        {threads.map((t) => (
          <Link
            key={t.threadid}
            to={`/courses/${courseId}/forums/${forumId}/threads/${t.threadid}`}
            className="block bg-white rounded-lg shadow-sm p-4 hover:shadow-md border border-gray-100 transition-shadow"
          >
            <p className="font-semibold text-gray-800">{t.title}</p>
            <p className="text-xs text-gray-500 mt-1">
              by {t.authorname} · {new Date(t.createdat).toLocaleString()} · {t.replycount} replies
            </p>
          </Link>
        ))}
        {threads.length === 0 && <p className="text-gray-400 text-sm">No threads yet. Start one below.</p>}
      </div>

      {msg && <p className="text-green-600 text-sm mb-3">{msg}</p>}

      <div className="bg-gray-50 rounded-lg p-5">
        <h3 className="font-semibold text-gray-700 mb-3">Start a new thread</h3>
        <form onSubmit={handleCreate} className="space-y-3">
          <input
            placeholder="Title"
            value={newThread.title}
            onChange={(e) => setNewThread(t => ({ ...t, title: e.target.value }))}
            required
            className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
          <textarea
            placeholder="Post content…"
            value={newThread.content}
            onChange={(e) => setNewThread(t => ({ ...t, content: e.target.value }))}
            required
            rows={4}
            className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
          <button className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-5 py-2 rounded transition-colors">
            Post Thread
          </button>
        </form>
      </div>
    </div>
  )
}
