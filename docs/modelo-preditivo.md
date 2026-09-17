# Modelagem Estocástica de Absenteísmo

## 1. Simulação de Monte Carlo com Cópula Gaussiana

### 1.1 Premissas de Modelagem

Quatro decisões sustentam o motor de simulação (`monte_carlo_engine.dart`, ~776 linhas):

1. **Faltas do mesmo dia não são independentes.** Fatores sistêmicos (clima, greve, feriados) empurram todos os desfechos na mesma direção. A dependência é introduzida por cópula gaussiana de um fator, preservando as probabilidades marginais exatamente.

2. **Três estados, não dois.** Cancelar com antecedência libera a vaga; faltar não libera nada. Tratá-los como equivalentes superestima a capacidade recuperável.

3. **Overbooking é decidido por slot (médico × hora), não por dia.** Uma falta às 16h não gera capacidade disponível às 9h.

4. **A fila vem antes do overbooking.** Vagas liberadas por cancelamento são preenchidas sem criar espera; encaixes especulativos criam.

### 1.2 Modelo de Risco Categórico

A classe `ModeloRisco` converte o nível de risco categórico de cada agendamento em probabilidades marginais:

| Nível de risco | $p(\text{falta})$ | $p(\text{cancel})$ | $p(\text{comparece})$ |
|:---|:---:|:---:|:---:|
| `low` | 0.06 | 0.03 | 0.91 |
| `medium` | 0.15 | 0.06 | 0.79 |
| `high` | 0.32 | 0.10 | 0.58 |

Estas são taxas padrão calibráveis: `MonteCarloCalibracao` as substitui pelas taxas observadas na base real quando a amostra é suficiente ($n \geq 50$, com intervalo de Wilson).

### 1.3 Cópula Gaussiana de Um Fator

Para $n$ consultas do dia, com $Z \sim \mathcal{N}(0,1)$ (fator sistêmico compartilhado) e $\varepsilon_i \sim \mathcal{N}(0,1)$ (componente idiossincrático):

$$X_i = \sqrt{\rho}\,Z + \sqrt{1-\rho}\,\varepsilon_i$$

Limiares na escala latente:
- $z_i^{\text{falta}} = \Phi^{-1}(p_i^{\text{falta}})$
- $z_i^{\text{cancel}} = \Phi^{-1}(p_i^{\text{falta}} + p_i^{\text{cancel}})$

Desfecho:
$$\text{desfecho}_i = \begin{cases}
\texttt{falta} & X_i \leq z_i^{\text{falta}} \\
\texttt{cancel} & z_i^{\text{falta}} < X_i \leq z_i^{\text{cancel}} \\
\texttt{comparece} & X_i > z_i^{\text{cancel}}
\end{cases}$$

**Propriedade fundamental:** as marginais são preservadas exatamente. Apenas a estrutura de dependência (variância da contagem total) muda com $\rho$.

### 1.4 Inversa da Normal (Acklam)

A implementação usa o algoritmo de Acklam para $\Phi^{-1}(p)$ com precisão $\sim 10^{-9}$, evitando dependências numéricas externas.

### 1.5 Intervenção via Razão de Chances

$$p_{\text{pós}} = \frac{p \cdot \omega}{(1-p) + p\cdot\omega}$$

onde $\omega < 1$ reduz a chance de falta. Parte da massa migrada da falta para o comparecimento transita como cancelamento com aviso — exatamente o desfecho que a intervenção tenta produzir.

### 1.6 Configuração da Simulação

| Parâmetro | Padrão | Justificativa |
|:---|:---:|:---|
| `nRuns` | 20.000 | Sob $\rho = 0{,}03$, o erro de MC do P95 estabiliza aqui; 50.000 gasta 2,5× mais para mover número estacionário |
| `seed` | 42 | Determinismo: mesma entrada → mesmo resultado |
| `rho` | 0.03 | Mediana observada; reestimar semanalmente |
| `pFaltaEncaixe` | 0.15 | Encaixes são pacientes chamados de última hora — adesão diferente da média |

---

## 2. Cadeia de Markov Absorvente

### 2.1 Espaço de Estados

7 estados: 3 transitórios + 4 absorventes. Reagendado é estado próprio (não cancelamento).

### 2.2 Estimação Dirichlet

Pseudo-contagem $\alpha = 1$ (Laplace): garante que toda linha seja distribuição válida. Estados absorventes recebem auto-laço puro ($P_{s,s} = 1$) sem suavização.

### 2.3 Não-Homogeneidade Temporal

Matrizes independentes por faixa de dias até a consulta. Sem isso, o modelo afirma que a chance de confirmar é a mesma faltando 30 dias e faltando 1 — empiricamente falso.

### 2.4 Shrinkage Hierárquico

$$\hat{P} = w P_{\text{segmento}} + (1-w) P_{\text{global}}, \qquad w = \frac{n}{n+k}$$

Resolve partida a frio: $k = 50$ observações dá peso 50/50.

### 2.5 Probabilidades de Absorção

Iteração da distribuição até massa transitória $< 10^{-12}$. Teto de 2.000 iterações como salvaguarda contra matrizes malformadas. Massa residual é atribuída a `cancelado` para manter a distribuição fechada.
