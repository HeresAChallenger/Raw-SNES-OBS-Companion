# Changelog

## [1.0.0] — 2026-10-31

- Versão inicial do companion independente para RAW-SNES e Super Nintendo.
- Filtro de achievements SNES/Super Famicom com emblemas, pontos e títulos.
- Overlay transparente para OBS Studio (520 × 160) e som demonstrativo CC0.
- Painel local, modo de demonstração e cinco intervalos de consulta.
- Porta 8766, separada da porta 8765 usada pelo MegaRaw OBS Companion.
- Web API Key armazenada com DPAPI em diretório específico do companion.
- Código Python 3 sem dependências externas; sem distribuição de conteúdo do RAW-SNES.
- Testes unitários e teste HTTP de demonstração.

**Limitadores**: não recebe eventos internos do RAW-SNES, depende de polling e de atualizações da API RetroAchievements. Não foi testado em uma sessão real de SNES no Windows/OBS nesta primeira versão.
**Validação em hardware:** confirmado funcionamento com Super Nintendo real, RAW-SNES e OBS pelo responsável do projeto.
