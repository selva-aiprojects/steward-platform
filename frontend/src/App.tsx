import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Portfolio from './pages/Portfolio';
import './styles/theme.css';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="app-layout">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/portfolio" element={<Portfolio />} />
            </Routes>
          </main>
        </div>

        <style>{`
          .app-layout {
            display: flex;
            min-height: 100vh;
          }
          .main-content {
            flex: 1;
            margin-left: 240px; /* Navbar width */
            padding: var(--space-8);
            min-width: 0; /* Foundation for Recharts responsivity */
          }
        `}</style>
      </Router>
    </ThemeProvider>
  );
}

export default App;
