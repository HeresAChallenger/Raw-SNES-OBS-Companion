# RAW-SNES OBS Companion v1.0.0

**Primeira versão estável** — 31 de outubro de 2026.

**Validação:** o responsável confirmou o funcionamento com RAW-SNES, Super Nintendo real e OBS.

Notificações de achievements do RetroAchievements para o OBS enquanto você joga Super Nintendo/Super Famicom no hardware original com RAW-SNES.

### Destaques

- Overlay transparente 520 × 160 com título, descrição, emblema, pontos, jogo e modo Softcore/Hardcore.
- Painel local e botão de demonstração; reprodução de WAV CC0 editável localmente.
- Consulta da API com intervalos 2/3/5/10/15 segundos, com detecção de HTTP 429 e backoff.
- Credenciais do **companion** criptografadas com DPAPI por usuário Windows.
- Porta 8766, independente da 8765 usada no MegaRaw-OBS-Companion.
- Sem código, EXE ou dados sensíveis do RAW-SNES no pacote.

### Testes realizados

- Testes unitários para filtragem SNES, compatibilidade dos nomes dos campos e URLs de emblemas.
- Teste local da porta 8766, overlay, botão de demonstração, entrega de evento e arquivo WAV.

### Testes ainda necessários

- Exercício em Windows real com o OBS e RAW-SNES operando com FXPak Pro / SD2SNES.
- Registro de uma conquista nova e comparação da latência com a notificação nativa do RAW-SNES.
- Se houver falhas de limites da API, iniciar com 5 segundos e aumentar para 10/15 s.

**Compatibilidade:** Windows 10/11, Python 3.10+, OBS Studio. O pacote não contém RAW-SNES.