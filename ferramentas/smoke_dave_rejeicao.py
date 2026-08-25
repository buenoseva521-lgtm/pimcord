from __future__ import annotations

import json

import dave

from pimcord.adaptador_dave import AdaptadorDAVEPy


def principal() -> None:
    adaptador = AdaptadorDAVEPy(dave)
    adaptador.inicializar(versao=1, grupo_id=123, usuario_id="123456789")
    adaptador.definir_usuarios_reconhecidos({"123456789", "987654321"})
    resultados: dict[str, str] = {}
    for nome, funcao in (
        ("propostas", lambda: adaptador.processar_propostas(b"invalid-mls")),
        ("commit", lambda: adaptador.processar_commit(b"invalid-mls")),
        ("welcome", lambda: adaptador.processar_welcome(b"invalid-mls")),
    ):
        try:
            retorno = funcao()
        except Exception as erro:  # o wheel nativo pode variar a exceção concreta
            resultados[nome] = type(erro).__name__
        else:
            resultados[nome] = "rejeitado-sem-efeito" if retorno is None else "aceito-indebidamente"
    print(json.dumps(resultados, ensure_ascii=False, sort_keys=True))
    if any(valor == "aceito-indebidamente" for valor in resultados.values()):
        raise SystemExit("backend aceitou mensagem MLS inválida")


if __name__ == "__main__":
    principal()
