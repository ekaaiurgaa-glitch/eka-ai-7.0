import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context';
import { SubscriptionProvider } from './context';
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

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function AppLayout() {
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

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <SubscriptionProvider>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/app/*" element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            } />
          </Routes>
        </SubscriptionProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
