import { useState, type FormEvent } from 'react'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'
import { Navigate } from 'react-router-dom'

type ReportKey = 'courses-50plus' | 'students-5plus' | 'lecturers-3plus' | 'top10-enrolled' | 'top10-averages'

const REPORTS: { key: ReportKey; label: string }[] = [
  { key: 'courses-50plus',   label: 'Courses with 50+ students' },
  { key: 'students-5plus',   label: 'Students in 5+ courses' },
  { key: 'lecturers-3plus',  label: 'Lecturers teaching 3+ courses' },
  { key: 'top10-enrolled',   label: 'Top 10 most enrolled courses' },
  { key: 'top10-averages',   label: 'Top 10 students by average' },
]

export default function AdminPanel() {
  const { user } = useAuth()

  const [courseForm, setCourseForm] = useState({
    course_id: '', title: '', code: '', description: '', lec_id: '',
  })
  const [assignForm, setAssignForm] = useState({ course_id: '', lec_id: '' })
  const [report,     setReport]     = useState<ReportKey>('courses-50plus')
  const [reportData, setReportData] = useState<Record<string, unknown>[]>([])
  const [msg,        setMsg]        = useState('')
  const [error,      setError]      = useState('')

  if (user?.account_type !== 'Admin') return <Navigate to="/" replace />

  async function createCourse(e: FormEvent) {
    e.preventDefault()
    setMsg(''); setError('')
    try {
      await api.post('/courses', {
        ...courseForm,
        lec_id: courseForm.lec_id || undefined,
      })
      setMsg(`Course "${courseForm.title}" created!`)
      setCourseForm({ course_id: '', title: '', code: '', description: '', lec_id: '' })
    } catch (err: unknown) {
      setError((err as { response?: { data?: { error?: string } } })?.response?.data?.error ?? 'Error')
    }
  }

  async function assignLecturer(e: FormEvent) {
    e.preventDefault()
    setMsg(''); setError('')
    try {
      await api.post(`/courses/${assignForm.course_id}/assign-lecturer`, { lec_id: assignForm.lec_id })
      setMsg(`Lecturer ${assignForm.lec_id} assigned to ${assignForm.course_id}!`)
      setAssignForm({ course_id: '', lec_id: '' })
    } catch (err: unknown) {
      setError((err as { response?: { data?: { error?: string } } })?.response?.data?.error ?? 'Error')
    }
  }

  async function loadReport() {
    const { data } = await api.get(`/reports/${report}`)
    setReportData(data)
  }

  return (
    <div className="space-y-10">
      <h1 className="text-2xl font-bold text-gray-800">Admin Panel</h1>

      {msg   && <p className="text-green-600 text-sm">{msg}</p>}
      {error && <p className="text-red-600 text-sm">{error}</p>}

      {/* ── Create Course ── */}
      <section className="bg-white rounded-xl shadow p-6 border border-gray-100">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">Create Course</h2>
        <form onSubmit={createCourse} className="grid grid-cols-2 gap-3">
          {(
            [
              { name: 'course_id',   label: 'Course ID',   placeholder: 'e.g. C201' },
              { name: 'title',       label: 'Title',        placeholder: 'Course title' },
              { name: 'code',        label: 'Course Code',  placeholder: 'e.g. COMP3161' },
              { name: 'lec_id',      label: 'Lecturer ID',  placeholder: 'Optional' },
            ] as const
          ).map(({ name, label, placeholder }) => (
            <div key={name}>
              <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
              <input
                value={courseForm[name]}
                onChange={(e) => setCourseForm(f => ({ ...f, [name]: e.target.value }))}
                placeholder={placeholder}
                className="w-full border rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                required={name !== 'lec_id'}
              />
            </div>
          ))}
          <div className="col-span-2">
            <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
            <textarea
              value={courseForm.description}
              onChange={(e) => setCourseForm(f => ({ ...f, description: e.target.value }))}
              rows={2}
              className="w-full border rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
          <div className="col-span-2">
            <button className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-5 py-2 rounded transition-colors">
              Create Course
            </button>
          </div>
        </form>
      </section>

      {/* ── Assign Lecturer ── */}
      <section className="bg-white rounded-xl shadow p-6 border border-gray-100">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">Assign Lecturer to Course</h2>
        <form onSubmit={assignLecturer} className="flex gap-3 items-end">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Course ID</label>
            <input
              value={assignForm.course_id}
              onChange={(e) => setAssignForm(f => ({ ...f, course_id: e.target.value }))}
              required
              placeholder="e.g. C1"
              className="border rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Lecturer ID</label>
            <input
              value={assignForm.lec_id}
              onChange={(e) => setAssignForm(f => ({ ...f, lec_id: e.target.value }))}
              required
              placeholder="e.g. L1"
              className="border rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
          <button className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-5 py-2 rounded transition-colors">
            Assign
          </button>
        </form>
      </section>

      {/* ── Reports ── */}
      <section className="bg-white rounded-xl shadow p-6 border border-gray-100">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">Reports</h2>
        <div className="flex flex-wrap gap-2 mb-4">
          {REPORTS.map((r) => (
            <button
              key={r.key}
              onClick={() => setReport(r.key)}
              className={`text-xs px-3 py-1.5 rounded border transition-colors ${
                report === r.key
                  ? 'bg-indigo-600 text-white border-indigo-600'
                  : 'border-gray-300 text-gray-600 hover:border-indigo-400'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
        <button
          onClick={loadReport}
          className="bg-gray-700 hover:bg-gray-800 text-white text-sm px-4 py-1.5 rounded mb-4 transition-colors"
        >
          Run Report
        </button>

        {reportData.length > 0 && (
          <div className="overflow-x-auto">
            <table className="min-w-full text-xs border border-gray-200 rounded">
              <thead className="bg-gray-50">
                <tr>
                  {Object.keys(reportData[0]).map((k) => (
                    <th key={k} className="px-3 py-2 text-left font-medium text-gray-600 border-b">
                      {k}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {reportData.map((row, i) => (
                  <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    {Object.values(row).map((v, j) => (
                      <td key={j} className="px-3 py-2 text-gray-700 border-b">
                        {String(v ?? '—')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}
