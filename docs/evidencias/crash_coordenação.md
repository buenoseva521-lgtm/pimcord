

## Execução adicional — 2026-08-18

`ferramentas/smoke_coordenacao_prolongada.py` completou novamente 20 rodadas entre subprocessos, com épocas avançando de 2 até 40 e recuperação após encerramento abrupto. A execução confirma a propriedade de leases, WAL e retomada atômica no cenário SQLite reproduzível. Ela não substitui observação prolongada com Voice Gateway, UDP e recursos nativos reais; esse bloqueador permanece aberto.


## Verificação de transporte e resiliência — 2026-08-18

A cobertura existente de `test_gateway.py`, `test_voz.py`, `test_recepcao_voz.py`, `test_rtp_jitter.py`, `test_sharding.py` e `test_falhas_prolongadas.py` aprovou 33 testes após as 20 rodadas prolongadas. Esses resultados comprovam contratos offline de Gateway, RTP/Jitter, sharding e recuperação SQLite. Não comprovam observação com Voice Gateway/UDP externo, sessão Discord real, binding DAVE nativo ou múltiplos dispositivos/arquiteturas; esses pontos continuam bloqueadores.


## Crash externo de checkpoint — 2026-08-18

`ferramentas/validar_crash_externo.py` retornou `crash_externo=aprovado`, `retomada=aprovada` e `checkpoint=validado`. Essa execução reforça a atomicidade do checkpoint e a recuperação do processo local. Ela não representa uma conexão externa ao Voice Gateway, tráfego UDP real ou uma falha de transporte Discord; esses bloqueadores permanecem separados.
