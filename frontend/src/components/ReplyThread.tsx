/**
 * Recursive reply component — renders a reply and all its nested children.
 * The flat reply list from the API is converted into a tree on first render.
 */
import type { Reply } from '../pages/ThreadDetail'

interface Props {
  reply: Reply & { children: (Reply & { children: Reply[] })[] }
  depth?: number
}

export default function ReplyThread({ reply, depth = 0 }: Props) {
  return (
    <div className={`mt-3 ${depth > 0 ? 'ml-6 border-l-2 border-primary-100 pl-4' : ''}`}>
      <div className="bg-white rounded-xl border border-neutral-100 shadow-card p-4">
        <p className="text-xs text-neutral-400 mb-2">
          <span className="font-semibold text-neutral-700">
            {reply.authorname ?? reply.userid}
          </span>
          {' · '}
          {new Date(reply.createdat).toLocaleString()}
        </p>
        <p className="text-sm text-neutral-800 whitespace-pre-wrap leading-relaxed">
          {reply.content}
        </p>
      </div>

      {reply.children?.map((child) => (
        <ReplyThread key={child.replyid} reply={child as never} depth={depth + 1} />
      ))}
    </div>
  )
}
