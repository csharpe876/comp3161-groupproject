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

interface Forum       { forumid: number; title: string; description: string; threadcount: number }
interface Event       { eventid: number; title: string; eventdate: string; eventtime: string | null; description: string }
interface Section     { sectionid: number; sectionname: string; content: ContentItem[] }
interface ContentItem { contentid: number; title: string; contenttype: string; contenturl: string }
interface Assignment  { assignmentid: number; title: string; description: string; duedate: string | null; maxgrade: number }
interface Member      { userid: string; name: string; email: string }

const inputCls = 'input-field'
const btnCls   = 'btn-primary !py-2 !text-xs'

export default function CourseDetail() {
  const { courseId } = useParams<{ courseId: string }>()
  const { user }     = useAuth()

  const [tab,         setTab]         = useState<Tab>('overview')
  const [course,      setCourse]      = useState<Course | null>(null)
  const [forums,      setForums]      = useState<Forum[]>([])
  const [events,      setEvents]      = useState<Event[]>([])
  const [sections,    setSections]    = useState<Section[]>([])
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [members,     setMembers]     = useState<{ lecturer: Member | null; students: Member[] } | null>(null)
  const [loading,     setLoading]     = useState(true)
  const [error,       setError]       = useState('')

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
      } catch {
        setError('Course not found')
      } finally {
        setLoading(false)
      }
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

  if (loading) return (
    <div className="flex items-center justify-center py-16 text-neutral-400 text-sm">Loading…</div>
  )
  if (error) return (
    <div className="bg-red-50 border border-red-200 text-error rounded-xl px-4 py-3 text-sm">{error}</div>
  )
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
      {/* Course header */}
      <div className="page-header">
        <span className="badge-primary uppercase tracking-wide text-[10px]">
          {course.coursecode}
        </span>
        <h1 className="page-title mt-2">{course.coursetitle}</h1>
        {course.lecturername && (
          <p className="page-subtitle">Lecturer: {course.lecturername}</p>
        )}
        {course.description && (
          <p className="mt-2 text-sm text-neutral-500">{course.description}</p>
        )}
        <div className="mt-4 flex items-center gap-3">
          {user?.account_type === 'Student' && (
            <button onClick={enroll} className="btn-primary !py-2 !text-xs">
              Enrol in course
            </button>
          )}
          {submitMsg && (
            <span className="text-success text-sm font-medium">{submitMsg}</span>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-neutral-100 mb-6 gap-0.5">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => { setTab(t.id); setSubmitMsg('') }}
            className={`px-4 py-2.5 text-sm font-medium transition-colors rounded-t-lg ${
              tab === t.id
                ? 'text-primary border-b-2 border-primary bg-primary-50/50'
                : 'text-neutral-400 hover:text-neutral-700 hover:bg-neutral-50'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* ── Overview ── */}
      {tab === 'overview' && (
        <div className="card max-w-lg space-y-3 text-sm text-neutral-700">
          <p><span className="font-semibold text-neutral-900">Course ID:</span> {course.courseid}</p>
          <p><span className="font-semibold text-neutral-900">Code:</span> {course.coursecode}</p>
          <p><span className="font-semibold text-neutral-900">Lecturer:</span> {course.lecturername ?? 'Unassigned'}</p>
          <p><span className="font-semibold text-neutral-900">Description:</span> {course.description ?? '—'}</p>
        </div>
      )}

      {/* ── Content ── */}
      {tab === 'content' && (
        <div>
          {sections.map((sec) => (
            <div key={sec.sectionid} className="mb-6">
              <h3 className="font-semibold text-neutral-800 mb-3">{sec.sectionname}</h3>
              <ul className="space-y-2">
                {sec.content.map((item) => (
                  <li key={item.contentid}
                      className="flex items-center gap-3 bg-white rounded-xl border border-neutral-100 px-4 py-3 text-sm shadow-card">
                    <span className="badge bg-neutral-100 text-neutral-500 uppercase text-[10px]">
                      {item.contenttype}
                    </span>
                    <a
                      href={item.contenturl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:text-primary-600 font-medium"
                    >
                      {item.title}
                    </a>
                  </li>
                ))}
                {sec.content.length === 0 && (
                  <li className="text-neutral-400 text-xs pl-1">No content yet.</li>
                )}
              </ul>
            </div>
          ))}
          {sections.length === 0 && (
            <p className="text-neutral-400 text-sm">No sections yet.</p>
          )}

          {isLecturerOrAdmin && (
            <form onSubmit={submitSection} className="mt-6 card space-y-3 border border-neutral-100">
              <h4 className="font-semibold text-neutral-800">Add Section</h4>
              <input placeholder="Section name" value={newSection.section_name} required
                onChange={(e) => setNewSection(s => ({ ...s, section_name: e.target.value }))}
                className={inputCls} />
              <button className={btnCls}>Add Section</button>
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
                className="card-hover no-underline block group"
              >
                <p className="font-semibold text-neutral-900 group-hover:text-primary transition-colors">
                  {f.title}
                </p>
                <p className="text-xs text-neutral-400 mt-1">
                  {f.description} &middot; {f.threadcount} threads
                </p>
              </Link>
            ))}
            {forums.length === 0 && (
              <p className="text-neutral-400 text-sm">No forums yet.</p>
            )}
          </div>

          {isLecturerOrAdmin && (
            <form onSubmit={submitForum} className="mt-6 card space-y-3">
              <h4 className="font-semibold text-neutral-800">Create Forum</h4>
              <input placeholder="Forum title" value={newForum.title} required
                onChange={(e) => setNewForum(f => ({ ...f, title: e.target.value }))}
                className={inputCls} />
              <input placeholder="Description (optional)" value={newForum.description}
                onChange={(e) => setNewForum(f => ({ ...f, description: e.target.value }))}
                className={inputCls} />
              <button className={btnCls}>Create</button>
            </form>
          )}
        </div>
      )}

      {/* ── Calendar ── */}
      {tab === 'calendar' && (
        <div>
          <ul className="space-y-3">
            {events.map((ev) => (
              <li key={ev.eventid} className="card flex items-start gap-4">
                <div className="flex-shrink-0 w-12 text-center">
                  <div className="text-primary font-bold text-lg leading-none">
                    {new Date(ev.eventdate).getDate()}
                  </div>
                  <div className="text-neutral-400 text-xs uppercase">
                    {new Date(ev.eventdate).toLocaleString('default', { month: 'short' })}
                  </div>
                </div>
                <div>
                  <p className="font-semibold text-neutral-900">{ev.title}</p>
                  {ev.eventtime && (
                    <p className="text-xs text-primary mt-0.5">at {ev.eventtime}</p>
                  )}
                  {ev.description && (
                    <p className="text-sm text-neutral-500 mt-1">{ev.description}</p>
                  )}
                </div>
              </li>
            ))}
            {events.length === 0 && (
              <p className="text-neutral-400 text-sm">No events scheduled.</p>
            )}
          </ul>

          {isLecturerOrAdmin && (
            <form onSubmit={submitEvent} className="mt-6 card space-y-3">
              <h4 className="font-semibold text-neutral-800">Add Calendar Event</h4>
              <input placeholder="Event title" value={newEvent.title} required
                onChange={(e) => setNewEvent(v => ({ ...v, title: e.target.value }))}
                className={inputCls} />
              <div className="flex gap-2">
                <input type="date" value={newEvent.event_date} required
                  onChange={(e) => setNewEvent(v => ({ ...v, event_date: e.target.value }))}
                  className={`${inputCls} flex-1`} />
                <input type="time" value={newEvent.event_time}
                  onChange={(e) => setNewEvent(v => ({ ...v, event_time: e.target.value }))}
                  className={`${inputCls} flex-1`} />
              </div>
              <textarea placeholder="Description (optional)" rows={2} value={newEvent.description}
                onChange={(e) => setNewEvent(v => ({ ...v, description: e.target.value }))}
                className={inputCls} />
              <button className={btnCls}>Add Event</button>
            </form>
          )}
        </div>
      )}

      {/* ── Assignments ── */}
      {tab === 'assignments' && (
        <div>
          <ul className="space-y-3">
            {assignments.map((a) => (
              <li key={a.assignmentid} className="card">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-semibold text-neutral-900">{a.title}</p>
                    {a.description && (
                      <p className="text-sm text-neutral-500 mt-1">{a.description}</p>
                    )}
                  </div>
                  <div className="text-right flex-shrink-0">
                    {a.duedate && (
                      <span className="badge badge-warning text-[10px]">
                        Due {new Date(a.duedate).toLocaleDateString()}
                      </span>
                    )}
                    <p className="text-xs text-neutral-400 mt-1">Max: {a.maxgrade}</p>
                  </div>
                </div>
              </li>
            ))}
            {assignments.length === 0 && (
              <p className="text-neutral-400 text-sm">No assignments yet.</p>
            )}
          </ul>

          {isLecturerOrAdmin && (
            <form onSubmit={submitAssignment} className="mt-6 card space-y-3">
              <h4 className="font-semibold text-neutral-800">Create Assignment</h4>
              <input placeholder="Title" value={newAssign.title} required
                onChange={(e) => setNewAssign(v => ({ ...v, title: e.target.value }))}
                className={inputCls} />
              <textarea placeholder="Description" rows={2} value={newAssign.description}
                onChange={(e) => setNewAssign(v => ({ ...v, description: e.target.value }))}
                className={inputCls} />
              <div className="flex gap-2">
                <input type="datetime-local" value={newAssign.due_date}
                  onChange={(e) => setNewAssign(v => ({ ...v, due_date: e.target.value }))}
                  className={`${inputCls} flex-1`} />
                <input type="number" placeholder="Max grade" value={newAssign.max_grade}
                  onChange={(e) => setNewAssign(v => ({ ...v, max_grade: Number(e.target.value) }))}
                  className={`${inputCls} w-28`} />
              </div>
              <button className={btnCls}>Create Assignment</button>
            </form>
          )}
        </div>
      )}

      {/* ── Members ── */}
      {tab === 'members' && members && (
        <div className="space-y-6">
          {members.lecturer && (
            <div>
              <h3 className="font-semibold text-neutral-800 mb-2">Lecturer</h3>
              <div className="card flex items-center gap-3 !p-4">
                <div className="w-8 h-8 rounded-full bg-primary-50 text-primary font-bold
                                flex items-center justify-center text-sm">
                  {members.lecturer.name.charAt(0)}
                </div>
                <div>
                  <p className="text-sm font-semibold text-neutral-900">{members.lecturer.name}</p>
                  <p className="text-xs text-neutral-400">{members.lecturer.email}</p>
                </div>
              </div>
            </div>
          )}
          <div>
            <h3 className="font-semibold text-neutral-800 mb-2">
              Students ({members.students.length})
            </h3>
            <ul className="space-y-2">
              {members.students.map((s) => (
                <li key={s.userid} className="card flex items-center gap-3 !p-4">
                  <div className="w-8 h-8 rounded-full bg-secondary-50 text-secondary font-bold
                                  flex items-center justify-center text-sm">
                    {s.name.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-neutral-900">{s.name}</p>
                    <p className="text-xs text-neutral-400">{s.email}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
