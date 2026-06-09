'use client';

interface RiskGaugeProps {
  risk: number;
}

export default function RiskGauge({ risk }: RiskGaugeProps) {
  const percentage = (risk * 100).toFixed(1);
  const isHighRisk = risk > 0.4;
  
  return (
    <div className="glass-panel fade-in">
      <h3>🚜 Risco de Safra (IA)</h3>
      <div style={{ display: 'flex', alignItems: 'center', gap: '2rem', marginTop: '1rem' }}>
        <div style={{
          position: 'relative', width: '120px', height: '120px', 
          borderRadius: '50%', background: `conic-gradient(${isHighRisk ? 'var(--danger)' : 'var(--success)'} ${percentage}%, rgba(255,255,255,0.1) 0)`
        }}>
          <div style={{
            position: 'absolute', top: '10px', left: '10px', right: '10px', bottom: '10px',
            background: 'var(--panel-bg)', borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1.5rem', fontWeight: 'bold'
          }}>
            {percentage}%
          </div>
        </div>
        <div>
          <p className="header-subtitle" style={{ marginBottom: '0.5rem' }}>
            {isHighRisk ? 'Risco Elevado detectado pelos satélites.' : 'Safra com Risco Controlado.'}
          </p>
          <span className={`status-badge ${isHighRisk ? 'status-danger' : 'status-success'}`}>
            {isHighRisk ? 'Alerta' : 'Saudável'}
          </span>
        </div>
      </div>
    </div>
  );
}
