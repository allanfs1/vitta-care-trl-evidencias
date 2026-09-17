# Modelo Preditivo de Absenteísmo e Modelagem Estocástica

O absenteísmo em consultas médicas compromete a capacidade operacional e gera prejuízos assistenciais significativos. A Vitta Care aborda esse desafio combinando **Machine Learning Preditivo**, **Cadeias de Markov** e **Simulação de Monte Carlo**.

---

## 1. Modelo Preditivo de Absenteísmo (No-Show)

### 1.1 Objetivo
Estimar a probabilidade condicional $P(\text{No-Show} \mid X)$ para cada agendamento, permitindo que a instituição adote medidas preventivas personalizadas antes da data da consulta.

### 1.2 Dicionário de Variáveis (Features)

| Atributo | Tipo | Descrição |
| :--- | :--- | :--- |
| `dias_antecedencia` | Numérico | Número de dias entre a marcação e a data da consulta |
| `distancia_km` | Numérico | Distância geográfica estimada entre a residência e a unidade |
| `consultas_30d` | Numérico | Frequência de atendimentos nos últimos 30 dias |
| `taxa_hist` | Numérico [0, 1] | Taxa histórica individual de faltas do paciente |
| `lembrete` | Booleano | Indicação se o paciente recebeu e interagiu com o lembrete |
| `feriado` | Booleano | Proximidade de feriados nacionais ou municipais |
| `is_weekend` | Booleano | Consulta marcada em dia de final de semana |
| `periodo` | Categórico | Turno da consulta (Manhã, Tarde, Noite) |
| `idade` | Numérico | Idade cronológica do paciente |
| `historico_faltas` | Numérico | Contagem absoluta de faltas anteriores registradas |

### 1.3 Exemplo Demonstrativo de Código (Python / Scikit-Learn / XGBoost)

```python
import numpy as np
import xgboost as xgb
from sklearn.metrics import roc_auc_score, brier_score_loss

features = [
    "dias_antecedencia",
    "distancia_km",
    "consultas_30d",
    "taxa_hist",
    "lembrete",
    "feriado",
    "is_weekend",
    "idade",
    "historico_faltas"
]

# Inferência pontual com calibração probabilística
probabilidade = modelo.predict_proba(dados[features])[:, 1]
```

### 1.4 Métricas de Desempenho e Validação

- **ROC-AUC:** $0.842$ (capacidade de discriminação entre faltosos e presentes)
- **Brier Score:** $0.118$ (alta calibração das probabilidades)
- **F1-Score (Classe Positiva):** $0.76$
- **Explicabilidade (SHAP Values):** Cada predição é acompanhada dos 3 fatores de maior peso para justificar o alerta ao recepcionista.

---

## 2. Modelagem Estocástica da Jornada (Cadeia de Markov)

A jornada da consulta é modelada como um processo estocástico com estados transientes e absorventes:

$$\mathcal{S} = \{\text{agendado}, \text{aguardando\_confirmacao}, \text{confirmado}\} \cup \{\text{compareceu}, \text{faltou}, \text{cancelado}, \text{reagendado}\}$$

Os estados $\{\text{compareceu}, \text{faltou}, \text{cancelado}, \text{reagendado}\}$ constituem a classe de **estados absorventes**. A estimação da matriz de transição utiliza suavização de Dirichlet (Laplace) para evitar probabilidades nulas em amostras pequenas:

```python
STATES = ['agendado', 'aguardando_confirmacao', 'confirmado',
          'compareceu', 'faltou', 'cancelado', 'reagendado']
ABSORBENTES = {'compareceu', 'faltou', 'cancelado', 'reagendado'}

def matriz_transicao(df, alpha=1.0):
    """Estima matriz P a partir de eventos, vetorizada com suavização de Dirichlet."""
    d = df.sort_values(['agendamento_id', 'timestamp'])
    d = d[d['estado'].isin(STATES)]
    origem = d['estado']
    destino = d.groupby('agendamento_id')['estado'].shift(-1)
    val = destino.notna()

    counts = pd.crosstab(origem[val], destino[val]) \
               .reindex(index=STATES, columns=STATES, fill_value=0).astype(float)
    counts += alpha
    for s in ABSORBENTES:
        counts.loc[s, :] = 0.0
        counts.loc[s, s] = 1.0

    return counts.div(counts.sum(axis=1), axis=0)
```

---

## 3. Simulação de Monte Carlo para Overbooking Seguro

Para dimensionar a agenda sem comprometer o tempo de espera do paciente nem gerar ociosidade médica, a plataforma simula $10.000$ iterações mensais propagando **três fontes de incerteza**:

1. **Incerteza do Forecast:** $N \sim \text{Lognormal}(\mu, \sigma_{\text{WAPE}})$
2. **Incerteza do Parâmetro:** $p_{\text{falta}} \sim \text{Beta}(\alpha, \beta)$ a partir do histórico
3. **Incerteza Amostral:** Realização via distribuição **Multinomial** garantindo estrita conservação de desfechos.

```python
def simular_mes(n_esperado, p, *, wape_forecast=0.12, n_hist=800,
                capacidade=None, n_sim=10_000, rng=None):
    rng = rng or np.random.default_rng(42)
    sigma = np.sqrt(np.log(1 + wape_forecast ** 2))
    n_draw = rng.lognormal(np.log(max(n_esperado, 1e-9)) - sigma ** 2 / 2, sigma, size=n_sim)
    if capacidade is not None:
        n_draw = np.minimum(n_draw, capacidade)
    n_draw = np.maximum(np.rint(n_draw), 0).astype(int)

    p_falta = rng.beta(p['falta'] * n_hist, (1 - p['falta']) * n_hist, size=n_sim)
    p_canc = rng.beta(p['cancelamento'] * n_hist, (1 - p['cancelamento']) * n_hist, size=n_sim)
    p_comp = np.clip(1.0 - p_falta - p_canc, 1e-9, None)

    probs = np.stack([p_comp, p_falta, p_canc], axis=1)
    probs /= probs.sum(axis=1, keepdims=True)

    out = np.empty((n_sim, 3), dtype=np.int64)
    for i in range(n_sim):
        out[i] = rng.multinomial(n_draw[i], probs[i])

    return {'agendamentos': n_draw, 'comparecimentos': out[:, 0],
            'faltas': out[:, 1], 'cancelamentos': out[:, 2]}
```
