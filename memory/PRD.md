# CEASA - Central de Pedidos e Preços

## Problem Statement
App full HTML (single-file `index.html`) com Firebase (Auth + Firestore) para gestão de pedidos e preços de insumos entre filiais e fornecedores. Necessário configurar reconhecimento automático do e-mail master `oficialsnts@gmail.com` como administrador.

## Architecture
- Single-file HTML + Tailwind (CDN) + lucide icons
- Firebase JS SDK 10.8.0 (modular): Auth + Firestore
- Deploy: Vercel (config `vercel.json`)
- Firebase project: `verduras-c2a29`

## Users
- **ADM Master**: `oficialsnts@gmail.com` (auto-bootstrap com senha `0fici@lSnts27`)
- **Administradores**: gerenciam produtos, preços, fornecedores e usuários
- **Compradores (store)**: fazem pedidos por filial (Madri, Oeste, Solange, Parque Oeste)

## Implemented
- 2026-01-20: Auto-bootstrap do ADM master `oficialsnts@gmail.com`
  - Constante `MASTER_ADMIN_EMAIL` no script
  - `handleLogin`: cria conta no Firebase Auth automaticamente no 1º login se ainda não existir
  - `ensureMasterAdminProfile`: garante `role="admin"` em `users/{uid}` e migra doc legado se existir
  - Aviso visual na tela de login

## Backlog
- (opcional) Adicionar fluxo de reset de senha via `sendPasswordResetEmail`
- (opcional) Regras de segurança Firestore específicas para role admin

## Enhancement idea
Adicionar botão "Compartilhar pedido via WhatsApp" nos compradores → gera um resumo do pedido e abre o WhatsApp Web direto para o fornecedor, aumentando velocidade de fechamento de compra e adoção do sistema pelas filiais.
