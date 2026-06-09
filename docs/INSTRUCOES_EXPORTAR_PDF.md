# Instruções rápidas — exportar PDF para a FIAP

## Caminho recomendado (automático)

Na raiz do projeto:

```bash
python scripts/generate_assets.py   # opcional — atualiza figuras
python scripts/generate_entrega_pdf.py
```

Saída canônica: **`docs/OrbitalBasis_Entrega_FIAP_2026.1.pdf`** (cópia também em `Downloads/`).

---

## Caminho manual (Word / Google Docs)

Use: **`PDF_ENTREGA_FIAP_COPIAR_WORD.txt`** (texto limpo, sem Markdown).

Alternativa com tabelas Markdown: `PDF_ENTREGA_FIAP.md`.

---

## Passo a passo (Word)

1. Abra `PDF_ENTREGA_FIAP_COPIAR_WORD.txt` → **Ctrl+A** → **Ctrl+C**.
2. Abra Word em branco → **Ctrl+V**.
3. Selecione cada bloco de código (indentado) → fonte **Consolas** 9 pt.
4. Título da página 1 e frase de pódio → **negrito**, 14 pt.
5. Seção 3 → **Inserir imagem** (sua captura do dashboard).
6. Seção 5 → substitua `[COLE AQUI O LINK...]` pelo URL do YouTube.
7. **Arquivo → Salvar como → PDF** → nome: `OrbitalBasis_Entrega_FIAP_2026.1.pdf`.

---

## Passo a passo (Google Docs)

1. Novo documento → colar o conteúdo do `.txt`.
2. Mesmas fontes (Consolas para código).
3. **Arquivo → Fazer download → Documento PDF**.

---

## Checklist final (1 minuto)

- [ ] Frase exata na 1ª página: **OrbitalBasis Team. QUERO CONCORRER.**
- [ ] 4 nomes completos + RMs
- [ ] Seções: Introdução, Desenvolvimento, Resultados, Conclusões, Links
- [ ] Nenhum código em imagem
- [ ] Link GitHub + YouTube preenchidos
- [ ] Um único arquivo PDF (não ZIP)

---

## Depois do PDF

1. Atualize `README.md` (seção Entrega FIAP) com links do PDF (Drive/portfolio) e YouTube.
2. Envie pelo portal conforme edital da disciplina.
