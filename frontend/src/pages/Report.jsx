import { API_BASE_URL } from '../services/api'

export default function Report() {
  return (
    <div className="p-6">
      <button
        onClick={() => window.open(`${API_BASE_URL}/generate-pdf`)}
        className="btn"
      >
        Download PDF
      </button>
    </div>
  )
}
