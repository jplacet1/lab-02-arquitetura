# Uso de IA generativa neste laboratório

Grupo GridVision (G4). Nesta disciplina somos João Pedro e Henrique Bouwman.

**Ferramenta:** Claude (Claude Code, modelo Claude Sonnet 5.5), usado pelo grupo (João Pedro e Henrique, trabalhando juntos) em sessões de trabalho até 08/10/2026. A sessão rodou na máquina do João, e o Claude leu e executou código nela. Os pedidos foram feitos por nós dois em conjunto. Os dados do cliente (fotos e CSVs originais) ficaram só no computador dele, e nenhuma foto está neste repositório.

## O que a IA fez e o que nós fizemos

| Etapa | O que o Claude fez | O que nós fizemos |
|---|---|---|
| Passo a passo | O João pediu um passo a passo do laboratório a partir do enunciado e do guia. | Conferimos com o enunciado e decidimos a ordem de trabalho. |
| Amostra e esquema v1 | Escreveu `src/amostra.py` (amostra de 300 fotos) e uma primeira versão do esquema de classes. | Revisamos as classes e sorteamos as fotos comuns entre nós dois. |
| Interface de rotulagem | Escreveu `src/rotular.py` (teclado, salva CSV, volta). Escreveu `src/kappa.py`. | **Rotulamos todas as fotos à mão, cada um sozinho e às cegas.** O Claude não rotulou nenhuma foto. |
| Kappa v1 e divergências | Escreveu `revisar.py` e `aplicar_decisoes.py` para registrar as decisões. | O kappa v1 (50 fotos comuns) mostrou classes abaixo de 0,6 (cena=nao_medidor 0,000; reflexo 0,337; enquadramento 0,389; display_apagado 0,370). Decidimos juntos as 29 divergências. |
| Esquema v2 e kappa v2 | Escreveu `src/amostra_v2.py` e registrou o resultado em `esquema.md`. | Reescrevemos as regras de cena, reflexo, enquadramento e display apagado. Rotulamos de novo, às cegas, 30 fotos novas. O kappa v2 ficou ≥ 0,71 em todas as classes. `cena_ocorrencia` e `nao_medidor` têm 1 caso cada, então o kappa 1,0 delas não prova nada. |
| Partição por lote | Escreveu `src/particao.py`, que prova 0 vazamento. | Escolhemos treino 05-20 e 05-21, validação 05-22 e teste 07-03. |
| Modelo e notebook | Escreveu `src/triagem.py` (MobileNetV3-Small, duas cabeças) e `lab02.ipynb` (sanidade, baselines, calibração, cobertura × risco, ajuste fino, curva de dados). | Executamos o notebook e lemos os resultados. |
| Mais rótulos | Escreveu `src/amostra_extra.py` e `src/juntar_extra.py` (200 fotos extras). | Rotulamos 100 fotos cada um. A base chegou a 500 fotos. |
| Documentos | Redigiu `ARQUITETURA.md` (seguindo o guia) e `README.md` com os números do notebook. A latência foi medida pelo Claude em uma CPU de desenvolvimento. | Revisamos o texto e as decisões de projeto. |

## O que descartamos ou corrigimos

- **Grupo errado.** A primeira versão partiu de que éramos o grupo Korvian (tarefas K1–K4). O João corrigiu: o GridVision não tem parte específica no enunciado. Os nomes foram trocados e nenhuma tarefa K foi feita.
- **Três rotuladores.** O Claude dividiu as 200 fotos extras em 3 pessoas. A Alana não cursa a disciplina. Refeito para 2 (100 fotos cada).
- **Meta provisória de 80% / 5%.** O Claude a pôs sem base no material do cliente. Ficou a meta de cobertura ≥ 70% com risco ≤ 5%, que é uma hipótese do grupo a validar com a Neoenergia.
- **Kappa 1,0 como prova.** Não usamos o kappa de `cena_ocorrencia` e `nao_medidor` como evidência: são 1 caso cada.
- **Ajuste fino como padrão.** Medimos e não trouxe ganho consistente com poucas fotos, e custa mais CPU. Ficou como experimento.
- **Afirmações sem medida.** Onde o Claude escreveu algo que não medimos (licença dos pesos do ImageNet, volume real, ResNet-18 não treinada), marcamos como hipótese ou "a verificar".
- **Resultado que não bate com a meta.** A meta 70/5 não cabe com o modelo atual. Está escrito assim no `README.md`, sem ajuste para parecer melhor.
- **Divisão por medidor do SR1.** O SR1 propõe 70/15/15 por medidor. O enunciado exige partição por lote, então seguimos o enunciado.

## O que não foi feito pela IA

- Os rótulos das fotos.
- As decisões das 29 divergências do kappa v1.
- A escolha de aceitar ou recusar o que o Claude propôs, listada acima.

## Outros usos

Não usamos nenhuma outra ferramenta de IA generativa neste laboratório. (Henrique: se você usou outra ferramenta por conta própria, acrescente aqui. Se não, apague este aviso.)

## Declaração

Cada integrante é capaz de explicar qualquer linha do código entregue.
