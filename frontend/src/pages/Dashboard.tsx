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

  return (
    <div>
      {/* Header */}
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="page-title">
            {user?.account_type === 'Admin' ? 'All Courses' : 'My Courses'}
          </h1>
          <p className="page-subtitle">
            {user?.account_type === 'Student'
              ? 'Your enrolled courses'
              : user?.account_type === 'Lecturer'
              ? 'Courses you teach'
              : 'All courses in the system'}
          </p>
        </div>
        <input
          type="search"
          placeholder="Search courses…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input-field !w-52"
        />
      </div>

      {loading && (
        <div className="flex items-center justify-center py-16 text-neutral-400 text-sm">
          Loading courses…
        </div>
      )}
      {error && (
        <div className="bg-red-50 border border-red-200 text-error rounded-xl px-4 py-3 text-sm">
          {error}
        </div>
      )}

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((c) => (
          <Link
            key={c.courseid}
            to={`/courses/${c.courseid}`}
            className="card-hover no-underline group block"
          >
            <span className="badge-primary uppercase tracking-wide text-[10px]">
              {c.coursecode}
            </span>
            <h2 className="mt-3 text-base font-semibold text-neutral-900 leading-snug
                           group-hover:text-primary transition-colors">
              {c.coursetitle}
            </h2>
            {c.description && (
              <p className="mt-1 text-xs text-neutral-400 line-clamp-2">
                {c.description}
              </p>
            )}
            <div className="mt-4 flex items-center justify-between text-xs text-neutral-400">
              {c.lecturername && <span>{c.lecturername}</span>}
              {c.enrolledcount !== undefined && (
                <span className="badge bg-neutral-100 text-neutral-500">
                  {c.enrolledcount} students
                </span>
              )}
            </div>
          </Link>
        ))}

        {!loading && filtered.length === 0 && (
          <p className="col-span-3 text-neutral-400 text-sm py-8 text-center">
            No courses found.
          </p>
        )}
      </div>
    </div>
  )
}
