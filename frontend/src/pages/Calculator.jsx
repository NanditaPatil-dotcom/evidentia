import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const PASSWORD_KEY = 'evidentia-password'

export default function Calculator() {
  const [input, setInput] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleClick = (val) => {
    setError('')
    setInput((p) => p + val)
  }

  const handleEquals = () => {
    const savedPassword = localStorage.getItem(PASSWORD_KEY)

    if (!savedPassword || input === savedPassword) {
      setError('')
      navigate('/home')
    } else {
      setError('Wrong password')
      setInput('')
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-100 px-4">
      <div className="mb-4 w-64 max-w-full text-center">
        <p className="text-sm font-medium text-gray-600">
          {localStorage.getItem(PASSWORD_KEY)
            ? 'Enter your saved password'
            : 'No password set yet. Press = to continue, then set one in Settings.'}
        </p>
      </div>

      <div className="mb-2 w-64 rounded bg-white p-4 text-right text-xl shadow-sm">
        {input || '0'}
      </div>

      {error && <p className="mb-3 text-sm text-red-500">{error}</p>}

      <div className="grid grid-cols-4 gap-2 w-64">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => (
          <button
            key={n}
            onClick={() => handleClick(n)}
            className="rounded bg-gray-200 p-4 transition hover:bg-gray-300"
          >
            {n}
          </button>
        ))}
        <button
          onClick={() => {
            setError('')
            setInput('')
          }}
          className="rounded bg-red-400 p-4 text-white transition hover:bg-red-500"
        >
          C
        </button>
        <button
          onClick={() => handleClick('0')}
          className="rounded bg-gray-200 p-4 transition hover:bg-gray-300"
        >
          0
        </button>
        <button
          onClick={handleEquals}
          className="col-span-2 rounded bg-green-500 p-4 text-white transition hover:bg-green-600"
        >
          =
        </button>
      </div>
    </div>
  )
}
