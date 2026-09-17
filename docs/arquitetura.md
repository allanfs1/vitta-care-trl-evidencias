# Arquitetura da Solução

## 1. Organização em Camadas

A plataforma opera em quatro camadas desacopladas:

| Camada | Responsabilidade | Tecnologias |
|:---|:---|:---|
| **Apresentação** | Renderização reativa e responsiva | Flutter 3.x (Web/Mobile), Material Design 3, Riverpod |
| **Roteamento e Módulos** | Governança do grafo de dependências | GoRouter, ModuleGraph (DAG), hot-swap de módulos |
| **Dados e Segurança** | Persistência, autenticação e privacy | Cloud Firestore, Firebase Auth, PHI Guard |
| **Modelagem Matemática** | Simulação, predição e otimização | Monte Carlo (cópula gaussiana), Markov, Poisson-Binomial |

## 2. Grafo Acíclico Dirigido (DAG) de Módulos

Os 28 módulos são registrados declarativamente em `ModuleRegistry`. O `ModuleGraph` valida três invariantes simultaneamente:

1. **Aciclicidade** — DFS com coloração tripartite (branco/cinza/preto).
2. **Completude de dependências** — toda aresta aponta para um módulo existente.
3. **Isolamento de coleções** — cada coleção Firestore `owned` pertence a no máximo um módulo.

A **ordenação topológica** fornece uma sequência de implementação que respeita todas as dependências. Na interface, módulos podem ser habilitados/desabilitados em tempo de execução; o grafo bloqueia automaticamente as rotas dos dependentes transitivos.

### Hierarquia de Prioridades e Arestas

```text
P0 (Base)
  auth → navegação → home → agendamentos → criar_agendamento

P1 (Fluxo diário)
  home → recepção
  home → pacientes
  home → equipe_médica
  agendamentos → totem

P2 (Analytics / Absenteísmo)
  home → absenteísmo
  agendamentos + equipe_médica + overbooking → monte_carlo
  agendamentos + monte_carlo → projeção_12m
  equipe_médica → overbooking

P3 (Avançado)
  criar_agendamento → ia → evidências
  ia → integrações → whatsapp
```

## 3. Isolamento de Coleções

Cada módulo declara explicitamente:
- `ownedCollections`: coleções onde o módulo **pode escrever**.
- `readsCollections`: coleções que o módulo **apenas lê**.

Se dois módulos declaram `owned` sobre a mesma coleção, a validação do grafo rejeita a configuração como conflito de isolamento. Esta invariante impede que escritas concorrentes de módulos distintos corrompam o estado compartilhado.

## 4. Gerenciamento de Estado

O estado reativo da aplicação é gerenciado por **Riverpod** com granularidade de provider por domínio:

- `appointmentsProvider`: stream de agendamentos filtrado por clínica ativa.
- `clinicDoctorsProvider`: equipe médica da unidade selecionada.
- `selectedClinicIdProvider`: persistido em SharedPreferences com validação de ownership.
- `disabledModulesProvider`: módulos desativados pelo operador, sincronizados com o GoRouter.

## 5. Roteamento e Deep Linking

O `GoRouter` é configurado como provider Riverpod reagindo a mudanças de autenticação e de módulos habilitados. O `redirect` aplica regras em cascata:

1. Rotas públicas (totem, monitor, agenda médica pública) são liberadas sem autenticação.
2. Usuário não autenticado → login.
3. Autenticado sem plano → seleção de plano.
4. Módulo desabilitado → home (redirect transparente).
