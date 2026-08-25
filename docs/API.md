# Referência da API Pimcord

> Arquivo gerado offline a partir das assinaturas públicas do código-fonte. Não é necessário importar o pacote nem acessar a rede.

## `pimcord/__init__`

## `pimcord/adaptador_dave`

### Classe `AdaptadorDAVEPy`

Implementa o contrato Pimcord sobre ``dave.py`` sem esconder limitações.

- `AdaptadorDAVEPy.inicializar(self, *, versao: int, grupo_id: int, usuario_id: str, chave_transitoria: Any | None=None) -> None`
- `AdaptadorDAVEPy.definir_usuarios_reconhecidos(self, usuarios: Iterable[str]) -> None`
- `AdaptadorDAVEPy.definir_external_sender(self, pacote: bytes) -> None`
- `AdaptadorDAVEPy.gerar_key_package(self) -> bytes`
- `AdaptadorDAVEPy.processar_mensagem_mls(self, dados: bytes) -> None`
- `AdaptadorDAVEPy.processar_propostas(self, dados: bytes) -> bytes | None`
- `AdaptadorDAVEPy.processar_commit(self, dados: bytes) -> None`
- `AdaptadorDAVEPy.processar_welcome(self, dados: bytes) -> None`
- `AdaptadorDAVEPy.consumir_resposta_mls(self) -> bytes | None`
- `AdaptadorDAVEPy.processar_mensagem_tipada(self, mensagem: MensagemMLSDAVE) -> None`
- `AdaptadorDAVEPy.preparar_epoca(self, epoca: int) -> None`
- `AdaptadorDAVEPy.obter_ratchet_remetente(self, remetente_id: str) -> Any`
- `AdaptadorDAVEPy.exportar_chave_remetente(self, remetente_id: str) -> bytes`
- `AdaptadorDAVEPy.preparar_ratchets(self) -> dict[str, Any]`
- `AdaptadorDAVEPy.configurar_midia(self, *, tipo: str, ssrc: int, codec: str) -> None`
- `AdaptadorDAVEPy.cifrar_frame(self, remetente_id: str, frame: bytes) -> bytes`
- `AdaptadorDAVEPy.decifrar_frame(self, remetente_id: str, frame: bytes) -> bytes`
- `AdaptadorDAVEPy.autenticador_epoca(self, epoca: int, dados: bytes) -> bytes`

## `pimcord/automod`

### Classe `AcaoModeracao`


### Classe `RegraModeracao`

Regra local; padrões são comparados após normalização de texto.


### Classe `DecisaoModeracao`


### Classe `RegistroModeracao`


### Classe `TicketModeracao`

- `TicketModeracao.fechar(self, observacao: str | None=None) -> None`

### Função `normalizar_texto(texto: str) -> str`

### Classe `MotorAutomoderacao`

Avalia mensagens sem rede e conserva evidências de cada decisão.

- `MotorAutomoderacao.adicionar_regra(self, regra: RegraModeracao) -> RegraModeracao`
- `MotorAutomoderacao.remover_regra(self, nome: str) -> RegraModeracao | None`
- `MotorAutomoderacao.avaliar(self, conteudo: str, *, servidor_id: str | None=None, canal_id: str | None=None, mensagem_id: str | None=None, usuario_id: str | None=None) -> DecisaoModeracao`
- `MotorAutomoderacao.tickets_abertos(self) -> list[TicketModeracao]`
- `MotorAutomoderacao.exportar_logs(self) -> list[dict[str, Any]]`

## `pimcord/banco`

### Classe `BancoSQLite`

- `BancoSQLite.conectar(self) -> 'BancoSQLite'`
- `BancoSQLite.executar(self, sql: str, parametros: Iterable[Any]=()) -> sqlite3.Cursor`
- `BancoSQLite.buscar(self, sql: str, parametros: Iterable[Any]=()) -> list[dict[str, Any]]`
- `BancoSQLite.commit(self) -> None`
- `BancoSQLite.rollback(self) -> None`
- `BancoSQLite.fechar(self) -> None`

## `pimcord/bot`

### Classe `Comando`


### Classe `OpcaoSlash`

- `OpcaoSlash.para_dict(self) -> dict[str, Any]`

### Classe `ComandoSlash`


### Classe `Cache`

Cache local LRU com TTL opcional e métricas de acesso.

- `Cache.obter(self, chave: str, padrao: Any=None) -> Any`
- `Cache.definir(self, chave: str, valor: Any, *, ttl: float | None=None) -> None`
- `Cache.remover(self, chave: str) -> None`
- `Cache.limpar(self) -> None`
- `Cache.expurgar(self) -> int`
- `Cache.estatisticas(self) -> dict[str, int | float | None]`

### Classe `Tarefa`

- `Tarefa.iniciar(self) -> None`
- `Tarefa.parar(self) -> None`

### Classe `Bot`

- `Bot.entrar_em_voz(self, servidor_id: str, canal_id: str, *, auto_mudo: bool=False, auto_surdo: bool=False) -> Any`
- `Bot.voz_do_servidor(self, servidor_id: str) -> Any`
- `Bot.sair_da_voz(self, servidor_id: str) -> None`
- `Bot.user(self) -> Usuario | None`
- `Bot.usuario(self) -> Usuario | None`
- `Bot.me(self) -> Usuario | None`
- `Bot.application_id(self) -> str | None`
- `Bot.id(self) -> str | None`
- `Bot.servidores(self) -> list[Servidor]`
- `Bot.guilds(self) -> list[Servidor]`
- `Bot.canais(self) -> list[Canal]`
- `Bot.latency(self) -> float | None`
- `Bot.latencia(self) -> float | None`
- `Bot.latencia_ms(self) -> float | None`
- `Bot.conectado(self) -> bool`
- `Bot.estado_conexao(self) -> str`
- `Bot.ws(self) -> Any`
- `Bot.configurar_logs(self, nivel: int=logging.INFO) -> None`
- `Bot.comando_prefixo(self) -> str`
- `Bot.commands(self) -> list[Comando]`
- `Bot.is_ready(self) -> bool`
- `Bot.is_closed(self) -> bool`
- `Bot.adicionar_comando(self, comando: Comando) -> Comando`
- `Bot.obter_comando(self, nome: str) -> Comando | None`
- `Bot.remover_comando(self, nome: str) -> Comando | None`
- `Bot.event(self, fn)`
- `Bot.listen(self, nome: str | None=None)`
- `Bot.check(self, fn)`
- `Bot.antes_de_comando(self, fn)`
- `Bot.depois_de_comando(self, fn)`
- `Bot.adicionar_regra_automoderacao(self, regra: RegraModeracao) -> RegraModeracao`
- `Bot.remover_regra_automoderacao(self, nome: str) -> RegraModeracao | None`
- `Bot.adicionar_view(self, view: Any) -> Any`
- `Bot.registrar_view(self, view: Any) -> Any`
- `Bot.add_view(self, view: Any) -> Any`
- `Bot.obter_servidor(self, servidor_id: str) -> Servidor | None`
- `Bot.get_guild(self, guild_id: str) -> Servidor | None`
- `Bot.obter_canal(self, canal_id: str) -> Canal | None`
- `Bot.get_channel(self, channel_id: str) -> Canal | None`
- `Bot.obter_usuario(self, usuario_id: str) -> Usuario | None`
- `Bot.get_user(self, user_id: str) -> Usuario | None`
- `Bot.esperar_pronto(self) -> None`
- `Bot.setup_hook(self) -> None`
- `Bot.wait_for(self, evento: str, *, check: Callable[..., Any] | None=None, timeout: float | None=None) -> Any`
- `Bot.wait_until_ready(self) -> None`
- `Bot.fechar(self) -> None`
- `Bot.close(self) -> None`
- `Bot.conectar(self, token: str | None=None) -> None`
- `Bot.rodar(self, token: str | None=None) -> None`
- `Bot.comando(self, nome: str, *, aliases: list[str] | None=None)`
- `Bot.slash(self, nome: str, *, descricao: str='Comando Pimcord', opcoes: list[OpcaoSlash | dict[str, Any]] | None=None)`
- `Bot.comando_slash(self, nome: str, *, descricao: str='Comando Pimcord', opcoes: list[OpcaoSlash | dict[str, Any]] | None=None)`
- `Bot.hibrido(self, nome: str, *, descricao: str='Comando Pimcord', aliases: list[str] | None=None, opcoes: list[OpcaoSlash | dict[str, Any]] | None=None)`
- `Bot.comando_hibrido(self, nome: str, *, descricao: str='Comando Pimcord', aliases: list[str] | None=None, opcoes: list[OpcaoSlash | dict[str, Any]] | None=None)`
- `Bot.sincronizar_comandos(self) -> Any`
- `Bot.grupo(self, nome: str, *, descricao: str='Grupo de comandos Pimcord')`
- `Bot.evento(self, nome: str | Callable[..., Any] | None=None)`
- `Bot.tarefa(self, intervalo: float)`
- `Bot.agendar(self, nome: str, intervalo: float, *, politica: Any=None)`
- `Bot.carregar_extensao(self, caminho: str, *, dependencias: tuple[str, ...]=()) -> Any`
- `Bot.descarregar_extensao(self, caminho: str) -> None`
- `Bot.recarregar_extensao(self, caminho: str) -> Any`
- `Bot.disparar(self, nome: str, *args: Any, **kwargs: Any) -> list[Any]`
- `Bot.diagnostico_saude(self, *, exigir_token: bool=False) -> Any`
- `Bot.criar_simulador(self) -> Any`
- `Bot.diagnostico(self) -> dict[str, Any]`
- `Bot.processar_comando(self, conteudo: str, *, autor: Any=None, mensagem: Any=None) -> Any`
- `Bot.receber_interacao(self, dados: dict[str, Any]) -> None`
- `Bot.receber_mensagem(self, dados: dict[str, Any]) -> None`
- `Bot.executar(self, token: str | None=None) -> None`
- `Bot.iniciar(self, token: str | None=None) -> None`
- `Bot.start(self, token: str | None=None) -> None`
- `Bot.run(self, token: str | None=None) -> None`
- `Bot.parar(self) -> None`

## `pimcord/cache/__init__`

## `pimcord/cli`

### Função `novo(caminho: str) -> int`

### Função `diagnostico() -> int`

### Função `main(argv: list[str] | None=None) -> int`

## `pimcord/comandos/__init__`

### Classe `Cooldown`

- `Cooldown.verificar(self, chave: str) -> bool`

### Função `limitar(chamadas: int, por: float) -> Callable[[Callback], Callback]`

### Função `autocomplete(funcao: Callable[[Any], Any]) -> Callable[[Callback], Callback]`

### Função `verificar(check: Callable[[Any], bool | Awaitable[bool]]) -> Callable[[Callback], Callback]`

### Função `converter(tipo: type) -> Callable[[str], Any]`

### Função `preparar_argumentos(callback: Callback, argumentos: tuple[str, ...]) -> tuple[Any, ...]`

### Função `executar_checks(callback: Callback, contexto: Any) -> None`

### Classe `Subcomando`

- `Subcomando.para_dict(self) -> dict[str, Any]`

### Classe `SubgrupoDeComandos`

- `SubgrupoDeComandos.subcomando(self, nome: str, *, descricao: str='Subcomando Pimcord', opcoes: list[dict[str, Any]] | None=None) -> Callable[[Callback], Callback]`
- `SubgrupoDeComandos.para_dict(self) -> dict[str, Any]`

### Classe `GrupoDeComandos`

- `GrupoDeComandos.subcomando(self, nome: str, *, descricao: str='Subcomando Pimcord', opcoes: list[dict[str, Any]] | None=None) -> Callable[[Callback], Callback]`
- `GrupoDeComandos.subgrupo(self, nome: str, *, descricao: str='Subgrupo de comandos Pimcord') -> Callable[[Callable[..., Any]], SubgrupoDeComandos]`
- `GrupoDeComandos.para_dict(self) -> dict[str, Any]`

## `pimcord/comandos`

### Classe `Cooldown`

- `Cooldown.verificar(self, chave: str) -> bool`

### Função `limitar(chamadas: int, por: float) -> Callable[[Callback], Callback]`

### Função `autocomplete(funcao: Callable[[Any], Any]) -> Callable[[Callback], Callback]`

### Função `verificar(check: Callable[[Any], bool | Awaitable[bool]]) -> Callable[[Callback], Callback]`

### Função `converter(tipo: type) -> Callable[[str], Any]`

### Função `preparar_argumentos(callback: Callback, argumentos: tuple[str, ...]) -> tuple[Any, ...]`

### Função `executar_checks(callback: Callback, contexto: Any) -> None`

### Classe `GrupoDeComandos`

- `GrupoDeComandos.subcomando(self, nome: str) -> Callable[[Callback], Callback]`

## `pimcord/coordenacao`

### Classe `Lease`

- `Lease.válida(self) -> bool`

### Classe `TransporteCoordenação`

- `TransporteCoordenação.adquirir(self, chave: str, trabalhador: str, *, duração: float=30.0) -> Lease | None`
- `TransporteCoordenação.renovar(self, lease: Lease, *, duração: float=30.0) -> Lease | None`
- `TransporteCoordenação.liberar(self, lease: Lease) -> bool`
- `TransporteCoordenação.publicar(self, chave: str, estado: dict[str, Any]) -> None`
- `TransporteCoordenação.estados(self) -> dict[str, dict[str, Any]]`

### Classe `CoordenaçãoLocal`

Coordenador determinístico para modo offline e um único processo.

- `CoordenaçãoLocal.adquirir(self, chave: str, trabalhador: str, *, duração: float=30.0) -> Lease | None`
- `CoordenaçãoLocal.renovar(self, lease: Lease, *, duração: float=30.0) -> Lease | None`
- `CoordenaçãoLocal.liberar(self, lease: Lease) -> bool`
- `CoordenaçãoLocal.publicar(self, chave: str, estado: dict[str, Any]) -> None`
- `CoordenaçãoLocal.estados(self) -> dict[str, dict[str, Any]]`
- `CoordenaçãoLocal.expurgar(self) -> int`

## `pimcord/coordenacao_sqlite`

### Classe `CoordenaçãoSQLite`

Implementa ``TransporteCoordenação`` com um arquivo SQLite compartilhado.

- `CoordenaçãoSQLite.adquirir(self, chave: str, trabalhador: str, *, duração: float=30.0) -> Lease | None`
- `CoordenaçãoSQLite.renovar(self, lease: Lease, *, duração: float=30.0) -> Lease | None`
- `CoordenaçãoSQLite.liberar(self, lease: Lease) -> bool`
- `CoordenaçãoSQLite.publicar(self, chave: str, estado: dict[str, Any]) -> None`
- `CoordenaçãoSQLite.estados(self) -> dict[str, dict[str, Any]]`
- `CoordenaçãoSQLite.expurgar(self) -> int`
- `CoordenaçãoSQLite.fechar(self) -> None`

## `pimcord/dave`

### Classe `OpcodeDAVE`


### Classe `TipoMensagemMLS`

Tipos explícitos aceitos pela sessão DAVE/libdave.


### Classe `MensagemMLSDAVE`

Envelope semântico para impedir dispatch MLS por adivinhação de bytes.


### Classe `BackendDAVE`

- `BackendDAVE.gerar_key_package(self) -> bytes`
- `BackendDAVE.processar_mensagem_mls(self, dados: bytes) -> None`
- `BackendDAVE.preparar_epoca(self, epoca: int) -> None`
- `BackendDAVE.exportar_chave_remetente(self, remetente_id: str) -> bytes`

### Classe `BackendDAVEEnvelope`

Operações semânticas exigidas para encaminhar mensagens MLS com segurança.

- `BackendDAVEEnvelope.processar_propostas(self, dados: bytes) -> None`
- `BackendDAVEEnvelope.processar_commit(self, dados: bytes) -> None`
- `BackendDAVEEnvelope.processar_welcome(self, dados: bytes) -> None`

### Classe `BackendDAVEReal`

Contrato adicional exigido por um adaptador E2EE realmente integrado.

Declarar este protocolo não implementa criptografia. Ele apenas torna visível
a superfície que um binding libdave auditado precisa fornecer antes que o
Pimcord possa habilitar mídia protegida.

- `BackendDAVEReal.cifrar_frame(self, remetente_id: str, frame: bytes) -> bytes`
- `BackendDAVEReal.decifrar_frame(self, remetente_id: str, frame: bytes) -> bytes`
- `BackendDAVEReal.autenticador_epoca(self, epoca: int, dados: bytes) -> bytes`

### Classe `MensagemDAVE`

- `MensagemDAVE.serializar(self) -> bytes`
- `MensagemDAVE.desserializar(cls, dados: bytes, *, tem_sequencia: bool=False) -> 'MensagemDAVE'`

### Função `validar_backend_dave(backend: BackendDAVE) -> BackendDAVE`

### Função `exigir_backend_dave_real(backend: BackendDAVE) -> BackendDAVE`

### Classe `EstadoDAVE`

Máquina de transição DAVE sem operações criptográficas embutidas.

- `EstadoDAVE.identificar(self) -> dict[str, int]`
- `EstadoDAVE.receber_preparacao(self, *, versao: int, epoca: int, transicao_id: int) -> bytes | None`
- `EstadoDAVE.receber_mensagem_mls(self, dados: bytes) -> None`
- `EstadoDAVE.receber_remetente_externo(self, dados: bytes) -> None`
- `EstadoDAVE.receber_propostas(self, dados: bytes) -> None`
- `EstadoDAVE.receber_commit(self, dados: bytes) -> None`
- `EstadoDAVE.receber_welcome(self, dados: bytes) -> None`
- `EstadoDAVE.receber_mensagem_mls_tipada(self, mensagem: MensagemMLSDAVE) -> None`
- `EstadoDAVE.exportar_chave_remetente(self, remetente_id: str) -> bytes`
- `EstadoDAVE.marcar_pronto(self) -> MensagemDAVE`
- `EstadoDAVE.executar(self, *, transicao_id: int) -> None`

## `pimcord/discord/__init__`

## `pimcord/discord/modelos`

### Classe `Usuario`

- `Usuario.de_dict(cls, dados: dict[str, Any]) -> 'Usuario'`
- `Usuario.mencao(self) -> str`

### Classe `Cargo`

- `Cargo.de_dict(cls, dados: dict[str, Any]) -> 'Cargo'`

### Classe `Anexo`

- `Anexo.de_dict(cls, dados: dict[str, Any]) -> 'Anexo'`

### Classe `Canal`

- `Canal.enviar(self, conteudo: str='', *, embed: Embed | None=None, embeds: list[Embed] | None=None, view: Any=None, arquivos: list[Any] | None=None) -> dict[str, Any]`
- `Canal.buscar(self) -> dict[str, Any]`
- `Canal.editar(self, **campos: Any) -> dict[str, Any]`
- `Canal.excluir(self) -> dict[str, Any]`
- `Canal.definir_permissoes(self, sobrescrita: Any, *, motivo: str | None=None) -> Any`
- `Canal.remover_permissoes(self, alvo_id: str, *, motivo: str | None=None) -> Any`
- `Canal.historico(self, *, limite: int=50, antes_de: str | None=None, depois_de: str | None=None, em_torno_de: str | None=None) -> list['Mensagem']`
- `Canal.purge(self, *, limite: int=100, check: Callable[['Mensagem'], bool | Awaitable[bool]] | None=None, antes_de: str | None=None, depois_de: str | None=None) -> list['Mensagem']`
- `Canal.apagar_mensagens(self, **opcoes: Any) -> list['Mensagem']`

### Classe `Servidor`

- `Servidor.de_dict(cls, dados: dict[str, Any], cliente: Any=None) -> 'Servidor'`
- `Servidor.buscar_canal(self, canal_id: str) -> Canal`
- `Servidor.buscar_canais(self) -> list[Canal]`
- `Servidor.criar_categoria(self, nome: str, *, sobrescritas: list[Any] | None=None, motivo: str | None=None) -> Canal`
- `Servidor.criar_canal(self, nome: str, *, tipo: int | str='texto', categoria_id: str | None=None, topico: str | None=None, nsfw: bool=False, sobrescritas: list[Any] | None=None, motivo: str | None=None) -> Canal`

### Classe `Membro`

- `Membro.id(self) -> str`
- `Membro.nome(self) -> str`
- `Membro.de_dict(cls, dados: dict[str, Any], servidor_id: str) -> 'Membro'`

### Classe `Mensagem`

- `Mensagem.de_gateway(cls, dados: dict[str, Any], cliente: Any) -> 'Mensagem'`
- `Mensagem.mencao_autor(self) -> str`
- `Mensagem.responder(self, conteudo: str='', *, embed: Embed | None=None, embeds: list[Embed] | None=None, view: Any=None) -> dict[str, Any]`
- `Mensagem.editar(self, conteudo: str | None=None, **campos: Any) -> dict[str, Any]`
- `Mensagem.excluir(self) -> dict[str, Any]`
- `Mensagem.apagar(self) -> dict[str, Any]`
- `Mensagem.delete(self) -> dict[str, Any]`
- `Mensagem.deletar(self) -> dict[str, Any]`

## `pimcord/discord/recursos`

### Classe `ModeloDiscord`

Base comum que preserva campos não conhecidos pelo modelo.

- `ModeloDiscord.de_dict(cls, dados: dict[str, Any] | None, **extras: Any)`
- `ModeloDiscord.para_dict(self) -> dict[str, Any]`

### Classe `Emoji`

- `Emoji.mencao(self) -> str`

### Classe `EmojiParcial`


### Classe `Adesivo`


### Classe `MetadadosThread`


### Classe `MembroThread`


### Classe `TagForum`


### Classe `CanalCompleto`


### Classe `Banimento`


### Classe `AlteracaoAuditoria`

- `AlteracaoAuditoria.de_dict(cls, dados: dict[str, Any] | None, **extras: Any)`

### Classe `OpcaoAuditoria`

- `OpcaoAuditoria.de_dict(cls, dados: dict[str, Any] | None, **extras: Any)`

### Classe `EntradaAuditoria`

- `EntradaAuditoria.de_dict(cls, dados: dict[str, Any] | None, **extras: Any)`

### Classe `RegistroAuditoria`

- `RegistroAuditoria.de_dict(cls, dados: dict[str, Any] | None, **extras: Any)`

### Classe `Entitlement`


### Classe `AssinaturaAplicacao`


### Classe `SkuAplicacao`


### Classe `Convite`


### Classe `Integracao`


### Classe `WebhookInfo`


### Classe `EventoAgendado`


### Classe `InstanciaStage`


### Classe `RegiaoVoz`


### Classe `SomSoundboard`

- `SomSoundboard.de_dict(cls, dados: dict[str, Any] | None, **extras: Any)`

### Classe `EstadoVoz`


### Classe `Presenca`


### Classe `Reacao`


### Classe `AplicacaoComando`


### Classe `IntegracaoAplicacao`


### Classe `DireitoAplicacao`


### Classe `ModeloServidor`


### Classe `TelaBoasVindas`


### Classe `GatilhoAutomoderacao`


### Classe `AcaoAutomoderacao`


### Classe `RegraAutomoderacao`


### Classe `EnqueteResposta`


### Classe `Enquete`


### Classe `MetadadoCargo`


### Classe `MetadadoConexao`

- `MetadadoConexao.de_dict(cls, dados: dict[str, Any] | None, **extras: Any)`

### Classe `ConexaoUsuario`

- `ConexaoUsuario.de_dict(cls, dados: dict[str, Any] | None, **extras: Any)`

## `pimcord/economia`

### Classe `EconomiaSQLite`

- `EconomiaSQLite.saldo(self, usuario_id: str) -> int`
- `EconomiaSQLite.diaria(self, usuario_id: str, *, agora: float | None=None) -> int`
- `EconomiaSQLite.transferir(self, remetente: str, destinatario: str, valor: int) -> tuple[int, int]`
- `EconomiaSQLite.ranking(self, limite: int=10) -> list[dict[str, Any]]`
- `EconomiaSQLite.fechar(self) -> None`

## `pimcord/extensoes/__init__`

### Classe `Extensao`

- `Extensao.iniciar(self, bot: Any) -> None`
- `Extensao.parar(self, bot: Any) -> None`

### Classe `GerenciadorDeExtensoes`

- `GerenciadorDeExtensoes.carregar(self, caminho: str, *, dependencias: tuple[str, ...]=()) -> ModuleType | Extensao`
- `GerenciadorDeExtensoes.descarregar(self, caminho: str) -> None`
- `GerenciadorDeExtensoes.recarregar(self, caminho: str) -> ModuleType | Extensao`
- `GerenciadorDeExtensoes.carregar_lote(self, extensoes: dict[str, tuple[str, ...]]) -> list[ModuleType | Extensao]`
- `GerenciadorDeExtensoes.diagnostico(self) -> dict[str, str]`

## `pimcord/extensoes`

### Classe `Extensao`

Classe base para módulos reutilizáveis de um bot.

- `Extensao.iniciar(self, bot: Any) -> None`
- `Extensao.parar(self, bot: Any) -> None`

### Classe `GerenciadorDeExtensoes`

- `GerenciadorDeExtensoes.carregar(self, caminho: str, *, dependencias: tuple[str, ...]=()) -> ModuleType | Extensao`
- `GerenciadorDeExtensoes.descarregar(self, caminho: str) -> None`
- `GerenciadorDeExtensoes.recarregar(self, caminho: str) -> ModuleType | Extensao`
- `GerenciadorDeExtensoes.carregar_lote(self, extensoes: dict[str, tuple[str, ...]]) -> list[ModuleType | Extensao]`
- `GerenciadorDeExtensoes.diagnostico(self) -> dict[str, str]`

## `pimcord/gateway/__init__`

## `pimcord/gateway/cliente`

### Classe `Gateway`

- `Gateway.latencia(self) -> float | None`
- `Gateway.executar(self) -> None`
- `Gateway.parar(self) -> None`

## `pimcord/gateway/eventos`

### Função `modelar_evento(nome: str, dados: dict[str, Any], cliente: Any=None) -> Any`

## `pimcord/http/__init__`

## `pimcord/http/cliente`

### Classe `ClienteHTTP`

Transporte REST com retries, buckets locais, JSON e multipart.

Os métodos de recurso são apenas uma camada ergonômica sobre ``requisitar``;
``requisitar`` continua disponível para endpoints novos do Discord.

- `ClienteHTTP.abrir(self) -> None`
- `ClienteHTTP.fechar(self) -> None`
- `ClienteHTTP.requisitar(self, metodo: str, rota: str, *, json: Any=None, dados: Any=None, arquivos: Iterable[Any] | None=None, campos_multipart: dict[str, Any] | None=None, parametros: dict[str, Any] | None=None, motivo: str | None=None, cabecalhos: dict[str, str] | None=None, tentativas: int=3, bruto: bool=False) -> Any`
- `ClienteHTTP.endpoint(self, metodo: str, rota: str, **kwargs: Any) -> Any`
- `ClienteHTTP.paginar(self, metodo: str, rota: str, *, limite: int=100, campo: str | None=None, antes_de: str | None=None, depois_de: str | None=None, **kwargs: Any) -> AsyncIterator[Any]`
- `ClienteHTTP.gateway(self) -> str`
- `ClienteHTTP.enviar_mensagem(self, canal_id: str, conteudo: str='', *, embed: dict[str, Any] | None=None, embeds: list[dict[str, Any]] | None=None, view: Any=None, arquivos: Iterable[Any] | None=None, permitido_mencionar: dict[str, Any] | None=None, tts: bool=False, reply: str | None=None) -> dict[str, Any]`
- `ClienteHTTP.buscar_mensagem(self, canal_id: str, mensagem_id: str) -> dict[str, Any]`
- `ClienteHTTP.editar_mensagem(self, canal_id: str, mensagem_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.apagar_mensagem(self, canal_id: str, mensagem_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.indicar_digitacao(self, canal_id: str) -> None`
- `ClienteHTTP.publicar_mensagem(self, canal_id: str, mensagem_id: str) -> dict[str, Any]`
- `ClienteHTTP.encerrar_enquete(self, canal_id: str, mensagem_id: str) -> dict[str, Any]`
- `ClienteHTTP.listar_usuarios_reacao(self, canal_id: str, mensagem_id: str, emoji: str, *, limite: int=25, depois_de: str | None=None) -> list[dict[str, Any]]`
- `ClienteHTTP.adicionar_reacao(self, canal_id: str, mensagem_id: str, emoji: str, *, usuario_id: str='@me') -> None`
- `ClienteHTTP.remover_reacao(self, canal_id: str, mensagem_id: str, emoji: str, *, usuario_id: str='@me') -> None`
- `ClienteHTTP.listar_reacoes(self, canal_id: str, mensagem_id: str, emoji: str, **parametros: Any) -> list[dict[str, Any]]`
- `ClienteHTTP.limpar_reacoes(self, canal_id: str, mensagem_id: str, emoji: str | None=None) -> None`
- `ClienteHTTP.adicionar_reacao_atual(self, canal_id: str, mensagem_id: str, emoji: str) -> None`
- `ClienteHTTP.remover_reacao_atual(self, canal_id: str, mensagem_id: str, emoji: str) -> None`
- `ClienteHTTP.limpar_reacoes_emoji(self, canal_id: str, mensagem_id: str, emoji: str) -> None`
- `ClienteHTTP.limpar_todas_reacoes(self, canal_id: str, mensagem_id: str) -> None`
- `ClienteHTTP.buscar_mensagens(self, canal_id: str, *, limite: int=50, antes_de: str | None=None, depois_de: str | None=None, em_torno_de: str | None=None) -> list[dict[str, Any]]`
- `ClienteHTTP.apagar_mensagens(self, canal_id: str, mensagens: list[str], *, motivo: str | None=None) -> None`
- `ClienteHTTP.obter_canal(self, canal_id: str) -> dict[str, Any]`
- `ClienteHTTP.listar_votantes_enquete(self, canal_id: str, mensagem_id: str, resposta_id: str, *, limite: int=25, depois_de: str | None=None) -> list[dict[str, Any]]`
- `ClienteHTTP.editar_canal(self, canal_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.excluir_canal(self, canal_id: str, *, motivo: str | None=None) -> dict[str, Any]`
- `ClienteHTTP.listar_canais_servidor(self, servidor_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.criar_canal(self, servidor_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.mover_canais(self, servidor_id: str, canais: list[dict[str, Any]]) -> None`
- `ClienteHTTP.definir_permissoes(self, canal_id: str, alvo_id: str, **dados: Any) -> None`
- `ClienteHTTP.remover_permissoes(self, canal_id: str, alvo_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.listar_pins(self, canal_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.listar_mensagens_fixadas(self, canal_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.fixar_mensagem_oficial(self, canal_id: str, mensagem_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.desafixar_mensagem_oficial(self, canal_id: str, mensagem_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.fixar_mensagem(self, canal_id: str, mensagem_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.desafixar_mensagem(self, canal_id: str, mensagem_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.adicionar_destinatario(self, canal_id: str, usuario_id: str, *, acesso: str | None=None) -> None`
- `ClienteHTTP.remover_destinatario(self, canal_id: str, usuario_id: str) -> None`
- `ClienteHTTP.criar_thread(self, canal_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.criar_thread_mensagem(self, canal_id: str, mensagem_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.listar_threads_ativas(self, servidor_id: str) -> dict[str, Any]`
- `ClienteHTTP.listar_threads_arquivadas(self, canal_id: str, *, publicas: bool=True, **parametros: Any) -> dict[str, Any]`
- `ClienteHTTP.listar_threads_privadas_do_usuario(self, canal_id: str, **parametros: Any) -> dict[str, Any]`
- `ClienteHTTP.buscar_threads(self, canal_id: str, **parametros: Any) -> dict[str, Any]`
- `ClienteHTTP.entrar_thread(self, thread_id: str, usuario_id: str='@me') -> None`
- `ClienteHTTP.sair_thread(self, thread_id: str, usuario_id: str='@me') -> None`
- `ClienteHTTP.entrar_thread_como_eu(self, thread_id: str) -> None`
- `ClienteHTTP.sair_thread_como_eu(self, thread_id: str) -> None`
- `ClienteHTTP.listar_membros_thread(self, thread_id: str, **parametros: Any) -> list[dict[str, Any]]`
- `ClienteHTTP.obter_membro_thread(self, thread_id: str, usuario_id: str) -> dict[str, Any]`
- `ClienteHTTP.obter_servidor(self, servidor_id: str, *, contagem: bool=False) -> dict[str, Any]`
- `ClienteHTTP.editar_servidor(self, servidor_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.excluir_servidor(self, servidor_id: str) -> None`
- `ClienteHTTP.buscar_mensagens_servidor(self, servidor_id: str, *, consulta: str | None=None, limite: int=25, antes_de: str | None=None, depois_de: str | None=None) -> dict[str, Any]`
- `ClienteHTTP.listar_contagens_cargos(self, servidor_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.obter_membro_usuario_atual(self, servidor_id: str) -> dict[str, Any]`
- `ClienteHTTP.buscar_membros(self, servidor_id: str, consulta: str, *, limite: int=1) -> list[dict[str, Any]]`
- `ClienteHTTP.listar_membros(self, servidor_id: str, *, limite: int=1000, depois_de: str | None=None) -> list[dict[str, Any]]`
- `ClienteHTTP.obter_membro(self, servidor_id: str, usuario_id: str) -> dict[str, Any]`
- `ClienteHTTP.obter_membro_atual(self, servidor_id: str) -> dict[str, Any]`
- `ClienteHTTP.alterar_apelido_atual(self, servidor_id: str, apelido: str | None, *, motivo: str | None=None) -> dict[str, Any]`
- `ClienteHTTP.editar_membro(self, servidor_id: str, usuario_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.editar_membro_atual(self, servidor_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.expulsar_membro(self, servidor_id: str, usuario_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.banir_membro(self, servidor_id: str, usuario_id: str, *, dias_mensagens: int=0, motivo: str | None=None) -> None`
- `ClienteHTTP.desbanir_membro(self, servidor_id: str, usuario_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.obter_banimento(self, servidor_id: str, usuario_id: str) -> dict[str, Any]`
- `ClienteHTTP.listar_banimentos(self, servidor_id: str, *, limite: int=1000, antes_de: str | None=None, depois_de: str | None=None) -> list[dict[str, Any]]`
- `ClienteHTTP.listar_banimentos_modelados(self, servidor_id: str, *, limite: int=1000, antes_de: str | None=None, depois_de: str | None=None) -> list[Any]`
- `ClienteHTTP.listar_cargos(self, servidor_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.obter_cargo(self, servidor_id: str, cargo_id: str) -> dict[str, Any]`
- `ClienteHTTP.criar_cargo(self, servidor_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.editar_cargo(self, servidor_id: str, cargo_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.excluir_cargo(self, servidor_id: str, cargo_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.mover_cargos(self, servidor_id: str, cargos: list[dict[str, Any]]) -> None`
- `ClienteHTTP.adicionar_cargo(self, servidor_id: str, usuario_id: str, cargo_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.remover_cargo(self, servidor_id: str, usuario_id: str, cargo_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.obter_auditoria(self, servidor_id: str, *, usuario_id: str | None=None, acao: int | None=None, antes_de: str | None=None, limite: int=50, **parametros: Any) -> dict[str, Any]`
- `ClienteHTTP.obter_auditoria_modelada(self, servidor_id: str, **parametros: Any) -> Any`
- `ClienteHTTP.listar_registros_auditoria(self, servidor_id: str, **parametros: Any) -> list[Any]`
- `ClienteHTTP.listar_convites_canal(self, canal_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.listar_convites_servidor(self, servidor_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.criar_convite(self, canal_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.obter_convite(self, codigo: str, *, contagem: bool=False, expiracao: bool=False) -> dict[str, Any]`
- `ClienteHTTP.excluir_convite(self, codigo: str, *, motivo: str | None=None) -> dict[str, Any]`
- `ClienteHTTP.obter_usuarios_alvo_convite(self, codigo: str) -> bytes`
- `ClienteHTTP.atualizar_usuarios_alvo_convite(self, codigo: str, arquivo: Any, *, nome_arquivo: str='usuarios.csv') -> dict[str, Any]`
- `ClienteHTTP.obter_status_usuarios_alvo_convite(self, codigo: str) -> dict[str, Any]`
- `ClienteHTTP.atualizar_lobbies(self, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.criar_lobby(self, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.obter_lobby(self, lobby_id: str) -> dict[str, Any]`
- `ClienteHTTP.excluir_lobby(self, lobby_id: str) -> None`
- `ClienteHTTP.editar_lobby(self, lobby_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.editar_vinculo_canal_lobby(self, lobby_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.sair_lobby(self, lobby_id: str) -> None`
- `ClienteHTTP.convidar_eu_para_lobby(self, lobby_id: str) -> dict[str, Any]`
- `ClienteHTTP.adicionar_membros_lobby(self, lobby_id: str, membros: list[Any]) -> list[dict[str, Any]]`
- `ClienteHTTP.adicionar_membro_lobby(self, lobby_id: str, usuario_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.remover_membro_lobby(self, lobby_id: str, usuario_id: str) -> None`
- `ClienteHTTP.convidar_membro_lobby(self, lobby_id: str, usuario_id: str) -> dict[str, Any]`
- `ClienteHTTP.listar_mensagens_lobby(self, lobby_id: str, *, limite: int | None=None) -> list[dict[str, Any]]`
- `ClienteHTTP.enviar_mensagem_lobby(self, lobby_id: str, dados: Any) -> dict[str, Any]`
- `ClienteHTTP.definir_metadata_moderacao_mensagem_lobby(self, lobby_id: str, mensagem_id: str, dados: Any, *, formulario: bool=False) -> None`
- `ClienteHTTP.criar_anexo_aplicacao(self, aplicacao_id: str, arquivo: Any, *, nome_arquivo: str='arquivo') -> dict[str, Any]`
- `ClienteHTTP.desvincular_conta_provisoria(self, dados: dict[str, Any]) -> None`
- `ClienteHTTP.desvincular_conta_provisoria_bot(self, external_user_id: str) -> None`
- `ClienteHTTP.obter_token_partner(self, dados: dict[str, Any]) -> dict[str, Any]`
- `ClienteHTTP.obter_token_partner_bot(self, external_user_id: str, *, provisional_user_id: str | None=None, preferred_global_name: str | None=None) -> dict[str, Any]`
- `ClienteHTTP.definir_metadata_moderacao_dm_partner(self, usuario_id_1: str, usuario_id_2: str, mensagem_id: str, dados: dict[str, Any], *, formulario: bool=False) -> None`
- `ClienteHTTP.executar_webhook_github(self, webhook_id: str, token: str, dados: dict[str, Any], *, esperar: bool=False, thread_id: str | None=None) -> Any`
- `ClienteHTTP.executar_webhook_slack(self, webhook_id: str, token: str, dados: dict[str, Any], *, esperar: bool=False, thread_id: str | None=None, formulario: bool=False) -> Any`
- `ClienteHTTP.criar_webhook(self, canal_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.listar_webhooks_canal(self, canal_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.listar_webhooks_servidor(self, servidor_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.obter_webhook(self, webhook_id: str) -> dict[str, Any]`
- `ClienteHTTP.obter_webhook_token(self, webhook_id: str, token: str) -> dict[str, Any]`
- `ClienteHTTP.editar_webhook(self, webhook_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.editar_webhook_token(self, webhook_id: str, token: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.excluir_webhook(self, webhook_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.excluir_webhook_token(self, webhook_id: str, token: str) -> None`
- `ClienteHTTP.executar_webhook(self, webhook_id: str, token: str, *, arquivos: Iterable[Any] | None=None, campos_multipart: dict[str, Any] | None=None, **dados: Any) -> Any`
- `ClienteHTTP.obter_mensagem_webhook_original(self, webhook_id: str, token: str) -> dict[str, Any]`
- `ClienteHTTP.editar_mensagem_webhook_original(self, webhook_id: str, token: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.apagar_mensagem_webhook_original(self, webhook_id: str, token: str) -> None`
- `ClienteHTTP.obter_mensagem_webhook(self, webhook_id: str, token: str, mensagem_id: str) -> dict[str, Any]`
- `ClienteHTTP.editar_mensagem_webhook(self, webhook_id: str, token: str, mensagem_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.apagar_mensagem_webhook(self, webhook_id: str, token: str, mensagem_id: str) -> None`
- `ClienteHTTP.listar_emojis(self, servidor_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.obter_emoji(self, servidor_id: str, emoji_id: str) -> dict[str, Any]`
- `ClienteHTTP.criar_emoji(self, servidor_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.editar_emoji(self, servidor_id: str, emoji_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.excluir_emoji(self, servidor_id: str, emoji_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.listar_stickers_servidor(self, servidor_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.criar_sticker(self, servidor_id: str, *, nome: str, tags: str, arquivo: Any, nome_arquivo: str='sticker.png', descricao: str | None=None, motivo: str | None=None) -> dict[str, Any]`
- `ClienteHTTP.obter_sticker(self, sticker_id: str) -> dict[str, Any]`
- `ClienteHTTP.obter_sticker_servidor(self, servidor_id: str, sticker_id: str) -> dict[str, Any]`
- `ClienteHTTP.editar_sticker(self, servidor_id: str, sticker_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.excluir_sticker(self, servidor_id: str, sticker_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.listar_stickers_modelados(self, servidor_id: str) -> list[Any]`
- `ClienteHTTP.obter_sticker_modelado(self, sticker_id: str) -> Any`
- `ClienteHTTP.criar_instancia_stage(self, servidor_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.obter_instancia_stage(self, canal_id: str) -> dict[str, Any]`
- `ClienteHTTP.obter_instancia_stage_modelada(self, canal_id: str) -> Any`
- `ClienteHTTP.editar_instancia_stage(self, canal_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.excluir_instancia_stage(self, canal_id: str) -> None`
- `ClienteHTTP.listar_integracoes(self, servidor_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.listar_integracoes_modeladas(self, servidor_id: str) -> list[Any]`
- `ClienteHTTP.excluir_integracao(self, servidor_id: str, integracao_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.listar_regioes_voz(self) -> list[dict[str, Any]]`
- `ClienteHTTP.listar_regioes_servidor(self, servidor_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.listar_regioes_voz_modeladas(self) -> list[Any]`
- `ClienteHTTP.obter_widget(self, servidor_id: str) -> dict[str, Any]`
- `ClienteHTTP.obter_configuracao_widget(self, servidor_id: str) -> dict[str, Any]`
- `ClienteHTTP.obter_widget_png(self, servidor_id: str) -> bytes`
- `ClienteHTTP.editar_configuracao_widget(self, servidor_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.contar_poda(self, servidor_id: str, *, dias: int=7, incluir_cargos: bool=False) -> dict[str, Any]`
- `ClienteHTTP.podar_membros(self, servidor_id: str, *, dias: int=7, calcular_contagem: bool=True, incluir_cargos: bool=False) -> dict[str, Any]`
- `ClienteHTTP.obter_preview_servidor(self, servidor_id: str) -> dict[str, Any]`
- `ClienteHTTP.listar_solicitacoes_entrada(self, servidor_id: str, *, status: str | None=None, limite: int=100, antes_de: str | None=None, depois_de: str | None=None) -> list[dict[str, Any]]`
- `ClienteHTTP.modificar_solicitacao_entrada(self, servidor_id: str, solicitacao_id: str, *, acao: str, motivo_rejeicao: str | None=None) -> dict[str, Any]`
- `ClienteHTTP.obter_url_personalizada(self, servidor_id: str) -> dict[str, Any]`
- `ClienteHTTP.obter_estado_voz(self, servidor_id: str, usuario_id: str='@me') -> dict[str, Any]`
- `ClienteHTTP.alterar_estado_voz(self, servidor_id: str, *, canal_id: str | None=None, suprimido: bool | None=None, pedido_fala_em: str | None=None) -> None`
- `ClienteHTTP.alterar_estado_voz_usuario(self, servidor_id: str, usuario_id: str, *, canal_id: str | None=None, suprimido: bool | None=None) -> None`
- `ClienteHTTP.obter_tela_boas_vindas(self, servidor_id: str) -> dict[str, Any]`
- `ClienteHTTP.obter_boas_vindas_novos_membros(self, servidor_id: str) -> dict[str, Any]`
- `ClienteHTTP.obter_onboarding(self, servidor_id: str) -> dict[str, Any]`
- `ClienteHTTP.editar_onboarding(self, servidor_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.editar_tela_boas_vindas(self, servidor_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.modificar_acoes_incidente(self, servidor_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.obter_usuario(self, usuario_id: str='@me') -> dict[str, Any]`
- `ClienteHTTP.editar_usuario_atual(self, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.criar_dm(self, usuario_id: str) -> dict[str, Any]`
- `ClienteHTTP.listar_conexoes_usuario(self) -> list[dict[str, Any]]`
- `ClienteHTTP.listar_conexoes_usuario_modeladas(self) -> list[Any]`
- `ClienteHTTP.remover_conexao_cargo_usuario(self, aplicacao_id: str='@me') -> None`
- `ClienteHTTP.obter_conexao_cargo_usuario(self, aplicacao_id: str='@me') -> dict[str, Any]`
- `ClienteHTTP.obter_conexao_cargo_usuario_modelada(self, aplicacao_id: str='@me') -> Any`
- `ClienteHTTP.atualizar_conexao_cargo_usuario(self, dados: dict[str, Any], aplicacao_id: str='@me') -> dict[str, Any]`
- `ClienteHTTP.atualizar_conexao_cargo_usuario_modelada(self, dados: dict[str, Any], aplicacao_id: str='@me') -> Any`
- `ClienteHTTP.criar_dm_grupo(self, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.obter_aplicacao(self, aplicacao_id: str='@me') -> dict[str, Any]`
- `ClienteHTTP.editar_aplicacao(self, aplicacao_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.obter_oauth2_atual(self) -> dict[str, Any]`
- `ClienteHTTP.obter_aplicacao_oauth2_atual(self) -> dict[str, Any]`
- `ClienteHTTP.obter_chaves_oauth2(self) -> dict[str, Any]`
- `ClienteHTTP.obter_userinfo_oauth2(self) -> dict[str, Any]`
- `ClienteHTTP.obter_metadados_conexoes_cargo(self, aplicacao_id: str='@me') -> list[dict[str, Any]]`
- `ClienteHTTP.obter_metadados_conexoes_cargo_modelados(self, aplicacao_id: str='@me') -> list[Any]`
- `ClienteHTTP.substituir_metadados_conexoes_cargo(self, metadados: list[dict[str, Any]], aplicacao_id: str='@me') -> list[dict[str, Any]]`
- `ClienteHTTP.substituir_metadados_conexoes_cargo_modelados(self, metadados: list[dict[str, Any]], aplicacao_id: str='@me') -> list[Any]`
- `ClienteHTTP.executar_comando_aplicacao(self, aplicacao_id: str, token: str, **dados: Any) -> None`
- `ClienteHTTP.listar_emojis_aplicacao(self, aplicacao_id: str) -> dict[str, Any]`
- `ClienteHTTP.criar_emoji_aplicacao(self, aplicacao_id: str, *, nome: str, imagem: str) -> dict[str, Any]`
- `ClienteHTTP.obter_emoji_aplicacao(self, aplicacao_id: str, emoji_id: str) -> dict[str, Any]`
- `ClienteHTTP.editar_emoji_aplicacao(self, aplicacao_id: str, emoji_id: str, *, nome: str) -> dict[str, Any]`
- `ClienteHTTP.excluir_emoji_aplicacao(self, aplicacao_id: str, emoji_id: str) -> None`
- `ClienteHTTP.listar_entitlements(self, aplicacao_id: str, **parametros: Any) -> list[dict[str, Any]]`
- `ClienteHTTP.listar_entitlements_modelados(self, aplicacao_id: str, **parametros: Any) -> list[Any]`
- `ClienteHTTP.obter_entitlement(self, aplicacao_id: str, entitlement_id: str) -> dict[str, Any]`
- `ClienteHTTP.obter_entitlement_modelado(self, aplicacao_id: str, entitlement_id: str) -> Any`
- `ClienteHTTP.criar_entitlement_teste(self, aplicacao_id: str, *, sku_id: str, owner_id: str, tipo_dono: int) -> dict[str, Any]`
- `ClienteHTTP.criar_entitlement_teste_modelado(self, aplicacao_id: str, *, sku_id: str, owner_id: str, tipo_dono: int) -> Any`
- `ClienteHTTP.excluir_entitlement_teste(self, aplicacao_id: str, entitlement_id: str) -> None`
- `ClienteHTTP.consumir_entitlement(self, aplicacao_id: str, entitlement_id: str) -> None`
- `ClienteHTTP.listar_skus(self, aplicacao_id: str='@me', **parametros: Any) -> list[dict[str, Any]]`
- `ClienteHTTP.obter_sku(self, aplicacao_id: str, sku_id: str) -> dict[str, Any]`
- `ClienteHTTP.listar_assinaturas(self, aplicacao_id: str='@me', **parametros: Any) -> list[dict[str, Any]]`
- `ClienteHTTP.obter_assinatura(self, aplicacao_id: str, assinatura_id: str) -> dict[str, Any]`
- `ClienteHTTP.cancelar_assinatura(self, aplicacao_id: str, assinatura_id: str) -> None`
- `ClienteHTTP.listar_skus_modelados(self, aplicacao_id: str='@me', **parametros: Any) -> list[Any]`
- `ClienteHTTP.obter_sku_modelado(self, aplicacao_id: str, sku_id: str) -> Any`
- `ClienteHTTP.listar_assinaturas_modeladas(self, aplicacao_id: str='@me', **parametros: Any) -> list[Any]`
- `ClienteHTTP.listar_assinaturas_sku(self, sku_id: str, *, antes: str | None=None, depois: str | None=None, limite: int | None=None, usuario_id: str | None=None) -> list[dict[str, Any]]`
- `ClienteHTTP.obter_assinatura_sku(self, sku_id: str, assinatura_id: str, *, usuario_id: str | None=None) -> dict[str, Any]`
- `ClienteHTTP.obter_assinatura_modelada(self, aplicacao_id: str, assinatura_id: str) -> Any`
- `ClienteHTTP.obter_usuario_atual(self) -> dict[str, Any]`
- `ClienteHTTP.obter_aplicacao_atual(self) -> dict[str, Any]`
- `ClienteHTTP.editar_aplicacao_atual(self, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.listar_comandos_aplicacao(self, aplicacao_id: str, *, servidor_id: str | None=None) -> list[dict[str, Any]]`
- `ClienteHTTP.listar_comandos_servidor(self, aplicacao_id: str, servidor_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.criar_comando_aplicacao(self, aplicacao_id: str, *, servidor_id: str | None=None, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.criar_comando_servidor(self, aplicacao_id: str, servidor_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.substituir_comandos(self, aplicacao_id: str, comandos: list[dict[str, Any]], *, servidor_id: str | None=None) -> list[dict[str, Any]]`
- `ClienteHTTP.obter_comando_aplicacao(self, aplicacao_id: str, comando_id: str, *, servidor_id: str | None=None) -> dict[str, Any]`
- `ClienteHTTP.editar_comando_aplicacao(self, aplicacao_id: str, comando_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.excluir_comando_aplicacao(self, aplicacao_id: str, comando_id: str) -> None`
- `ClienteHTTP.editar_comando_servidor(self, aplicacao_id: str, servidor_id: str, comando_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.excluir_comando_servidor(self, aplicacao_id: str, servidor_id: str, comando_id: str) -> None`
- `ClienteHTTP.obter_permissoes_comandos_servidor(self, aplicacao_id: str, servidor_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.obter_permissoes_comando(self, aplicacao_id: str, servidor_id: str, comando_id: str) -> dict[str, Any]`
- `ClienteHTTP.substituir_permissoes_comando(self, aplicacao_id: str, servidor_id: str, comando_id: str, permissoes: list[dict[str, Any]]) -> dict[str, Any]`
- `ClienteHTTP.listar_regras_automoderacao(self, servidor_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.obter_regra_automoderacao(self, servidor_id: str, regra_id: str) -> dict[str, Any]`
- `ClienteHTTP.criar_regra_automoderacao(self, servidor_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.editar_regra_automoderacao(self, servidor_id: str, regra_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.excluir_regra_automoderacao(self, servidor_id: str, regra_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.listar_eventos_agendados(self, servidor_id: str, *, incluir_entidade: bool=False) -> list[dict[str, Any]]`
- `ClienteHTTP.obter_evento_agendado(self, servidor_id: str, evento_id: str, *, incluir_entidade: bool=False) -> dict[str, Any]`
- `ClienteHTTP.criar_evento_agendado(self, servidor_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.editar_evento_agendado(self, servidor_id: str, evento_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.excluir_evento_agendado(self, servidor_id: str, evento_id: str, *, motivo: str | None=None) -> None`
- `ClienteHTTP.listar_eventos_agendados_modelados(self, servidor_id: str, *, incluir_entidade: bool=False) -> list[Any]`
- `ClienteHTTP.obter_evento_agendado_modelado(self, servidor_id: str, evento_id: str, *, incluir_entidade: bool=False) -> Any`
- `ClienteHTTP.listar_inscritos_evento(self, servidor_id: str, evento_id: str, *, limite: int=100, antes_de: str | None=None, depois_de: str | None=None, incluir_membro: bool=False) -> list[dict[str, Any]]`
- `ClienteHTTP.listar_inscritos_excecao_evento(self, servidor_id: str, evento_id: str, excecao_id: str, *, limite: int=100, antes_de: str | None=None, depois_de: str | None=None, incluir_membro: bool=False) -> list[dict[str, Any]]`
- `ClienteHTTP.criar_excecao_evento(self, servidor_id: str, evento_id: str, usuario_id: str | None=None, *, inicio_original: str | None=None, inicio: str | None=None, fim: str | None=None, cancelada: bool | None=None, **dados_legados: Any) -> dict[str, Any]`
- `ClienteHTTP.editar_excecao_evento(self, servidor_id: str, evento_id: str, usuario_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.excluir_excecao_evento(self, servidor_id: str, evento_id: str, usuario_id: str) -> None`
- `ClienteHTTP.listar_templates(self, servidor_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.obter_template(self, codigo: str) -> dict[str, Any]`
- `ClienteHTTP.criar_template(self, servidor_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.editar_template(self, servidor_id: str, codigo: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.excluir_template(self, servidor_id: str, codigo: str) -> None`
- `ClienteHTTP.sincronizar_template(self, servidor_id: str, codigo: str) -> dict[str, Any]`
- `ClienteHTTP.listar_sons_padrao(self) -> dict[str, Any]`
- `ClienteHTTP.listar_sons_padrao_modelados(self) -> list[Any]`
- `ClienteHTTP.listar_sons_servidor(self, servidor_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.listar_sons_servidor_modelados(self, servidor_id: str) -> list[Any]`
- `ClienteHTTP.obter_som_servidor(self, servidor_id: str, som_id: str) -> dict[str, Any]`
- `ClienteHTTP.obter_som_servidor_modelado(self, servidor_id: str, som_id: str) -> Any`
- `ClienteHTTP.enviar_som(self, canal_id: str, som_id: str, *, servidor_origem_id: str | None=None) -> None`
- `ClienteHTTP.criar_som_servidor(self, servidor_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.editar_som_servidor(self, servidor_id: str, som_id: str, **dados: Any) -> dict[str, Any]`
- `ClienteHTTP.excluir_som_servidor(self, servidor_id: str, som_id: str) -> None`
- `ClienteHTTP.listar_servidores_usuario(self, *, limite: int=100, antes_de: str | None=None, depois_de: str | None=None) -> list[dict[str, Any]]`
- `ClienteHTTP.sair_servidor(self, servidor_id: str) -> None`
- `ClienteHTTP.adicionar_membro_oauth(self, servidor_id: str, usuario_id: str, token_acesso: str, *, dados: dict[str, Any] | None=None) -> dict[str, Any]`
- `ClienteHTTP.obter_canais_voz(self, servidor_id: str) -> list[dict[str, Any]]`
- `ClienteHTTP.gateway_publico(self) -> dict[str, Any]`
- `ClienteHTTP.listar_pacotes_sticker(self) -> list[dict[str, Any]]`
- `ClienteHTTP.obter_pacote_sticker(self, pacote_id: str) -> dict[str, Any]`
- `ClienteHTTP.obter_instancia_atividade(self, aplicacao_id: str, instancia_id: str) -> dict[str, Any]`
- `ClienteHTTP.listar_entitlements_usuario(self, aplicacao_id: str, **parametros: Any) -> list[dict[str, Any]]`
- `ClienteHTTP.listar_contagens_inscritos_evento(self, servidor_id: str, evento_id: str, **parametros: Any) -> list[dict[str, Any]]`
- `ClienteHTTP.seguir_canal(self, canal_id: str, webhook_canal_id: str) -> dict[str, Any]`
- `ClienteHTTP.banir_membros_em_lote(self, servidor_id: str, usuarios: list[str], *, dias_mensagens: int=0, motivo: str | None=None) -> dict[str, Any]`
- `ClienteHTTP.alterar_status_voz(self, canal_id: str, *, status: str | None=None) -> None`

### Função `json_module_loads(texto: str) -> Any`

## `pimcord/ia`

### Classe `ErroGeradorIA`

Resposta ausente, inválida ou fora do contrato seguro.


### Função `validar_plano(plano: Any) -> dict[str, Any]`

### Classe `GeradorPlanoIA`

Gera planos seguros a partir de um cliente OpenAI-compatible injetado.

- `GeradorPlanoIA.gerar_plano(self, descricao: str) -> dict[str, Any]`

## `pimcord/interacoes/__init__`

## `pimcord/interacoes/modelos`

### Classe `Interacao`

- `Interacao.entitlements_modelados(self) -> list[Any]`
- `Interacao.authorizing_integration_owners(self) -> dict[str, str]`
- `Interacao.attachment_size_limit(self) -> int | None`
- `Interacao.app_permissions(self) -> str | None`
- `Interacao.responder(self, conteudo: str='', *, embed: Embed | None=None, view: Any=None, ephemeral: bool=False, arquivos: Iterable[Any] | None=None, campos_multipart: dict[str, Any] | None=None) -> Any`
- `Interacao.responder_autocomplete(self, escolhas: list[dict[str, Any]] | list[str]) -> Any`
- `Interacao.adiar(self, *, ephemeral: bool=False) -> Any`
- `Interacao.followup(self, conteudo: str='', *, embed: Embed | None=None, view: Any=None, ephemeral: bool=False, arquivos: Iterable[Any] | None=None, campos_multipart: dict[str, Any] | None=None) -> Any`
- `Interacao.obter_followup(self, mensagem_id: str) -> Any`
- `Interacao.apagar_followup(self, mensagem_id: str) -> Any`
- `Interacao.editar_followup(self, mensagem_id: str, conteudo: str | None=None, *, embed: Embed | None=None, view: Any=None) -> Any`
- `Interacao.apagar_resposta(self) -> Any`
- `Interacao.editar_resposta(self, conteudo: str | None=None, *, embed: Embed | None=None, view: Any=None) -> Any`

## `pimcord/metricas`

### Classe `Metricas`

- `Metricas.contar_evento(self, nome: str) -> None`
- `Metricas.snapshot(self) -> dict[str, object]`

## `pimcord/nucleo`

### Classe `PimcordErro`


### Classe `ErroDeConfiguracao`


### Classe `ErroDeConexao`


### Classe `ErroDeAutenticacao`


### Classe `ErroDePermissao`


### Classe `ComandoNaoEncontrado`


### Classe `ComandoInvalido`


### Classe `InteracaoExpirada`


### Classe `RateLimitado`


### Classe `ErroDaAPI`


### Classe `ErroDoGateway`


### Classe `Permissoes`

- `Permissoes.todas(cls) -> 'Permissoes'`

### Classe `Intents`

- `Intents.todos(cls) -> 'Intents'`
- `Intents.all(cls) -> 'Intents'`
- `Intents.mascara(self) -> int`

### Classe `Configuracao`

- `Configuracao.ambiente(cls, prefixo: str='!') -> 'Configuracao'`
- `Configuracao.validar(self) -> None`

### Classe `Embed`

- `Embed.adicionar_campo(self, nome: str, valor: str, inline: bool=False) -> 'Embed'`
- `Embed.para_dict(self) -> dict[str, Any]`

### Classe `Contexto`

- `Contexto.message(self) -> Any`
- `Contexto.responder(self, conteudo: str='', *, embed: Embed | None=None, view: Any=None, ephemeral: bool=False) -> Any`
- `Contexto.responder_embed(self, embed: Embed) -> Any`
- `Contexto.enviar(self, *args: Any, **kwargs: Any) -> Any`

### Classe `Botao`

- `Botao.para_dict(self) -> dict[str, Any]`

### Classe `OpcaoSelect`

- `OpcaoSelect.para_dict(self) -> dict[str, Any]`

### Classe `Select`

- `Select.adicionar_opcao(self, rotulo: str, valor: str, *, descricao: str | None=None, emoji: str | None=None, padrao: bool=False) -> 'Select'`
- `Select.para_dict(self) -> dict[str, Any]`

### Classe `EntradaModal`

- `EntradaModal.para_dict(self) -> dict[str, Any]`

### Classe `Modal`

- `Modal.adicionar_entrada(self, entrada: EntradaModal) -> 'Modal'`
- `Modal.para_dict(self) -> dict[str, Any]`

### Classe `UploadArquivos`

Componente Discord de upload de arquivos (tipo 19).

- `UploadArquivos.para_dict(self) -> dict[str, Any]`

### Classe `View`

- `View.persistente(self) -> bool`
- `View.adicionar_item(self, item: Any) -> 'View'`
- `View.adicionar_select(self, select: Select) -> 'View'`
- `View.select(self, custom_id: str, *, placeholder: str | None=None, minimo: int=1, maximo: int=1, linha: int=0)`
- `View.botao(self, custom_id: str, *, texto: str, estilo: str='primario', linha: int=0)`
- `View.upload(self, custom_id: str, *, minimo: int=1, maximo: int=1, obrigatorio: bool=True, tipos_arquivo: list[str] | None=None, linha: int=0)`
- `View.para_componentes(self) -> list[dict[str, Any]]`
- `View.encerrar(self) -> None`

## `pimcord/oauth2`

### Classe `TokenOAuth2`

Resposta normalizada do endpoint de token OAuth2.

- `TokenOAuth2.de_dict(cls, dados: Mapping[str, Any]) -> 'TokenOAuth2'`

### Classe `ClienteOAuth2`

Constrói URLs e executa os três fluxos OAuth2 suportados pelo Discord.

O parâmetro ``transportador`` recebe ``(url, dados_formulario)`` e deve
devolver o JSON decodificado. Assim, a parte determinística permanece
utilizável em Pydroid/Termux e a rede fica sob controle da aplicação.

- `ClienteOAuth2.url_autorizacao(self, *, redirecionamento: str, escopos: list[str] | tuple[str, ...], estado: str | None=None, resposta: str='code', permissao: int | None=None, prompt: str | None=None, servidor_id: str | None=None, desabilitar_selecao_servidor: bool | None=None, tipo_integracao: int | None=None) -> str`
- `ClienteOAuth2.formulario_codigo(self, codigo: str, *, redirecionamento: str, segredo: str | None=None) -> dict[str, str]`
- `ClienteOAuth2.formulario_renovacao(self, token_renovacao: str, *, escopo: str | None=None, segredo: str | None=None) -> dict[str, str]`
- `ClienteOAuth2.codificar_formulario(dados: Mapping[str, str]) -> str`
- `ClienteOAuth2.trocar_codigo(self, codigo: str, *, redirecionamento: str, segredo: str | None=None) -> TokenOAuth2`
- `ClienteOAuth2.renovar(self, token_renovacao: str, *, escopo: str | None=None, segredo: str | None=None) -> TokenOAuth2`
- `ClienteOAuth2.criar_anexo_atividade(self, token: str, arquivo: bytes, *, nome_arquivo: str='arquivo', tipo_mime: str='application/octet-stream') -> Mapping[str, Any]`
- `ClienteOAuth2.revogar(self, token: str, *, tipo: str='access_token', segredo: str | None=None) -> None`

## `pimcord/opus`

### Classe `OpusIndisponivel`

Sinaliza que libopus não está instalada ou não pôde ser carregada.


### Classe `CodecOpus`

Codificador/decodificador Opus real, adequado a frames de voz Discord.

- `CodecOpus.codificar(self, pcm: bytes) -> bytes`
- `CodecOpus.decodificar(self, pacote: bytes, *, frame_size: int | None=None) -> bytes`
- `CodecOpus.fechar(self) -> None`

## `pimcord/permissoes`

### Classe `SobrescritaPermissao`

Regra de permissão para um cargo ou usuário em um canal.

- `SobrescritaPermissao.cargo(cls, cargo_id: str, *, permitir: Permissoes=Permissoes(0), negar: Permissoes=Permissoes(0)) -> 'SobrescritaPermissao'`
- `SobrescritaPermissao.usuario(cls, usuario_id: str, *, permitir: Permissoes=Permissoes(0), negar: Permissoes=Permissoes(0)) -> 'SobrescritaPermissao'`
- `SobrescritaPermissao.para_dict(self) -> dict[str, Any]`

## `pimcord/projeto_ia`

### Classe `ErroProjetoIA`

Projeto gerado fora do contrato ou com conteúdo não permitido.


### Função `validar_projeto(projeto: Any) -> dict[str, Any]`

### Classe `ProjetoGerado`

- `ProjetoGerado.nome(self) -> str`
- `ProjetoGerado.caminhos(self) -> tuple[str, ...]`
- `ProjetoGerado.salvar(self, diretorio: str | os.PathLike[str]) -> Path`
- `ProjetoGerado.executar(self, diretorio: str | os.PathLike[str], *, token: str | None=None) -> int`

### Classe `GeradorProjetoIA`

Gera um projeto completo estruturado, sem executar o resultado.

- `GeradorProjetoIA.gerar(self, pedido: str) -> ProjetoGerado`

### Função `criar_projeto_ia(pedido: str, cliente: Any, diretorio: str | os.PathLike[str], *, modelo: str='gpt-5-mini', executar: bool=False, token: str | None=None) -> ProjetoGerado`

## `pimcord/pronto`

### Classe `ErroBotPronto`

Descrição inválida ou capacidade não permitida na DSL.


### Classe `DefinicaoComando`


### Classe `DefinicaoBot`


### Função `interpretar(descricao: str) -> DefinicaoBot`

### Função `construir_plano(plano: dict[str, Any], *, token: str | None=None) -> Any`

### Função `construir(descricao: str, *, token: str | None=None) -> Any`

### Função `construir_com_ia(descricao: str, gerador: Any, *, token: str | None=None) -> Any`

### Função `bot_pronto(descricao: str, *, token: str | None=None, iniciar: bool=True, gerador: Any=None) -> Any`

## `pimcord/saude`

### Classe `Verificacao`


### Classe `RelatorioSaude`

- `RelatorioSaude.aprovado(self) -> bool`
- `RelatorioSaude.avisos(self) -> list[Verificacao]`
- `RelatorioSaude.para_dict(self) -> dict[str, Any]`

### Função `diagnosticar(bot: Any, *, exigir_token: bool=False) -> RelatorioSaude`

## `pimcord/seguranca`

### Classe `FiltroSegredos`

Redige valores sensíveis em mensagens e argumentos de um LogRecord.

- `FiltroSegredos.adicionar(self, *segredos: str) -> None`
- `FiltroSegredos.redigir(self, valor: Any) -> str`
- `FiltroSegredos.filter(self, registro: logging.LogRecord) -> bool`

### Função `token_redigido(token: str | None) -> str`

## `pimcord/sharding`

### Classe `ShardInfo`

- `ShardInfo.pertence(self, servidor_id: int | str) -> bool`
- `ShardInfo.marcar(self, estado: str, *, latencia: float | None=None, erro: Exception | None=None) -> None`

### Classe `GerenciadorDeShards`

- `GerenciadorDeShards.shard_de_servidor(self, servidor_id: int | str) -> ShardInfo`
- `GerenciadorDeShards.saudavel(self) -> bool`
- `GerenciadorDeShards.estado(self) -> dict[int, dict[str, Any]]`
- `GerenciadorDeShards.iniciar(self) -> None`
- `GerenciadorDeShards.aguardar_saude(self, tempo_limite: float | None=None) -> bool`
- `GerenciadorDeShards.reiniciar(self, shard_id: int) -> None`
- `GerenciadorDeShards.parar(self) -> None`

## `pimcord/simulador`

### Classe `RegistroSimulado`


### Classe `Simulador`

Ambiente local para exercitar um Bot sem conectar ao Discord.

- `Simulador.iniciar(self, usuario: dict[str, Any] | None=None, servidores: list[dict[str, Any]] | None=None) -> None`
- `Simulador.emitir(self, evento: str, dados: dict[str, Any] | None=None) -> Any`
- `Simulador.mensagem(self, conteudo: str, *, autor: dict[str, Any] | None=None, canal_id: str='canal-simulado') -> Any`
- `Simulador.interacao(self, dados: dict[str, Any]) -> Any`
- `Simulador.registrar_resposta(self, dados: dict[str, Any]) -> dict[str, Any]`
- `Simulador.parar(self) -> None`

## `pimcord/tarefas/__init__`

### Classe `PoliticaRetentativa`

- `PoliticaRetentativa.atraso(self, tentativa: int) -> float`

### Classe `TarefaAgendada`

- `TarefaAgendada.ativa(self) -> bool`
- `TarefaAgendada.iniciar(self) -> 'TarefaAgendada'`
- `TarefaAgendada.parar(self) -> None`

### Classe `Agendador`

- `Agendador.registrar(self, nome: str, funcao: Callable[[], Any], intervalo: float, *, politica: PoliticaRetentativa | None=None) -> TarefaAgendada`
- `Agendador.iniciar_todas(self) -> None`
- `Agendador.parar_todas(self) -> None`

### Classe `FilaAssincrona`

Fila limitada com produtores, consumidores e encerramento explícito.

- `FilaAssincrona.colocar(self, item: T) -> None`
- `FilaAssincrona.consumir(self, funcao: Callable[[T], Any], *, consumidores: int=1) -> list[asyncio.Task[Any]]`
- `FilaAssincrona.encerrar(self, consumidores: int=1) -> None`

## `pimcord/voz`

### Classe `CodificadorAudio`

- `CodificadorAudio.codificar(self, pcm: bytes) -> bytes`

### Classe `CriptografadorVoz`

- `CriptografadorVoz.cifrar(self, dados: bytes, nonce: bytes) -> bytes`

### Classe `InformacoesVoz`

- `InformacoesVoz.de_pronto(cls, servidor_id: str, usuario_id: str, sessao_id: str, token: str, dados: dict[str, Any]) -> 'InformacoesVoz'`

### Classe `PacoteRTP`

- `PacoteRTP.serializar(self) -> bytes`
- `PacoteRTP.desserializar(cls, dados: bytes) -> 'PacoteRTP'`

### Classe `BufferJitter`

Ordena pacotes RTP recebidos e descarta duplicatas fora da janela.

- `BufferJitter.pendentes(self) -> int`
- `BufferJitter.inserir(self, pacote: PacoteRTP) -> list[PacoteRTP]`
- `BufferJitter.avançar_sequencia(self, sequencia: int) -> int`

### Classe `TransporteUDP`

Transporte UDP de voz com estado observável e injeção de socket.

- `TransporteUDP.connection_made(self, transporte: asyncio.BaseTransport) -> None`
- `TransporteUDP.datagram_received(self, dados: bytes, endereco: tuple[str, int]) -> None`
- `TransporteUDP.error_received(self, erro: Exception) -> None`
- `TransporteUDP.connection_lost(self, erro: Exception | None) -> None`
- `TransporteUDP.enviar(self, dados: bytes, endereco: tuple[str, int]) -> None`
- `TransporteUDP.fechar(self) -> None`

### Classe `SessaoVoz`

Orquestra uma sessão de voz sem esconder estados de protocolo.

- `SessaoVoz.ativar_dave(self, backend: Any, *, codec: str='opus') -> Any`
- `SessaoVoz.dave_ativo(self) -> bool`
- `SessaoVoz.conectada(self) -> bool`
- `SessaoVoz.modo_criptografia(self) -> str | None`
- `SessaoVoz.entrar(self, canal_id: str, *, auto_mudo: bool=False, auto_surdo: bool=False) -> None`
- `SessaoVoz.preparar_servidor(self, dados: dict[str, Any], sessao_id: str) -> InformacoesVoz`
- `SessaoVoz.preparar_udp(self, *, ip: str, porta: int, loop: asyncio.AbstractEventLoop | None=None) -> TransporteUDP`
- `SessaoVoz.descobrir_ip(self, *, timeout: float=5.0) -> tuple[str, int]`
- `SessaoVoz.selecionar_modo(self, preferidos: tuple[str, ...]=('aead_xchacha20_poly1305_rtpsize', 'aead_aes256_gcm_rtpsize', 'xsalsa20_poly1305_lite_rtpsize', 'xsalsa20_poly1305_lite')) -> str`
- `SessaoVoz.construir_select_protocol(self, *, endereco: str, porta: int, modo: str | None=None) -> dict[str, Any]`
- `SessaoVoz.iniciar_heartbeat(self, enviar: Any, intervalo: float | None=None) -> None`
- `SessaoVoz.receber_audio(self, dados: bytes, *, decodificador: Any=None, gravador: Any=None, processador: Any=None, remetente_id: str | None=None) -> list[bytes]`
- `SessaoVoz.construir_audio(self, carga: bytes, *, marcador: bool=False, tipo_carga: int=120, criptografador: CriptografadorVoz | None=None) -> bytes`
- `SessaoVoz.enviar_audio(self, carga: bytes, *, criptografador: CriptografadorVoz | None=None) -> None`
- `SessaoVoz.sair(self) -> None`

### Classe `ClienteGatewayVoz`

Cliente WebSocket do Voice Gateway com dependência HTTP injetável.

- `ClienteGatewayVoz.conectar(self) -> None`
- `ClienteGatewayVoz.processar_binario(self, dados: bytes) -> None`
- `ClienteGatewayVoz.enviar_binario_dave(self, dados: bytes) -> None`
- `ClienteGatewayVoz.processar(self, pacote: dict[str, Any]) -> None`
- `ClienteGatewayVoz.executar(self, *, maximo_tentativas: int | None=None) -> None`
- `ClienteGatewayVoz.enviar(self, pacote: dict[str, Any]) -> None`
- `ClienteGatewayVoz.selecionar_protocolo(self, cliente: 'ClienteGatewayVoz', *, endereco: str, porta: int) -> None`
- `ClienteGatewayVoz.sinalizar_fala(self, falando: bool, *, prioridade: int=0) -> None`
- `ClienteGatewayVoz.fechar(self) -> None`

### Classe `FonteAudio`

- `FonteAudio.proximo_quadro(self) -> bytes | None`

### Classe `FontePCM`

- `FontePCM.proximo_quadro(self) -> bytes | None`

### Classe `FonteSilencio`

- `FonteSilencio.proximo_quadro(self) -> bytes | None`

### Classe `FilaAudio`

Fila limitada que evita explodir a memória durante reprodução.

- `FilaAudio.adicionar(self, fonte: FonteAudio) -> None`
- `FilaAudio.parar(self) -> None`
- `FilaAudio.reproduzir(self, sessao: SessaoVoz, *, intervalo: float=0.02, codificador: CodificadorAudio | None=None) -> None`
- `FilaAudio.duracao_aproximada(self) -> float`

### Classe `CodificadorIdentidade`

Codec simples para transporte de PCM em simuladores e testes.

- `CodificadorIdentidade.codificar(self, pcm: bytes) -> bytes`

### Classe `FonteWAV`

Fonte WAV baseada apenas na biblioteca padrão do Python.

- `FonteWAV.proximo_quadro(self) -> bytes | None`
- `FonteWAV.fechar(self) -> None`

### Classe `GravadorWAV`

Gravador WAV PCM leve, útil para testes e bots móveis.

- `GravadorWAV.escrever(self, dados: bytes) -> None`
- `GravadorWAV.fechar(self) -> None`

### Classe `InterpoladorPCM`

Interpola linearmente dois quadros PCM 16-bit conhecidos.

A classe não decide quando uma perda deve ser preenchida. O aplicativo deve
fornecer os quadros vizinhos e a posição intermediária explicitamente.

- `InterpoladorPCM.interpolar(self, inicio: bytes, fim: bytes, *, passo: int, total_passos: int) -> bytes`

### Classe `ProcessadorPCMRecebido`

Etapa explícita para frames PCM já ordenados pelo recebedor RTP.

O processador nunca decide perdas sozinho. O chamador escolhe se deseja
misturar o lote ou interpolar uma lacuna com quadros vizinhos conhecidos.

- `ProcessadorPCMRecebido.processar(self, quadros: list[bytes] | tuple[bytes, ...], *, misturar: bool=False, gravador: Any=None) -> list[bytes]`
- `ProcessadorPCMRecebido.preencher_lacuna(self, inicio: bytes, fim: bytes, *, passo: int, total_passos: int) -> bytes`

### Classe `MisturadorPCM`

Mistura quadros PCM little-endian assinados com saturação.

O mixador exige a mesma largura de amostra e não preenche perdas. Quadros
ausentes devem ser tratados pela política de perdas antes desta etapa.

- `MisturadorPCM.misturar(self, quadros: list[bytes] | tuple[bytes, ...]) -> bytes`

### Classe `CodificadorOpus`

Codec Opus real com backend nativo e compatibilidade opuslib.

O backend ctypes não exige `opuslib`, o que reduz a superfície de instalação
em Linux e permite que ambientes móveis escolham explicitamente seu backend.

- `CodificadorOpus.codificar(self, pcm: bytes) -> bytes`
- `CodificadorOpus.decodificar(self, pacote: bytes, *, frame_size: int=960) -> bytes`
- `CodificadorOpus.fechar(self) -> None`

### Classe `CriptografiaVozOpcional`

Cifras opcionais reais; nunca rotula uma cifra incompatível como XChaCha20/DAVE.

- `CriptografiaVozOpcional.cifrar(self, dados: bytes, nonce: bytes) -> bytes`
- `CriptografiaVozOpcional.cifrar_pacote(self, cabecalho_rtp: bytes, carga: bytes, *, contador: int=0) -> bytes`

## `pimcord/webhooks`

### Classe `Webhook`

- `Webhook.enviar(self, conteudo: str='', *, nome: str | None=None, avatar_url: str | None=None, embed: Embed | None=None, embeds: list[Embed] | None=None, esperar: bool=False, permitido_mencionar: dict[str, Any] | None=None) -> Any`
- `Webhook.editar_mensagem(self, mensagem_id: str, *, conteudo: str | None=None, embed: Embed | None=None) -> Any`
- `Webhook.apagar_mensagem(self, mensagem_id: str) -> None`
