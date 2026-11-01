# Checklist de publicação no GitHub

1. Crie um **repositório independente**, por exemplo `RAW-SNES-OBS-Companion`, para não misturar o projeto com o MegaRaw.
2. Adicione **somente** os arquivos desta pasta. O ZIP de release deve ser criado com o conteúdo do companion, sem `raw-snes.exe` ou `rawsnes_config.json`.
3. Verifique `git status` para ter certeza de que nenhuma credencial, gravação pessoal, ROM ou log será publicado. O `.gitignore` ignora arquivos comuns de risco, mas confira também o histórico Git.
4. Execute `python -m unittest discover -s tests -v` e `python rawsnes_obs.py --demo`.
5. A integração com RAW-SNES e OBS no Super Nintendo real foi validada pelo responsável pelo projeto. Faça nova validação se houver alterações importantes no código.
6. Faça tag `v1.0.0` e anexe um ZIP contendo os scripts, docs, LICENSE e WAV demonstrativo CC0. Indique no texto que é a **primeira versão estável**, com validação em hardware real.
7. Inclua links para o projeto original do Liqui e seu MegaRaw-OBS-Companion, preservando a atribuição MIT.

**Nunca redistribua RAW-SNES.** A licença do autor é diferente da licença do companion.

## Publicação assistida

Este pacote contém `.github/workflows/tests.yml` para rodar os cinco testes no Windows automaticamente a cada push ou pull request. Publique como **release estável**: deixe **Set as a pre-release** desmarcado e, se disponível, marque **Set as the latest release**.
