import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from "./components/theme-provider"
import { Layout } from "./components/layout/layout"
import { Dashboard } from "./pages/Dashboard"
import Portfolio from "./pages/Portfolio"
import { TradingHub } from "./pages/TradingHub"
import { Reports } from "./pages/Reports"
import { Users } from "./pages/Users"

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="stocksteward-ui-theme">
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/trading" element={<TradingHub />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/users" element={<Users />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
