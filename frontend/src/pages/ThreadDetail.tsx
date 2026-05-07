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

  if (loading) return (
    <div className="flex items-center justify-center py-16 text-neutral-400 text-sm">Loading…</div>
  )
  if (!thread) return null

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
        <Link to={`/courses/${courseId}/forums/${forumId}`} className="hover:text-primary no-underline transition-colors">
          Forum
        </Link>
        <span>/</span>
        <span className="text-neutral-700 font-medium truncate max-w-xs">{thread.title}</span>
      </nav>

      {/* Original post */}
      <div className="bg-secondary rounded-2xl p-6 mb-6 text-white">
        <h1 className="text-xl font-bold text-white mb-2">{thread.title}</h1>
        <div className="flex items-center gap-2 mb-4">
          <div className="w-7 h-7 rounded-full bg-white/20 flex items-center justify-center
                          text-white text-xs font-bold">
            {thread.authorname.charAt(0).toUpperCase()}
          </div>
          <span className="text-white/70 text-sm">
            {thread.authorname} &middot; {new Date(thread.createdat).toLocaleString()}
          </span>
        </div>
        <p className="text-white/85 text-sm whitespace-pre-wrap leading-relaxed">
          {thread.content}
        </p>
      </div>

      {/* Reply tree */}
      <div className="mb-6">
        <h2 className="text-xs font-semibold text-neutral-400 uppercase tracking-wide mb-3">
          {replies.length} {replies.length === 1 ? 'reply' : 'replies'}
        </h2>
        {replies.map((r) => (
          <ReplyThread key={r.replyid} reply={r} />
        ))}
      </div>

      {/* Reply form */}
      {msg && <p className="text-success text-sm mt-4 font-medium">{msg}</p>}
      <form onSubmit={handleReply} className="mt-4 bg-white rounded-xl border border-neutral-100 shadow-card p-5 space-y-3">
        <h3 className="font-semibold text-neutral-800 text-sm">Add a reply</h3>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
          rows={3}
          placeholder="Write your reply…"
          className="input-field"
        />
        <button className="btn-primary">Reply</button>
      </form>
    </div>
  )
}
