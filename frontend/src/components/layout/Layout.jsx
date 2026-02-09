import React from "react";
import { Outlet } from "react-router-dom";

// This is the main layout component that wraps all pages
const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col md:flex-row">
      {/* Main content area */}
      <main className="flex-1">
        {children || <Outlet />}
      </main>
    </div>
  );
};

export { Layout };