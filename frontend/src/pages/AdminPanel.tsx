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

const inputCls = 'input-field'

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
    <div className="space-y-8">
      <div className="page-header">
        <h1 className="page-title">Admin Panel</h1>
        <p className="page-subtitle">Manage courses, staff, and view system reports</p>
      </div>

      {msg   && <p className="text-success text-sm font-medium">{msg}</p>}
      {error && <p className="text-error text-sm font-medium">{error}</p>}

      {/* ── Create Course ── */}
      <section className="card">
        <h2 className="font-semibold text-neutral-900 mb-5">Create Course</h2>
        <form onSubmit={createCourse} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {(
            [
              { name: 'course_id',   label: 'Course ID',   placeholder: 'e.g. C201' },
              { name: 'title',       label: 'Title',        placeholder: 'Course title' },
              { name: 'code',        label: 'Course Code',  placeholder: 'e.g. COMP3161' },
              { name: 'lec_id',      label: 'Lecturer ID',  placeholder: 'Optional' },
            ] as const
          ).map(({ name, label, placeholder }) => (
            <div key={name}>
              <label className="input-label">{label}</label>
              <input
                value={courseForm[name]}
                onChange={(e) => setCourseForm(f => ({ ...f, [name]: e.target.value }))}
                placeholder={placeholder}
                className={inputCls}
                required={name !== 'lec_id'}
              />
            </div>
          ))}
          <div className="col-span-1 sm:col-span-2">
            <label className="input-label">Description</label>
            <textarea
              value={courseForm.description}
              onChange={(e) => setCourseForm(f => ({ ...f, description: e.target.value }))}
              rows={2}
              className={inputCls}
            />
          </div>
          <div className="col-span-1 sm:col-span-2">
            <button className="btn-primary">Create Course</button>
          </div>
        </form>
      </section>

      {/* ── Assign Lecturer ── */}
      <section className="card">
        <h2 className="font-semibold text-neutral-900 mb-5">Assign Lecturer to Course</h2>
        <form onSubmit={assignLecturer} className="flex flex-wrap gap-3 items-end">
          <div>
            <label className="input-label">Course ID</label>
            <input
              value={assignForm.course_id}
              onChange={(e) => setAssignForm(f => ({ ...f, course_id: e.target.value }))}
              required
              placeholder="e.g. C1"
              className={`${inputCls} !w-36`}
            />
          </div>
          <div>
            <label className="input-label">Lecturer ID</label>
            <input
              value={assignForm.lec_id}
              onChange={(e) => setAssignForm(f => ({ ...f, lec_id: e.target.value }))}
              required
              placeholder="e.g. L1"
              className={`${inputCls} !w-36`}
            />
          </div>
          <button className="btn-secondary">Assign</button>
        </form>
      </section>

      {/* ── Reports ── */}
      <section className="card">
        <h2 className="font-semibold text-neutral-900 mb-5">Reports</h2>
        <div className="flex flex-wrap gap-2 mb-4">
          {REPORTS.map((r) => (
            <button
              key={r.key}
              onClick={() => setReport(r.key)}
              className={`text-xs px-3 py-1.5 rounded-lg border font-medium transition-colors ${
                report === r.key
                  ? 'bg-primary text-white border-primary'
                  : 'border-neutral-200 text-neutral-500 hover:border-primary hover:text-primary'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
        <button onClick={loadReport} className="btn-outline !py-2 !text-xs mb-5">
          Run Report
        </button>

        {reportData.length > 0 && (
          <div className="overflow-x-auto rounded-xl border border-neutral-100">
            <table className="min-w-full text-xs">
              <thead className="bg-neutral-50">
                <tr>
                  {Object.keys(reportData[0]).map((k) => (
                    <th key={k} className="px-4 py-3 text-left font-semibold text-neutral-600 border-b border-neutral-100">
                      {k}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {reportData.map((row, i) => (
                  <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-neutral-50/50'}>
                    {Object.values(row).map((v, j) => (
                      <td key={j} className="px-4 py-3 text-neutral-700 border-b border-neutral-100">
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
