import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'

type Role = 'Student' | 'Lecturer' | 'Admin'

export default function Register() {
  const navigate = useNavigate()

  const [form, setForm] = useState({
    userid: '',
    password: '',
    name: '',
    email: '',
    account_type: 'Student' as Role,
  })
  const [error,   setError]   = useState('')
  const [loading, setLoading] = useState(false)

  function handleChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/auth/register', form)
      navigate('/login')
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { error?: string } } })?.response?.data?.error ??
        'Registration failed'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex">
      {/* Left hero panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-secondary to-secondary-700
                      flex-col items-center justify-center px-16 text-white">
        <div className="max-w-xs text-center">
          <div className="text-5xl font-extrabold mb-4">
            <span className="text-primary">E</span>Tutor
          </div>
          <p className="text-secondary-100 text-base leading-relaxed">
            Start learning with thousands of courses.
          </p>
        </div>
      </div>

      {/* Right form panel */}
      <div className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">
          <div className="mb-8 text-center">
            <h1 className="text-2xl font-bold text-neutral-900">Create your account</h1>
            <p className="mt-1 text-sm text-neutral-400">Join ETutor today</p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-error
                            rounded-xl px-4 py-3 mb-5 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {(
              [
                { name: 'userid',   label: 'User ID',   type: 'text' },
                { name: 'name',     label: 'Full Name', type: 'text' },
                { name: 'email',    label: 'Email',     type: 'email' },
                { name: 'password', label: 'Password',  type: 'password' },
              ] as const
            ).map(({ name, label, type }) => (
              <div key={name}>
                <label className="input-label">{label}</label>
                <input
                  type={type}
                  name={name}
                  value={form[name]}
                  onChange={handleChange}
                  required
                  className="input-field"
                />
              </div>
            ))}

            <div>
              <label className="input-label">Role</label>
              <select
                name="account_type"
                value={form.account_type}
                onChange={handleChange}
                className="input-field"
              >
                <option value="Student">Student</option>
                <option value="Lecturer">Lecturer</option>
                <option value="Admin">Admin</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full"
            >
              {loading ? 'Registering…' : 'Create account'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-neutral-400">
            Already have an account?{' '}
            <Link
              to="/login"
              className="font-semibold text-primary hover:text-primary-600 no-underline"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
