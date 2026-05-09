import { Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import ProfilePage from './pages/ProfilePage'
import JobsPage from './pages/JobsPage'
import MatchPage from './pages/MatchPage'
import ResumePage from './pages/ResumePage'
import HRSimulatorPage from './pages/HRSimulatorPage'
import InterviewPage from './pages/InterviewPage'
import DashboardPage from './pages/DashboardPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<Navigate to="/profile" replace />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="jobs" element={<JobsPage />} />
        <Route path="match/:jobId?" element={<MatchPage />} />
        <Route path="resume/:jobId?" element={<ResumePage />} />
        <Route path="hr/:jobId?" element={<HRSimulatorPage />} />
        <Route path="interview/:jobId?" element={<InterviewPage />} />
        <Route path="dashboard" element={<DashboardPage />} />
      </Route>
    </Routes>
  )
}

export default App
