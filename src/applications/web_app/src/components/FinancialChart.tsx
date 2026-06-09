'use client';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, LabelList } from 'recharts';
import { useState } from 'react';

interface FinancialChartProps {
  basis_atual: number;
  basis_indicativo: number;
  futures_prices: number[];
  curve_shape: string;
  market_meta?: any;
  localPrices?: any;
  activeCommodity: string;
  setActiveCommodity: (c: string) => void;
}

export default function FinancialChart({ basis_atual, basis_indicativo, futures_prices, curve_shape, market_meta, localPrices, activeCommodity, setActiveCommodity }: FinancialChartProps) {
  const [currencyMode, setCurrencyMode] = useState('BRL'); 

  const ptax = market_meta?.ptax_media || 5.0;

  // Conversões (Cents p/ Bolsa -> USD p/ Saca/Arroba)
  const conv_soy = (cents: number) => (cents / 100) * 2.2046;
  const conv_corn = (cents: number) => (cents / 100) * 2.3622;
  const conv_coffee = (cents: number) => (cents / 100) * 132.277;
  const conv_cattle = (cents: number) => (cents / 100) * 33.069;
  
  const getConvertedPrice = (cents: number, type: string, mode: string) => {
    if (!cents) return 0;
    if (mode === 'Bolsa') return cents;
    let usd = 0;
    if (type === 'soja') usd = conv_soy(cents);
    if (type === 'milho') usd = conv_corn(cents);
    if (type === 'cafe') usd = conv_coffee(cents);
    if (type === 'boi') usd = conv_cattle(cents);
    if (mode === 'USD') return usd;
    if (mode === 'BRL') return usd * ptax;
    return cents;
  };

  const getFormatLabel = (type: string, mode: string) => {
    if (mode === 'BRL') return type === 'boi' ? 'R$/@' : 'R$/sc';
    if (mode === 'USD') return type === 'boi' ? 'U$/@' : 'U$/sc';
    if (type === 'soja' || type === 'milho') return '¢/bu';
    return '¢/lb';
  };

  // Curva Dinamica e Basis Dinamico (Sincronizado com activeCommodity)
  let dynamicLineData = [];
  let dynamicBasisData = [];
  let currentCurveShape = 'flat';

  if (activeCommodity === 'soja') {
    dynamicLineData = futures_prices?.map((p, i) => ({
      name: i === 0 ? 'M1 (curto)' : i === 1 ? 'M2' : 'M3 (longo)',
      price: p || 0
    })) || [];
    dynamicBasisData = [
      { name: 'Atual', pts: basis_atual || 0 },
      { name: 'Indicativo', pts: basis_indicativo || 0 }
    ];
    currentCurveShape = curve_shape;
  } else if (activeCommodity === 'milho') {
    const c = market_meta?.corn_cents || 0;
    dynamicLineData = [{name: 'M1 (curto)', price: c-5}, {name: 'M2', price: c}, {name: 'M3 (longo)', price: c+8}];
    const spread = (localPrices?.corn || 0) - getConvertedPrice(c, 'milho', 'BRL');
    dynamicBasisData = [{name: 'Atual', pts: spread}, {name: 'Indicativo', pts: spread + 2.5}];
    currentCurveShape = 'contango';
  } else if (activeCommodity === 'cafe') {
    const c = market_meta?.coffee_cents || 0;
    dynamicLineData = [{name: 'M1 (curto)', price: c+10}, {name: 'M2', price: c}, {name: 'M3 (longo)', price: c-5}];
    const spread = (localPrices?.coffee || 0) - getConvertedPrice(c, 'cafe', 'BRL');
    dynamicBasisData = [{name: 'Atual', pts: spread}, {name: 'Indicativo', pts: spread - 15}];
    currentCurveShape = 'backwardation';
  } else if (activeCommodity === 'boi') {
    const c = market_meta?.cattle_cents || 0;
    dynamicLineData = [{name: 'M1 (curto)', price: c-2}, {name: 'M2', price: c}, {name: 'M3 (longo)', price: c+3}];
    const spread = (localPrices?.cattle || 0) - getConvertedPrice(c, 'boi', 'BRL');
    dynamicBasisData = [{name: 'Atual', pts: spread}, {name: 'Indicativo', pts: spread + 1.5}];
    currentCurveShape = 'contango';
  }

  // Historico Dinamico
  let rawHistoryData = [];
  let currentCommodityStr = '';
  
  if (activeCommodity === 'soja') {
    rawHistoryData = market_meta?.b3_history || [];
    currentCommodityStr = `Soja (CBOT ${market_meta?.b3_contract || 'ZS=F'})`;
  } else if (activeCommodity === 'milho') {
    rawHistoryData = market_meta?.corn_history || [];
    currentCommodityStr = 'Milho (CBOT ZC=F)';
  } else if (activeCommodity === 'cafe') {
    rawHistoryData = market_meta?.coffee_history || [];
    currentCommodityStr = 'Café (ICE KC=F)';
  } else if (activeCommodity === 'boi') {
    rawHistoryData = market_meta?.cattle_history || [];
    currentCommodityStr = 'Boi Gordo (CME LE=F)';
  }

  const historyData = rawHistoryData.map((d: any) => ({
    date: d.date,
    price: parseFloat(getConvertedPrice(d.price, activeCommodity, currencyMode).toFixed(2))
  }));

  const yAxisDomain = currencyMode === 'Bolsa' ? ['auto', 'auto'] : [
    (dataMin: number) => Math.max(0, dataMin - (dataMin * 0.05)), 
    (dataMax: number) => dataMax + (dataMax * 0.05)
  ];

  return (
    <div className="glass-panel fade-in" style={{ animationDelay: '0.2s' }}>
      <h3 style={{ marginBottom: '1rem' }}>Mercado — Basis & Curva</h3>

      {/* PAINEL DE MERCADOS GLOBAIS VS LOCAIS */}
      {market_meta && localPrices && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
          {/* Soja */}
          <div style={{ background: 'rgba(59, 130, 246, 0.1)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Soja (CBOT {market_meta.b3_contract})</p>
            <p style={{ fontSize: '1.4rem', fontWeight: 'bold' }}>R$ {getConvertedPrice(market_meta.cbot_cents, 'soja', 'BRL').toFixed(2)} <span style={{fontSize:'0.8rem', color:'var(--text-muted)'}}>/sc</span></p>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>U$ {getConvertedPrice(market_meta.cbot_cents, 'soja', 'USD').toFixed(2)} /sc</p>
            <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
               <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Físico Local: R$ {localPrices.soy?.toFixed(2)}/sc</p>
               <p style={{ fontSize: '0.85rem', fontWeight: 'bold', color: basis_atual > 0 ? 'var(--success)' : 'var(--danger)' }}>Basis: {basis_atual > 0 ? '+' : ''}{basis_atual?.toFixed(2)} pts</p>
            </div>
          </div>
          
          {/* Milho */}
          <div style={{ background: 'rgba(234, 179, 8, 0.1)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(234, 179, 8, 0.3)' }}>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Milho (CBOT ZC=F)</p>
            <p style={{ fontSize: '1.4rem', fontWeight: 'bold', color: '#eab308' }}>R$ {getConvertedPrice(market_meta.corn_cents, 'milho', 'BRL').toFixed(2)} <span style={{fontSize:'0.8rem', color:'var(--text-muted)'}}>/sc</span></p>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>U$ {getConvertedPrice(market_meta.corn_cents, 'milho', 'USD').toFixed(2)} /sc</p>
            <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
               <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Físico Local: R$ {localPrices.corn?.toFixed(2)}/sc</p>
               <p style={{ fontSize: '0.85rem', fontWeight: 'bold', color: 'var(--text-main)' }}>Spread: {(localPrices.corn - getConvertedPrice(market_meta.corn_cents, 'milho', 'BRL')).toFixed(2)} R$/sc</p>
            </div>
          </div>

          {/* Café */}
          <div style={{ background: 'rgba(120, 53, 15, 0.1)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(120, 53, 15, 0.3)' }}>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Café Arábica (ICE KC=F)</p>
            <p style={{ fontSize: '1.4rem', fontWeight: 'bold', color: '#fcd34d' }}>R$ {getConvertedPrice(market_meta.coffee_cents, 'cafe', 'BRL').toFixed(2)} <span style={{fontSize:'0.8rem', color:'var(--text-muted)'}}>/sc</span></p>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>U$ {getConvertedPrice(market_meta.coffee_cents, 'cafe', 'USD').toFixed(2)} /sc</p>
            <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
               <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Físico Local: R$ {localPrices.coffee?.toFixed(2)}/sc</p>
               <p style={{ fontSize: '0.85rem', fontWeight: 'bold', color: 'var(--text-main)' }}>Spread: {(localPrices.coffee - getConvertedPrice(market_meta.coffee_cents, 'cafe', 'BRL')).toFixed(2)} R$/sc</p>
            </div>
          </div>

          {/* Boi Gordo */}
          <div style={{ background: 'rgba(217, 119, 6, 0.1)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(217, 119, 6, 0.3)' }}>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Boi Gordo (CME LE=F)</p>
            <p style={{ fontSize: '1.4rem', fontWeight: 'bold', color: '#d97706' }}>R$ {getConvertedPrice(market_meta.cattle_cents, 'boi', 'BRL').toFixed(2)} <span style={{fontSize:'0.8rem', color:'var(--text-muted)'}}>/@</span></p>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>U$ {getConvertedPrice(market_meta.cattle_cents, 'boi', 'USD').toFixed(2)} /@</p>
            <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
               <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Físico Local: R$ {localPrices.cattle?.toFixed(2)}/@</p>
               <p style={{ fontSize: '0.85rem', fontWeight: 'bold', color: 'var(--text-main)' }}>Spread: {(localPrices.cattle - getConvertedPrice(market_meta.cattle_cents, 'boi', 'BRL')).toFixed(2)} R$/@</p>
            </div>
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div style={{ height: '220px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={dynamicLineData} margin={{ top: 20, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} tickMargin={10} />
              <YAxis stroke="var(--text-muted)" fontSize={12} domain={['auto', 'auto']} tickFormatter={(v) => v.toFixed(0)} />
              <Tooltip 
                contentStyle={{ background: '#101623', border: '1px solid var(--panel-border)', borderRadius: '8px' }}
                labelStyle={{ color: 'var(--text-muted)', marginBottom: '5px' }}
                formatter={(value: number) => [`${value} ¢`, 'Cotação']}
              />
              <Line type="monotone" dataKey="price" stroke="var(--accent-primary)" strokeWidth={3} dot={{ r: 4, fill: 'var(--accent-primary)' }} activeDot={{ r: 6 }} name="Preço">
                <LabelList dataKey="price" position="top" fill="rgba(255,255,255,0.8)" fontSize={11} formatter={(v: any) => typeof v === 'number' ? v.toFixed(1) : ''} />
              </Line>
            </LineChart>
          </ResponsiveContainer>
          <div style={{ textAlign: 'center', marginTop: '0.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Curva Futuros (Formato: <span style={{ color: currentCurveShape === 'backwardation' ? 'var(--danger)' : currentCurveShape === 'contango' ? 'var(--success)' : 'var(--text-main)', fontWeight: 'bold', textTransform: 'capitalize' }}>{currentCurveShape}</span>)
          </div>
        </div>

        <div style={{ height: '220px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dynamicBasisData} margin={{ top: 20, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} tickMargin={10} />
              <YAxis stroke="var(--text-muted)" fontSize={12} domain={['auto', 'auto']} />
              <Tooltip 
                contentStyle={{ background: '#101623', border: '1px solid var(--panel-border)', borderRadius: '8px' }}
                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                formatter={(value: number) => [`${value}`, activeCommodity === 'soja' ? 'Pontos (pts)' : 'R$ Spread']}
              />
              <Bar dataKey="pts" radius={[4, 4, 0, 0]}>
                {dynamicBasisData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.pts > 0 ? 'var(--success)' : entry.pts < 0 ? 'var(--danger)' : '#6b7280'} />
                ))}
                <LabelList dataKey="pts" position="top" fill="rgba(255,255,255,0.8)" fontSize={11} formatter={(v: any) => typeof v === 'number' ? v.toFixed(2) : ''} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div style={{ textAlign: 'center', marginTop: '0.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Evolução do {activeCommodity === 'soja' ? 'Basis' : 'Spread'} (Atual vs Esperado)
          </div>
        </div>
      </div>

      {/* GRÁFICO HISTÓRICO YFINANCE */}
      {market_meta && historyData.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Evolução Histórica 30 Dias — {currentCommodityStr}</p>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                 {['soja', 'milho', 'cafe', 'boi'].map(c => (
                   <button 
                      key={c}
                      onClick={() => setActiveCommodity(c)}
                      style={{
                        padding: '0.3rem 0.8rem', fontSize: '0.8rem', borderRadius: '4px', cursor: 'pointer',
                        background: activeCommodity === c ? 'var(--accent-primary)' : 'rgba(255,255,255,0.1)',
                        border: 'none', color: '#fff', fontWeight: activeCommodity === c ? 'bold' : 'normal'
                      }}
                   >
                     {c.toUpperCase()}
                   </button>
                 ))}
              </div>
            </div>
            
            <div style={{ textAlign: 'right' }}>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Moeda / Unidade</p>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                 {['USD', 'BRL'].map(m => (
                   <button 
                      key={m}
                      onClick={() => setCurrencyMode(m)}
                      style={{
                        padding: '0.3rem 0.8rem', fontSize: '0.8rem', borderRadius: '4px', cursor: 'pointer',
                        background: currencyMode === m ? 'var(--success)' : 'rgba(255,255,255,0.1)',
                        border: 'none', color: '#fff', fontWeight: currencyMode === m ? 'bold' : 'normal'
                      }}
                   >
                     {m}
                   </button>
                 ))}
              </div>
            </div>
          </div>

          <div style={{ height: '250px', width: '100%', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', padding: '1rem', border: '1px dashed var(--panel-border)' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={historyData} margin={{ top: 20, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={11} tickMargin={10} minTickGap={20} />
                <YAxis stroke="var(--text-muted)" fontSize={11} domain={yAxisDomain} tickFormatter={(v) => v.toFixed(currencyMode==='Bolsa'?0:2)} />
                <Tooltip 
                  contentStyle={{ background: '#101623', border: '1px solid var(--panel-border)', borderRadius: '8px' }}
                  labelStyle={{ color: 'var(--text-muted)', marginBottom: '5px' }}
                  formatter={(value: number) => [`${value} ${getFormatLabel(activeCommodity, currencyMode)}`, 'Fechamento']}
                />
                <Line type="monotone" dataKey="price" stroke="#10b981" strokeWidth={2} dot={{ r: 0 }} activeDot={{ r: 5, fill: '#10b981' }} name="Fechamento">
                  <LabelList dataKey="price" position="top" fill="rgba(255,255,255,0.3)" fontSize={9} formatter={(v: any) => typeof v === 'number' ? v.toFixed(1) : ''} />
                </Line>
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
