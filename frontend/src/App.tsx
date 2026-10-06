import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import DashboardScreen from './components/DashboardScreen';
import MeetingScreen from './components/MeetingScreen';
import UploadScreen from './components/UploadScreen';

function AppContent() {
  return (
    <div className="bg-surface font-body-md text-ink-primary min-h-screen selection:bg-accent-forest selection:text-white">
      {/* We can pass stage="results" or nothing to Header if we want to simplify it, or leave it mostly static */}
      <Header stage="upload" setStage={() => {}} />
      <main className="w-full pt-28 bg-surface min-h-screen">
        <div className="flex flex-col w-full h-full">
          <div className="max-w-7xl mx-auto w-full px-gutter py-space-xl">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardScreen />} />
              <Route path="/upload" element={<UploadScreen />} />
              <Route path="/meeting/:id" element={<MeetingScreen />} />
            </Routes>
          </div>
        </div>
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
