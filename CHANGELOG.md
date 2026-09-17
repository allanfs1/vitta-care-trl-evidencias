# Histórico de Evolução Tecnológica — Vitta Care

## [v0.4.0] — 2026-09
### Adicionado
- Módulo de Mapa de Arquitetura e Grafo de Dependências (`ModuleGraph`) com validação topológica de 28 módulos.
- Integração do Simulador de Monte Carlo com propagação de 3 camadas de incerteza (forecast lognormal WAPE, parâmetro Beta posterior e realização multinomial).
- Modelagem estocástica com Cadeia de Markov e regularização de Laplace Dirichlet.
- Totem de autoatendimento e painel de chamada sincronizado em tempo real para recepção física.
- Dashboard de Health Score de pacientes e estratificação de risco de no-show.

## [v0.3.0] — 2026-06
### Adicionado
- Pipeline de inferência de absenteísmo integrado à tela de agendamentos.
- Estrutura de anonimização e conformidade LGPD (PHI Guard).
- Automação de réguas de mensagens de confirmação e reagendamento via WhatsApp API.
- Dashboard com indicadores operacionais (taxa de ocupação, índice de faltas e receita recuperável).

## [v0.2.0] — 2026-03
### Adicionado
- Pipeline inicial de engenharia de atributos com janelas móveis de absenteísmo.
- Primeiro modelo preditivo de no-show baseado em árvores de decisão e regressão logística calibrada.
- Módulo de Medicina Baseada em Evidências integrado à API NCBI E-Utilities (PubMed).

## [v0.1.0] — 2025-11
### Adicionado
- Arquitetura base em Flutter com autenticação (Firebase Auth) e controle de perfil de usuário.
- Telas operacionais de recepção, cadastro de pacientes e gestão de agendamentos médicos.
- Estruturação do banco de dados na nuvem.
