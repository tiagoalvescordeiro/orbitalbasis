'use client';

interface MetricsPanelProps {
  ndvi_mean: number;
  stress_pct: number;
  risk_score: number;
  app_stress: number;
  basis_atual: number;
  basis_ind: number;
  gap: number;
  ppe: number;
}

const Metric = ({ title, value, color }: any) => (
  <div style={{ background: 'rgba(255,255,255,0.03)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--panel-border)' }}>
    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>{title}</p>
    <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: color || 'var(--text-main)' }}>{value}</p>
  </div>
);

export default function MetricsPanel(p: MetricsPanelProps) {
  return (
    <div className="glass-panel fade-in" style={{ animationDelay: '0.15s' }}>
      <h3 style={{ marginBottom: '1rem' }}>Métricas de Convergência</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1rem' }}>
        <Metric title="NDVI médio" value={p.ndvi_mean?.toFixed(3)} />
        <Metric title="Estresse severo" value={`${p.stress_pct?.toFixed(1)}%`} color="var(--warning)" />
        <Metric title="Risco safra" value={`${p.risk_score}/100`} color={p.risk_score > 40 ? 'var(--danger)' : 'var(--success)'} />
        <Metric title="APP stress" value={`${p.app_stress?.toFixed(1)}%`} color={p.app_stress > 5 ? 'var(--danger)' : 'var(--text-main)'} />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
        <Metric title="Basis atual" value={p.basis_atual?.toFixed(2)} color="var(--accent-primary)" />
        <Metric title="Basis indicativo" value={p.basis_ind?.toFixed(2)} color="var(--success)" />
        <Metric title="Gap convergência" value={`${p.gap > 0 ? '+' : ''}${p.gap?.toFixed(2)}`} color="var(--text-main)" />
        <Metric title="PPE hint (R$/saca)" value={p.ppe?.toFixed(2)} />
      </div>
    </div>
  );
}
