import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import CourseList from './components/CourseList'
import CourseDetail from './components/CourseDetail'
import LearnUnit from './components/LearnUnit'
import Profile from './components/Profile'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<CourseList />} />
        <Route path="/course/:courseId" element={<CourseDetail />} />
        <Route path="/learn/:courseId/:unitId" element={<LearnUnit />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}
