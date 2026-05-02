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
      <Link
        to={`/courses/${courseId}/forums/${forumId}`}
        className="inline-flex items-center gap-1 text-sm text-neutral-400
                   hover:text-primary transition-colors no-underline"
      >
        ← Back to forum
      </Link>

      {/* Original post */}
      <div className="mt-4 card">
        <h1 className="text-xl font-bold text-neutral-900 mb-1">{thread.title}</h1>
        <p className="text-xs text-neutral-400 mb-4">
          by {thread.authorname} · {new Date(thread.createdat).toLocaleString()}
        </p>
        <p className="text-sm text-neutral-700 whitespace-pre-wrap leading-relaxed">
          {thread.content}
        </p>
      </div>

      {/* Reply tree */}
      <div className="mt-6">
        <h2 className="text-sm font-semibold text-neutral-500 mb-3">
          {replies.length} {replies.length === 1 ? 'reply' : 'replies'}
        </h2>
        {replies.map((r) => (
          <ReplyThread key={r.replyid} reply={r} />
        ))}
      </div>

      {/* Reply form */}
      {msg && <p className="text-success text-sm mt-4 font-medium">{msg}</p>}
      <form onSubmit={handleReply} className="mt-6 card space-y-3">
        <h3 className="font-semibold text-neutral-800">Add a reply</h3>
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
