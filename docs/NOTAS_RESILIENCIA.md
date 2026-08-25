
## Checkpoint persistente — 18/08/2026

`GerenciadorDeShards` agora aceita `caminho_checkpoint` opcional. O estado é gravado de forma atômica em arquivo temporário com `fsync` e `os.replace`, contendo total, trabalhador e estado resumido de cada shard. Ao reconstruir o supervisor, shards anteriormente conectados ou encerrados são marcados como `retomando`, nunca como conectados; a supervisão precisa reconectá-los antes de declarar saúde. O contrato cobre persistência, reconstrução e retomada sem rede.
