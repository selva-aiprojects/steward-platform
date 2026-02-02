import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from "./components/theme-provider"
import { Layout } from "./components/layout/layout"
import { Dashboard } from "./pages/Dashboard"
import Portfolio from "./pages/Portfolio"
import { TradingHub } from "./pages/TradingHub"
import { Reports } from "./pages/Reports"
import { Users } from "./pages/Users"
import { Login } from "./pages/Login"
import Subscription from "./pages/Subscription"
import { Help } from "./pages/Help";
import Support from "./pages/Support";
import { useUser } from "./context/UserContext"
import { useNavigate, useLocation, Navigate } from "react-router-dom"

// Inner components for Auth Logic to be inside Router context
const AuthWrapper = ({ children }) => {
  return children;
};

const RequireAuth = ({ children }) => {
  const { user, loading } = useUser();
  const location = useLocation();

  // If loading, show nothing or spinner
  if (loading) return null;

  if (!user) {
    // Redirect to login but save where they were trying to go
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="stocksteward-ui-theme">
      <Router>
        <AuthWrapper>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<RequireAuth><Layout><Dashboard /></Layout></RequireAuth>} />
            <Route path="/trading" element={<RequireAuth><Layout><TradingHub /></Layout></RequireAuth>} />
            <Route path="/portfolio" element={
              <RequireAuth>
                <Layout>
                  <Portfolio />
                </Layout>
              </RequireAuth>
            } />
            <Route path="/subscription" element={
              <RequireAuth>
                <Layout>
                  <Subscription />
                </Layout>
              </RequireAuth>
            } />
            <Route path="/help" element={<RequireAuth><Layout><Help /></Layout></RequireAuth>} />
            <Route path="/reports" element={<RequireAuth><Layout><Reports /></Layout></RequireAuth>} />
            <Route path="/users" element={<RequireAuth><Layout><Users /></Layout></RequireAuth>} />
            <Route path="/support" element={<RequireAuth><Layout><Support /></Layout></RequireAuth>} />
          </Routes>
        </AuthWrapper>
      </Router>
    </ThemeProvider>
  );
}

export default App;
