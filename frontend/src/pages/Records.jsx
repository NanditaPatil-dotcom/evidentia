import { useEffect, useState } from 'react'
import API from '../services/api'

export default function Records() {
  const [records, setRecords] = useState([])

  useEffect(() => {
    API.get('/get-records/').then((res) => setRecords(res.data))
  }, [])

  return (
    <div className="p-6">
      {records.map((r, i) => (
        <div key={i} className="border p-3 mb-2">
          {r.english_text}
        </div>
      ))}
    </div>
  )
}
