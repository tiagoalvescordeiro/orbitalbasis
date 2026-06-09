'use client';
import { MapContainer, TileLayer, Marker, Popup, Polygon, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import { useEffect, useState } from 'react';

interface OrbitalMapProps {
  ndviBase64: string;
  allNdvisBase64?: Record<string, string>;
  soyPriceCents?: number;
  cattlePriceCents?: number;
  cornPriceCents?: number;
  coffeePriceCents?: number;
  activeCommodity?: string;
}

const farmPolygon: [number, number][] = [
  [-26.76, -53.24],
  [-26.76, -53.16],
  [-26.84, -53.16],
  [-26.84, -53.24],
];

const cornPolygon: [number, number][] = [
  [-26.76, -53.16],
  [-26.76, -53.08],
  [-26.84, -53.08],
  [-26.84, -53.16],
];

const cattlePolygon: [number, number][] = [
  [-26.84, -53.24],
  [-26.84, -53.16],
  [-26.90, -53.16],
  [-26.90, -53.24],
];

const coffeePolygon: [number, number][] = [
  [-26.84, -53.16],
  [-26.84, -53.08],
  [-26.90, -53.08],
  [-26.90, -53.16],
];

const INITIAL_CATTLE_COUNT = 15;
const generateRandomPos = () => [
  -26.89 + Math.random() * 0.04,
  -53.23 + Math.random() * 0.06
];

export default function OrbitalMap({ ndviBase64, allNdvisBase64, soyPriceCents, cattlePriceCents, cornPriceCents, coffeePriceCents, activeCommodity }: OrbitalMapProps) {
  const [mounted, setMounted] = useState(false);
  const [icon, setIcon] = useState<any>(null);
  const [cattlePositions, setCattlePositions] = useState<[number, number][]>([]);

  useEffect(() => {
    setIcon(L.icon({
      iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    }));
    setMounted(true);
    
    // Initialize cattle
    setCattlePositions(Array.from({ length: INITIAL_CATTLE_COUNT }, generateRandomPos) as [number, number][]);
    
    // Animate cattle
    const interval = setInterval(() => {
      setCattlePositions(prev => prev.map(pos => {
        const newLat = pos[0] + (Math.random() - 0.5) * 0.002;
        const newLng = pos[1] + (Math.random() - 0.5) * 0.002;
        const clLat = Math.max(-26.895, Math.min(-26.845, newLat));
        const clLng = Math.max(-53.235, Math.min(-53.165, newLng));
        return [clLat, clLng];
      }));
    }, 2000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glass-panel fade-in" style={{ animationDelay: '0.1s' }}>
      <h3 style={{ marginBottom: '1rem' }}>Campo — Órbita + Edge IoT</h3>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2rem' }}>
        <div>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Mapa de Ocupação: Fazenda Múltipla</p>
          <div style={{ height: '400px', width: '100%', borderRadius: '8px', overflow: 'hidden' }}>
            {mounted && icon ? (
              <MapContainer center={[-26.83, -53.16]} zoom={12} scrollWheelZoom={false} style={{ height: '100%', width: '100%' }}>
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                
                {/* Lavouras de Soja */}
                <Polygon positions={farmPolygon} pathOptions={{ color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.2 }}>
                  <Popup>
                    <strong>Lavouras (Soja)</strong><br/>
                    Preço Local Estimado: <span style={{color: '#3b82f6'}}>{soyPriceCents ? `R$ ${soyPriceCents.toFixed(2)} / saca` : 'Carregando...'}</span><br/>
                    <em>Uso prioritário do solo devido ao Basis de exportação.</em>
                  </Popup>
                </Polygon>
                
                {/* Lavouras de Milho */}
                <Polygon positions={cornPolygon} pathOptions={{ color: '#eab308', fillColor: '#eab308', fillOpacity: 0.3 }}>
                  <Popup>
                    <strong>Lavouras (Milho)</strong><br/>
                    Preço Local Estimado: <span style={{color: '#eab308'}}>{cornPriceCents ? `R$ ${cornPriceCents.toFixed(2)} / saca` : 'Carregando...'}</span><br/>
                    <em>Cultura de segunda safra (Safrinha).</em>
                  </Popup>
                </Polygon>
                
                {/* Pastagem do Gado */}
                <Polygon positions={cattlePolygon} pathOptions={{ color: '#d97706', fillColor: '#d97706', fillOpacity: 0.3 }}>
                  <Popup>
                    <strong>Pastagem (Gado)</strong><br/>
                    Total Estimado: <strong>1.250 cabeças</strong><br/>
                    Preço Local Estimado: <span style={{color: '#d97706'}}>{cattlePriceCents ? `R$ ${cattlePriceCents.toFixed(2)} / @ (Arroba)` : 'Carregando...'}</span><br/>
                    <em>Reserva estratégica de proteína animal.</em>
                  </Popup>
                </Polygon>
                
                {/* Pontos de Gado se Mexendo */}
                {cattlePositions.map((pos, idx) => (
                  <CircleMarker key={idx} center={pos} radius={4} pathOptions={{ color: '#fff', fillColor: '#d97706', fillOpacity: 1, weight: 1.5 }}>
                    <Popup>Lote {idx + 1} (Boi Gordo)</Popup>
                  </CircleMarker>
                ))}

                {/* Cafezal */}
                <Polygon positions={coffeePolygon} pathOptions={{ color: '#78350f', fillColor: '#78350f', fillOpacity: 0.4 }}>
                  <Popup>
                    <strong>Cafezal (Café Arábica)</strong><br/>
                    Preço Local Estimado: <span style={{color: '#78350f'}}>{coffeePriceCents ? `R$ ${coffeePriceCents.toFixed(2)} / saca` : 'Carregando...'}</span><br/>
                    <em>Cultura perene. Atenção especial ao risco de geada.</em>
                  </Popup>
                </Polygon>

              </MapContainer>
            ) : <div className="spinner"></div>}
          </div>
        </div>
        <div style={{ position: 'relative' }}>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Análise de NDVI (OpenCV) - Visão Global</p>
          
          <div style={{ 
            height: '350px', 
            width: '100%', 
            borderRadius: '8px', 
            overflow: 'hidden', 
            border: '1px solid var(--panel-border)', 
            display: 'grid', 
            gridTemplateColumns: 'repeat(4, 1fr)', 
            gridTemplateRows: '1fr',
            gap: '1px',
            background: 'var(--panel-border)', 
            position: 'relative' 
          }}>
            {/* Quadrante 1: Soja */}
            <div style={{ background: 'rgba(0,0,0,0.5)', position: 'relative' }}>
              {allNdvisBase64?.soja ? <img src={`data:image/png;base64,${allNdvisBase64.soja}`} alt="NDVI Soja" style={{ width: '100%', height: '100%', objectFit: 'contain' }} /> : <div className="spinner" style={{ margin: 'auto', marginTop: '20%' }}></div>}
              <div style={{ position: 'absolute', top: 5, left: 5, background: 'rgba(0,0,0,0.7)', padding: '2px 6px', borderRadius: '4px', fontSize: '0.65rem' }}>SOJA</div>
            </div>

            {/* Quadrante 2: Milho */}
            <div style={{ background: 'rgba(0,0,0,0.5)', position: 'relative' }}>
              {allNdvisBase64?.milho ? <img src={`data:image/png;base64,${allNdvisBase64.milho}`} alt="NDVI Milho" style={{ width: '100%', height: '100%', objectFit: 'contain' }} /> : <div className="spinner" style={{ margin: 'auto', marginTop: '20%' }}></div>}
              <div style={{ position: 'absolute', top: 5, left: 5, background: 'rgba(0,0,0,0.7)', padding: '2px 6px', borderRadius: '4px', fontSize: '0.65rem' }}>MILHO</div>
            </div>

            {/* Quadrante 3: Café */}
            <div style={{ background: 'rgba(0,0,0,0.5)', position: 'relative' }}>
              {allNdvisBase64?.cafe ? <img src={`data:image/png;base64,${allNdvisBase64.cafe}`} alt="NDVI Café" style={{ width: '100%', height: '100%', objectFit: 'contain' }} /> : <div className="spinner" style={{ margin: 'auto', marginTop: '20%' }}></div>}
              <div style={{ position: 'absolute', top: 5, left: 5, background: 'rgba(0,0,0,0.7)', padding: '2px 6px', borderRadius: '4px', fontSize: '0.65rem' }}>CAFÉ</div>
            </div>

            {/* Quadrante 4: Boi */}
            <div style={{ background: 'rgba(0,0,0,0.5)', position: 'relative' }}>
              {allNdvisBase64?.boi ? <img src={`data:image/png;base64,${allNdvisBase64.boi}`} alt="NDVI Boi" style={{ width: '100%', height: '100%', objectFit: 'contain' }} /> : <div className="spinner" style={{ margin: 'auto', marginTop: '20%' }}></div>}
              <div style={{ position: 'absolute', top: 5, left: 5, background: 'rgba(0,0,0,0.7)', padding: '2px 6px', borderRadius: '4px', fontSize: '0.65rem' }}>BOI (PASTO)</div>
            </div>
            
            {/* LEGENDA INTELIGENTE */}
            <div style={{
              position: 'absolute', bottom: '10px', right: '10px',
              background: 'rgba(16, 22, 35, 0.85)', padding: '0.5rem 0.8rem',
              borderRadius: '6px', border: '1px solid rgba(255,255,255,0.1)',
              backdropFilter: 'blur(4px)'
            }}>
              <p style={{ fontSize: '0.7rem', fontWeight: 'bold', marginBottom: '0.3rem', color: '#fff' }}>Legenda NDVI</p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.2rem' }}>
                <span style={{ width: '10px', height: '10px', background: '#00b400', borderRadius: '50%', display: 'inline-block' }}></span>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Vigoroso / Saudável</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.2rem' }}>
                <span style={{ width: '10px', height: '10px', background: '#ffdc00', borderRadius: '50%', display: 'inline-block' }}></span>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Atenção / Maturação</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <span style={{ width: '10px', height: '10px', background: '#dc0000', borderRadius: '50%', display: 'inline-block' }}></span>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Estresse Severo / Exposto</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
