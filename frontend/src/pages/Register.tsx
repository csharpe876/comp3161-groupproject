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
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">

        {/* Header band */}
        <div className="bg-secondary rounded-t-2xl px-8 py-7 text-center">
          <div className="text-4xl font-extrabold text-white tracking-tight">
            <span className="text-accent">E</span>Tutor
          </div>
          <p className="text-white/60 text-sm mt-1">Learning Management System</p>
        </div>

        {/* Form card */}
        <div className="bg-white rounded-b-2xl shadow-card-hover px-8 py-8">
          <h2 className="text-xl font-semibold text-neutral-900 mb-2">Create your account</h2>
          <p className="text-sm text-neutral-400 mb-6">
            Fill in the details below to register.
          </p>

          {error && (
            <div className="bg-red-50 border border-red-200 text-error
                            rounded-lg px-4 py-3 mb-5 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {(
              [
                { name: 'userid',   label: 'User ID',   type: 'text',     placeholder: 'e.g. S100001' },
                { name: 'name',     label: 'Full Name', type: 'text',     placeholder: 'Your full name' },
                { name: 'email',    label: 'Email',     type: 'email',    placeholder: 'you@example.com' },
                { name: 'password', label: 'Password',  type: 'password', placeholder: 'Min. 6 characters' },
              ] as const
            ).map(({ name, label, type, placeholder }) => (
              <div key={name}>
                <label className="input-label">{label}</label>
                <input
                  type={type}
                  name={name}
                  value={form[name]}
                  onChange={handleChange}
                  required
                  placeholder={placeholder}
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
              className="btn-primary w-full !py-3 mt-2"
            >
              {loading ? 'Creating account…' : 'Create account'}
            </button>
          </form>

          <hr className="border-neutral-100 my-6" />

          <p className="text-center text-sm text-neutral-400">
            Already have an account?{' '}
            <Link
              to="/login"
              className="font-semibold text-primary hover:text-primary-600 no-underline"
            >
              Log in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
