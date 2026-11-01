# Arquitetura

- `rawsnes_obs.py` roda um servidor HTTP no loopback `127.0.0.1:8766`.
- A thread de consulta usa `API_GetUserRecentAchievements.php?u=...&y=...&m=60` com credencial Web API local.
- São aceitas apenas conquistas com `ConsoleName` de Super Nintendo/SNES/Super Famicom.
- Na primeira resposta, as conquistas pré-existentes são marcadas como conhecidas para evitar avisos antigos.
- Eventos novos são entregues por `/api/events?after=<seq>` e sondados pelo overlay a cada 250 ms.
- O overlay usa DOM via `textContent`, não injeta HTML dos dados recebidos.
- `/api/test` permite a demonstração via POST de origem local. `/audio/alert.wav` oferece o efeito CC0.
- O servidor local não fornece credenciais ao navegador; a chave fica no Windows DPAPI.
- Não há integração com o processo ou USB do RAW-SNES; a integração é exclusivamente **Web API do RetroAchievements → companion → OBS Browser Source**.

## Limitação de latência

Atraso total = tempo de reconhecimento/registro do achievement pelo serviço + tempo de atualização da API + espera até a próxima consulta (configurável) + até 250 ms para o Browser Source consultar o companion. Por isso, o intervalo configurado não garante atraso máximo exato.
