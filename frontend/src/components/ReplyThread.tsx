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
    <div
      className={`mt-3 ${depth > 0 ? 'ml-6 border-l-2 border-gray-200 pl-4' : ''}`}
    >
      <div className="bg-white rounded shadow-sm p-3">
        <p className="text-xs text-gray-500 mb-1">
          <span className="font-medium text-gray-700">{reply.authorname ?? reply.userid}</span>
          {' · '}
          {new Date(reply.createdat).toLocaleString()}
        </p>
        <p className="text-sm text-gray-800 whitespace-pre-wrap">{reply.content}</p>
      </div>

      {reply.children?.map((child) => (
        <ReplyThread key={child.replyid} reply={child as never} depth={depth + 1} />
      ))}
    </div>
  )
}
