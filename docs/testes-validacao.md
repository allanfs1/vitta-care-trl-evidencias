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
- **Objetivo:** Validar o cálculo da probabilidade de falta, a classificação de risco (Baixo, Médio, Alto) e o tempo de resposta da inferência.
- **Entrada:** Lote de $500$ registros de agendamentos ambulatoriais anonimizados.
- **Resultado:** 
  - Tempo médio de inferência por agendamento: **114 ms**.
  - Calibração de probabilidade dentro da margem de erro aceitável (Brier score: $0.118$).
  - Associação precisa do risco no painel operacional de agendamentos.
  - Evidências visuais e suite diagnóstica completa arquivada em [`../evidencias/resultados-ia-preditiva/`](../evidencias/resultados-ia-preditiva/).
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
