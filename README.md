# RAW-SNES OBS Companion

**Notificações do RetroAchievements para OBS Studio ao jogar Super Nintendo / Super Famicom real com RAW-SNES.**

**v1.0.0 — versão estável, testada com Super Nintendo real, RAW-SNES e OBS.**

Projeto independente de **HeresAChallenger**, adaptado de seu [MegaRaw-OBS-Companion](https://github.com/HeresAChallenger/MegaRaw-OBS-Companion), publicado sob MIT. O RAW-SNES é desenvolvido por [Liqui](https://github.com/liquid-wq/raw-snes) e tem licença **própria, restritiva**. Nenhum arquivo ou código do RAW-SNES faz parte desta distribuição.

## O que faz

- Consulta as conquistas **confirmadas** da conta pela Web API oficial do RetroAchievements.
- Filtra o sistema do achievement para **Super Nintendo / SNES / Super Famicom**; conquistas de Mega Drive e outros sistemas não aparecem.
- Mostra **título, descrição, emblema, jogo, pontos e modo** numa fonte Navegador transparente do OBS.
- Reproduz um WAV próprio pela fonte Navegador do OBS, que pode ser substituído localmente.
- Fornece um **painel de demonstração**, sem consumir conquistas reais.
- Intervalos de **2, 3, 5, 10 ou 15 segundos**, com redução automática de consultas quando a API falha.
- Mantém a **Web API Key criptografada via DPAPI do Windows** em `%LOCALAPPDATA%\RawSNESObsOverlay\config_local.json`.
- Usa somente **Python 3.10+ e a biblioteca padrão**. Não executa, lê dados internos, modifica, intercepta ou redistribui `raw-snes.exe`.

**Limitação importante:** o companion **não recebe o evento instantâneo do RAW-SNES**. O alerta depende de o RetroAchievements registrar a conquista e de a API disponibilizá-la; portanto há atraso variável. O intervalo de 2 segundos é experimental e pode causar HTTP 429. Comece com **5 segundos**.

## Requisitos

- Windows 10 ou 11; Python 3.10 ou superior instalado (comando `py -3` ou `python`).
- OBS Studio com fonte **Navegador**.
- Usuário RetroAchievements e sua **Web API Key**, obtida em [RetroAchievements → Control Panel → Keys](https://retroachievements.org/controlpanel.php). **A chave Web API não é o `ra_token` salvo no arquivo de configuração do RAW-SNES.**
- Para jogar no console original: Super Nintendo/Super Famicom + SD2SNES ou FXPak Pro com RAW-SNES, configurados conforme as [instruções do desenvolvedor](https://github.com/liquid-wq/raw-snes).

## Instalação e teste

1. Extraia todo o conteúdo do pacote para uma pasta independente, por exemplo `C:\RawSNES-OBS-Companion`.
2. Execute **`INICIAR.bat`**, escolha **1 — DEMONSTRAÇÃO**.
3. No OBS Studio, use **Fontes → + → Navegador**. Configure:

   | Configuração | Valor |
   | --- | --- |
   | URL | `http://127.0.0.1:8766/overlay` |
   | Largura | `520` |
   | Altura | `160` |
   | Controlar áudio via OBS | **Ativado** |
   | Ordem | Acima da captura do console |

4. O painel deve abrir em `http://127.0.0.1:8766/painel`. Clique em **Exibir notificação de teste**.
5. Confira imagem e áudio. Para ouvir o som também nos fones, use **Propriedades avançadas de áudio → Monitorar e enviar para a saída**. Evite capturá-lo duas vezes.
6. Feche o auxiliar usando `Ctrl+C` e reinicie `INICIAR.bat` com **2 — LIVE 5 segundos**.
7. Informe seu **usuário** e sua **Web API Key** quando solicitados na primeira execução; a consulta inicial descarta conquistas antigas.
8. Inicie o RAW-SNES separadamente, conecte o FXPak Pro / SD2SNES via USB e jogue normalmente. Mantenha o companion em execução durante a live.

O MegaRaw Companion usa **porta 8765** e o RAW-SNES Companion usa **8766**, para permitir os dois instalados no mesmo PC sem conflito. Cada um possui configuração de conta isolada. É possível usar a **mesma Web API Key** nos dois; a frequência combinada de chamadas conta para os limites da API.

### Alertas sonoros

O pacote inclui `som_alerta.wav`, **efeito demonstrativo original CC0**, não o som proprietário do RAW-SNES. Se possuir um WAV com os direitos necessários, pode substituí-lo **localmente** e reiniciar o auxiliar. Para overlay sem som, use `http://127.0.0.1:8766/overlay?som=0`.

### Outros comandos

```powershell
python rawsnes_obs.py --demo
python rawsnes_obs.py --interval 5
python rawsnes_obs.py --interval 3
python rawsnes_obs.py --interval 2
python rawsnes_obs.py --reset
python -m unittest discover -s tests -v
```

## Dificuldades comuns

- **A fonte ficou vazia após reiniciar:** confirme que o BAT está executando, abra `/painel` e clique em **Atualizar cache da página atual** nas propriedades da fonte Navegador.
- **Som não aparece na live:** ative **Controlar áudio via OBS**, confirme o mixer e se o arquivo WAV existe.
- **Conquistas não surgem:** elas só aparecem após a primeira consulta; confirme que o serviço confirmou o desbloqueio, que o jogo é classificado como SNES na API e que o painel mostra **Monitorando conquistas do SNES**.
- **HTTP 429:** troque para 10 ou 15 segundos; consulte a política de uso da API.
- **Trocar conta:** opção 7 do BAT remove somente a configuração protegida **deste companion**, não do RAW-SNES ou do RetroAchievements.

## Segurança, créditos e limitações

- **Não publique** `rawsnes_config.json`, seu `ra_token`, sua Web API Key ou `%LOCALAPPDATA%\RawSNESObsOverlay\config_local.json`.
- O servidor atende apenas em `127.0.0.1:8766`. A chave não é entregue ao OBS.
- O companion recebe os dados **da API**, não do `raw-snes.exe`; portanto também pode exibir conquistas SNES obtidas via outro cliente na mesma conta, caso ocorram durante a sessão.
- O pacote **não inclui** `raw-snes.exe`, ROMs, firmware, arquivos do cartucho, badge externo ou qualquer trecho do código RAW-SNES.
- **RAW-SNES** © 2025–2026 Liqui, [licença separada](https://github.com/liquid-wq/raw-snes/blob/main/LICENSE). O RAW-SNES registra atualmente os desbloqueios em **Softcore**, conforme seu README.
- **RAW-SNES OBS Companion** © 2026 HeresAChallenger, licença MIT, com atribuição ao MegaRaw-OBS-Companion.
- **Som incluído**: efeito sintetizado próprio, CC0 1.0 (ver `AUDIO-LICENSE.txt`).
- **RetroAchievements** e **OBS Studio** são serviços/projetos independentes deste companion.

Consulte `docs/SEGURANCA.md` antes de publicar uma release.