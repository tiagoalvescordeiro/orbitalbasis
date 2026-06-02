"""
Parâmetros de referência — Ancord Agro 100 (formação de preço / basis / PPE).

Uso educacional e calibração do demo OrbitalBasis. Não substitui cotações ao vivo.
Fonte: planilha interna Ancord Agro 100 (Aulas 1 e 2).
"""

from __future__ import annotations

# --- Aula 2: basis cash vs CBOT ---
ANCORD_AULA2_CASH_RS_SACA = 115.63425008758172
ANCORD_AULA2_CAMBIO = 5.5
ANCORD_AULA2_CBOT_CENTS = 1063.0
ANCORD_AULA2_BASIS_CENTS = -109.3390589298267

# --- Aula 1: cascata PPE / exportação ---
ANCORD_AULA1_CAMBIO = 5.38
ANCORD_AULA1_CBOT_CENTS = 1158.0
ANCORD_PREMIO_FOB_USD_T = 50.0
ANCORD_FOBBINGS_USD_T = 11.0
ANCORD_FRETE_MAR_USD_T = 46.0  # Aula 2; Aula 1 usa ~45
ANCORD_LOG_RS_T = 470.0
ANCORD_FRETE_INTERNO_RS_T = 460.0
ANCORD_PPE_EX_WORKS_RS_SACA = 111.53509464959997

# Conversão soja (Anec / Ancord): bushels por tonelada métrica
SOY_BUSHELS_PER_US_TON = 36.7454

# kg por bushel de soja → fator saca (60 kg) / bushel; Ancord usa 2,2046
SACA_TO_BUSHEL_FACTOR = 2.2046

# Frete interno na origem (R$/saca), calibrado para PPE Ex-Works ≈ 111,54 (Aula 1)
ANCORD_FRETE_ORIGEM_RS_SACA = 38.4

# Default demo: cash físico da Aula 2 (pareado com exercício de basis)
DEFAULT_SACA_RS = round(ANCORD_AULA2_CASH_RS_SACA, 2)
