import React from 'react';

export default function App() {
  return (
    <div style={{ maxWidth: 900, margin: 'auto', padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      {/* Header Mockup */}
      <div style={{ padding: '1rem 0', borderBottom: '2px solid #ccc', textAlign: 'center' }}>
        <h1 style={{ margin: 0 }}>Options Trading Dashboard</h1>
      </div>

      {/* Form Mockup */}
      <div
        style={{
          marginTop: '2rem',
          padding: '1rem',
          border: '2px dashed #999',
          borderRadius: '4px',
          textAlign: 'center',
        }}
      >
        <p style={{ margin: 0, color: '#666' }}>[ Ticker & Expiration Form ]</p>
      </div>

      {/* Data & Chart Mockup Container */}
      <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
        {/* Table Mockup */}
        <div
          style={{
            flex: 1,
            padding: '1rem',
            border: '2px dashed #999',
            borderRadius: '4px',
            minHeight: '250px',
            textAlign: 'center',
            color: '#666',
          }}
        >
          [ Option Chain Table ]
        </div>

        {/* Chart Mockup */}
        <div
          style={{
            flex: 1,
            padding: '1rem',
            border: '2px dashed #999',
            borderRadius: '4px',
            minHeight: '250px',
            textAlign: 'center',
            color: '#666',
          }}
        >
          [ Signal Chart ]
        </div>
      </div>

      {/* Footer Mockup */}
      <div
        style={{
          marginTop: '2rem',
          padding: '0.5rem 0',
          borderTop: '1px solid #eee',
          textAlign: 'right',
          fontSize: '0.875rem',
          color: '#999',
        }}
      >
        [ Footer / Status Bar ]
      </div>
    </div>
  );
}

