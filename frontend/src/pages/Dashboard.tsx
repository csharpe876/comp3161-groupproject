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
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">
          {user?.account_type === 'Admin' ? 'All Courses' : 'My Courses'}
        </h1>
        <input
          type="search"
          placeholder="Search courses…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-300 rounded px-3 py-1.5 text-sm w-52 focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
      </div>

      {loading && <p className="text-gray-500">Loading…</p>}
      {error   && <p className="text-red-600">{error}</p>}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((c) => (
          <Link
            key={c.courseid}
            to={`/courses/${c.courseid}`}
            className="bg-white rounded-xl shadow hover:shadow-md transition-shadow p-5 border border-gray-100"
          >
            <span className="text-xs font-semibold bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded uppercase tracking-wide">
              {c.coursecode}
            </span>
            <h2 className="mt-2 text-base font-semibold text-gray-800 leading-snug">
              {c.coursetitle}
            </h2>
            {c.lecturername && (
              <p className="text-xs text-gray-500 mt-1">👤 {c.lecturername}</p>
            )}
            {c.enrolledcount !== undefined && (
              <p className="text-xs text-gray-400 mt-1">
                {c.enrolledcount} students
              </p>
            )}
          </Link>
        ))}

        {!loading && filtered.length === 0 && (
          <p className="text-gray-500 col-span-3">No courses found.</p>
        )}
      </div>
    </div>
  )
}
