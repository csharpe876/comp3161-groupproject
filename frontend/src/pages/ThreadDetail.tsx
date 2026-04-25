import { useEffect, useState, type FormEvent } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../services/api'
import ReplyThread from '../components/ReplyThread'

export interface Reply {
  replyid: number
  threadid: number
  parentreplyid: number | null
  userid: string
  authorname: string
  content: string
  createdat: string
  depth: number
}

interface ReplyNode extends Reply {
  children: ReplyNode[]
}

/** Build a tree from the flat depth-ordered list returned by the API. */
function buildTree(flat: Reply[]): ReplyNode[] {
  const map = new Map<number, ReplyNode>()
  const roots: ReplyNode[] = []

  for (const r of flat) {
    map.set(r.replyid, { ...r, children: [] })
  }
  for (const node of map.values()) {
    if (node.parentreplyid === null) {
      roots.push(node)
    } else {
      const parent = map.get(node.parentreplyid)
      parent?.children.push(node)
    }
  }
  return roots
}

export default function ThreadDetail() {
  const { courseId, forumId, threadId } = useParams<{
    courseId: string
    forumId: string
    threadId: string
  }>()

  const [thread,  setThread]  = useState<{ title: string; content: string; authorname: string; createdat: string } | null>(null)
  const [replies, setReplies] = useState<ReplyNode[]>([])
  const [loading, setLoading] = useState(true)
  const [content, setContent] = useState('')
  const [msg,     setMsg]     = useState('')

  async function loadThread() {
    const { data } = await api.get(`/threads/${threadId}`)
    setThread(data.thread)
    setReplies(buildTree(data.replies as Reply[]))
    setLoading(false)
  }

  useEffect(() => { loadThread() }, [threadId])  // eslint-disable-line

  async function handleReply(e: FormEvent) {
    e.preventDefault()
    await api.post(`/threads/${threadId}/replies`, { content })
    setContent('')
    setMsg('Reply posted!')
    loadThread()
  }

  if (loading) return <p className="text-gray-500">Loading…</p>
  if (!thread) return null

  return (
    <div>
      <Link
        to={`/courses/${courseId}/forums/${forumId}`}
        className="text-indigo-500 text-sm hover:underline"
      >
        ← Back to forum
      </Link>

      {/* Original post */}
      <div className="mt-4 bg-white rounded-xl shadow p-5 border border-gray-100">
        <h1 className="text-xl font-bold text-gray-800 mb-1">{thread.title}</h1>
        <p className="text-xs text-gray-500 mb-3">
          by {thread.authorname} · {new Date(thread.createdat).toLocaleString()}
        </p>
        <p className="text-sm text-gray-700 whitespace-pre-wrap">{thread.content}</p>
      </div>

      {/* Reply tree */}
      <div className="mt-6">
        <h2 className="text-sm font-semibold text-gray-600 mb-2">
          {replies.length} {replies.length === 1 ? 'reply' : 'replies'}
        </h2>
        {replies.map((r) => (
          <ReplyThread key={r.replyid} reply={r} />
        ))}
      </div>

      {/* Reply form */}
      {msg && <p className="text-green-600 text-sm mt-4">{msg}</p>}
      <form onSubmit={handleReply} className="mt-6 bg-gray-50 rounded-lg p-4 space-y-3">
        <h3 className="font-medium text-gray-700">Add a reply</h3>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
          rows={3}
          placeholder="Write your reply…"
          className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
        <button className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-5 py-2 rounded transition-colors">
          Reply
        </button>
      </form>
    </div>
  )
}
