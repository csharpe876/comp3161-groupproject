import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'

interface Course {
  courseid: string
  coursetitle: string
  coursecode: string
  description: string | null
  lecturername: string | null
  enrolledcount?: number
}

// Rotating colour accents for card top borders (Moodle-style)
const CARD_ACCENTS = [
  'border-t-primary',
  'border-t-accent',
  'border-t-success',
  'border-t-warning',
  'border-t-secondary',
  'border-t-purple-500',
]

export default function Dashboard() {
  const { user } = useAuth()

  const [courses, setCourses] = useState<Course[]>([])
  const [search,  setSearch]  = useState('')
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  useEffect(() => {
    async function load() {
      try {
        let url = '/courses'
        if (user?.account_type === 'Student') {
          url = `/students/${user.userid}/courses`
        } else if (user?.account_type === 'Lecturer') {
          url = `/lecturers/${user.userid}/courses`
        }
        const { data } = await api.get(url)
        setCourses(data)
      } catch {
        setError('Failed to load courses')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [user])

  const filtered = courses.filter(
    (c) =>
      c.coursetitle.toLowerCase().includes(search.toLowerCase()) ||
      c.coursecode.toLowerCase().includes(search.toLowerCase())
  )

  const pageTitle =
    user?.account_type === 'Admin'
      ? 'All Courses'
      : user?.account_type === 'Lecturer'
      ? 'My Courses'
      : 'My Courses'

  const pageSubtitle =
    user?.account_type === 'Student'
      ? 'Courses you are enrolled in'
      : user?.account_type === 'Lecturer'
      ? 'Courses you are teaching'
      : 'All courses in the system'

  return (
    <div>
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">{pageTitle}</h1>
          <p className="mt-0.5 text-sm text-neutral-400">{pageSubtitle}</p>
        </div>
        <input
          type="search"
          placeholder="Search courses…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input-field !w-full sm:!w-56"
        />
      </div>

      {loading && (
        <div className="flex items-center justify-center py-20 text-neutral-400 text-sm">
          <span className="animate-pulse">Loading courses…</span>
        </div>
      )}
      {error && (
        <div className="bg-red-50 border border-red-200 text-error rounded-xl px-4 py-3 text-sm mb-6">
          {error}
        </div>
      )}

      {/* Course grid */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((c, i) => (
          <Link
            key={c.courseid}
            to={`/courses/${c.courseid}`}
            className={`group block bg-white rounded-xl border border-neutral-100 shadow-card
                        hover:shadow-card-hover transition-shadow duration-200 no-underline
                        overflow-hidden border-t-4 ${CARD_ACCENTS[i % CARD_ACCENTS.length]}`}
          >
            <div className="p-5">
              {/* Course code badge */}
              <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold
                               tracking-wider uppercase bg-primary-50 text-primary-700 mb-3">
                {c.coursecode}
              </span>

              {/* Title */}
              <h2 className="text-base font-semibold text-neutral-900 leading-snug
                             group-hover:text-primary transition-colors line-clamp-2">
                {c.coursetitle}
              </h2>

              {/* Description */}
              {c.description && (
                <p className="mt-1.5 text-xs text-neutral-400 line-clamp-2 leading-relaxed">
                  {c.description}
                </p>
              )}

              {/* Footer */}
              <div className="mt-4 pt-3 border-t border-neutral-50 flex items-center justify-between
                              text-xs text-neutral-400">
                <span className="truncate max-w-[55%]">
                  {c.lecturername ?? 'No lecturer assigned'}
                </span>
                {c.enrolledcount !== undefined && (
                  <span className="flex-shrink-0 bg-neutral-100 text-neutral-500
                                   px-2 py-0.5 rounded-full">
                    {c.enrolledcount} students
                  </span>
                )}
              </div>
            </div>

            {/* Go to course footer bar */}
            <div className="px-5 py-2.5 bg-neutral-50 border-t border-neutral-100
                            flex items-center justify-end">
              <span className="text-xs font-medium text-primary group-hover:text-primary-600
                               transition-colors">
                Go to course →
              </span>
            </div>
          </Link>
        ))}

        {!loading && filtered.length === 0 && (
          <div className="col-span-3 text-center py-16 text-neutral-400 text-sm">
            <p className="text-4xl mb-3">📚</p>
            <p className="font-medium">No courses found.</p>
            {search && (
              <p className="mt-1 text-xs">Try a different search term.</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}


