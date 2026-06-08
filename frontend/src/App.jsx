import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './hooks/useTheme'
import Layout from './components/Layout'
import Home from './pages/Home'
import Pipeline from './pages/Pipeline'
import Results from './pages/Results'
import Review from './pages/Review'
import EmailLogs from './pages/EmailLogs'

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/pipeline" element={<Pipeline />} />
            <Route path="/results" element={<Results />} />
            <Route path="/review" element={<Review />} />
            <Route path="/logs" element={<EmailLogs />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </ThemeProvider>
  )
}
