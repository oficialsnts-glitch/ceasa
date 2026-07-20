# CEASA - Central de Pedidos e Preços

## Problem Statement
App full HTML (single-file `index.html`) com Firebase (Auth + Firestore) para gestão de pedidos e preços de insumos entre filiais e fornecedores.

## Architecture
- Single-file HTML + Tailwind (CDN) + lucide icons
- Firebase JS SDK 10.8.0 (modular): Auth + Firestore
- Deploy: Vercel (config `vercel.json` com rewrites que preservam assets estáticos)
- Firebase project: `verduras-c2a29`
- **PWA installável** com service worker próprio (`/sw.js`) e manifest (`/manifest.webmanifest`)
- Servidor local (preview): `serve` estático na porta 3000 via supervisor

## Users
- **ADM Master**: `oficialsnts@gmail.com` (auto-bootstrap com senha `0fici@lSnts27`)
- **Administradores**: gerenciam produtos, preços, fornecedores e usuários
- **Compradores (store)**: fazem pedidos por filial (Madri, Oeste, Solange, Parque Oeste)

## Implemented
- 2026-01-20: **Cards do ADM iniciam fechados + ordenação alfabética**
  - Todos os cards de fornecedor no painel ADM começam **fechados**; abrem apenas com clique no header (evita scroll infinito ao entrar na Home com muitos fornecedores)
  - Cada card exibe badge com **contador de produtos** ao lado do nome
  - Botão de ordenação alfabética `A → Z` / `Z → A` no header do card (ícone `arrow-down-a-z` / `arrow-up-a-z`), com `event.stopPropagation()` para não confundir com o clique de abrir/fechar
  - Comparação usa `localeCompare(..., 'pt-BR', { sensitivity: 'base' })` (respeita acentuação e caixa)
  - Comprador (store) também recebe ordenação A→Z automática dos produtos dentro de cada fornecedor — melhora muito a busca visual
- 2026-01-20: **Coluna "Nome do Produto" fixa (sticky) durante rolagem horizontal**
  - Admin: coluna Ref foi consolidada num badge dentro da célula do Nome (economiza espaço, evita duas colunas fixas)
  - CSS `.table-sticky-first` reforçado: sombra direita mais visível (`6px 0 6px -4px`), borda separadora, fundos opacos preservados no hover e em linhas destacadas (`row-highlight`)
  - Comprador (store): Nome do Produto já era a primeira coluna, sticky ativa
  - Testado: com 400px de scroll lateral, Nome permanece em `left:13px` (fixo). Restante das colunas (Unidade, Preços, Filiais, Total, Ações) rola normalmente.
- 2026-01-20: **Formulário de inserção rápida na Home**
  - Barra de ações agora contém: Fornecedor, Nome do Produto, Preço de Compra (com máscara BRL), Quantidade e Unidade (un/kg/g/cx/dz/sc/L/ml/pct)
  - Ao clicar "Inserir Produto" o item é gravado no Firestore já com todos os campos preenchidos e o Custo Unitário recalculado
  - Formulário reseta e foca no Nome para inserção contínua rápida
- 2026-01-20: **Máscara de dinheiro BRL** (`formatBRL` / `parseBRL` / `formatBRLString`)
  - Digitação da direita pra esquerda: `1` → `0,01`, `12345` → `123,45`, `1000000` → `10.000,00`
  - Sem necessidade de apagar zeros ou digitar vírgula manualmente
  - Aplicada a: novo Preço de Compra na Home, Preço de Compra por linha, Preço de Venda Geral, Preço Multi por loja
  - Exibição consistente em pt-BR (custo unitário, tabela de preços, modal de resumo do pedido)
- 2026-01-20: Auto-bootstrap do ADM master `oficialsnts@gmail.com`
- 2026-01-20: **PWA completo** (imagem, instalação, mobile)
  - Ícone gerado via **Gemini Nano Banana** — caixa de madeira com hortifruti sobre gradiente esmeralda
  - Ícones em 6 tamanhos (16, 32, 180 apple, 192, 256, 384, 512 + maskable-512 + favicon.ico)
  - `manifest.webmanifest` com display standalone, shortcuts (Pedido/Preços), theme #047857, cores emerald
  - `sw.js` com estratégia dupla:
    - App shell (index.html, ícones, manifest, CDNs) -> cache-first para offline básico
    - **Firebase (firestore/auth/gstatic APIs) SEMPRE via rede** -> nunca cacheado, evitando race entre compradores concorrentes
    - Auto-update: `SKIP_WAITING` + `controllerchange` recarrega em nova versão
  - Botão flutuante "Instalar app" (`#pwa-install-btn`) escutando `beforeinstallprompt`
  - Instruções manuais para iOS (Adicionar à Tela de Início)
  - Toast de status online/offline
  - `offline.html` bonito para queda de rede
  - Meta tags iOS/Android/Windows completas (apple-mobile-web-app, msapplication-TileColor)
  - `viewport-fit=cover` + safe-area-inset padding
- 2026-01-20: **Race-condition eliminada nos pedidos**
  - `updateStoreQuantity` e `updateStoreQuantityFromAdmin` agora usam `updateDoc` com dot-notation (`quantities.{productId}`) + `deleteField()` — writes atômicos por campo no Firestore, seguros para múltiplos compradores editando a mesma filial ao mesmo tempo
  - Fallback para `setDoc({merge:true})` no primeiro write (documento inexistente)
  - Debounce de 300ms nas quantidades da loja para reduzir writes durante digitação
- 2026-01-20: **UX Mobile melhorada**
  - Tabelas com rolagem horizontal (`scroll-x`) com inércia iOS + indicadores visuais de "mais colunas" e primeira coluna sticky (`table-sticky-first`) — resolve o problema de ver o nome do produto enquanto rola as colunas de filiais/preços
  - Headers (admin + comprador) responsivos com wrap, título truncado, "Sair" oculto no mobile
  - Nav de abas com scroll horizontal
  - Cards da tela do comprador em 2 colunas com dimensões reduzidas no mobile
  - Inputs com `font-size:16px` no mobile (evita zoom automático iOS)
  - Padding reduzido em containers principais
  - `viewport-fit=cover` + `safe-area-inset-*` — respeita notch do iPhone
- Correção do `vercel.json`: rewrites agora excluem assets estáticos (icons, sw.js, manifest, imagens, JS, CSS) para não jogar tudo em `/index.html`
- Headers apropriados para `/sw.js` (no-cache), `/manifest.webmanifest` (content-type correto) e `/icons/*` (cache imutável 1 ano)

## Files Added
- `/app/manifest.webmanifest`
- `/app/sw.js`
- `/app/offline.html`
- `/app/icons/{icon-192,256,384,512,apple-touch-icon,maskable-512,favicon-16,32}.png` + `favicon.ico`
- `/app/scripts/gen_icon.py` (Gemini Nano Banana)
- `/app/scripts/resize_icons.py`
- `/app/frontend/package.json` (static server local)
- `/app/backend/.env` com `EMERGENT_LLM_KEY`

## Backlog
- (opcional) Reset de senha via `sendPasswordResetEmail`
- (opcional) Regras de segurança Firestore específicas por role
- (opcional) Fila local de pedidos quando offline com sync ao voltar online

## Enhancement idea
Adicionar botão **"Compartilhar pedido via WhatsApp"** nos compradores → gera um resumo do pedido (fornecedor, itens, valores) e abre WhatsApp Web direto para o fornecedor, aumentando velocidade de fechamento de compra e adoção do sistema pelas filiais. Também considere um **push notification (Firebase Cloud Messaging)** para avisar o comprador quando o ADM ajustar preço de item do seu pedido em andamento — evita conferência manual e aumenta a confiança operacional.
