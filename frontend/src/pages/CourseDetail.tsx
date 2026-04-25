import { useEffect, useState, type FormEvent } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'

type Tab = 'overview' | 'content' | 'forums' | 'calendar' | 'assignments' | 'members'

interface Course {
  courseid: string
  coursetitle: string
  coursecode: string
  description: string | null
  lecturername: string | null
  lecid: string | null
}

interface Forum  { forumid: number; title: string; description: string; threadcount: number }
interface Event  { eventid: number; title: string; eventdate: string; eventtime: string | null; description: string }
interface Section { sectionid: number; sectionname: string; content: ContentItem[] }
interface ContentItem { contentid: number; title: string; contenttype: string; contenturl: string }
interface Assignment { assignmentid: number; title: string; description: string; duedate: string | null; maxgrade: number }
interface Member { userid: string; name: string; email: string }

export default function CourseDetail() {
  const { courseId } = useParams<{ courseId: string }>()
  const { user }     = useAuth()

  const [tab,     setTab]     = useState<Tab>('overview')
  const [course,  setCourse]  = useState<Course | null>(null)
  const [forums,  setForums]  = useState<Forum[]>([])
  const [events,  setEvents]  = useState<Event[]>([])
  const [sections,setSections]= useState<Section[]>([])
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [members, setMembers] = useState<{ lecturer: Member | null; students: Member[] } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  // Forms
  const [newEvent,   setNewEvent]   = useState({ title: '', event_date: '', event_time: '', description: '' })
  const [newForum,   setNewForum]   = useState({ title: '', description: '' })
  const [newSection, setNewSection] = useState({ section_name: '', order_index: 0 })
  const [newAssign,  setNewAssign]  = useState({ title: '', description: '', due_date: '', max_grade: 100 })
  const [submitMsg,  setSubmitMsg]  = useState('')

  const isLecturerOrAdmin = user?.account_type === 'Lecturer' || user?.account_type === 'Admin'

  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.get(`/courses/${courseId}`)
        setCourse(data)
      } catch { setError('Course not found') }
      finally  { setLoading(false) }
    }
    load()
  }, [courseId])

  useEffect(() => {
    if (!courseId) return
    if (tab === 'forums')      api.get(`/courses/${courseId}/forums`).then(r => setForums(r.data))
    if (tab === 'calendar')    api.get(`/courses/${courseId}/events`).then(r => setEvents(r.data))
    if (tab === 'content')     api.get(`/courses/${courseId}/content`).then(r => setSections(r.data.sections))
    if (tab === 'assignments') api.get(`/courses/${courseId}/assignments`).then(r => setAssignments(r.data))
    if (tab === 'members')     api.get(`/courses/${courseId}/members`).then(r => setMembers(r.data))
  }, [tab, courseId])

  async function submitEvent(e: FormEvent) {
    e.preventDefault()
    await api.post(`/courses/${courseId}/events`, newEvent)
    setSubmitMsg('Event created!')
    api.get(`/courses/${courseId}/events`).then(r => setEvents(r.data))
    setNewEvent({ title: '', event_date: '', event_time: '', description: '' })
  }

  async function submitForum(e: FormEvent) {
    e.preventDefault()
    await api.post(`/courses/${courseId}/forums`, newForum)
    setSubmitMsg('Forum created!')
    api.get(`/courses/${courseId}/forums`).then(r => setForums(r.data))
    setNewForum({ title: '', description: '' })
  }

  async function submitSection(e: FormEvent) {
    e.preventDefault()
    await api.post(`/courses/${courseId}/sections`, newSection)
    setSubmitMsg('Section created!')
    api.get(`/courses/${courseId}/content`).then(r => setSections(r.data.sections))
    setNewSection({ section_name: '', order_index: 0 })
  }

  async function submitAssignment(e: FormEvent) {
    e.preventDefault()
    await api.post(`/courses/${courseId}/assignments`, newAssign)
    setSubmitMsg('Assignment created!')
    api.get(`/courses/${courseId}/assignments`).then(r => setAssignments(r.data))
    setNewAssign({ title: '', description: '', due_date: '', max_grade: 100 })
  }

  async function enroll() {
    await api.post(`/courses/${courseId}/enroll`)
    setSubmitMsg('Enrolled successfully!')
  }

  if (loading) return <p className="text-gray-500">Loading…</p>
  if (error)   return <p className="text-red-600">{error}</p>
  if (!course) return null

  const tabs: { id: Tab; label: string }[] = [
    { id: 'overview',    label: 'Overview' },
    { id: 'content',     label: 'Content' },
    { id: 'forums',      label: 'Forums' },
    { id: 'calendar',    label: 'Calendar' },
    { id: 'assignments', label: 'Assignments' },
    { id: 'members',     label: 'Members' },
  ]

  return (
    <div>
      <div className="mb-1">
        <span className="text-xs font-semibold bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded uppercase">
          {course.coursecode}
        </span>
      </div>
      <h1 className="text-2xl font-bold text-gray-800 mb-1">{course.coursetitle}</h1>
      {course.lecturername && <p className="text-sm text-gray-500 mb-4">Lecturer: {course.lecturername}</p>}
      {course.description   && <p className="text-sm text-gray-600 mb-4">{course.description}</p>}

      {user?.account_type === 'Student' && (
        <button
          onClick={enroll}
          className="mb-4 bg-green-600 hover:bg-green-700 text-white text-sm px-4 py-1.5 rounded transition-colors"
        >
          Enrol in this course
        </button>
      )}
      {submitMsg && <p className="text-green-600 text-sm mb-3">{submitMsg}</p>}

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6 gap-1">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => { setTab(t.id); setSubmitMsg('') }}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              tab === t.id
                ? 'border-b-2 border-indigo-600 text-indigo-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* ── Overview ── */}
      {tab === 'overview' && (
        <div className="text-gray-700 text-sm space-y-2">
          <p><strong>Course ID:</strong> {course.courseid}</p>
          <p><strong>Code:</strong> {course.coursecode}</p>
          <p><strong>Lecturer:</strong> {course.lecturername ?? 'Unassigned'}</p>
          <p><strong>Description:</strong> {course.description ?? '—'}</p>
        </div>
      )}

      {/* ── Content ── */}
      {tab === 'content' && (
        <div>
          {sections.map((sec) => (
            <div key={sec.sectionid} className="mb-6">
              <h3 className="font-semibold text-gray-700 mb-2">{sec.sectionname}</h3>
              <ul className="space-y-1">
                {sec.content.map((item) => (
                  <li key={item.contentid} className="flex items-center gap-2 text-sm">
                    <span className="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded uppercase">
                      {item.contenttype}
                    </span>
                    <a
                      href={item.contenturl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-indigo-600 hover:underline"
                    >
                      {item.title}
                    </a>
                  </li>
                ))}
                {sec.content.length === 0 && (
                  <li className="text-gray-400 text-xs">No content yet.</li>
                )}
              </ul>
            </div>
          ))}
          {sections.length === 0 && <p className="text-gray-400 text-sm">No sections yet.</p>}

          {isLecturerOrAdmin && (
            <form onSubmit={submitSection} className="mt-6 bg-gray-50 rounded-lg p-4 space-y-3">
              <h4 className="font-medium text-gray-700">Add Section</h4>
              <input
                placeholder="Section name"
                value={newSection.section_name}
                onChange={(e) => setNewSection(s => ({ ...s, section_name: e.target.value }))}
                required
                className="w-full border rounded px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:outline-none"
              />
              <button className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-4 py-1.5 rounded">
                Add Section
              </button>
            </form>
          )}
        </div>
      )}

      {/* ── Forums ── */}
      {tab === 'forums' && (
        <div>
          <div className="space-y-3">
            {forums.map((f) => (
              <Link
                key={f.forumid}
                to={`/courses/${courseId}/forums/${f.forumid}`}
                className="block bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow border border-gray-100"
              >
                <p className="font-semibold text-gray-800">{f.title}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {f.description}  &middot; {f.threadcount} threads
                </p>
              </Link>
            ))}
            {forums.length === 0 && <p className="text-gray-400 text-sm">No forums yet.</p>}
          </div>

          {isLecturerOrAdmin && (
            <form onSubmit={submitForum} className="mt-6 bg-gray-50 rounded-lg p-4 space-y-3">
              <h4 className="font-medium text-gray-700">Create Forum</h4>
              <input
                placeholder="Forum title"
                value={newForum.title}
                onChange={(e) => setNewForum(f => ({ ...f, title: e.target.value }))}
                required
                className="w-full border rounded px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:outline-none"
              />
              <input
                placeholder="Description (optional)"
                value={newForum.description}
                onChange={(e) => setNewForum(f => ({ ...f, description: e.target.value }))}
                className="w-full border rounded px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:outline-none"
              />
              <button className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-4 py-1.5 rounded">
                Create
              </button>
            </form>
          )}
        </div>
      )}

      {/* ── Calendar ── */}
      {tab === 'calendar' && (
        <div>
          <ul className="space-y-3">
            {events.map((ev) => (
              <li key={ev.eventid} className="bg-white rounded-lg shadow-sm p-4 border border-gray-100">
                <p className="font-semibold text-gray-800">{ev.title}</p>
                <p className="text-xs text-indigo-600">
                  {ev.eventdate}{ev.eventtime ? ` at ${ev.eventtime}` : ''}
                </p>
                {ev.description && <p className="text-sm text-gray-600 mt-1">{ev.description}</p>}
              </li>
            ))}
            {events.length === 0 && <p className="text-gray-400 text-sm">No events scheduled.</p>}
          </ul>

          {isLecturerOrAdmin && (
            <form onSubmit={submitEvent} className="mt-6 bg-gray-50 rounded-lg p-4 space-y-3">
              <h4 className="font-medium text-gray-700">Add Calendar Event</h4>
              <input
                placeholder="Event title"
                value={newEvent.title}
                onChange={(e) => setNewEvent(v => ({ ...v, title: e.target.value }))}
                required
                className="w-full border rounded px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:outline-none"
              />
              <div className="flex gap-2">
                <input type="date" value={newEvent.event_date}
                  onChange={(e) => setNewEvent(v => ({ ...v, event_date: e.target.value }))}
                  required
                  className="flex-1 border rounded px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:outline-none"
                />
                <input type="time" value={newEvent.event_time}
                  onChange={(e) => setNewEvent(v => ({ ...v, event_time: e.target.value }))}
                  className="flex-1 border rounded px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:outline-none"
                />
              </div>
              <textarea
                placeholder="Description (optional)"
                value={newEvent.description}
                onChange={(e) => setNewEvent(v => ({ ...v, description: e.target.value }))}
                rows={2}
                className="w-full border rounded px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:outline-none"
              />
              <button className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-4 py-1.5 rounded">
                Add Event
              </button>
            </form>
          )}
        </div>
      )}

      {/* ── Assignments ── */}
      {tab === 'assignments' && (
        <div>
          <ul className="space-y-3">
            {assignments.map((a) => (
              <li key={a.assignmentid} className="bg-white rounded-lg shadow-sm p-4 border border-gray-100">
                <p className="font-semibold text-gray-800">{a.title}</p>
                {a.duedate && (
                  <p className="text-xs text-red-500">Due: {new Date(a.duedate).toLocaleString()}</p>
                )}
                <p className="text-xs text-gray-500">Max grade: {a.maxgrade}</p>
                {a.description && <p className="text-sm text-gray-600 mt-1">{a.description}</p>}
              </li>
            ))}
            {assignments.length === 0 && (
              <p className="text-gray-400 text-sm">No assignments yet.</p>
            )}
          </ul>

          {isLecturerOrAdmin && (
            <form onSubmit={submitAssignment} className="mt-6 bg-gray-50 rounded-lg p-4 space-y-3">
              <h4 className="font-medium text-gray-700">Create Assignment</h4>
              <input
                placeholder="Title"
                value={newAssign.title}
                onChange={(e) => setNewAssign(v => ({ ...v, title: e.target.value }))}
                required
                className="w-full border rounded px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:outline-none"
              />
              <textarea
                placeholder="Description"
                value={newAssign.description}
                onChange={(e) => setNewAssign(v => ({ ...v, description: e.target.value }))}
                rows={2}
                className="w-full border rounded px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:outline-none"
              />
              <div className="flex gap-2">
                <input
                  type="datetime-local"
                  value={newAssign.due_date}
                  onChange={(e) => setNewAssign(v => ({ ...v, due_date: e.target.value }))}
                  className="flex-1 border rounded px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:outline-none"
                />
                <input
                  type="number"
                  placeholder="Max grade"
                  value={newAssign.max_grade}
                  onChange={(e) => setNewAssign(v => ({ ...v, max_grade: Number(e.target.value) }))}
                  className="w-28 border rounded px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:outline-none"
                />
              </div>
              <button className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-4 py-1.5 rounded">
                Create Assignment
              </button>
            </form>
          )}
        </div>
      )}

      {/* ── Members ── */}
      {tab === 'members' && members && (
        <div>
          {members.lecturer && (
            <div className="mb-4">
              <h3 className="font-semibold text-gray-700 mb-1">Lecturer</h3>
              <div className="bg-white rounded-lg shadow-sm p-3 border border-gray-100 text-sm">
                {members.lecturer.name} &lt;{members.lecturer.email}&gt;
              </div>
            </div>
          )}
          <h3 className="font-semibold text-gray-700 mb-2">
            Students ({members.students.length})
          </h3>
          <ul className="space-y-1">
            {members.students.map((s) => (
              <li key={s.userid} className="bg-white rounded px-3 py-2 text-sm border border-gray-100">
                {s.name} &lt;{s.email}&gt;
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
