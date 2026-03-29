import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const PASSWORD_KEY = 'evidentia-password'

export default function Settings() {
  const navigate = useNavigate()
  const [password, setPassword] = useState(localStorage.getItem(PASSWORD_KEY) || '')
  const [message, setMessage] = useState('')

  const handleSave = (event) => {
    event.preventDefault()

    const nextPassword = password.trim()

    if (!nextPassword) {
      setMessage('Please enter a password before saving.')
      return
    }

    localStorage.setItem(PASSWORD_KEY, nextPassword)
    setPassword(nextPassword)
    setMessage('Password saved. Use it the next time you unlock the app.')
  }

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-md rounded-3xl bg-white p-6 shadow-sm">
        <div className="mb-6">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">
            Security
          </p>
          <h1 className="mt-2 text-3xl font-semibold text-slate-900">
            Settings
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            Set a password for future logins. Once saved, the calculator lock
            will require this password.
          </p>
        </div>

        <form onSubmit={handleSave} className="space-y-4">
          <label className="block text-left text-sm font-medium text-slate-700">
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => {
                setMessage('')
                setPassword(event.target.value)
              }}
              placeholder="Enter a password"
              className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 text-base outline-none transition focus:border-slate-400"
            />
          </label>

          {message && <p className="text-sm text-slate-600">{message}</p>}

          <div className="flex gap-3">
            <button type="submit" className="btn">
              Save Password
            </button>
            <button
              type="button"
              onClick={() => navigate('/home')}
              className="rounded-2xl border border-slate-300 px-5 py-3 font-medium text-slate-700 transition hover:bg-slate-100"
            >
              Back Home
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
