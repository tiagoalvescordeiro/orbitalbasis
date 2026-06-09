'use client';

interface TelemetryCardProps {
  moisture: number;
  nitrogen: number;
  temperature: number;
  cattleActivity?: number;
}

export default function TelemetryCard({ moisture, nitrogen, temperature, cattleActivity = 85 }: TelemetryCardProps) {
  return (
    <div className="glass-panel fade-in" style={{ animationDelay: '0.3s' }}>
      <h3 style={{ marginBottom: '1rem' }}>Sensores Edge IoT (Tempo Real)</h3>
      
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>ESP32_SOJA_01 (Umidade Solo)</span>
          <span style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#3b82f6' }}>{moisture.toFixed(1)}%</span>
        </div>
        <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', marginTop: '0.5rem', overflow: 'hidden' }}>
          <div style={{ width: `${moisture}%`, height: '100%', background: '#3b82f6', transition: 'width 0.5s ease' }}></div>
        </div>
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>ESP32_MILHO_01 (Nitrogênio NPK)</span>
          <span style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#eab308' }}>{nitrogen.toFixed(1)}%</span>
        </div>
        <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', marginTop: '0.5rem', overflow: 'hidden' }}>
          <div style={{ width: `${nitrogen}%`, height: '100%', background: '#eab308', transition: 'width 0.5s ease' }}></div>
        </div>
      </div>

      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>ESP32_CAFE_01 (Temp / Geada)</span>
          <span style={{ fontSize: '1.2rem', fontWeight: 'bold', color: temperature < 10 ? '#ef4444' : '#10b981' }}>{temperature.toFixed(1)} °C</span>
        </div>
        <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', marginTop: '0.5rem', overflow: 'hidden' }}>
          <div style={{ width: `${(temperature / 40) * 100}%`, height: '100%', background: temperature < 10 ? '#ef4444' : '#10b981', transition: 'width 0.5s ease' }}></div>
        </div>
      </div>

      <div style={{ marginTop: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>ESP32_BOI_01 (Movimentação / RFID)</span>
          <span style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#f97316' }}>{cattleActivity.toFixed(1)}%</span>
        </div>
        <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', marginTop: '0.5rem', overflow: 'hidden' }}>
          <div style={{ width: `${cattleActivity}%`, height: '100%', background: '#f97316', transition: 'width 0.5s ease' }}></div>
        </div>
      </div>

    </div>
  );
}
