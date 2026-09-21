# Testes e Validação Tecnológica

Este documento consolida os testes de validação técnica executados na plataforma **Vitta Care** para comprovação de prontidão tecnológica (TRL).

---

## Teste 01 — Sanitização e Anonimização (PHI Guard)
- **Objetivo:** Verificar se dados de identificação pessoal (CPF, nome, telefone) são completamente interceptados e removidos antes do envio para modelos analíticos ou provedores externos.
- **Entrada:** Payload de teste contendo nome do paciente, CPF fictício, número de WhatsApp e texto livre com histórico de saúde.
- **Resultado:** O módulo de validação filtrou 100% dos dados sensíveis, convertendo endereços em distâncias relativas (`distancia_km`) e chaves primárias em hashes unidirecionais.
- **Status:** **Aprovado.**

---

## Teste 02 — Inferência Preditiva de Absenteísmo (No-Show)
- **Objetivo:** Validar a capacidade de discriminação, calibração de probabilidade, identificação de limiar operacional ótimo (Youden / KS) e tempo de resposta de inferência.
- **Entrada:** Lote de validação com $3.236$ registros de agendamentos ambulatoriais (1.618 faltas e 1.618 comparecimentos), derivado de base de treinamento de $12.942$ amostras.
- **Resultado:**
  - **Capacidade Discriminativa:** $\text{ROC-AUC} = \mathbf{0.9442}$, com ponto de máxima divergência Kolmogorov-Smirnov $\text{KS} = \mathbf{0.7756}$.
  - **Sustentação de Precisão:** $\text{Average Precision (AP)} = \mathbf{0.9266}$ (frente ao baseline de prevalência de $0.500$).
  - **Calibração Probabilística:** Brier score de $\mathbf{0.1070}$, garantindo fidelidade estocástica para os motores de Monte Carlo e Markov.
  - **Ponto de Operação Ótimo:** Threshold $\mathbf{0.370}$, elevando a sensibilidade para $\mathbf{91.90\%}$ ($1.487$ faltas detectadas), com especificidade de $85.66\%$ e acurácia de $88.78\%$.
  - **Eficiência de Priorização:** Curva de Lift de até $\mathbf{1.93\times}$ e captura de $87\%$ das faltas nos primeiros $50\%$ da base abordada.
  - **Tempo médio de inferência por agendamento:** **114 ms**.
  - **Evidências visuais e suite diagnóstica completa:** Arquivada em [`../evidencias/resultados-ia-preditiva/`](../evidencias/resultados-ia-preditiva/).
- **Status:** **Aprovado.**

---

## Teste 03 — Simulação Estocástica de Monte Carlo
- **Objetivo:** Garantir a consistência matemática da conservação multinomial ($\sum \text{desfechos} = N$) e a propagação correta das 3 fontes de incerteza (forecast, parâmetro, amostral).
- **Entrada:** Cenário clínico de $800$ consultas mensais previstas com taxa histórica de falta de $24\%$ e cancelamento de $11\%$, $10.000$ iterações.
- **Resultado:** Distribuição empírica convergente com intervalos de confiança de $95\%$ bem delimitados. Nenhuma linha gerou valores negativos ou violação do teto físico de capacidade.
- **Status:** **Aprovado.**

---

## Teste 04 — Grafo de Dependências e Isolamento Modular (DAG)
- **Objetivo:** Assegurar que os 28 módulos da aplicação respeitam regras estritas de dependência e podem ser ativados/desativados sem quebrar o sistema.
- **Entrada:** Execução do validador `ModuleGraph.validate()` e cálculo da ordem topológica.
- **Resultado:** Grafo 100% acíclico confirmado (zero dependências circulares), permitindo desligamento isolado de módulos como totem, telemedicina ou simulador sem falha no núcleo do sistema.
- **Status:** **Aprovado.**

---

## Teste 05 — Sincronização em Tempo Real Recepção ↔ Totem
- **Objetivo:** Validar a atualização instantânea do chamado de pacientes entre a triagem, o totem de entrada e o monitor de TV.
- **Entrada:** Emissão de senha no totem e acionamento de "Chamar Próximo" pelo médico.
- **Resultado:** Atualização da tela do monitor de recepção em menos de **300 ms**, com sinalização sonora e visual.
- **Status:** **Aprovado.**
