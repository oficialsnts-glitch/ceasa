# Test Credentials

## ADM Master (auto-bootstrap)
- **Email:** oficialsnts@gmail.com
- **Senha:** 0fici@lSnts27
- **Role:** admin
- **Observação:** No primeiro login, se a conta não existir no Firebase Auth, é criada automaticamente com esta senha. O documento `users/{uid}` é forçado para `role="admin"` e `storeName="Central"`.

## Firebase Project
- **Project ID:** verduras-c2a29
- **Requisitos no console (uma vez):**
  1. Authentication → Sign-in method → Email/Password: **habilitado**
  2. Authentication → Authorized domains: incluir domínio de deploy (Vercel)
  3. Firestore Rules: permitir leitura/escrita autenticada em `users`, `suppliers`, `products`, `orders`
