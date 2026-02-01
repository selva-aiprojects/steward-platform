import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from "./components/theme-provider"
import { Layout } from "./components/layout/layout"
import { Dashboard } from "./pages/dashboard"
import { Portfolio } from "./pages/portfolio"

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="stocksteward-ui-theme">
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/portfolio" element={<Portfolio />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
