# Segurança e licença: RAW-SNES OBS Companion

1. O arquivo original `rawsnes_config.json` contém uma credencial (`ra_token`). **Não deve ser enviado ao GitHub, anexado a releases nem compartilhado em capturas de tela.** Se exposto, invalide/renove a credencial conforme as opções disponíveis no RetroAchievements.
2. **A Web API Key usada pelo companion é diferente do token de login do RAW-SNES.** Peça-a no painel do usuário. A chave é protegida pelo Windows DPAPI e gravada sob `%LOCALAPPDATA%\RawSNESObsOverlay\`.
3. O companion nunca utiliza `raw-snes.exe` nem o lê internamente: trata-se de uma integração via Web API pública. Não inclua nem altere o programa original.
4. O `LICENSE` do RAW-SNES não permite redistribuição do executável/código, trabalhos derivados nem engenharia reversa sem consentimento escrito do autor. Este projeto independente inclui apenas código MIT próprio e um som CC0.
5. A fonte OBS local (`127.0.0.1:8766`) não exige uma autenticação porque só deve ser usada no mesmo computador. Não exponha a porta em encaminhamentos de rede ou túneis. Por segurança, o servidor verifica o cabeçalho `Host` e a origem do POST de demonstração.
6. Em GitHub, publique apenas o fonte, `INICIAR.bat`, WAV CC0, testes e documentação. Nunca publique `raw-snes.exe`, `rawsnes_config.json`, chaves, ROMs, firmware, screenshots privadas ou logs pessoais.
7. O intervalo de 2 s é experimental e pode atingir o limite da API; começar em 5 s e aumentar para 10/15 s em HTTP 429.
