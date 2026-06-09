'use client';

import { useState, useEffect } from 'react';
import { Settings, Map as MapIcon, LineChart, Cpu, Menu } from 'lucide-react';
import dynamic from 'next/dynamic';
import FinancialChart from '@/components/FinancialChart';
import MetricsPanel from '@/components/MetricsPanel';
import EsgStatus from '@/components/EsgStatus';
import TelemetryCard from '@/components/TelemetryCard';
import ChatPanel from '@/components/ChatPanel';

const OrbitalMap = dynamic(() => import('@/components/OrbitalMap'), { ssr: false });

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('Visão Geral');
  
  // Configuration State
  const [useIoT, setUseIoT] = useState(true);
  const [esgFlag, setEsgFlag] = useState(false);
  const [sacaPrice, setSacaPrice] = useState(130.0);
  const [cornPrice, setCornPrice] = useState(60.0);
  const [coffeePrice, setCoffeePrice] = useState(1400.0);
  const [cattlePrice, setCattlePrice] = useState(250.0);
  
  // Commodity Ativa Global
  const [activeCommodity, setActiveCommodity] = useState('soja');
  
  // Polling State (velocidade de medição em segundos)
  const [pollingSpeed, setPollingSpeed] = useState(0); 
  
  // Sensor States
  const [moistureState, setMoistureState] = useState(22.0);
  const [nitrogenState, setNitrogenState] = useState(85.0);
  const [tempState, setTempState] = useState(18.0);
  const [cattleState, setCattleState] = useState(85.0);

  const fetchAnalysis = async (autoRefresh = false) => {
    if (!autoRefresh) setLoading(true);
    try {
      const res = await fetch('/api/analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          esg_red_flag: esgFlag,
          soil_moisture_pct: moistureState, 
          saca_rs: sacaPrice, // fallback para compatibilidade
          active_commodity: activeCommodity,
          local_prices: {
            soy: sacaPrice,
            corn: cornPrice,
            coffee: coffeePrice,
            cattle: cattlePrice
          },
          use_telemetry_soil: useIoT
        })
      });
      const result = await res.json();
      setData(result);
    } catch (err) {
      console.error(err);
    }
    if (!autoRefresh) setLoading(false);
  };

  useEffect(() => {
    fetchAnalysis();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [esgFlag, sacaPrice, cornPrice, coffeePrice, cattlePrice, useIoT, activeCommodity]);

  // Polling Effect
  useEffect(() => {
    if (pollingSpeed <= 0) return;
    
    const interval = setInterval(() => {
      setMoistureState(m => Math.max(10, Math.min(40, m + (Math.random() - 0.5) * 2)));
      setNitrogenState(n => Math.max(60, Math.min(100, n + (Math.random() - 0.5) * 3)));
      setTempState(t => Math.max(0, Math.min(35, t + (Math.random() - 0.5) * 1.5)));
      setCattleState(c => Math.max(0, Math.min(100, c + (Math.random() - 0.5) * 4)));
      fetchAnalysis(true); // Chamada silenciosa sem travar a UI (autoRefresh=true)
    }, pollingSpeed * 1000);

    return () => clearInterval(interval);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pollingSpeed, esgFlag, sacaPrice, useIoT]);

  return (
    <div className="app-container">
      {/* Sidebar Enxuta (Sem Formulários) */}
      <aside className="sidebar" style={{ padding: '2rem' }}>
        <h1 className="header-title" style={{ fontSize: '1.6rem', marginBottom: '0.2rem' }}>OrbitalBasis</h1>
        <p className="header-subtitle" style={{ marginBottom: '2rem' }}>FIAP Global Solution</p>
        
        <div style={{ marginBottom: '2rem' }}>
          <div className={`menu-item ${activeTab === 'Visão Geral' ? 'active' : ''}`} onClick={() => setActiveTab('Visão Geral')}><Menu size={18} /> Visão Geral</div>
          <div className={`menu-item ${activeTab === 'Mapa Orbital' ? 'active' : ''}`} onClick={() => setActiveTab('Mapa Orbital')}><MapIcon size={18} /> Mapa Orbital</div>
          <div className={`menu-item ${activeTab === 'Mercado' ? 'active' : ''}`} onClick={() => setActiveTab('Mercado')}><LineChart size={18} /> Mercado & Basis</div>
          <div className={`menu-item ${activeTab === 'IoT' ? 'active' : ''}`} onClick={() => setActiveTab('IoT')}><Cpu size={18} /> Edge IoT</div>
          <div className={`menu-item ${activeTab === 'Configurações' ? 'active' : ''}`} onClick={() => setActiveTab('Configurações')}><Settings size={18} /> Configurações</div>
        </div>

        {pollingSpeed > 0 && (
          <div style={{ marginTop: 'auto', padding: '1rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '8px', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-primary)', fontSize: '0.85rem', fontWeight: 'bold' }}>
              <span className="spinner" style={{ width: '12px', height: '12px', borderWidth: '2px', borderColor: 'var(--accent-primary) transparent var(--accent-primary) transparent' }}></span>
              Telemetria Ativa ({pollingSpeed}s)
            </div>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {data && data.rag_context ? (
          <div className="dashboard-grid fade-in">
            
            {/* Métricas Globais */}
            {(activeTab === 'Visão Geral' || activeTab === 'Mercado' || activeTab === 'Mapa Orbital') && (
              <div className="dashboard-wide">
                <MetricsPanel 
                  ndvi_mean={data.ndvi_summary?.ndvi_mean}
                  stress_pct={data.ndvi_summary?.stress_pct_severe}
                  risk_score={data.rag_context?.yield_risk_score}
                  app_stress={data.esg?.app_stress_pct}
                  basis_atual={data.basis?.basis_atual}
                  basis_ind={data.basis?.basis_indicativo}
                  gap={data.basis?.convergence_gap}
                  ppe={data.basis?.ppe_hint_rs_saca}
                />
              </div>
            )}

            {/* ABA: Visão Geral (Agora com Chat!) */}
            {activeTab === 'Visão Geral' && (
              <>
                <div className="dashboard-wide">
                  <EsgStatus redFlag={data.esg?.red_flag} reason={data.esg?.message} />
                </div>
                <div className="dashboard-wide">
                  <ChatPanel ragContext={data.rag_context} />
                </div>
              </>
            )}

            {/* ABA: Mapa Orbital */}
            {activeTab === 'Mapa Orbital' && (
              <div className="dashboard-wide">
                <OrbitalMap 
                  ndviBase64={data.ndvi_overlay_png_b64} 
                  allNdvisBase64={data.all_ndvis_b64}
                  activeCommodity={activeCommodity}
                  soyPriceCents={sacaPrice}
                  cornPriceCents={cornPrice}
                  coffeePriceCents={coffeePrice}
                  cattlePriceCents={cattlePrice}
                />
              </div>
            )}

            {/* ABA: Mercado & Basis */}
            {activeTab === 'Mercado' && (
              <div className="dashboard-wide">
                <FinancialChart 
                  basis_atual={data.basis?.basis_atual}
                  basis_indicativo={data.basis?.basis_indicativo}
                  futures_prices={data.futures_curve?.prices}
                  curve_shape={data.basis?.curve_shape}
                  market_meta={data.market_meta}
                  activeCommodity={activeCommodity}
                  setActiveCommodity={setActiveCommodity}
                  localPrices={{
                    soy: sacaPrice,
                    corn: cornPrice,
                    coffee: coffeePrice,
                    cattle: cattlePrice
                  }}
                />
              </div>
            )}

            {/* ABA: Edge IoT */}
            {activeTab === 'IoT' && data.rag_context?.soil_moisture_pct !== undefined && (
              <div className="dashboard-wide">
                 <TelemetryCard moisture={moistureState} nitrogen={nitrogenState} temperature={tempState} cattleActivity={cattleState} />
              </div>
            )}

            {/* ABA: Configurações (Formulários movidos para cá + Briefing antigo) */}
            {activeTab === 'Configurações' && (
              <>
                <div className="glass-panel dashboard-wide" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                  
                  {/* Formulário de Configuração */}
                  <div>
                    <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Settings size={18} /> Controles da Simulação
                    </h3>
                    <form onSubmit={(e) => { e.preventDefault(); fetchAnalysis(); }}>
                      
                      <div className="form-group">
                        <label style={{ display: 'flex', alignItems: 'center' }}>
                          <input type="checkbox" checked={esgFlag} onChange={e => setEsgFlag(e.target.checked)} />
                          Simular Red Flag (ESG)
                        </label>
                      </div>

                      <div className="form-group">
                        <label>Preço Físico Soja (R$/saca)</label>
                        <input type="number" value={sacaPrice} onChange={e => setSacaPrice(Number(e.target.value))} step="0.5" />
                      </div>

                      <div className="form-group">
                        <label>Preço Físico Milho (R$/saca)</label>
                        <input type="number" value={cornPrice} onChange={e => setCornPrice(Number(e.target.value))} step="0.5" />
                      </div>

                      <div className="form-group">
                        <label>Preço Físico Café (R$/saca)</label>
                        <input type="number" value={coffeePrice} onChange={e => setCoffeePrice(Number(e.target.value))} step="5" />
                      </div>

                      <div className="form-group">
                        <label>Preço Físico Boi Gordo (R$/@)</label>
                        <input type="number" value={cattlePrice} onChange={e => setCattlePrice(Number(e.target.value))} step="1" />
                      </div>

                      <div className="form-group">
                        <label style={{ display: 'flex', alignItems: 'center' }}>
                          <input type="checkbox" checked={useIoT} onChange={e => setUseIoT(e.target.checked)} />
                          Ativar Edge IoT / Mock
                        </label>
                      </div>

                      <div className="form-group">
                        <label>Velocidade de Medição (Polling Rate em Segundos)</label>
                        <input type="range" min="0" max="30" step="1" value={pollingSpeed} onChange={e => setPollingSpeed(Number(e.target.value))} />
                        <div style={{ textAlign: 'right', fontSize: '0.85rem', color: pollingSpeed > 0 ? 'var(--success)' : 'var(--text-muted)' }}>
                          {pollingSpeed > 0 ? `Atualizando a cada ${pollingSpeed}s` : 'Desligado (Manual)'}
                        </div>
                      </div>

                      <button type="submit" className="primary" disabled={loading} style={{ marginTop: '1rem' }}>
                        {loading ? 'Sincronizando...' : 'Sincronizar Agora'}
                      </button>
                    </form>
                  </div>

                  {/* Informações de Sistema (Antigo Briefing) */}
                  <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1.5rem', borderRadius: '8px', border: '1px dashed var(--panel-border)' }}>
                    <h3 style={{ marginBottom: '1rem', fontSize: '1rem', color: 'var(--text-muted)' }}>Relatório de Sistema (Raw Briefing)</h3>
                    <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6', fontSize: '0.85rem', color: 'var(--text-main)', maxHeight: '300px', overflowY: 'auto' }}>
                      {data.briefing_markdown}
                    </div>
                  </div>

                </div>
              </>
            )}

          </div>
        ) : data && data.error ? (
          <div className="glass-panel" style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--danger)' }}>
            <h3>Erro de Conexão</h3>
            <p style={{ color: 'var(--text-muted)' }}>O Back-end Python não está rodando ou ocorreu um erro:</p>
            <p style={{ color: 'var(--danger)', marginTop: '0.5rem', fontFamily: 'monospace' }}>{data.error}</p>
          </div>
        ) : (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <span className="spinner" style={{ width: '40px', height: '40px' }}></span>
          </div>
        )}
      </main>
    </div>
  );
}
