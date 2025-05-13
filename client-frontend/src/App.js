import React from 'react';
import TickerForm from './components/TickerForm';
import OptionChain from './components/OptionChain';
import SignalChart from './components/SignalChart';

export default function App() {
  return (
    <div style={{ maxWidth: 900, margin: 'auto', padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      {/* Header */}
      <header style={{ borderBottom: '2px solid #ccc', paddingBottom: '1rem' }}>
        <h1>Options Trading Dashboard</h1>
      </header>

      {/* Form Stub */}
      <TickerForm />

      {/* Data & Chart Stubs */}
      <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
        <OptionChain />
        <SignalChart />
      </div>

      {/* Footer Stub */}
      <footer style={{ borderTop: '1px solid #eee', marginTop: '2rem', paddingTop: '0.5rem', textAlign: 'right', color: '#999' }}>
        Footer / Status Bar
      </footer>
    </div>
  );
}
