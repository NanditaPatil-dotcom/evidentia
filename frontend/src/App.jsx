import { Routes, Route } from 'react-router-dom'
import Calculator from './pages/Calculator'
import Home from './pages/Home'
import Record from './pages/Record'
import Records from './pages/Records'
import Report from './pages/Report'
import Settings from './pages/Settings'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Calculator />} />
      <Route path="/home" element={<Home />} />
      <Route path="/record" element={<Record />} />
      <Route path="/records" element={<Records />} />
      <Route path="/report" element={<Report />} />
      <Route path="/settings" element={<Settings />} />
    </Routes>
  )
}
