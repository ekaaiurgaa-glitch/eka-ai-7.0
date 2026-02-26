import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth, SubscriptionProvider, ThemeProvider } from './context';
import Sidebar from './components/Sidebar';
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
import { useEffect } from 'react';

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function AppLayout() {
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ctrl + J: New Job Card
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
        navigate('/app/dashboard');
      }
      // Ctrl + F: Search (focus existing search input)
      if (e.ctrlKey && e.key === 'f') {
        e.preventDefault();
        const searchInput = document.querySelector('input[placeholder*="Search"]');
        if (searchInput) searchInput.focus();
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
