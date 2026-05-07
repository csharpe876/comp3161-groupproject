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

const CONTENT_ICONS: Record<string, string> = { link: '??', file: '??', slide: '??' }

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
  const [submitErr,  setSubmitErr]  = useState('')

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

  async function wrap(fn: () => Promise<void>) {
    setSubmitMsg(''); setSubmitErr('')
    try { await fn() } catch (err: unknown) {
      setSubmitErr(
        (err as { response?: { data?: { error?: string } } })?.response?.data?.error ?? 'Error'
      )
    }
  }

  const submitEvent = (e: FormEvent) => { e.preventDefault(); wrap(async () => {
    await api.post(`/courses/${courseId}/events`, newEvent)
    setSubmitMsg('Event created!')
    api.get(`/courses/${courseId}/events`).then(r => setEvents(r.data))
    setNewEvent({ title: '', event_date: '', event_time: '', description: '' })
  })}

  const submitForum = (e: FormEvent) => { e.preventDefault(); wrap(async () => {
    await api.post(`/courses/${courseId}/forums`, newForum)
    setSubmitMsg('Forum created!')
    api.get(`/courses/${courseId}/forums`).then(r => setForums(r.data))
    setNewForum({ title: '', description: '' })
  })}

  const submitSection = (e: FormEvent) => { e.preventDefault(); wrap(async () => {
    await api.post(`/courses/${courseId}/sections`, newSection)
    setSubmitMsg('Section created!')
    api.get(`/courses/${courseId}/content`).then(r => setSections(r.data.sections))
    setNewSection({ section_name: '', order_index: 0 })
  })}

  const submitAssignment = (e: FormEvent) => { e.preventDefault(); wrap(async () => {
    await api.post(`/courses/${courseId}/assignments`, newAssign)
    setSubmitMsg('Assignment created!')
    api.get(`/courses/${courseId}/assignments`).then(r => setAssignments(r.data))
    setNewAssign({ title: '', description: '', due_date: '', max_grade: 100 })
  })}

  const enroll = () => wrap(async () => {
    await api.post(`/courses/${courseId}/enroll`)
    setSubmitMsg('Enrolled successfully!')
  })

  if (loading) return (
    <div className="flex items-center justify-center py-20 text-neutral-400 text-sm animate-pulse">
      Loading course…
    </div>
  )
  if (error) return (
    <div className="bg-red-50 border border-red-200 text-error rounded-xl px-4 py-3 text-sm">{error}</div>
  )
  if (!course) return null

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'overview',    label: 'Overview',    icon: '?' },
    { id: 'content',     label: 'Content',     icon: '??' },
    { id: 'forums',      label: 'Forums',      icon: '??' },
    { id: 'calendar',    label: 'Calendar',    icon: '??' },
    { id: 'assignments', label: 'Assignments', icon: '??' },
    { id: 'members',     label: 'Members',     icon: '??' },
  ]

  return (
    <div>
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-xs text-neutral-400 mb-5">
        <Link to="/" className="hover:text-primary no-underline transition-colors">Dashboard</Link>
        <span>/</span>
        <span className="text-neutral-700 font-medium">{course.coursetitle}</span>
      </nav>

      {/* Course header card */}
      <div className="bg-secondary rounded-2xl p-6 mb-6 text-white">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <span className="inline-block px-2.5 py-0.5 rounded text-[10px] font-bold tracking-wider
                             uppercase bg-white/20 text-white mb-3">
              {course.coursecode}
            </span>
            <h1 className="text-2xl font-bold text-white leading-tight">{course.coursetitle}</h1>
            {course.lecturername && (
              <p className="text-white/70 text-sm mt-1">Lecturer: {course.lecturername}</p>
            )}
            {course.description && (
              <p className="text-white/60 text-sm mt-2 leading-relaxed max-w-2xl">
                {course.description}
              </p>
            )}
          </div>
          {user?.account_type === 'Student' && (
            <button
              onClick={enroll}
              className="flex-shrink-0 bg-white text-secondary font-semibold text-sm
                         px-5 py-2.5 rounded-lg hover:bg-neutral-50 transition-colors"
            >
              Enrol in course
            </button>
          )}
        </div>
        {submitMsg && (
          <p className="mt-3 text-sm text-white/90 font-medium">{submitMsg}</p>
        )}
        {submitErr && (
          <p className="mt-3 text-sm text-red-200 font-medium">{submitErr}</p>
        )}
      </div>

      {/* Tab bar */}
      <div className="flex flex-wrap border-b border-neutral-200 mb-6 gap-0">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => { setTab(t.id); setSubmitMsg(''); setSubmitErr('') }}
            className={`flex items-center gap-1.5 px-4 py-3 text-sm font-medium
                        transition-colors border-b-2 -mb-px
                        ${tab === t.id
                          ? 'text-primary border-primary'
                          : 'text-neutral-400 border-transparent hover:text-neutral-700 hover:border-neutral-300'
                        }`}
          >
            <span className="text-base leading-none">{t.icon}</span>
            {t.label}
          </button>
        ))}
      </div>

      {/* -- Overview -- */}
      {tab === 'overview' && (
        <div className="grid sm:grid-cols-2 gap-4 max-w-2xl">
          {[
            ['Course ID',   course.courseid],
            ['Course Code', course.coursecode],
            ['Lecturer',    course.lecturername ?? 'Unassigned'],
            ['Description', course.description ?? '—'],
          ].map(([label, value]) => (
            <div key={label} className="bg-white rounded-xl border border-neutral-100 shadow-card p-4">
              <p className="text-xs font-semibold text-neutral-400 uppercase tracking-wide">{label}</p>
              <p className="mt-1 text-sm text-neutral-800 font-medium">{value}</p>
            </div>
          ))}
        </div>
      )}

      {/* -- Content -- */}
      {tab === 'content' && (
        <div>
          {sections.length === 0 && (
            <p className="text-neutral-400 text-sm mb-6">No sections yet.</p>
          )}
          {sections.map((sec) => (
            <details key={sec.sectionid} open className="mb-4 group">
              <summary className="flex items-center gap-2 cursor-pointer select-none
                                   bg-white rounded-xl border border-neutral-100 shadow-card
                                   px-5 py-3 font-semibold text-neutral-800 text-sm
                                   hover:bg-neutral-50 transition-colors list-none">
                <span className="text-primary mr-1">?</span>
                {sec.sectionname}
                <span className="ml-auto text-xs text-neutral-400 font-normal">
                  {sec.content.length} item{sec.content.length !== 1 ? 's' : ''}
                </span>
              </summary>
              <div className="mt-1 ml-4 border-l-2 border-primary-100 pl-4 space-y-1.5">
                {sec.content.map((item) => (
                  <div key={item.contentid}
                       className="flex items-center gap-3 bg-white rounded-lg border border-neutral-100
                                  px-4 py-2.5 text-sm">
                    <span className="text-base">{CONTENT_ICONS[item.contenttype] ?? '??'}</span>
                    <a
                      href={item.contenturl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:text-primary-600 font-medium flex-1"
                    >
                      {item.title}
                    </a>
                    <span className="text-[10px] uppercase font-medium text-neutral-400 tracking-wide">
                      {item.contenttype}
                    </span>
                  </div>
                ))}
                {sec.content.length === 0 && (
                  <p className="text-neutral-400 text-xs py-2">No items in this section.</p>
                )}
              </div>
            </details>
          ))}

          {isLecturerOrAdmin && (
            <form onSubmit={submitSection}
                  className="mt-6 bg-white rounded-xl border border-neutral-100 shadow-card p-5 space-y-3">
              <h4 className="font-semibold text-neutral-800 text-sm">Add New Section</h4>
              <input placeholder="Section name" value={newSection.section_name} required
                onChange={(e) => setNewSection(s => ({ ...s, section_name: e.target.value }))}
                className="input-field" />
              <button className="btn-primary !py-2 !text-xs">Add Section</button>
            </form>
          )}
        </div>
      )}

      {/* -- Forums -- */}
      {tab === 'forums' && (
        <div>
          <div className="space-y-3 mb-6">
            {forums.length === 0 && <p className="text-neutral-400 text-sm">No forums yet.</p>}
            {forums.map((f) => (
              <Link
                key={f.forumid}
                to={`/courses/${courseId}/forums/${f.forumid}`}
                className="flex items-center gap-4 bg-white rounded-xl border border-neutral-100
                           shadow-card hover:shadow-card-hover transition-shadow no-underline group px-5 py-4"
              >
                <div className="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center
                                text-primary text-xl flex-shrink-0">
                  ??
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-neutral-900 group-hover:text-primary
                                transition-colors text-sm truncate">
                    {f.title}
                  </p>
                  {f.description && (
                    <p className="text-xs text-neutral-400 mt-0.5 truncate">{f.description}</p>
                  )}
                </div>
                <span className="flex-shrink-0 text-xs text-neutral-400">
                  {f.threadcount} thread{f.threadcount !== 1 ? 's' : ''}
                </span>
              </Link>
            ))}
          </div>

          {isLecturerOrAdmin && (
            <form onSubmit={submitForum}
                  className="bg-white rounded-xl border border-neutral-100 shadow-card p-5 space-y-3">
              <h4 className="font-semibold text-neutral-800 text-sm">Create Forum</h4>
              <input placeholder="Forum title" value={newForum.title} required
                onChange={(e) => setNewForum(f => ({ ...f, title: e.target.value }))}
                className="input-field" />
              <input placeholder="Description (optional)" value={newForum.description}
                onChange={(e) => setNewForum(f => ({ ...f, description: e.target.value }))}
                className="input-field" />
              <button className="btn-primary !py-2 !text-xs">Create Forum</button>
            </form>
          )}
        </div>
      )}

      {/* -- Calendar -- */}
      {tab === 'calendar' && (
        <div>
          {events.length === 0 && <p className="text-neutral-400 text-sm mb-6">No events scheduled.</p>}
          <ul className="space-y-3 mb-6">
            {events.map((ev) => (
              <li key={ev.eventid}
                  className="flex items-start gap-4 bg-white rounded-xl border border-neutral-100
                             shadow-card px-5 py-4">
                {/* Date badge */}
                <div className="flex-shrink-0 w-12 bg-primary-50 rounded-lg text-center py-2">
                  <div className="text-primary font-bold text-xl leading-none">
                    {new Date(ev.eventdate + 'T00:00:00').getDate()}
                  </div>
                  <div className="text-primary-400 text-[10px] uppercase font-medium mt-0.5">
                    {new Date(ev.eventdate + 'T00:00:00').toLocaleString('default', { month: 'short' })}
                  </div>
                </div>
                <div>
                  <p className="font-semibold text-neutral-900 text-sm">{ev.title}</p>
                  {ev.eventtime && (
                    <p className="text-xs text-primary mt-0.5 font-medium">at {ev.eventtime}</p>
                  )}
                  {ev.description && (
                    <p className="text-xs text-neutral-500 mt-1">{ev.description}</p>
                  )}
                </div>
              </li>
            ))}
          </ul>

          {isLecturerOrAdmin && (
            <form onSubmit={submitEvent}
                  className="bg-white rounded-xl border border-neutral-100 shadow-card p-5 space-y-3">
              <h4 className="font-semibold text-neutral-800 text-sm">Add Calendar Event</h4>
              <input placeholder="Event title" value={newEvent.title} required
                onChange={(e) => setNewEvent(v => ({ ...v, title: e.target.value }))}
                className="input-field" />
              <div className="flex gap-2">
                <input type="date" value={newEvent.event_date} required
                  onChange={(e) => setNewEvent(v => ({ ...v, event_date: e.target.value }))}
                  className="input-field flex-1" />
                <input type="time" value={newEvent.event_time}
                  onChange={(e) => setNewEvent(v => ({ ...v, event_time: e.target.value }))}
                  className="input-field flex-1" />
              </div>
              <textarea placeholder="Description (optional)" rows={2} value={newEvent.description}
                onChange={(e) => setNewEvent(v => ({ ...v, description: e.target.value }))}
                className="input-field" />
              <button className="btn-primary !py-2 !text-xs">Add Event</button>
            </form>
          )}
        </div>
      )}

      {/* -- Assignments -- */}
      {tab === 'assignments' && (
        <div>
          {assignments.length === 0 && <p className="text-neutral-400 text-sm mb-6">No assignments yet.</p>}
          <ul className="space-y-3 mb-6">
            {assignments.map((a) => {
              const overdue = a.duedate && new Date(a.duedate) < new Date()
              return (
                <li key={a.assignmentid}
                    className="bg-white rounded-xl border border-neutral-100 shadow-card px-5 py-4">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-semibold text-neutral-900 text-sm">{a.title}</p>
                      {a.description && (
                        <p className="text-xs text-neutral-500 mt-1">{a.description}</p>
                      )}
                    </div>
                    <div className="text-right flex-shrink-0 space-y-1">
                      {a.duedate && (
                        <span className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-medium
                                         ${overdue
                                           ? 'bg-red-50 text-error'
                                           : 'bg-orange-50 text-warning'}`}>
                          {overdue ? 'Overdue · ' : 'Due '}
                          {new Date(a.duedate).toLocaleDateString()}
                        </span>
                      )}
                      <p className="text-xs text-neutral-400">Max grade: {a.maxgrade}</p>
                    </div>
                  </div>
                </li>
              )
            })}
          </ul>

          {isLecturerOrAdmin && (
            <form onSubmit={submitAssignment}
                  className="bg-white rounded-xl border border-neutral-100 shadow-card p-5 space-y-3">
              <h4 className="font-semibold text-neutral-800 text-sm">Create Assignment</h4>
              <input placeholder="Title" value={newAssign.title} required
                onChange={(e) => setNewAssign(v => ({ ...v, title: e.target.value }))}
                className="input-field" />
              <textarea placeholder="Description (optional)" rows={2} value={newAssign.description}
                onChange={(e) => setNewAssign(v => ({ ...v, description: e.target.value }))}
                className="input-field" />
              <div className="flex gap-2">
                <input type="datetime-local" value={newAssign.due_date}
                  onChange={(e) => setNewAssign(v => ({ ...v, due_date: e.target.value }))}
                  className="input-field flex-1" />
                <input type="number" placeholder="Max grade" value={newAssign.max_grade}
                  onChange={(e) => setNewAssign(v => ({ ...v, max_grade: Number(e.target.value) }))}
                  className="input-field w-28" />
              </div>
              <button className="btn-primary !py-2 !text-xs">Create Assignment</button>
            </form>
          )}
        </div>
      )}

      {/* -- Members -- */}
      {tab === 'members' && members && (
        <div className="space-y-6">
          {members.lecturer && (
            <div>
              <h3 className="text-xs font-semibold text-neutral-400 uppercase tracking-wide mb-2">
                Lecturer
              </h3>
              <div className="flex items-center gap-3 bg-white rounded-xl border border-neutral-100
                              shadow-card px-4 py-3">
                <div className="w-9 h-9 rounded-full bg-primary-100 text-primary font-bold
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
            <h3 className="text-xs font-semibold text-neutral-400 uppercase tracking-wide mb-2">
              Students ({members.students.length})
            </h3>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {members.students.map((s) => (
                <div key={s.userid}
                     className="flex items-center gap-3 bg-white rounded-xl border border-neutral-100
                                shadow-card px-4 py-3">
                  <div className="w-8 h-8 rounded-full bg-secondary-100 text-secondary font-bold
                                  flex items-center justify-center text-xs flex-shrink-0">
                    {s.name.charAt(0)}
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-neutral-900 truncate">{s.name}</p>
                    <p className="text-xs text-neutral-400 truncate">{s.email}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


