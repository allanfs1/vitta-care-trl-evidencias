# Pipeline de Inteligência Artificial — Predição de Absenteísmo

## Visão Geral do Fluxo End-to-End

O pipeline de IA da Vitta Care opera em **três estágios** interconectados: (1) treinamento e avaliação na nuvem (Azure ML), (2) inferência via endpoint REST e (3) consumo e simulação no frontend Flutter. O diagrama abaixo mostra o fluxo completo de dados:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                        AZURE ML WORKSPACE                                   │
│                                                                              │
│  ┌─────────────┐   ┌───────────────┐   ┌──────────────┐   ┌──────────────┐  │
│  │  Dataset     │──▶│ Pré-processo  │──▶│  Treinamento │──▶│  Avaliação   │  │
│  │  (Firestore  │   │  (Pipeline    │   │  (4 modelos  │   │  (14 gráf.   │  │
│  │   histórico) │   │   sklearn)    │   │   + CV + AUC)│   │   + SHAP)    │  │
│  └─────────────┘   └───────────────┘   └──────┬───────┘   └──────────────┘  │
│                                                │                             │
│                                     ┌──────────▼───────────┐                 │
│                                     │  model.pkl           │                 │
│                                     │  (modelo + pipeline  │                 │
│                                     │   + threshold ótimo) │                 │
│                                     └──────────┬───────────┘                 │
│                                                │                             │
│                                     ┌──────────▼───────────┐                 │
│                                     │  ACI Endpoint REST   │                 │
│                                     │  predict_proba()     │                 │
│                                     └──────────┬───────────┘                 │
└────────────────────────────────────────────────┼─────────────────────────────┘
                                                 │
                              ┌──────────────────▼──────────────────┐
                              │     CLOUD FUNCTION / PIPELINE       │
                              │     Denormaliza predição no          │
                              │     tb_agendamentos + dashboard_risco│
                              └──────────────────┬──────────────────┘
                                                 │
┌────────────────────────────────────────────────▼─────────────────────────────┐
│                         FLUTTER APP (FRONTEND)                               │
│                                                                              │
│  appointment_service.dart                                                    │
│  ├── Lê probabilidade_falta de tb_agendamentos                              │
│  ├── Enriquece com dashboard_risco (riscoPercent)                            │
│  └── Converte para RiskLevel (low/medium/high)                               │
│                                                                              │
│  Monte Carlo Engine                                                          │
│  ├── pFaltaPrevista presente? → usa diretamente como marginal                │
│  └── ausente? → mapeia RiskLevel → ModeloRisco (taxas padrão/calibradas)     │
│                                                                              │
│  Markov Engine                                                               │
│  └── Projeta absorção em 12 meses com/sem intervenção                        │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Dados de Entrada — Feature Engineering

### 1.1 Dataset

O dataset `consultas_historico_atualizado_mes_seguinte.csv` contém o histórico de agendamentos com a variável alvo binária:

| Campo | Semântica |
|:---|:---|
| `confirmado` | **Variável alvo.** `1` = paciente compareceu, `0` = faltou/cancelou |

### 1.2 Features Selecionadas (18 variáveis)

As features são divididas em três grupos com tratamento distinto no pipeline de pré-processamento:

**Numéricas contínuas** (5) — StandardScaler + mediana para missing:

| Feature | Tipo | Descrição |
|:---|:---|:---|
| `dias_antecedencia` | int | Dias entre agendamento e consulta |
| `distancia_km` | float | Distância estimada paciente → clínica |
| `renda_media_bairro` | float | Proxy socioeconômico por CEP |
| `numero_consultas_ult_30d` | int | Frequência recente do paciente |
| `taxa_historica` | float | Taxa histórica de comparecimento do paciente |

**Binárias** (4) — Imputação por moda:

| Feature | Descrição |
|:---|:---|
| `lembrete_enviado` | Se o paciente recebeu lembrete para esta consulta |
| `feriado_proximo` | Proximidade de feriado (fator sistêmico) |
| `is_weekend` | Consulta em final de semana |
| `lembrete_hist` | Se o paciente já recebeu lembretes anteriormente |

**Dummies categóricas** (9) — Imputação por moda:

| Feature | Descrição |
|:---|:---|
| `dist_perto`, `dist_medio`, `dist_longe` | Faixa de distância discretizada |
| `renda_baixo`, `renda_medio`, `renda_alto`, `renda_muito_alto` | Faixa de renda discretizada |
| `periodo_Manhã`, `periodo_Tarde` | Período do dia |

### 1.3 Pipeline de Pré-processamento

O pipeline é construído com `ColumnTransformer` do scikit-learn, garantindo que cada tipo de variável receba o tratamento correto:

```python
preprocessor = ColumnTransformer(
    transformers=[
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ]), num_cols),
        ('bin', Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent'))
        ]), bin_cols),
        ('dummy', Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent'))
        ]), dummy_cols)
    ]
)

feature_engineering = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('feature_selector', SelectKBest(score_func=f_classif, k='all'))
])
```

**Decisão de design:** O `SelectKBest` com `k='all'` inicia retendo todas as features; pode ser reduzido para poda automática por ANOVA F-score sem alterar a interface do pipeline.

---

## 2. Balanceamento de Classes — SMOTE

Se a classe minoritária (`confirmado = 1`) representar menos de 30% da base, aplica-se **SMOTE** (Synthetic Minority Over-sampling Technique):

```python
aplicar_smote = y_train.mean() < 0.3
```

### 2.1 SMOTE Dentro da Validação Cruzada (Sem Vazamento)

O script implementa uma proteção crucial contra **data leakage**: o SMOTE é aplicado **dentro de cada dobra** da validação cruzada usando `imblearn.pipeline.Pipeline`, não sobre o treino inteiro antes da CV:

```python
if SMOTE_DENTRO_DA_CV and aplicar_smote:
    # SMOTE recalculado dentro de cada dobra → AUC de CV honesto
    estimador = ImbPipeline([
        ('smote', SMOTE(random_state=42)),
        ('clf', model)
    ])
    X_cv, y_cv = X_train_preprocessed, y_train  # dados originais
```

**Por que isso importa:** Se o SMOTE fosse aplicado antes da CV, as amostras sintéticas geradas a partir do treino contaminariam a dobra de validação, inflando artificialmente a AUC medida. Com o `ImbPipeline`, cada dobra vê apenas dados reais na validação.

Para o **treino final** (após seleção do modelo), o SMOTE é aplicado sobre todo o conjunto de treino, pois não há mais risco de vazamento — o teste já está separado.

---

## 3. Competição de Modelos — Seleção por AUC-ROC

Quatro algoritmos competem na mesma validação cruzada estratificada (5-fold):

| Modelo | Tratamento de Desbalanceamento | Hiperparâmetros |
|:---|:---|:---|
| **Random Forest** | `class_weight='balanced'` | Padrão do sklearn |
| **Gradient Boosting** | Sem (confia no SMOTE) | Padrão do sklearn |
| **Logistic Regression** | `class_weight='balanced'` | `solver='saga'`, `max_iter=1000` |
| **XGBoost** | `scale_pos_weight = n₀/n₁` | `eval_metric='logloss'` |

### 3.1 Métrica de Seleção

A métrica de seleção é **ROC AUC** (Area Under the Receiver Operating Characteristic Curve). O modelo com maior AUC média na CV de 5 dobras é selecionado:

```python
cv_scores = cross_val_score(
    estimador, X_cv, y_cv,
    cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
    scoring='roc_auc', n_jobs=-1
)
```

**Por que AUC e não acurácia:** Em problemas de classificação desbalanceada (que é o caso do absenteísmo — a maioria dos pacientes comparece), a acurácia é enganosa: um modelo que sempre prevê "compareceu" já tem ~80% de acurácia, mas é operacionalmente inútil. A AUC mede a capacidade de **ranquear** pacientes por risco, independente do threshold.

### 3.2 Scale Pos Weight (XGBoost)

O XGBoost usa `scale_pos_weight` como alternativa ao `class_weight` do sklearn. O valor é calculado como a razão de negativos para positivos:

$$w_{\text{pos}} = \frac{|\{y = 0\}|}{|\{y = 1\}|}$$

Isso dá mais peso aos exemplos da classe minoritária durante o treinamento.

---

## 4. Sistema de Avaliação Completa

Após selecionar o melhor modelo, o módulo `avaliacao.py` executa uma bateria de 20+ métricas e 14+ gráficos de diagnóstico.

### 4.1 Métricas Calculadas (em dois thresholds)

Todas as métricas são calculadas tanto no threshold padrão (`0.5`) quanto no **threshold ótimo por Kolmogorov-Smirnov** (maximiza $\text{TPR} - \text{FPR}$, equivalente ao ponto de Youden $J$):

| Métrica | Fórmula / Significado |
|:---|:---|
| **Accuracy** | $(TP + TN) / (TP + TN + FP + FN)$ |
| **Balanced Accuracy** | $(\text{Sensibilidade} + \text{Especificidade}) / 2$ |
| **Precision** | $TP / (TP + FP)$ — dos que o modelo alertou, quantos de fato faltaram |
| **Recall (Sensibilidade)** | $TP / (TP + FN)$ — dos que faltaram, quantos o modelo detectou |
| **Especificidade** | $TN / (TN + FP)$ — dos que compareceram, quantos o modelo acertou |
| **F1-Score** | $2 \cdot \text{Precision} \cdot \text{Recall} / (\text{Precision} + \text{Recall})$ |
| **ROC AUC** | Área sob a curva ROC |
| **Average Precision** | Área sob a curva Precision-Recall (PR AUC) |
| **Log Loss** | $-\frac{1}{n}\sum[y_i \log(\hat{p}_i) + (1-y_i)\log(1-\hat{p}_i)]$ |
| **Brier Score** | $\frac{1}{n}\sum(y_i - \hat{p}_i)^2$ — calibração das probabilidades |
| **Matthews Correlation** | $\frac{TP \cdot TN - FP \cdot FN}{\sqrt{(TP+FP)(TP+FN)(TN+FP)(TN+FN)}}$ |
| **Cohen's Kappa** | Concordância acima do acaso |
| **KS Statistic** | $\max|\text{CDF}_1(s) - \text{CDF}_0(s)|$ — separação entre distribuições |
| **Gini Coefficient** | $2 \cdot \text{AUC} - 1$ |

### 4.2 Threshold Ótimo (Youden J / KS)

O threshold ótimo é encontrado maximizando a estatística de Kolmogorov-Smirnov:

$$t^* = \arg\max_t \left[ \text{TPR}(t) - \text{FPR}(t) \right]$$

Este é o **ponto de Youden** — o threshold que maximiza simultaneamente sensibilidade e especificidade. É mais adequado que 0.5 para problemas desbalanceados.

O threshold ótimo é **salvo junto com o modelo** no arquivo `model.pkl` e usado pelo endpoint de inferência:

```python
joblib.dump({
    'model': best_model,
    'feature_engineering': feature_engineering,
    'features': all_features,
    'threshold_sugerido': resultado_avaliacao['threshold_otimo'],
    'metricas_teste': metricas,
}, "model.pkl")
```

#### Resultados de Validação Homologados na Base de Teste ($N = 3.236$)

| Métrica | Threshold Padrão ($0.500$) | Threshold Ótimo Youden/KS ($0.370$) |
|:---|:---:|:---:|
| **Acurácia (Accuracy)** | 86.06% | **88.78%** |
| **Sensibilidade (Recall)** | 81.58% (1.320/1.618) | **91.90% (1.487/1.618)** |
| **Especificidade** | **90.54% (1.465/1.618)** | 85.66% (1.386/1.618) |
| **Precisão** | **89.61%** | 86.50% |
| **F1-Score** | 85.41% | **89.12%** |
| **ROC-AUC** | **0.9442** | **0.9442** |
| **Average Precision (PR-AUC)** | **0.9266** | **0.9266** |
| **Estatística KS** | — | **0.7756** (@ score 0.370) |
| **Brier Score** | **0.1070** | **0.1070** |
| **Lift Decil 1** | **1.93x** | **1.93x** |

> **Nota de Decisão Arquitetural:** O threshold de produção recomendado no artefato `model.pkl` é **$0.370$**, pois reduz em **$56.0\%$ as faltas não detectadas** (de 298 para 131), priorizando a capacidade assistencial com um custo operacional mínimo de falsos positivos.


### 4.3 Gráficos de Diagnóstico (14+)

> 📁 **Evidências geradas:** Os 15 gráficos resultantes da validação diagnóstica dos primeiros testes encontram-se arquivados em [`../evidencias/resultados-ia-preditiva/`](../evidencias/resultados-ia-preditiva/).

| # | Gráfico | O que diagnostica |
|:---|:---|:---|
| 01 | Matriz de Confusão (thr=0.5) | Erros absolutos e relativos por classe |
| 01b | Matriz de Confusão (thr=ótimo) | Idem, no ponto de operação sugerido |
| 02 | Curva ROC | Capacidade de discriminação global |
| 03 | Curva Precision-Recall | Desempenho sob desbalanceamento |
| 04 | Curva de Lift | Ganho de eficiência sobre aleatório, por decil |
| 05 | Curva de Ganho (Gain) | % de positivos capturados vs % da população |
| 06 | Curva KS | Separação das distribuições das duas classes |
| 07 | Calibration Curve | Concordância entre P prevista e P observada |
| 08 | Distribuição de Probabilidades | KDE separada por classe real |
| 09 | Histograma de Probabilidades | Distribuição geral + empilhada por classe |
| 10 | Distribuição de Classes | Contagem e proporção (treino/teste/SMOTE) |
| 11 | Importância de Variáveis | `feature_importances_` ou `|coef_|` ou permutação |
| 12 | SHAP Summary (violin) | Impacto direcional de cada feature |
| 13 | SHAP Beeswarm | Distribuição dos valores SHAP individuais |
| 14 | SHAP Bar Plot | `|SHAP|` médio — importância global |

### 4.4 Explicabilidade com SHAP

O SHAP (SHapley Additive exPlanations) é integrado com seleção automática do explainer adequado:

```python
if hasattr(modelo, "feature_importances_"):   # árvores / boosting
    explicador = shap.TreeExplainer(modelo)
elif hasattr(modelo, "coef_"):                  # linear
    explicador = shap.LinearExplainer(modelo, Xdf)
else:                                            # fallback genérico
    explicador = shap.Explainer(lambda d: modelo.predict_proba(d)[:, 1], fundo)
```

Para modelos de árvore (Random Forest, XGBoost, Gradient Boosting), usa-se `TreeExplainer` que calcula os valores SHAP exatos em tempo polinomial, sem aproximação. O resultado é um vetor $\phi_j$ por feature $j$ para cada amostra, interpretado como:

$$\hat{f}(x) = \phi_0 + \sum_{j=1}^{M} \phi_j(x)$$

onde $\phi_0$ é a predição base (média da população) e $\phi_j(x)$ é a contribuição marginal da feature $j$ para a predição daquela amostra específica.

---

## 5. Endpoint de Inferência (Azure Container Instance)

### 5.1 Arquitetura de Deployment

O modelo é implantado como **endpoint REST** em Azure Container Instance (ACI):

- **CPU:** 2 cores
- **RAM:** 4 GB
- **Application Insights:** habilitado (telemetria)
- **Autenticação:** Bearer token obrigatório

### 5.2 Contrato da API

**Request:**
```json
{
  "input_data": {
    "columns": ["dias_antecedencia", "distancia_km", "renda_media_bairro",
                "numero_consultas_ult_30d", "taxa_historica", "lembrete_enviado",
                "feriado_proximo", "is_weekend", "lembrete_hist",
                "dist_perto", "dist_medio", "dist_longe",
                "renda_baixo", "renda_medio", "renda_alto", "renda_muito_alto",
                "periodo_Manhã", "periodo_Tarde"],
    "data": [[10, 0.50, 8000, 5, 0.05, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0]]
  }
}
```

**Response:**
```json
{
  "predictions": [0.73],
  "labels": [1],
  "threshold": 0.42
}
```

- `predictions`: probabilidade de **comparecimento** ($\hat{p}$), retornada por `predict_proba()[:, 1]`
- `labels`: classificação binária usando o threshold ótimo (KS) embutido no modelo
- `threshold`: o threshold salvo durante o treinamento

### 5.3 Script de Inferência (`teste.py`)

O script de inferência carrega o artefato completo e aplica o pipeline de feature engineering antes da predição:

```python
def init():
    artifacts = joblib.load(os.path.join(model_dir, 'model.pkl'))
    model         = artifacts['model']
    fe_pipeline   = artifacts['feature_engineering']
    feature_names = artifacts['features']
    threshold     = artifacts.get('threshold_sugerido', 0.5)

def run(raw_request):
    df = pd.DataFrame(data, columns=columns)
    X  = df[feature_names]
    X_pre = fe_pipeline.transform(X)    # aplica o mesmo pré-processamento do treino
    probs = model.predict_proba(X_pre)[:, 1].tolist()
    labels = [int(p >= threshold) for p in probs]
```

**Ponto crítico:** O `fe_pipeline` (pré-processador + seletor) é serializado junto com o modelo. Isso garante que a transformação em inferência seja **idêntica** à de treino — mesmos imputadores fitted, mesmas médias/desvios do StandardScaler. Sem isso, há feature skew (divergência treino/servir).

---

## 6. Integração Frontend — Do Score à Simulação

### 6.1 Fluxo de Dados no Flutter

A predição do Azure ML é consumida pelo Flutter em dois caminhos:

**Caminho 1: Denormalização direta**
Um pipeline (Cloud Function ou batch) escreve a probabilidade prevista diretamente no documento do agendamento em `tb_agendamentos`:
```
tb_agendamentos/{id}/probabilidade_falta → 0.32
```

O `AppointmentService` lê este campo e popula `pFaltaPrevista`:
```dart
pFaltaPrevista: _prob(d['probabilidade_falta'] ?? d['probabilidadeFalta']),
```

**Caminho 2: Enriquecimento via `dashboard_risco`**
A coleção `dashboard_risco` armazena scores agregados. O serviço mescla esses dados em tempo real:
```dart
final pct = risco['riscoPercent'] ?? risco['risco'];
final pFalta = pct is num ? pct.toDouble() / 100 : null;
final nivel = pFalta != null
    ? RiskLevel.fromScore(pFalta)
    : RiskLevel.fromString(risco['riscoLabel']?.toString());
```

### 6.2 Conversão Probabilidade → RiskLevel

O `RiskLevel` discretiza a probabilidade contínua em três faixas:

```dart
static RiskLevel fromScore(double score) {
    if (score >= 0.66) return RiskLevel.high;   // p ≥ 66% → Alto
    if (score >= 0.33) return RiskLevel.medium;  // 33% ≤ p < 66% → Médio
    return RiskLevel.low;                         // p < 33% → Baixo
}
```

> **Design intencional:** `fromString` retorna `null` (não `low`) quando não reconhece o rótulo. Cair em `low` por omissão faria todo paciente parecer de baixo risco — exatamente o modo de falha silenciosa que a estratificação deve evitar.

### 6.3 Uso no Motor de Monte Carlo

O Monte Carlo Engine usa a probabilidade de duas formas, em ordem de precedência:

1. **Se `pFaltaPrevista` existe** (predição individual do Azure ML): usa diretamente como probabilidade marginal de falta na simulação.

2. **Se não existe**: mapeia o `RiskLevel` categórico para a taxa média do `ModeloRisco`:

```dart
final base = modelo.pFaltaDe(a.patientRisk);  // low→0.06, medium→0.15, high→0.32
```

Estas taxas são substituídas pela **calibração** quando a clínica tem dados suficientes ($n \geq 50$ por faixa, intervalo de Wilson).

---

## 7. Garantias de Integridade Estatística

### 7.1 Proteção Contra Data Leakage

| Ponto de risco | Mitigação implementada |
|:---|:---|
| SMOTE antes da CV | `ImbPipeline` recalcula SMOTE dentro de cada dobra |
| Transformação de features | Pipeline fitted no treino, `.transform()` no teste |
| SelectKBest | Fitted no treino, a mesma máscara é aplicada ao teste |
| Threshold ótimo | Calculado no conjunto de teste, não no treino |

### 7.2 Intervalo de Confiança de Wilson (na Calibração)

O intervalo de Wilson é usado no lugar do Wald para taxas observadas:

$$\tilde{p} = \frac{p + \frac{z^2}{2n}}{1 + \frac{z^2}{n}} \pm \frac{z}{1 + \frac{z^2}{n}} \sqrt{\frac{p(1-p)}{n} + \frac{z^2}{4n^2}}$$

Com poucas observações ou taxa próxima de 0 ou 1, o Wald produz limites fora de $[0, 1]$ — Wilson nunca faz isso.

### 7.3 Versionamento de Labels

O campo `kLabelVersion = 'falta-v2.1'` acompanha o modelo. Se a definição do que constitui "falta" mudar (ex: incluir reagendamentos tardios), toda métrica histórica precisa ser recalculada. Comparar séries com rótulos diferentes é comparar coisas diferentes — o motor bloqueia essa comparação.

---

## 8. Diagrama Completo: Da Feature ao Slot de Overbooking

```text
                Azure ML                         Firestore                    Flutter
              ┌──────────┐                    ┌──────────────┐            ┌──────────────┐
              │ XGBoost/ │   predict_proba()  │ tb_agendamento│  stream   │ Appointment  │
              │ RF/GBT   │──────────────────▶ │ .probabilidade│─────────▶ │ .pFaltaPre-  │
              │ /LogReg  │                    │ _falta = 0.32 │           │  vista = 0.32│
              └──────────┘                    └──────────────┘            └──────┬───────┘
                                                                                 │
                                                                    ┌────────────▼──────────┐
                                                                    │ ModeloRisco           │
                                                                    │ pFalta = 0.32         │
                                                                    │ pCancel = 0.10        │
                                                                    └────────────┬──────────┘
                                                                                 │
                                                                    ┌────────────▼──────────┐
                                                                    │ Cópula Gaussiana      │
                                                                    │ X_i = √ρ·Z + √(1-ρ)·ε│
                                                                    │ 20.000 runs           │
                                                                    └────────────┬──────────┘
                                                                                 │
                                                                    ┌────────────▼──────────┐
                                                                    │ Distribuição de       │
                                                                    │ presentes por slot    │
                                                                    │ (médico × hora)       │
                                                                    └────────────┬──────────┘
                                                                                 │
                                                                    ┌────────────▼──────────┐
                                                                    │ Decisão de Overbooking│
                                                                    │ Alocação gulosa       │
                                                                    │ Risco pelo pior slot  │
                                                                    └───────────────────────┘
```
