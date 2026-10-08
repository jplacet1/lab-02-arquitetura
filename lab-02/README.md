# Laboratório 2 — GridVision (G4)

Grupo do Projeto 4, cliente Neoenergia Pernambuco. Integrantes desta entrega: João Pedro Lins e Henrique Bouwman.
Os números abaixo saem de [`lab02.ipynb`](lab02.ipynb), executado do zero. A ficha de arquitetura está em [`ARQUITETURA.md`](ARQUITETURA.md), o esquema de rótulos em [`rotulos/esquema.md`](rotulos/esquema.md) e o registro de IA em [`USO-DE-IA.md`](USO-DE-IA.md).

## 0. Leitura do docente e o que fizemos

O enunciado descreve o estágio de Korvian, Luminus, VoltLens e Nortdata e traz uma parte específica para cada um. **O GridVision não consta da tabela e não tem bloco específico.** Nosso grupo não participou dos acompanhamentos. Não tentamos encaixar uma tarefa de outro grupo como se fosse nossa.

O que o nosso material diz (kickoff de 12/09 e Status Report 1 de 03/10): a solução é um verificador de fotos de leitura em quatro etapas (qualidade, localização de medidor/ID/visor, leitura, comparação com o registro). Não existe nenhuma caixa anotada, e o OCR pronto lê 42% dos números de medidor e só 20% dos visores. O único bloco profundo que dá para treinar **hoje** é a triagem de cena e qualidade, e é ela que implementamos (parte comum, 0,80). Detector e reconhecedor ficam para o Marco 2, com o motivo escrito na seção 14 da ficha.

## 1. Como reproduzir

1. As fotos do cliente **não** estão no repositório. Aponte o caminho na variável de ambiente `DADOS_NEOENERGIA` ou edite `src/config.py`.
2. Python com `torch`, `torchvision`, `scikit-learn`, `pandas`, `matplotlib`, `pillow`, `scipy`.
3. `lab02.ipynb`: *Reiniciar e executar tudo* (≈15 min em CPU; o ajuste fino é a parte lenta).
4. Rótulos, na ordem: `src/amostra.py` → `src/rotular.py <nome>` → `src/kappa.py` → `src/aplicar_decisoes.py` → `src/juntar_extra.py` → `src/particao.py`.

## 2. Rótulos e partição (item C)

**Esquema (C1).** Cena exclusiva (digital, ciclométrico, cena de ocorrência, não é medidor) e cinco defeitos independentes (reflexo, fora de foco, tampa suja, enquadramento, display apagado), cada classe com definição operacional e dois exemplos-limite em `rotulos/esquema.md`. O esquema está na v2.

**Rótulos (C2).** 500 fotos, 125 por lote, uma foto por leitura:

| Rodada | Fotos | Quem rotulou |
|---|---|---|
| Amostra inicial | 300 (50 comuns) | João e Henrique |
| Extras | 200 | 100 cada, sem dupla |

**Kappa de Cohen (C3).** Na v1, 50 fotos comuns, às cegas. Na v2, 30 fotos novas, às cegas, depois de reescrever as definições:

| Classe | v1 (50 fotos) | v2 (30 fotos) | Positivos v2 (J / H) |
|---|---|---|---|
| cena (4 classes) | 0,718 | 0,917 | |
| digital | 0,864 | 0,911 | 23 / 22 |
| ciclometrico | 0,767 | 0,889 | 5 / 6 |
| cena_ocorrencia | **0,459** | 1,000 | 1 / 1 |
| nao_medidor | **0,000** | 1,000 | 1 / 1 |
| reflexo | **0,337** | 0,815 | 6 / 8 |
| fora_de_foco | 0,634 | 0,714 | 12 / 10 |
| tampa_suja | 0,649 | 0,793 | 5 / 7 |
| enquadramento | **0,389** | 0,712 | 4 / 4 |
| display_apagado | **0,370** | 0,783 | 3 / 2 |

Em negrito, as classes abaixo de 0,6 na v1. **O que mudou no esquema (v1 → v2):**
- ordem de decisão explícita: tipo identificável > ocorrência > não é medidor, e um atalho ("um analista conseguiria tentar ler o número?");
- `cena_ocorrencia` inclui medidor coberto, tampado ou sem tipo identificável, e passa a não receber defeitos, como `nao_medidor`;
- `nao_medidor` ficou restrito a "sem medidor e sem situação a documentar";
- `reflexo`: teste de tapar o brilho mentalmente; `enquadramento`: critério objetivo (~10 px de altura de dígito ou ~10% da largura); `display_apagado`: sombra com dígitos visíveis não conta.

**Ressalvas que importam:**
- Das 50 fotos comuns da v1, 29 divergiram. A dupla decidiu em conjunto (`rotulos/decisoes.csv`); essas decisões **não são às cegas** e não entram em nenhum kappa.
- A v2 tem n = 30. `cena_ocorrencia` e `nao_medidor` têm **1 caso cada**: o kappa 1,000 dessas duas não é evidência forte. As demais classes mostram melhora consistente.
- As 200 fotos extras foram rotuladas por uma pessoa cada, sem dupla; confiamos no kappa da v2 para a qualidade do esquema.

**Partição por lote (C4).** Treino = 2026-05-20 e 2026-05-21; validação = 2026-05-22; teste = 2026-07-03. Prova numérica (`src/particao.py`, `rotulos/particao.csv`):

| Universo | Chave | Valores distintos | Em 2+ conjuntos |
|---|---|---|---|
| 500 fotos rotuladas | id de leitura | 460 | 0 |
| 500 fotos rotuladas | número do medidor | 510 | 0 |
| Base inteira (12.340 fotos) | id de leitura | 11.474 | 0 |
| Base inteira | número do medidor | 12.609 | 0 |

Quarenta das 500 fotos não têm linha no CSV da base (órfãs): a partição vale pelo lote, mas não há chave para conferir nelas. O SR1 propunha dividir por medidor; usamos por lote, como o enunciado exige, e mantivemos o teste temporal.

## 3. O modelo (item B)

**Bloco profundo:** MobileNetV3-Small com duas cabeças (`src/triagem.py`), entrada 480×360 nativa.

- **B1, formas.** 480×360 → blocos do extrator → 15×12×576 → *pool* global → 576 → cabeças de 4 e 5 saídas. Tabela completa no notebook.
- **B2, parâmetros.**

| Configuração | Total | Treináveis |
|---|---|---|
| Ajuste fino | 932.201 | 932.201 |
| Extração (extrator congelado) | 932.201 | **5.193** (cabeça de cena 2.308 + qualidade 2.885) |

- **B3, ativação e perda.** A cena é exclusiva: softmax + `CrossEntropyLoss`. Os defeitos coexistem: uma sigmoide por defeito + `BCEWithLogitsLoss`. Prova na base: **162 das 500 fotos têm 2 ou mais defeitos**; `reflexo` + `fora_de_foco` coocorrem em 66 fotos e `fora_de_foco` + `tampa_suja` em 81. Uma softmax não consegue dizer "reflexo **e** fora de foco". A rede devolve logits e nenhuma softmax é aplicada antes das perdas. Ressalva: a exclusividade da cena vem da regra de desempate do esquema, não de uma separação natural (a fronteira digital × ocorrência foi a de menor kappa na v1).

## 4. Sanidade e baseline (item D)

- **D1.** Perda inicial com pesos aleatórios (64 fotos reais, 3 sementes): CE 1,380–1,384 (ln 4 = 1,386) e BCE 0,689–0,697 (ln 2 = 0,693).
- **D2.** Sobreajuste de 16 fotos reais: perda 2,06 → 0,0018 em 80 passos. O acerto em modo `eval` foi 15/16; a *BatchNorm* com lote de 16 usa estatística diferente no `eval` (explicação provável, não testada).
- **D3.** Extração de características comparada a baselines não profundas, mesma partição e mesmas métricas. Média ± desvio de 3 sementes; as regressões logísticas são determinísticas (sem desvio).

| Método | F1 macro da cena (val / teste) | AP médio dos defeitos (val / teste) |
|---|---|---|
| MobileNetV3, extração (profundo) | 0,550 ± 0,005 / 0,602 ± 0,020 | 0,509 ± 0,004 / 0,607 ± 0,002 |
| V0 (Laplaciano, brilho, histograma) + reg. logística | 0,281 / 0,293 | 0,360 / 0,425 |
| Características profundas + reg. logística | **0,647** / **0,657** | 0,498 / 0,561 |
| MobileNetV3, ajuste fino | 0,592 ± 0,016 / 0,545 ± 0,056 | 0,524 ± 0,001 / 0,609 ± 0,005 |

**Onde o modelo profundo perdeu e por quê.** A regressão logística sobre as mesmas características congeladas bate a cabeça treinada na cena (F1 0,647 contra 0,550). Nossa hipótese, **não testada**: a regressão usa características padronizadas, `class_weight="balanced"` e `C` próprio, e a cabeça treina com hiperparâmetros fixos, sem ponderar as classes raras; o F1 **macro** pune quem ignora `nao_medidor` e `cena_ocorrencia`. Nos defeitos a cabeça profunda fica à frente (AP 0,509 contra 0,498 na validação; 0,607 contra 0,561 no teste). O ajuste fino fica dentro do ruído da extração e muda de sinal entre validação e teste. Contra a V0 (a baseline oficial do SR1), o profundo ganha com folga nas duas métricas.

## 5. Confiança e recusa (item E)

- **E1.** *Temperature scaling* ajustado na validação (T ≈ 1,04). ECE da validação 0,059 → 0,044 e do teste 0,037 → 0,039 (médias de 3 sementes); a NLL não muda. O modelo já sai quase calibrado, e a diferença está na ordem do ruído com 125 fotos e 10 faixas. No ajuste fino, T sobe para ~1,35–1,39 (modelo supraconfiante) e o ECE melhora em 5 de 6 casos. Diagramas de confiabilidade no notebook.
- **E2.** A meta declarada pelo grupo é uma **hipótese a validar com a Neoenergia**: **cobertura ≥ 70% com risco ≤ 5%**. O SR1 deixa em aberto a taxa que o cliente aceita para dispensar a revisão. Limiar fixado na validação e aplicado uma vez ao teste:

| Método | Cobertura val | Risco val | Cobertura teste | Risco teste | Maior cobertura com risco ≤ 5% (val) |
|---|---|---|---|---|---|
| Profundo calibrado | 0,70 | 0,102 | 0,66 | 0,061 | 0,50 |
| Reg. logística, características profundas | 0,70 | 0,114 | 0,77 | 0,156 | 0,42 |
| V0 | 0,70 | 0,591 | 0,74 | 0,516 | 0,01 |

**A meta não cabe na curva.** Para risco ≤ 5% a cobertura cai para ~50%; para cobertura de 70% o risco é ~10%. No teste o limiar dá cobertura 0,66 e risco 0,061: perto, mas com cobertura abaixo da meta. Risco aqui é o erro de **cena** entre as fotos respondidas; a decisão completa (aceita/reprova/revisar, que também usa os defeitos) não foi avaliada.

## 6. Leitura dos resultados

1. A rede aprendida supera de longe a heurística do SR1 (Laplaciano e histograma) como filtro de qualidade e de cena. Esse é o resultado mais sólido.
2. Com 250 fotos de treino, ajuste fino e extração empatam. O ajuste fino custa ~140 s por semente em CPU e deixa o modelo supraconfiante.
3. **Curva de dados** (bônus; validação, 25/50/75/100% de 250 fotos de treino): F1 da cena 0,376 → 0,467 → 0,530 → 0,546; risco na cobertura 0,70: 0,174 → 0,159 → 0,125 → 0,098. Ainda desce; **rotular mais vale a pena**. A extrapolação linear (não medida) aponta ~100 fotos de treino a mais para risco ≤ 5%. A curva anterior (150 fotos de treino, validação de 75) não é comparável com esta.
4. `display_apagado` (17 positivos em 500) não é aprendida de forma útil: o AP (0,047) é do tamanho da prevalência (0,04). Precisa de mais exemplos ou de `pos_weight`.

## 7. Limites

- Validação e teste têm 125 fotos cada; diferenças abaixo de ~0,05 nas métricas são ruído.
- Só a cena foi calibrada. Os defeitos não.
- Não testados: `pos_weight`, perda focal, entrada a 224 px, ONNX, volume real com o cliente. Estão listados na seção 14 da ficha.
- Não treinamos detector nem reconhecedor (sem caixas anotadas).

## 8. Estrutura

```
lab-02/
├── README.md  ARQUITETURA.md  USO-DE-IA.md  lab02.ipynb
├── rotulos/   esquema.md  rotulos.csv  kappa.csv  kappa_v2.csv  particao.csv  decisoes.csv  divergencias.csv ...
└── src/       config.py  triagem.py  amostra*.py  rotular.py  kappa.py  aplicar_decisoes.py  juntar_extra.py  particao.py
```

As fotos do cliente **não** estão no repositório.
