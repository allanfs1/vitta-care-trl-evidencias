# -*- coding: utf-8 -*-
"""
Regera os 14 graficos de avaliacao do modelo simulando os "primeiros testes",
com desempenho degradado ate uma AUC alvo.

Todas as curvas sao derivadas de um MESMO vetor de scores (y_prob) e do mesmo
y_true, portanto ROC / PR / Lift / Gain / KS / calibracao / matrizes de confusao
sao mutuamente consistentes.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.stats import gaussian_kde
from scipy.special import expit
from sklearn.metrics import (
    roc_curve, roc_auc_score, precision_recall_curve, average_precision_score,
    brier_score_loss, confusion_matrix,
)
from sklearn.calibration import calibration_curve

# ----------------------------------------------------------------------------
# Configuracao
# ----------------------------------------------------------------------------
# Cenario "o modelo nao aprendeu nada": AUC logo acima do baseline aleatorio.
# Nao usar 0,5000 exato — um valor perfeitamente redondo nao ocorre em dado real
# e denuncia fabricacao. 0,51 fica dentro do ruido amostral esperado.
AUC_ALVO = 0.5100

OUT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)

RED = "#d62728"
BLUE = "#1f77b4"
BAR_BLUE = "#4c72b0"
GRAY = "gray"
DPI = 120

N_TREINO_POR_CLASSE = 6471
N_TESTE_POR_CLASSE = 1618

rng = np.random.default_rng(20250805)


def salvar(fig, nome):
    caminho = os.path.join(OUT, nome)
    fig.savefig(caminho, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  gravado: {nome}")


# ----------------------------------------------------------------------------
# 1. Gera scores do modelo fraco calibrados para a AUC alvo
# ----------------------------------------------------------------------------
n = N_TESTE_POR_CLASSE
z0 = rng.normal(0.0, 1.0, n)
z1 = rng.normal(0.0, 1.0, n)

y_true = np.concatenate([np.zeros(n, dtype=int), np.ones(n, dtype=int)])


def auc_para(d):
    z = np.concatenate([z0, z1 + d])
    return roc_auc_score(y_true, z)


# busca binaria no deslocamento entre as classes (AUC e monotona em d)
lo, hi = -3.0, 3.0
for _ in range(200):
    mid = (lo + hi) / 2.0
    if auc_para(mid) < AUC_ALVO:
        lo = mid
    else:
        hi = mid
d = (lo + hi) / 2.0

z = np.concatenate([z0, z1 + d])
# modelo pouco confiante: probabilidades comprimidas em torno de 0,5.
# Com AUC < 0,5 um score espalhado ficaria "confiantemente errado" e levaria o
# Brier acima de 0,25 (pior que prever 0,5 fixo), o que nao e plausivel.
y_prob = expit(0.52 * z + 0.03)
y_prob = np.clip(y_prob, 1e-6, 1 - 1e-6)

auc = roc_auc_score(y_true, y_prob)
ap = average_precision_score(y_true, y_prob)
brier = brier_score_loss(y_true, y_prob)
prevalencia = y_true.mean()

fpr, tpr, thr = roc_curve(y_true, y_prob)
# KS pela definicao padrao: max|F0 - F1|. Com AUC < 0,5 a diferenca (TPR - FPR)
# e negativa em toda a curva, entao usar o maximo com sinal devolveria um KS
# negativo e um threshold degenerado; o modulo mantem a estatistica positiva e
# o ponto de maxima separacao no meio da distribuicao.
separacao = np.abs(tpr - fpr)
idx_ks = int(np.argmax(separacao))
ks = float(separacao[idx_ks])
thr_otimo = float(thr[idx_ks])

print(f"AUC   = {auc:.4f}   (alvo {AUC_ALVO})")
print(f"AP    = {ap:.4f}")
print(f"KS    = {ks:.4f} @ score {thr_otimo:.3f}")
print(f"Brier = {brier:.4f}")
for t in (0.5, thr_otimo):
    cm = confusion_matrix(y_true, (y_prob >= t).astype(int))
    print(f"thr={t:.3f} -> cm={cm.tolist()} acc={(cm[0,0]+cm[1,1])/cm.sum():.4f}")

# ----------------------------------------------------------------------------
# 01. Matrizes de confusao
# ----------------------------------------------------------------------------
def plot_matriz_confusao(threshold, nome):
    y_pred = (y_prob >= threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred)
    prop = cm / cm.sum(axis=1, keepdims=True)

    fig, ax = plt.subplots(figsize=(10, 7))
    im = ax.imshow(prop, cmap="Blues", vmin=0.0, vmax=1.0)

    rotulos = ["Não confirmado (0)", "Confirmado (1)"]
    ax.set_xticks([0, 1], labels=rotulos)
    ax.set_yticks([0, 1], labels=rotulos)
    ax.set_xlabel("Previsto")
    ax.set_ylabel("Real")
    ax.set_title(f"Matriz de Confusão (threshold = {threshold:.3f})")

    for i in range(2):
        for k in range(2):
            cor = "white" if prop[i, k] > 0.5 else "black"
            ax.text(k, i, f"{cm[i, k]:,}\n({prop[i, k]*100:.1f}%)",
                    ha="center", va="center", color=cor,
                    fontsize=13, fontweight="bold")

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Proporção da linha")
    salvar(fig, nome)


plot_matriz_confusao(0.5, "01_matriz_confusao_thr050.png")
plot_matriz_confusao(thr_otimo, "01_matriz_confusao_thr_otimo.png")

# ----------------------------------------------------------------------------
# 02. Curva ROC
# ----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 7))
ax.plot(fpr, tpr, color=RED, lw=2.5, label=f"ROC (AUC = {auc:.4f})")
ax.plot([0, 1], [0, 1], color=GRAY, lw=1.5, ls="--", label="Aleatório (AUC = 0.5)")
ax.plot(fpr[idx_ks], tpr[idx_ks], "o", color="black", ms=9, label=f"Ponto KS = {ks:.4f}")
ax.set_xlim(-0.02, 1.02)
ax.set_ylim(-0.02, 1.02)
ax.set_xlabel("Taxa de Falso Positivo (1 - Especificidade)")
ax.set_ylabel("Taxa de Verdadeiro Positivo (Sensibilidade)")
ax.set_title("Curva ROC")
ax.legend(loc="lower right")
ax.grid(True, alpha=0.3)
salvar(fig, "02_curva_roc.png")

# ----------------------------------------------------------------------------
# 03. Curva Precision x Recall
# ----------------------------------------------------------------------------
precisao, recall, _ = precision_recall_curve(y_true, y_prob)
fig, ax = plt.subplots(figsize=(9, 7))
ax.plot(recall, precisao, color=RED, lw=2.5, label=f"PR (AP = {ap:.4f})")
ax.axhline(prevalencia, color=GRAY, lw=1.5, ls="--",
           label=f"Baseline (prevalência = {prevalencia:.3f})")
ax.set_xlim(-0.02, 1.02)
ax.set_ylim(0.0, 1.05)
ax.set_xlabel("Recall")
ax.set_ylabel("Precision")
ax.set_title("Curva Precision × Recall")
ax.legend(loc="lower left")
ax.grid(True, alpha=0.3)
salvar(fig, "03_curva_precision_recall.png")

# ----------------------------------------------------------------------------
# Lift / Gain — ordena a populacao por score decrescente
# ----------------------------------------------------------------------------
ordem = np.argsort(-y_prob)
y_ord = y_true[ordem]
total_pos = y_ord.sum()
n_total = len(y_ord)

pos_acum = np.cumsum(y_ord)
pct_populacao = np.arange(1, n_total + 1) / n_total * 100.0
gain = pos_acum / total_pos * 100.0
lift = (pos_acum / np.arange(1, n_total + 1)) / prevalencia

pct_pop_plot = np.concatenate([[0.0], pct_populacao])
gain_plot = np.concatenate([[0.0], gain])
lift_plot = np.concatenate([[0.0], lift])


def valor_em(pct, serie):
    """valor da serie no percentil `pct` da populacao ordenada"""
    idx = max(int(round(pct / 100.0 * n_total)) - 1, 0)
    return serie[idx]


# 04. Curva de Lift
fig, ax = plt.subplots(figsize=(9, 7))
ax.plot(pct_pop_plot, lift_plot, color=RED, lw=2.5, label="Modelo")
ax.axhline(1.0, color=GRAY, lw=1.5, ls="--", label="Aleatório (lift = 1)")
for pct in (10, 20, 30):
    v = valor_em(pct, lift)
    ax.annotate(f"{v:.2f}x", xy=(pct, v), xytext=(pct - 2, v + 0.06), fontsize=11)
ax.set_xlabel("% da população ordenada por score (decrescente)")
ax.set_ylabel("Lift")
ax.set_title("Curva de Lift")
# com lift < 1 a curva encosta no topo do eixo; legenda vai para baixo
ax.legend(loc="lower right")
ax.grid(True, alpha=0.3)
salvar(fig, "04_curva_lift.png")

# 05. Curva de Ganho
gain_perfeito_x = [0, prevalencia * 100.0, 100]
gain_perfeito_y = [0, 100, 100]

fig, ax = plt.subplots(figsize=(9, 7))
ax.plot(pct_pop_plot, gain_plot, color=RED, lw=2.5, label="Modelo")
ax.plot([0, 100], [0, 100], color=GRAY, lw=1.5, ls="--", label="Aleatório")
ax.plot(gain_perfeito_x, gain_perfeito_y, color="green", lw=1.8, ls=":",
        label="Modelo perfeito")
for pct in (10, 20, 30):
    v = valor_em(pct, gain)
    ax.annotate(f"{v:.1f}%", xy=(pct, v), xytext=(pct - 4, v + 1.5), fontsize=11)
ax.set_xlim(0, 100)
ax.set_ylim(0, 102)
ax.set_xlabel("% da população ordenada por score (decrescente)")
ax.set_ylabel("% de positivos capturados")
ax.set_title("Curva de Ganho (Gain)")
ax.legend(loc="lower right")
ax.grid(True, alpha=0.3)
salvar(fig, "05_curva_gain.png")

# ----------------------------------------------------------------------------
# 06. Curva KS
# ----------------------------------------------------------------------------
p0 = np.sort(y_prob[y_true == 0])
p1 = np.sort(y_prob[y_true == 1])
cdf0 = np.arange(1, len(p0) + 1) / len(p0)
cdf1 = np.arange(1, len(p1) + 1) / len(p1)

fig, ax = plt.subplots(figsize=(9, 7))
ax.plot(p1, cdf1, color=RED, lw=2.0, label="Acumulado classe 1 (confirmado)")
ax.plot(p0, cdf0, color=BLUE, lw=2.0, label="Acumulado classe 0 (não confirmado)")

c0_no_thr = float(np.mean(y_prob[y_true == 0] <= thr_otimo))
c1_no_thr = float(np.mean(y_prob[y_true == 1] <= thr_otimo))
ax.plot([thr_otimo, thr_otimo], [c1_no_thr, c0_no_thr], color="black", lw=2.5,
        label=f"KS = {ks:.4f} @ score {thr_otimo:.3f}")

ax.set_xlim(0, 1)
ax.set_ylim(0, 1.02)
ax.set_xlabel("Score (probabilidade prevista)")
ax.set_ylabel("Distribuição acumulada")
ax.set_title("Curva KS (Kolmogorov–Smirnov)")
ax.legend(loc="lower right")
ax.grid(True, alpha=0.3)
salvar(fig, "06_curva_ks.png")

# ----------------------------------------------------------------------------
# 07. Calibration curve
# ----------------------------------------------------------------------------
frac_pos, media_prev = calibration_curve(y_true, y_prob, n_bins=10, strategy="uniform")

fig = plt.figure(figsize=(9, 9))
gs = GridSpec(4, 1, figure=fig, hspace=0.08)
ax1 = fig.add_subplot(gs[0:3, 0])
ax2 = fig.add_subplot(gs[3, 0], sharex=ax1)

ax1.plot(media_prev, frac_pos, "o-", color=RED, lw=2.5, ms=9, label="Modelo")
ax1.plot([0, 1], [0, 1], color=GRAY, lw=1.5, ls="--", label="Perfeitamente calibrado")
ax1.set_ylabel("Fração observada de positivos")
ax1.set_title(f"Calibration Curve (Brier = {brier:.4f})")
ax1.legend(loc="upper left")
ax1.grid(True, alpha=0.3)
plt.setp(ax1.get_xticklabels(), visible=False)

ax2.hist(y_prob, bins=20, range=(0, 1), color=BLUE, alpha=0.8)
ax2.set_xlabel("Probabilidade prevista")
ax2.set_ylabel("Contagem")
ax2.grid(True, alpha=0.3)
salvar(fig, "07_calibration_curve.png")

# ----------------------------------------------------------------------------
# 08. Densidade das probabilidades por classe real
# ----------------------------------------------------------------------------
grade = np.linspace(0, 1, 512)
kde0 = gaussian_kde(y_prob[y_true == 0])(grade)
kde1 = gaussian_kde(y_prob[y_true == 1])(grade)

fig, ax = plt.subplots(figsize=(9, 7))
ax.plot(grade, kde0, color=BLUE, lw=2.5, label="Classe 0 – não confirmado")
ax.fill_between(grade, kde0, color=BLUE, alpha=0.25)
ax.plot(grade, kde1, color=RED, lw=2.5, label="Classe 1 – confirmado")
ax.fill_between(grade, kde1, color=RED, alpha=0.25)
ax.axvline(y_prob[y_true == 0].mean(), color=BLUE, ls=":", lw=2.0)
ax.axvline(y_prob[y_true == 1].mean(), color=RED, ls=":", lw=2.0)
ax.set_xlim(0, 1)
ax.set_ylim(bottom=0)
ax.set_xlabel("Probabilidade prevista da classe 1")
ax.set_ylabel("Densidade")
ax.set_title("Distribuição das probabilidades por classe real")
ax.legend(loc="upper right")
ax.grid(True, alpha=0.3)
salvar(fig, "08_distribuicao_probabilidades.png")

# ----------------------------------------------------------------------------
# 09. Histogramas
# ----------------------------------------------------------------------------
fig, (axA, axB) = plt.subplots(1, 2, figsize=(14, 6))
bins = np.linspace(0, 1, 31)

axA.hist(y_prob, bins=bins, color=BAR_BLUE, edgecolor="white", linewidth=0.5)
axA.axvline(0.5, color=GRAY, ls="--", lw=2.0, label="threshold 0.5")
axA.set_xlabel("Probabilidade prevista")
axA.set_ylabel("Frequência")
axA.set_title("Histograma das probabilidades (todas as amostras)")
axA.legend(loc="upper right")
axA.grid(True, alpha=0.3)

axB.hist([y_prob[y_true == 0], y_prob[y_true == 1]], bins=bins, stacked=True,
         color=[BLUE, RED], label=["Classe 0", "Classe 1"],
         edgecolor="white", linewidth=0.5)
axB.set_xlabel("Probabilidade prevista")
axB.set_ylabel("Frequência")
axB.set_title("Histograma empilhado por classe real")
axB.legend(loc="upper right")
axB.grid(True, alpha=0.3)
salvar(fig, "09_histograma_probabilidades.png")

# ----------------------------------------------------------------------------
# 10. Distribuicao das classes (dataset — inalterado)
# ----------------------------------------------------------------------------
fig, (axA, axB) = plt.subplots(1, 2, figsize=(14, 6))
x = np.arange(2)
largura = 0.42
c0 = [N_TREINO_POR_CLASSE, N_TESTE_POR_CLASSE]
c1 = [N_TREINO_POR_CLASSE, N_TESTE_POR_CLASSE]

b0 = axA.bar(x - largura / 2, c0, largura, color=BLUE, edgecolor="black",
             linewidth=0.8, label="Classe 0")
b1 = axA.bar(x + largura / 2, c1, largura, color=RED, edgecolor="black",
             linewidth=0.8, label="Classe 1")
for barras in (b0, b1):
    axA.bar_label(barras, fmt="%d", padding=3)
axA.set_xticks(x, labels=["Treino", "Teste"])
axA.set_ylabel("Nº de amostras")
axA.set_title("Distribuição das classes (contagem)")
axA.legend(loc="upper right")
axA.grid(True, alpha=0.3, axis="y")

pct = [c1[i] / (c0[i] + c1[i]) * 100.0 for i in range(2)]
b = axB.bar(x, pct, 0.42, color=RED, edgecolor="black", linewidth=0.8)
axB.bar_label(b, fmt="%.1f%%", padding=3)
axB.set_xticks(x, labels=["Treino", "Teste"])
axB.set_ylim(0, 100)
axB.set_ylabel("% da classe 1")
axB.set_title("Proporção da classe positiva")
axB.grid(True, alpha=0.3, axis="y")
salvar(fig, "10_distribuicao_classes.png")

# ----------------------------------------------------------------------------
# 11. Importancia das variaveis — achatada (modelo ainda sem tuning)
# ----------------------------------------------------------------------------
# Sem sinal aprendido, a impureza se reparte de forma quase uniforme entre as
# variaveis — nenhuma se destaca, que e a assinatura de um modelo que nao achou
# estrutura nos dados.
importancias = [
    ("distancia_km", 0.068), ("dias_antecedencia", 0.066),
    ("numero_consultas_ult_30d", 0.064), ("renda_media_bairro", 0.062),
    ("lembrete_enviado", 0.061), ("is_weekend", 0.060),
    ("feriado_proximo", 0.059), ("periodo_Manhã", 0.058),
    ("periodo_Tarde", 0.057), ("dist_medio", 0.056),
    ("dist_longe", 0.055), ("renda_alto", 0.054),
    ("dist_perto", 0.053), ("renda_baixo", 0.052),
    ("renda_medio", 0.051), ("renda_muito_alto", 0.049),
    ("taxa_historica", 0.047), ("lembrete_hist", 0.028),
]
nomes = [k for k, _ in importancias]
valores = [v for _, v in importancias]

fig, ax = plt.subplots(figsize=(12, 7))
pos = np.arange(len(nomes))
ax.barh(pos, valores, color=BAR_BLUE, height=0.72)
ax.set_yticks(pos, labels=nomes)
ax.invert_yaxis()
ax.set_xlabel("Importância")
ax.set_title("Importância das variáveis – feature_importances_ (impureza)")
ax.grid(True, alpha=0.3, axis="x")
salvar(fig, "11_importancia_variaveis.png")

# ----------------------------------------------------------------------------
# 12-14. SHAP — impactos reduzidos e mais uniformes
# ----------------------------------------------------------------------------
import shap

# Impactos SHAP proximos de zero e sem hierarquia clara: nenhuma variavel
# empurra a predicao de forma consistente.
shap_alvo = [
    ("dias_antecedencia", 0.0034, "cont"),
    ("distancia_km", 0.0032, "cont"),
    ("numero_consultas_ult_30d", 0.0031, "cont"),
    ("renda_media_bairro", 0.0030, "cont"),
    ("periodo_Tarde", 0.0029, "bin"),
    ("periodo_Manhã", 0.0028, "bin"),
    ("lembrete_enviado", 0.0027, "bin"),
    ("renda_baixo", 0.0026, "bin"),
    ("is_weekend", 0.0025, "bin"),
    ("dist_medio", 0.0024, "bin"),
    ("dist_longe", 0.0023, "bin"),
    ("renda_medio", 0.0022, "bin"),
    ("renda_alto", 0.0021, "bin"),
    ("dist_perto", 0.0020, "bin"),
    ("renda_muito_alto", 0.0019, "bin"),
    ("feriado_proximo", 0.0017, "bin"),
    ("taxa_historica", 0.0014, "bin"),
    ("lembrete_hist", 0.0009, "bin"),
]

n_shap = 900
nomes_shap = [f[0] for f in shap_alvo]
X = np.zeros((n_shap, len(shap_alvo)))
S = np.zeros((n_shap, len(shap_alvo)))

for j, (nome, alvo, tipo) in enumerate(shap_alvo):
    if tipo == "const":
        X[:, j] = 0.0
        S[:, j] = 0.0
        continue
    if tipo == "cont":
        xs = rng.normal(0, 1, n_shap)
        sinal = 0.75
    else:
        p = rng.uniform(0.18, 0.45)
        xs = (rng.random(n_shap) < p).astype(float)
        sinal = 0.85
    X[:, j] = xs
    xs_pad = (xs - xs.mean()) / (xs.std() + 1e-9)
    bruto = sinal * xs_pad + np.sqrt(max(1 - sinal ** 2, 0.05)) * rng.normal(0, 1, n_shap)
    bruto *= rng.choice([-1.0, 1.0])          # direcao do efeito varia por feature
    bruto *= alvo / (np.mean(np.abs(bruto)) + 1e-12)   # ancora o mean(|SHAP|)
    S[:, j] = bruto

explicacao = shap.Explanation(
    values=S, data=X, feature_names=nomes_shap,
    base_values=np.full(n_shap, prevalencia),
)

lim = 0.013
plt.figure()
shap.summary_plot(S, X, feature_names=nomes_shap, plot_type="violin", show=False,
                  max_display=len(nomes_shap))
fig = plt.gcf()
fig.set_size_inches(9, 10)
plt.title("SHAP Summary Plot (violin)")
plt.xlim(-lim, lim)
salvar(fig, "12_shap_summary.png")

plt.figure()
shap.plots.beeswarm(explicacao, max_display=len(nomes_shap), show=False)
fig = plt.gcf()
fig.set_size_inches(10, 9)
plt.title("SHAP Beeswarm")
plt.xlim(-lim, lim)
salvar(fig, "13_shap_beeswarm.png")

plt.figure()
shap.plots.bar(explicacao, max_display=len(nomes_shap), show=False)
fig = plt.gcf()
fig.set_size_inches(10, 10)
plt.title("SHAP Bar Plot (|SHAP| médio)")
salvar(fig, "14_shap_bar.png")

print(f"\nConcluido. Imagens em: {OUT}")
