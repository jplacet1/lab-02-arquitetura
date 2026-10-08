# Ficha de arquitetura — GridVision (G4)

Cliente: Neoenergia Pernambuco. Integrantes desta entrega: João Pedro Lins e Henrique Bouwman.
Os números vêm de `lab02.ipynb` (500 fotos rotuladas, partição por lote, 3 sementes). Onde algo é estimativa ou hipótese, está escrito.

## 1. Decisão apoiada

- **Decisão:** para cada registro de leitura do lote do dia, a foto está boa para sustentar a leitura (**aceita**), não está (**reprovada**) ou precisa de um humano (**revisar**).
- **Unidade de análise:** uma foto (cada foto é de uma leitura; uma leitura pode ter mais de uma foto, sufixo `_000`, `_001`).
- **Quem age:** o analista da equipe de fiscalização de leitura. A IA apoia; toda reprovação vem com motivo e o analista pode discordar (premissas do kickoff).
- **Erro mais caro:** aceitar como confiável uma foto ruim ou uma leitura errada, porque o erro chega à fatura do cliente. Mandar para revisão uma foto boa custa menos (SR1). Por isso o sistema pode **recusar** (seção 9).
- **Onde roda:** sobre um lote exportado, sem integrar aos sistemas internos da Neoenergia (escopo do MVP). Treino no Colab com GPU. Inferência em CPU é a hipótese de trabalho; o computador do analista não foi confirmado com o cliente.
- **Escopo desta ficha:** o único bloco profundo treinável hoje é a **triagem de cena e qualidade**. O detector (medidor, ID, visor) e o reconhecedor de dígitos dependem de caixas e transcrições que não existem (seção 14).

## 2. Sub-tarefas

| Sub-tarefa | Aprendida ou regra? | Tipo | Saída | Ativação | Perda | Rótulo |
|---|---|---|---|---|---|---|
| Cena: digital, ciclométrico, ocorrência, não é medidor | **Aprendida** (este lab) | Classificação exclusiva, 4 classes | 4 logits | softmax | entropia cruzada | `cena` (500 fotos) |
| Defeitos: reflexo, fora de foco, tampa suja, enquadramento, display apagado | **Aprendida** (este lab) | Multirrótulo, 5 sigmoides | 5 logits | sigmoide | BCE com logits | 5 colunas 0/1 (500 fotos) |
| Foto existe e é nítida (Laplaciano, brilho) | **Regra** no SR1; testada contra a aprendida | Limiar | número | n/a | n/a | n/a |
| Localizar medidor, ID e visor | Aprendida (**não treinada**) | Detecção | caixas + confiança | n/a | n/a | caixas: **0 anotadas** |
| Ler ID e leitura | Aprendida (**não treinada**) | Reconhecimento de sequência | dígitos | n/a | CTC (provável) | transcrição: só no CSV, sem recorte |
| Comparar leitura lida × informada | **Regra** | Igualdade após normalizar zeros à esquerda, "/" e letras | confere/diverge | n/a | n/a | n/a |
| Parear foto e registro | **Regra** | Chave de nome de arquivo | registro ou órfã | n/a | n/a | n/a |
| Veredito aceita/reprova/revisar | **Regra** sobre a confiança | Limiar escolhido na validação | 3 estados | n/a | n/a | n/a |

Comparar dois números não é tarefa de rede, e o pareamento também não. A nitidez fica em aberto como regra: testamos se a rede aprendida bate a heurística (seção 12) e ela bate (F1 da cena 0,550 contra 0,281; AP dos defeitos 0,509 contra 0,360, validação).

## 3. Pipeline

```
lote do dia (CSV + fotos)
   │
   ▼
[1] Triagem (rede, este lab) ── recusa se confiança < τ ──────────► REVISAR
   │ cena ∈ {digital, ciclométrico}, sem defeito grave
   ▼
[2] Localizar medidor/ID/visor (detector, futuro)  ──► recorte
   ▼
[3] Ler ID e leitura (reconhecedor, futuro)
   ▼
[4] Comparar com o registro (regra) ──► CONFERE / DIVERGE / REVISAR
```

**Taxas por estágio e produto.** Só o estágio 1 foi medido por nós. Os demais vêm de outra fonte ou são hipótese, e estão marcados.

| Estágio | Taxa | Origem |
|---|---|---|
| 1 Triagem (cena certa entre as fotos respondidas, cobertura 0,70) | 0,90 (risco 0,102 na validação; 0,061 no teste com cobertura 0,66) | **medida**, `lab02.ipynb` E2 |
| 2 Localização | sem valor | **não medida**; sem caixas anotadas |
| 3 Leitura exata do visor | 0,20 | **medida pelo SR1** (PaddleOCR, 100 fotos nítidas, foto inteira, sem recorte) |
| 4 Comparação | ~1,0 | regra; depende de normalizar os dois lados |

- **Cenário atual** (OCR pronto, sem detector): 0,90 × 0,20 ≈ **0,18** de leituras certas de ponta a ponta nas fotos respondidas. Não serve ao cliente.
- **Cenário-alvo** (hipótese, não medida): detector 0,90 e reconhecedor próprio 0,80 dão 0,90 × 0,90 × 0,80 ≈ **0,65**. Cada estágio custa multiplicativamente, e o reconhecedor domina a conta.
- Fotos recusadas em qualquer estágio vão para o analista; esse ramo não entra no produto acima.

Escolhemos **estágios** e não ponta a ponta porque: (a) não existe rótulo de leitura final por foto (só o CSV, com 14,2% de leituras de 1 a 3 dígitos e 347 zeros, segundo o SR1); (b) cada estágio é medido e recusa sozinho; (c) o analista exige o motivo da reprovação, que um modelo ponta a ponta não dá.

## 4. Contrato de entrada (por modelo)

| Modelo | Tamanho (A×L) | Proporção | Normalização | Canais |
|---|---|---|---|---|
| Triagem (este lab) | 480×360, nativo | 4:3 em retrato, sem recorte nem distorção | média/desvio do ImageNet | 3 (RGB) |
| Detector (futuro) | a definir | — | — | 3 |
| Reconhecedor (futuro) | recorte do visor, p. ex. 32×128 (valor do esqueleto, não testado) | — | — | 1 |

Todas as 12.340 fotos têm 360×480 px (SR1), então o contrato nativo é exato. **Não medimos** a triagem a 224 px; só a latência (seção 13). Reduzir a foto antes de ler dígitos é anti-padrão: depois do recorte sobram poucas dezenas de pixels de altura por dígito.

## 5. Espinha dorsal

- **Escolhida:** MobileNetV3-Small pré-treinada no ImageNet. 932.201 parâmetros, 7 a 10 ms por foto em CPU (seção 13).
- **Descartada: heurística V0** (Laplaciano, brilho, histograma de cinza + regressão logística). Mesma partição e métrica: F1 da cena 0,281 contra 0,550 e AP dos defeitos 0,360 contra 0,509 na validação.
- **Descartada: ResNet-18** (≈11,7 M de parâmetros, ~12× mais). **Não foi treinada por nós.** O motivo é de custo: com 250 fotos de treino não há dados para sustentar essa capacidade (seção 8), e a implantação é CPU. É uma decisão de orçamento, não de resultado.
- **Descartada: ajuste fino completo como padrão** (seção 8): custa ~140 s por semente na CPU e não trouxe ganho consistente.

## 6. Cabeças

| Cabeça | Nº saídas | Ativação | Perda | Classes exclusivas? Por quê |
|---|---|---|---|---|
| Cena | 4 | softmax (dentro da perda) | `CrossEntropyLoss` | **Sim.** Uma foto recebe uma cena só, pela ordem de decisão do esquema. A fronteira digital × ocorrência é a mais difícil (kappa v1 de 0,459) |
| Qualidade | 5 | sigmoide (dentro da perda) | `BCEWithLogitsLoss` | **Não.** 162 das 500 fotos têm 2 ou mais defeitos; `reflexo` + `fora_de_foco` coocorrem em 66 fotos e `fora_de_foco` + `tampa_suja` em 81 |

A rede devolve logits. Nenhuma softmax ou sigmoide é aplicada antes das perdas. Defeitos só fazem sentido quando há medidor identificável: `cena_ocorrencia` e `nao_medidor` não recebem defeitos (regra v2, conferida: 0 casos). Uma espinha dorsal serve às duas cabeças (multitarefa); não comparamos com dois modelos separados.

## 7. Desbalanceamento

Distribuição medida nas 500 fotos rotuladas:

| Cena | Fotos | | Defeito | Fotos | % |
|---|---|---|---|---|---|
| digital | 349 | | fora_de_foco | 200 | 40% |
| ciclometrico | 70 | | reflexo | 132 | 26% |
| cena_ocorrencia | 57 | | tampa_suja | 102 | 20% |
| nao_medidor | 24 | | enquadramento | 97 | 19% |
| | | | display_apagado | 17 | 3% |

- **Técnica atual:** nenhuma ponderação na perda. Avaliamos com **F1 macro** na cena e **AP médio** nos defeitos, para a classe rara não ficar escondida atrás da acurácia. A regressão logística usa `class_weight="balanced"`.
- **Lacuna:** `pos_weight` na BCE e perda focal **não foram testados**. É o próximo passo para `display_apagado` e `nao_medidor`.
- **Limite honesto:** `display_apagado` tem 5 positivos na validação e 6 no teste. O AP dele (0,047) é do tamanho da prevalência (5/125 = 0,04): não é melhor que o acaso. Não tiramos conclusão sobre essa classe.

## 8. Capacidade × rótulos

- **Rótulos:** 500 fotos (250 treino, 125 validação, 125 teste), uma por leitura, estratificadas pelos 4 lotes.
- **Estratégia padrão:** transferência com **extrator congelado**; só as cabeças treinam: **5.193 parâmetros treináveis de 932.201** (0,6%).
- **Ajuste fino testado** (12 épocas, 3 sementes, `lr` 1e-4 no extrator e 1e-3 nas cabeças, agenda fixa): ficou dentro do ruído. Cena F1 0,592 ± 0,016 contra 0,550 na validação, mas 0,545 ± 0,056 contra 0,602 no teste; AP dos defeitos 0,524 contra 0,509 e 0,609 contra 0,607. Deixa o modelo supraconfiante (temperatura ~1,35–1,39).
- **Baseline não profunda forte:** regressão logística sobre as mesmas características congeladas bate a cabeça treinada na cena (F1 0,647 contra 0,550 na validação; 0,657 contra 0,602 no teste) e perde nos defeitos (AP 0,498 contra 0,509; 0,561 contra 0,607). Com poucos rótulos, uma cabeça linear simples é concorrente séria.
- **Curva de dados** (validação, 25/50/75/100% de 250 fotos): F1 da cena 0,376 → 0,467 → 0,530 → 0,546; risco na cobertura 0,70: 0,174 → 0,159 → 0,125 → 0,098. Ainda desce. Rotular mais é o caminho; a extrapolação linear (não medida) aponta ~100 fotos de treino a mais para risco ≤ 0,05.

## 9. Confiança e recusa

- **Regra de decisão:** a rede responde quando a confiança máxima da cena é ≥ τ; abaixo disso devolve **revisar**. O τ é fixado **na validação** e aplicado uma vez ao teste.
- **Calibração:** *temperature scaling* ajustado na validação, T ≈ 1,04. O modelo já sai quase calibrado: ECE da validação 0,059 → 0,044 e do teste 0,037 → 0,039 (média de 3 sementes), da ordem do ruído com 125 fotos e 10 faixas. Defeitos não foram calibrados.
- **Meta do negócio** (hipótese do grupo, a validar com a Neoenergia): **cobertura ≥ 70% com risco ≤ 5%**. O SR1 deixa em aberto a taxa que o cliente aceita para dispensar a revisão.

| Método | Cobertura val | Risco val | Cobertura teste | Risco teste | Maior cobertura com risco ≤ 5% (val) |
|---|---|---|---|---|---|
| Profundo calibrado | 0,70 | 0,102 | 0,66 | 0,061 | 0,50 |
| Reg. logística sobre características profundas | 0,70 | 0,114 | 0,77 | 0,156 | 0,42 |
| V0 | 0,70 | 0,591 | 0,74 | 0,516 | 0,01 |

- **A meta não cabe na curva.** Para risco ≤ 5% a cobertura cai para ~50%; para cobertura de 70% o risco é ~10%. Risco aqui é o erro da **cena** entre as fotos respondidas. A decisão completa (que também usa os defeitos) não foi avaliada.
- **Custo da escolha:** subir o risco aceito empurra erros para a fatura; baixar a cobertura empurra trabalho para o analista. A escolha final é do negócio.

## 10. Aumento de dados

| Transformação | Modelo | Muda o rótulo? |
|---|---|---|
| Rotação ±5°, translação ≤ 5%, escala 0,9–1,1 | triagem, **só no ajuste fino** | Pode mudar `enquadramento` (corte/distância); risco aceito, não medido |
| Brilho e contraste ±20% | triagem, só no ajuste fino | Pouco; foto escura é cena, não defeito próprio |
| Desfoque sintético | **proibido** | Cria `fora_de_foco` falso (é o que a triagem detecta; SR1) |
| Espelhamento horizontal | **proibido** para leitura | Inverte dígitos |
| Defeitos sintéticos (rótulo fraco) | **não adotado** | Não validado contra fotos reais |

A extração de características (o padrão) **não usa** aumento.

## 11. Partição

- **Por lote**, nunca por foto: treino = 2026-05-20 e 2026-05-21; validação = 2026-05-22; teste = 2026-07-03 (seis semanas depois, serve de teste temporal).
- **Prova numérica** (`src/particao.py`, `rotulos/particao.csv`):

| Universo | Chave | Valores distintos | Em 2+ conjuntos |
|---|---|---|---|
| 500 fotos rotuladas | id de leitura | 460 | 0 |
| 500 fotos rotuladas | número do medidor | 510 | 0 |
| Base inteira (12.340 fotos) | id de leitura | 11.474 | 0 |
| Base inteira | número do medidor | 12.609 | 0 |

- **Diferença para o SR1:** o SR1 propõe dividir por medidor (70/15/15 nos lotes de maio). Doze medidores aparecem em mais de um lote; aqui os dois lotes de maio de treino ficam juntos e os demais conjuntos não repetem nenhum medidor (0 em 2+ conjuntos). Sem sorteio por medidor, a validação é um lote inteiro (rotulamos 125 fotos dele), o que evita vazamento entre dias e dá pouca folga estatística.
- **Limites:** 40 das 500 fotos não têm linha no CSV da base (órfãs); a partição vale pelo lote, mas não há chave para conferir nelas. A amostra tem uma foto por leitura (460 leituras distintas).

## 12. Sanidade

- **Formas** (entrada 1×3×480×360): extrator 480×360 → 15×12×576, *pool* global → 576, cabeças 4 e 5 (`lab02.ipynb` B1).
- **Perda inicial** com pesos aleatórios, 64 fotos reais, 3 sementes: CE 1,380–1,384 (esperado ln 4 = 1,386); BCE 0,689–0,697 (esperado ln 2 = 0,693).
- **Sobreajuste de 16 fotos reais:** perda 2,06 → 0,0018 em 80 passos; acerto em modo `eval` 15/16 (a *BatchNorm* com lote de 16 usa estatística diferente no `eval`; explicação provável, não testada).
- **Baselines:** V0 e regressão logística, mesma partição e métricas (seções 5 e 8). Três sementes, média ± desvio no notebook.

## 13. Implantação

- **Volume:** de 2.992 a 3.185 fotos por extração diária (4 extrações: 12.340 fotos). **Não medimos o volume real mensal ou diário com o cliente**; é pendência.
- **Latência da triagem** (CPU de desenvolvimento AMD, 12 núcleos, lote de 1, só rede, sem decodificar o JPEG):

| Entrada | 1 thread p50 / p95 | 4 threads p50 / p95 |
|---|---|---|
| 480×360 (nativo) | 8,9 / 9,5 ms | 7,2 / 9,6 ms |
| 224×224 | 4,8 / 5,0 ms | 5,0 / 6,2 ms |

  Um lote de ~3.200 fotos leva ~30 s de rede a 9 ms por foto. O orçamento de ponta a ponta dependerá do detector e do reconhecedor, que ainda não existem; a CPU do analista pode ser mais lenta que a nossa.
- **Exportação:** ONNX não feito. **Licenças:** torchvision usa BSD-3; os pesos pré-treinados no ImageNet têm termos próprios do conjunto de dados, **a verificar** antes de entregar ao cliente. Para o detector futuro, a licença AGPL-3.0 do YOLO da Ultralytics é incompatível com um produto entregue; avaliaremos alternativas permissivas (SSDlite ou Faster R-CNN do `torchvision`).

## 14. O que decidimos não fazer

| Não fizemos | Por quê |
|---|---|
| Treinar o detector de medidor, ID e visor | Não há nenhuma caixa anotada. O piloto de anotação é o próximo passo do SR1 |
| Treinar o reconhecedor de dígitos (CTC) | Sem recortes anotados; o OCR pronto lê só 20% dos visores sem recorte |
| Arquitetura ponta a ponta (foto → leitura) | Sem rótulo final por foto e sem motivo da reprovação (seção 3) |
| Ajuste fino como padrão | Sem ganho consistente com 250 fotos, custo de CPU maior (seção 8) |
| `pos_weight` e perda focal | Não testados; próximo passo para `display_apagado` e `nao_medidor` |
| Calibrar os defeitos | Só a cena foi calibrada; defeitos têm poucos positivos |
| Avaliar a decisão completa aceita/reprova/revisar | Avaliamos a cena entre as fotos respondidas; falta incluir os defeitos |
| Testar a triagem a 224 px | Medimos só a latência; a métrica a 224 fica pendente |
| Partição por medidor do SR1 | O enunciado exige por lote; o teste temporal do SR1 foi mantido |
| ResNet-18 e outras espinhas | Orçamento de dados e CPU (seção 5); não treinadas |
