# Esquema de rótulos (v2)

Uma foto recebe **uma cena** (exclusiva) e **zero ou mais defeitos** (independentes).
Defina pelo que se vê na foto, nunca pelo CSV ou pela nota de ocorrência.

## Cena (exclusiva, softmax)

| Classe | Definição operacional | Exemplo-limite: quase é | Exemplo-limite: quase não é |
|---|---|---|---|
| `digital` | O medidor principal da foto tem visor numérico (LCD/LED) e ele aparece, mesmo que ilegível, escuro ou apagado. | Visor apagado ou cortado na borda: continua `digital` (marque o defeito). Foto escura em que ainda se identifica o visor: continua `digital`. | Medidor digital ao fundo, pequeno, de outra unidade, com o principal fora do quadro: avalie o que o leiturista queria fotografar. |
| `ciclometrico` | O medidor tem mostrador de rolos/dígitos mecânicos ou discos. | Rolos parcialmente cobertos por reflexo: continua `ciclometrico`. Foto escura em que ainda se identifica o mostrador de rolos: continua `ciclometrico`. | Medidor eletromecânico só com disco girando e sem dígitos: não é `ciclometrico`; use `cena_ocorrencia` se o medidor não puder ser lido. |
| `cena_ocorrencia` | A foto documenta uma situação (portão fechado, medidor inacessível, fachada, rua, caixa lacrada, medidor coberto ou tampado) e **não** mostra um medidor com tipo identificável como foco. | Medidor visível dentro de uma caixa fechada ao fundo: `cena_ocorrencia`. Medidor visível mas coberto ou tampado, sem dar para identificar o tipo: `cena_ocorrencia`. | Medidor em primeiro plano com a porta da caixa aberta e o tipo identificável: não é ocorrência, mesmo que a caixa esteja em mau estado. |
| `nao_medidor` | Nada na foto é um medidor nem documenta ocorrência (chão, dedo, folhagem sem pista de medidor, foto escura sem conteúdo, objeto aleatório). | Foto quase preta onde só dá para adivinhar uma placa, sem identificar o tipo: `nao_medidor`. | Foto de fachada com medidor longe: é `cena_ocorrencia`. |

### Ordem de decisão (use sempre esta ordem)

1. Dá para identificar o **tipo** do medidor (visor numérico ou rolos/discos), mesmo ilegível,
   escuro ou apagado? Classe do tipo (`digital` ou `ciclometrico`), e marque os defeitos.
2. Senão: a foto mostra uma situação que explica a falta de leitura (portão, fachada, caixa
   fechada, medidor coberto ou tampado, medidor visível sem tipo identificável)? `cena_ocorrencia`.
3. Senão: `nao_medidor`.

Atalho para dúvida entre tipo e `cena_ocorrencia`: "um analista conseguiria tentar ler o
número nesta foto?". Sim: tipo de medidor. Não: `cena_ocorrencia`.

`nao_medidor` não é "não consegui ler": é "não há medidor nem situação a documentar".

## Defeitos de qualidade (multirrótulo, sigmoide)

Marque o defeito só se ele **atrapalha a leitura** do display ou da placa. Em `nao_medidor` e em `cena_ocorrencia` não se marcam defeitos (não há display ou placa legível como foco).

| Defeito | Marque quando | Quase marca / não marca |
|---|---|---|
| `reflexo` | Brilho ou clarão cobre parte do display ou da placa e esconde dígito. Teste: tape mentalmente o brilho; se algum dígito sumir, marque. | Brilho na carcaça ou no vidro longe do display: não marca. Reflexo de céu ou luz no vidro com todos os dígitos legíveis: não marca. |
| `fora_de_foco` | Os dígitos do display têm borda dupla ou borrada; você hesita ao ler. | Foto pequena (360x480) mas com dígitos nítidos: não marca. Borrão leve em que ainda se lê com certeza: não marca. |
| `tampa_suja` | Sujeira, poeira, teia ou risco no vidro/tampa esconde dígito. | Sujeira na carcaça fora da janela: não marca. Vidro embaçado com dígitos legíveis: não marca. |
| `enquadramento` | Display ou placa cortados, muito inclinados, ou muito distantes: dígitos com altura menor que ~10 px na imagem original. Se não dá para medir, marque quando o display ocupa menos de ~10% da largura da foto. | Display inteiro mas deslocado para o canto, com dígitos maiores que ~10 px: não marca. Foto tirada de cima ou de lado, mas display legível: não marca. |
| `display_apagado` | O visor digital não mostra dígitos (apagado, sem energia). Só vale para `digital`. | Visor mostrando todos os segmentos (teste): não é apagado. Visor só coberto por sombra, mas com dígitos visíveis: não é apagado. |

## Procedimento

1. Cada integrante roda `python lab-02/src/rotular.py <nome>` e rotula sua lista (175 fotos).
2. Não conversem sobre a lista até os dois terminarem: 50 fotos são comuns (dupla às cegas).
3. Rodem `src/kappa.py`. Classe com kappa < 0,6: reescrevam a definição acima, registrem no
   histórico abaixo e rerrotulem as fotos comuns afetadas.
4. Divergências ficam listadas em `rotulos/divergencias.csv`. Decidam em conjunto e registrem
   a regra nova aqui, em vez de só corrigir a foto.

## Histórico de versões

- v1 (08/10/2026): versão inicial. Nenhuma mudança por kappa ainda.
- v2 (08/10/2026): primeira rodada de kappa nas 50 fotos comuns (cena 0,718; abaixo de 0,6:
  `cena_ocorrencia` 0,459, `nao_medidor` 0,000, `reflexo` 0,337, `enquadramento` 0,389,
  `display_apagado` 0,370). Mudanças:
  - Cena: ordem de decisão explícita (tipo identificável > ocorrência > `nao_medidor`).
  - `digital`/`ciclometrico` valem também para foto escura em que o tipo ainda se identifica.
  - `cena_ocorrencia` inclui medidor coberto/tampado ou sem tipo identificável.
  - `nao_medidor` fica restrito a "sem medidor e sem situação"; foto só de folhagem entra aqui.
  - `cena_ocorrencia` passa a não receber defeitos, como `nao_medidor`.
  - `reflexo`: teste de tapar o brilho; reflexo que não esconde dígito não marca.
  - `enquadramento`: critério objetivo (~10 px de altura de dígito ou ~10% da largura).
  - `display_apagado`: sombra com dígitos visíveis não conta como apagado.
  - Pendente: rerrotular as fotos comuns afetadas (ver `divergencias.csv`) e rodar `kappa.py`
    de novo para medir a v2.

### Estado do kappa e da adjudicação (08/10/2026)

- Kappa medido na v1 (rótulos às cegas, 50 fotos comuns) está em `kappa.csv`. É o único
  kappa às cegas; a v2 ainda não tem kappa próprio.
- 29 das 50 fotos comuns divergiram (`divergencias.csv`). A dupla decidiu em conjunto
  (`decisoes.csv`, aplicado por `src/aplicar_decisoes.py`). Essa decisão **não é às cegas**
  e não serve para recalcular kappa.
- Kappa da v2 (08/10/2026): 30 fotos novas, mesmas para os dois, rotuladas às cegas sob as
  regras da v2 (`amostra_v2.csv`, `kappa_v2.csv`). Todas as classes ficaram acima de 0,6:

  | Classe | v1 (50 fotos) | v2 (30 fotos) | Positivos na v2 (J / H) |
  |---|---|---|---|
  | cena (4 classes) | 0,718 | 0,917 | |
  | digital | 0,864 | 0,911 | 23 / 22 |
  | ciclometrico | 0,767 | 0,889 | 5 / 6 |
  | cena_ocorrencia | 0,459 | 1,000 | 1 / 1 |
  | nao_medidor | 0,000 | 1,000 | 1 / 1 |
  | reflexo | 0,337 | 0,815 | 6 / 8 |
  | fora_de_foco | 0,634 | 0,714 | 12 / 10 |
  | tampa_suja | 0,649 | 0,793 | 5 / 7 |
  | enquadramento | 0,389 | 0,712 | 4 / 4 |
  | display_apagado | 0,370 | 0,783 | 3 / 2 |

  Cuidado ao ler: n=30, e `cena_ocorrencia` e `nao_medidor` têm 1 caso cada, então o 1,000
  dessas duas não é evidência forte. As demais mostram melhora consistente em relação à v1.

## Partição (C4)

Por lote: treino = 2026-05-20 e 2026-05-21; validação = 2026-05-22; teste = 2026-07-03
(`src/config.py`). `src/particao.py` confere por id de leitura e por número de medidor,
nas 300 fotos rotuladas e na base inteira (`particao.csv`): 0 valores em 2 conjuntos.
29 das 300 fotos não têm linha no CSV da base (órfãs); a partição vale para elas pelo lote,
mas não há id nem medidor para conferir.
