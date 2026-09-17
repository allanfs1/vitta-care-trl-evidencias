# Matriz de Integrações Tecnológicas

A plataforma **Vitta Care** possui integrações funcionais com serviços de mensageria, bases científicas internacionais e infraestrutura em nuvem.

---

## 1. Integração com WhatsApp (Mensageria e Confirmações)
- **Objetivo:** Automatizar a régua de comunicação com pacientes para confirmação, cancelamento e reagendamento antecipado de consultas.
- **Status:** Implementado e Homologado.
- **Forma de Integração:** REST API / Webhooks assíncronos (Z-API e WhatsApp Cloud API).
- **Resultado Obtido:** Envio automatizado de lembretes com botões interativos (ex.: "Confirmar Presença", "Remarcar Data"). Atualização instantânea do status do agendamento no painel operacional da clínica.
- **Próxima Evolução:** Agente conversacional de linguagem natural com LLM especializada em triagem de intenções de remarcação e respostas a dúvidas de preparo de exames.

---

## 2. Integração PubMed / NCBI E-Utilities
- **Objetivo:** Recuperação em tempo real de evidências clínicas e artigos médicos indexados para suporte à decisão na prescrição e conduta.
- **Status:** Implementado e Testado.
- **Forma de Integração:** API E-Utilities (ESearch, EFetch XML) com pipeline de sanitização via proxy backend e módulo `phi_guard.dart`.
- **Resultado Obtido:** Busca parametrizada por descritores MeSH, extração de resumo, nível de evidência e validação estrita de citações clínicas.
- **Próxima Evolução:** Indexação semântica em banco vetorial (RAG) para perguntas e respostas clínicas contextualizadas ao histórico do paciente.

---

## 3. Autenticação e Gestão de Identidade
- **Objetivo:** Prover acesso seguro, auditoria e controle de privilégios (RBAC) para diferentes perfis (Gestores, Médicos, Recepcionistas, Pacientes).
- **Status:** Implementado e Operacional.
- **Forma de Integração:** Firebase Authentication SDK + WebAuthn API (Biometria nativa: Windows Hello, Touch ID, leitor de impressão digital).
- **Resultado Obtido:** Login seguro multifator, controle de expiração de sessão e auditoria de acessos.
- **Próxima Evolução:** Integração com federações de identidade hospitalar (SAML / OAuth2 / Gov.br para SUS).

---

## 4. Totem de Autoatendimento e Painel de Chamada
- **Objetivo:** Agilizar o check-in na recepção física, diminuindo filas e atualizando o tempo de espera no sistema.
- **Status:** Implementado e Operacional.
- **Forma de Integração:** Rota dedicada no frontend Flutter (`/#/totem` e `/#/monitor-recepcao`) com WebSockets/Snapshot Listeners para sincronização em tempo real.
- **Resultado Obtido:** Emissão de senhas prioritárias e normais, confirmação de chegada pelo paciente e acionamento sonoro no monitor de TV da recepção.
- **Próxima Evolução:** Reconhecimento facial voluntário para check-in instantâneo e integração direta com impressoras térmicas de protocolo físico.
