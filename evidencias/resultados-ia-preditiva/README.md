# Resultados da Avaliação da I.A. Preditiva (Primeiros Testes & Métricas)

Este diretório reúne as evidências visuais e estatísticas da avaliação do modelo preditivo de absenteísmo (*no-show*) da plataforma **Vitta Care**, desenvolvida no âmbito do **Programa ELDORADO / Centelha / GovTech**.

Todas as curvas e métricas foram consolidadas a partir de um mesmo vetor de predições e rótulos reais de validação, permitindo avaliar o comportamento do discriminador, calibração de probabilidades e explicabilidade SHAP.

---

## 📈 Gráficos Principais de Validação

<div align="center">
  <img src="01_matriz_confusao_thr050.png" alt="Matriz de Confusão (threshold = 0.500)" width="48%"/>
  <img src="01_matriz_confusao_thr_otimo.png" alt="Matriz de Confusão (threshold = 0.370)" width="48%"/>
</div>
<br/>
<div align="center">
  <img src="02_curva_roc.png" alt="Curva ROC (AUC = 0.9442)" width="48%"/>
  <img src="03_curva_precision_recall.png" alt="Curva Precision x Recall (AP = 0.9266)" width="48%"/>
</div>
<br/>
<div align="center">
  <img src="04_curva_lift.png" alt="Curva de Lift" width="70%"/>
</div>

---

## 📊 Sumário dos Gráficos Gerados

| # | Arquivo | Descrição / Diagnóstico | Métrica / Finalidade |
|:---:|:---|:---|:---|
| **01** | [`01_matriz_confusao_thr050.png`](01_matriz_confusao_thr050.png) | Matriz de Confusão ($\text{threshold} = 0.500$) | Sensibilidade 81.6% (1.320/1.618), Especificidade 90.5% (1.465/1.618). |
| **01b** | [`01_matriz_confusao_thr_otimo.png`](01_matriz_confusao_thr_otimo.png) | Matriz de Confusão no Ponto Ótimo ($\text{threshold} = 0.370$) | Sensibilidade 91.9% (1.487/1.618), Especificidade 85.7% (1.386/1.618). |
| **02** | [`02_curva_roc.png`](02_curva_roc.png) | Curva ROC (*Receiver Operating Characteristic*) | $\text{AUC} = 0.9442$, Ponto KS $= 0.7756$. |
| **03** | [`03_curva_precision_recall.png`](03_curva_precision_recall.png) | Curva Precision-Recall | $\text{AP} = 0.9266$ vs Baseline de 0.500. |
| **04** | [`04_curva_lift.png`](04_curva_lift.png) | Curva de Lift Acumulado | Eficiência de priorização até $1.93\times$ sobre baseline aleatório. |
| **05** | [`05_curva_gain.png`](05_curva_gain.png) | Curva de Ganho Acumulado (*Cumulative Gain*) | Proporção de faltas identificadas em função do percentil da base abordada. |
| **06** | [`06_curva_ks.png`](06_curva_ks.png) | Estatística Kolmogorov-Smirnov (KS) | Grau máximo de separabilidade entre as distribuições das classes 0 e 1. |
| **07** | [`07_calibration_curve.png`](07_calibration_curve.png) | Curva de Calibração (*Reliability Diagram*) | Aderência entre a probabilidade estimada $p_i$ e a frequência empírica observada. |
| **08** | [`08_distribuicao_probabilidades.png`](08_distribuicao_probabilidades.png) | Densidade de Probabilidades (KDE) | Distribuição contínua de scores preditos estratificada por classe real. |
| **09** | [`09_histograma_probabilidades.png`](09_histograma_probabilidades.png) | Histograma de Frequências de Scores | Frequência de predições distribuída em bins de probabilidade. |
| **10** | [`10_distribuicao_classes.png`](10_distribuicao_classes.png) | Distribuição das Classes | Volumetria e balanceamento de classes na base de teste e treino. |
| **11** | [`11_importancia_variaveis.png`](11_importancia_variaveis.png) | Importância Global de Atributos | Relevância relativa de cada feature no modelo de machine learning. |
| **12** | [`12_shap_summary.png`](12_shap_summary.png) | SHAP Summary Plot | Direção e magnitude do impacto de cada feature nas predições individuais. |
| **13** | [`13_shap_beeswarm.png`](13_shap_beeswarm.png) | SHAP Beeswarm Plot | Distribuição densa dos valores Shapley por observação. |
| **14** | [`14_shap_bar.png`](14_shap_bar.png) | SHAP Bar Plot | Média absoluta dos valores de impacto $\|\text{SHAP}\|$ por feature. |

---

## 🔗 Referências e Especificações

- Pipeline de Machine Learning detalhado: [`../../docs/pipeline-ia-completo.md`](../../docs/pipeline-ia-completo.md)
- Protocolo de Testes e Validação: [`../../docs/testes-validacao.md`](../../docs/testes-validacao.md)
- Integração e Modelagem Estocástica: [`../../docs/modelo-preditivo.md`](../../docs/modelo-preditivo.md)
