import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth, SubscriptionProvider, ThemeProvider } from './context';
import Sidebar from './components/Sidebar';
import ShortcutsHelpModal from './components/ShortcutsHelpModal';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ChatPage from './pages/ChatPage';
import JobsPage from './pages/JobsPage';
import VehiclesPage from './pages/VehiclesPage';
import MGPage from './pages/MGPage';
import LandingPage from './pages/LandingPage';
import InvoicesPage from './pages/InvoicesPage';
import AnalyticsPage from './pages/AnalyticsPage';
import OperatorPage from './pages/OperatorPage';
import ApprovalsPage from './pages/ApprovalsPage';
import JobCardDetailPage from './pages/JobCardDetailPage';
import { useEffect, useState } from 'react';

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function AppLayout() {
  const navigate = useNavigate();
  const [showShortcuts, setShowShortcuts] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ignore if typing in input
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return;
      }

      // Ctrl + J: Job Cards
      if (e.ctrlKey && e.key === 'j') {
        e.preventDefault();
        navigate('/app/jobs');
      }
      // Ctrl + O: Operator AI
      if (e.ctrlKey && e.key === 'o') {
        e.preventDefault();
        navigate('/app/operator');
      }
      // Ctrl + D: Dashboard
      if (e.ctrlKey && e.key === 'd') {
        e.preventDefault();
        navigate('/app');
      }
      // Ctrl + F: Search
      if (e.ctrlKey && e.key === 'f') {
        e.preventDefault();
        const searchInput = document.querySelector('input[placeholder*="Search"], input[placeholder*="search"]');
        if (searchInput) searchInput.focus();
      }
      // ?: Show shortcuts help
      if (e.key === '?') {
        e.preventDefault();
        setShowShortcuts(true);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [navigate]);

  return (
    <>
      <Sidebar />
      <main className="main">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/operator" element={<OperatorPage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/jobs/:jobId" element={<JobCardDetailPage />} />
          <Route path="/vehicles" element={<VehiclesPage />} />
          <Route path="/invoices" element={<InvoicesPage />} />
          <Route path="/approvals" element={<ApprovalsPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/mg" element={<MGPage />} />
        </Routes>
      </main>
      <ShortcutsHelpModal 
        isOpen={showShortcuts} 
        onClose={() => setShowShortcuts(false)} 
      />
    </>
  );
}

function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/app/*" element={
        <ProtectedRoute>
          <AppLayout />
        </ProtectedRoute>
      } />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <SubscriptionProvider>
            <AppRouter />
          </SubscriptionProvider>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}
