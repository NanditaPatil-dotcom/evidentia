import { useEffect, useRef, useState } from 'react'
import API, { API_BASE_URL } from '../services/api'

function formatTimer(totalSeconds) {
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0')
  const seconds = String(totalSeconds % 60).padStart(2, '0')
  return `${minutes}:${seconds}`
}

export default function Record() {
  const [recording, setRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState(null)
  const [audioURL, setAudioURL] = useState(null)
  const [result, setResult] = useState(null)
  const [saveResult, setSaveResult] = useState(null)
  const [error, setError] = useState('')
  const [status, setStatus] = useState(
    'Click Start Recording and allow microphone access when your browser asks.',
  )
  const [secondsElapsed, setSecondsElapsed] = useState(0)
  const [processing, setProcessing] = useState(false)

  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const streamRef = useRef(null)

  useEffect(() => {
    if (!recording) {
      return undefined
    }

    const timerId = window.setInterval(() => {
      setSecondsElapsed((current) => current + 1)
    }, 1000)

    return () => window.clearInterval(timerId)
  }, [recording])

  useEffect(() => {
    return () => {
      if (audioURL) {
        URL.revokeObjectURL(audioURL)
      }

      streamRef.current?.getTracks().forEach((track) => track.stop())
    }
  }, [audioURL])

  const stopStream = () => {
    streamRef.current?.getTracks().forEach((track) => track.stop())
    streamRef.current = null
  }

  const getBrowserLocation = () =>
    new Promise((resolve) => {
      if (!navigator.geolocation) {
        resolve(null)
        return
      }

      navigator.geolocation.getCurrentPosition(
        (pos) => {
          resolve({
            coordinates: {
              latitude: pos.coords.latitude,
              longitude: pos.coords.longitude,
            },
          })
        },
        () => resolve(null),
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        },
      )
    })

  const startRecording = async () => {
    try {
      setError('')
      setResult(null)
      setSaveResult(null)
      setAudioBlob(null)
      setStatus(
        'Waiting for microphone permission. Please click Allow in the browser prompt.',
      )

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder

      audioChunksRef.current = []
      setSecondsElapsed(0)

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorder.onstop = async () => {
        const nextAudioBlob = new Blob(audioChunksRef.current, {
          type: 'audio/wav',
        })

        if (audioURL) {
          URL.revokeObjectURL(audioURL)
        }

        const url = URL.createObjectURL(nextAudioBlob)
        setAudioBlob(nextAudioBlob)
        setAudioURL(url)
        setStatus(
          'Recording ready. Click Save Record to upload it and fetch the current location for this record.',
        )
      }

      mediaRecorder.start()
      setRecording(true)
      setStatus('Recording in progress')
    } catch (err) {
      console.error(err)
      stopStream()
      setRecording(false)
      setStatus('Microphone access was not granted.')
      setError('Microphone access is required. Click Allow and try again.')
    }
  }

  const stopRecording = () => {
    if (!mediaRecorderRef.current) {
      return
    }

    setStatus('Stopping recording...')
    setRecording(false)
    mediaRecorderRef.current.stop()
    stopStream()
  }

  const saveRecording = async () => {
    if (!audioBlob) {
      return
    }

    const formData = new FormData()
    formData.append('file', audioBlob, 'recording.wav')

    try {
      setProcessing(true)
      setError('')
      setSaveResult(null)
      setStatus('Requesting current location for this record...')

      const browserLocation = await getBrowserLocation()

      if (browserLocation) {
        formData.append('browser_location', JSON.stringify(browserLocation))
      }

      setStatus('Processing recording...')
      const res = await API.post('/process-audio/', formData)
      setResult(res.data)
      setStatus('Saving record...')

      const saveRes = await API.post('/save-record/', res.data)
      setSaveResult(saveRes.data)
      setStatus('Record saved successfully.')
    } catch (err) {
      console.error(err)
      if (!err.response) {
        setError(
          `Cannot reach the backend at ${API_BASE_URL}. Start the FastAPI server and try again.`,
        )
        setStatus('Backend connection failed.')
      } else {
        setError(err.response?.data?.detail || 'Error processing audio')
        setStatus('Unable to save this recording.')
      }
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-xl font-bold">Record Incident</h1>
      <p className="text-sm text-slate-600">{status}</p>

      {recording && (
        <div className="flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-red-700">
          <span className="h-3 w-3 animate-pulse rounded-full bg-red-500"></span>
          <span className="font-medium">Recording in progress</span>
          <span className="ml-auto font-mono">{formatTimer(secondsElapsed)}</span>
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {!recording ? (
        <button
          onClick={startRecording}
          className="btn bg-green-500 hover:bg-green-600"
          disabled={processing}
        >
          Start Recording 🎤
        </button>
      ) : (
        <button
          onClick={stopRecording}
          className="btn bg-red-500 hover:bg-red-600"
        >
          Stop Recording ⏹
        </button>
      )}

      {audioURL && (
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <p>Preview:</p>
          <audio controls src={audioURL} className="mt-2 w-full"></audio>
          <div className="mt-4 flex gap-3">
            <button
              onClick={saveRecording}
              className="btn bg-blue-600 hover:bg-blue-700"
              disabled={processing}
            >
              Save Record
            </button>
            <button
              onClick={() => {
                if (audioURL) {
                  URL.revokeObjectURL(audioURL)
                }
                setAudioBlob(null)
                setAudioURL(null)
                setResult(null)
                setSaveResult(null)
                setError('')
                setStatus('Recording discarded. You can start a new recording.')
              }}
              className="rounded-2xl border border-slate-300 px-5 py-4 font-medium text-slate-700 transition hover:bg-slate-100"
              disabled={processing}
            >
              Discard
            </button>
          </div>
        </div>
      )}

      {processing && (
        <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
          Uploading and processing your recording...
        </div>
      )}

      {result && (
        <div className="mt-4 border p-4">
          <h2 className="font-bold">Processed Output:</h2>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}

      {saveResult && (
        <div className="rounded-xl border border-green-200 bg-green-50 p-4 text-green-800">
          <h2 className="font-bold">Record Saved</h2>
          <p className="mt-2 text-sm">
            Saved record ID: {saveResult.id}
          </p>
        </div>
      )}
    </div>
  )
}
