'use client';

import { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

interface DashboardLayoutProps {
  children: ReactNode;
  showSidebar?: boolean;
}

export function DashboardLayout({ children, showSidebar = true }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      {showSidebar && <Sidebar />}
      <div className={showSidebar ? 'lg:pl-64' : ''}>
        {showSidebar && <Header />}
        <main className={showSidebar ? 'p-4 lg:p-6 pt-20 lg:pt-6' : 'p-4 lg:p-6'}>
          {children}
        </main>
      </div>
    </div>
  );
}

