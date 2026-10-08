# Esquema de rótulos (v1)

Uma foto recebe **uma cena** (exclusiva) e **zero ou mais defeitos** (independentes).
Defina pelo que se vê na foto, nunca pelo CSV ou pela nota de ocorrência.

## Cena (exclusiva, softmax)

| Classe | Definição operacional | Exemplo-limite: quase é | Exemplo-limite: quase não é |
|---|---|---|---|
| `digital` | O medidor principal da foto tem visor numérico (LCD/LED) e ele aparece, mesmo que ilegível. | Visor apagado ou cortado na borda: continua `digital` (marque o defeito). | Medidor digital ao fundo, pequeno, de outra unidade, com o principal fora do quadro: avalie o que o leiturista queria fotografar. |
| `ciclometrico` | O medidor tem mostrador de rolos/dígitos mecânicos ou discos. | Rolos parcialmente cobertos por reflexo: continua `ciclometrico`. | Medidor eletromecânico só com disco girando e sem dígitos: não é `ciclometrico`; use `cena_ocorrencia` se o medidor não puder ser lido. |
| `cena_ocorrencia` | A foto documenta uma situação (portão fechado, medidor inacessível, fachada, rua, caixa lacrada) e **não** mostra um medidor legível como foco. | Medidor visível dentro de uma caixa fechada ao fundo: `cena_ocorrencia`. | Medidor em primeiro plano com a porta da caixa aberta: não é ocorrência. |
| `nao_medidor` | Nada na foto é um medidor nem documenta ocorrência (chão, dedo, foto escura sem conteúdo, objeto aleatório). | Foto quase preta onde dá para adivinhar uma placa: `nao_medidor`. | Foto de fachada com medidor longe: é `cena_ocorrencia`. |

Regra de desempate: se houver dúvida entre `digital`/`ciclometrico` e `cena_ocorrencia`, pergunte
"um analista conseguiria tentar ler o número nesta foto?". Sim: tipo de medidor. Não: `cena_ocorrencia`.

## Defeitos de qualidade (multirrótulo, sigmoide)

Marque o defeito só se ele **atrapalha a leitura** do display ou da placa. Em `nao_medidor` não se marcam defeitos.

| Defeito | Marque quando | Quase marca / não marca |
|---|---|---|
| `reflexo` | Brilho ou clarão cobre parte do display ou da placa e esconde dígito. | Brilho na carcaça longe do display: não marca. |
| `fora_de_foco` | Os dígitos do display têm borda dupla ou borrada; você hesita ao ler. | Foto pequena (360x480) mas com dígitos nítidos: não marca. Borrão leve em que ainda se lê com certeza: não marca. |
| `tampa_suja` | Sujeira, poeira, teia ou risco no vidro/tampa esconde dígito. | Sujeira na carcaça fora da janela: não marca. |
| `enquadramento` | Display ou placa cortados, muito distantes (dígitos menores que ~10 px) ou muito inclinados. | Display inteiro mas deslocado para o canto: não marca. |
| `display_apagado` | O visor digital não mostra dígitos (apagado, sem energia). Só vale para `digital`. | Visor mostrando todos os segmentos (teste): não é apagado. |

## Procedimento

1. Cada integrante roda `python src/rotular.py <nome>` e rotula sua lista (175 fotos).
2. Não conversem sobre a lista até os dois terminarem: 50 fotos são comuns (dupla às cegas).
3. Rodem `src/kappa.py`. Classe com kappa < 0,6: reescrevam a definição acima, registrem no
   histórico abaixo e rerrotulem as fotos comuns afetadas.

## Histórico de versões

- v1 (08/10/2026): versão inicial. Nenhuma mudança por kappa ainda.
