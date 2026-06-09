'use client';

interface EsgStatusProps {
  redFlag: boolean;
  reason: string;
}

export default function EsgStatus({ redFlag, reason }: EsgStatusProps) {
  return (
    <div className="glass-panel fade-in" style={{ animationDelay: '0.1s' }}>
      <h3 style={{ marginBottom: '0.5rem', color: redFlag ? 'var(--danger)' : 'var(--success)' }}>
        Validação ESG
      </h3>
      <div style={{ marginTop: '1rem', padding: '1rem', borderRadius: '8px', background: 'rgba(0,0,0,0.2)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <span style={{ fontWeight: 600 }}>Status Ambiental:</span>
          <span className={`status-badge ${redFlag ? 'status-danger' : 'status-success'}`}>
            {redFlag ? 'Red Flag 🛑' : 'Em Conformidade ✅'}
          </span>
        </div>
        {redFlag && (
          <p style={{ color: 'var(--danger)', fontSize: '0.9rem', marginTop: '0.5rem' }}>
            Motivo: {reason}
          </p>
        )}
        {!redFlag && (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.5rem' }}>
            Nenhuma sobreposição com Área de Preservação Permanente (APP) detectada.
          </p>
        )}
      </div>
    </div>
  );
}
