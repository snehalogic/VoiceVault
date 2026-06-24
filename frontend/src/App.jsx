import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Detector from './pages/Detector'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/detect" element={<Detector />} />
    </Routes>
  )
}