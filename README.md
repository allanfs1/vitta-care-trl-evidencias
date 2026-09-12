Vitta Care — Estrutura de Evidências de Desenvolvimento Tecnológico
> **Objetivo deste repositório:** reunir evidências técnicas do desenvolvimento da plataforma Vitta Care para apoiar a comprovação de maturidade tecnológica da solução, especialmente no contexto do Programa ELDORADO de Aceleração Tecnológica em IA para Startups.
>
> Este repositório deve concentrar **evidências de desenvolvimento tecnológico**. Evidências institucionais, cartas de intenção, fotos de eventos, registros de validação externa e outros documentos devem permanecer no Google Drive da startup.
---
1. Estrutura recomendada do repositório
```text
vitta-care-evidencias-desenvolvimento/
│
├── README.md
├── CHANGELOG.md
├── LICENSE.md                     # opcional
│
├── docs/
│   ├── arquitetura.md
│   ├── modelo-preditivo.md
│   ├── pipeline-dados.md
│   ├── integracoes.md
│   ├── testes-validacao.md
│   └── evolucao-tecnologica.md
│
├── evidencias/
│   ├── screenshots/
│   ├── dashboards/
│   ├── modelo-ia/
│   └── testes/
│
├── exemplos/
│   ├── exemplo_dados_anonimizados.csv
│   ├── exemplo_inferencia.json
│   └── exemplo_resultado.json
│
└── diagrams/
    ├── arquitetura-vitta-care.png
    ├── fluxo-ia.png
    └── pipeline-inferencia.png
```
---
2. README principal
Vitta Care — Plataforma de IA para Predição e Redução de Absenteísmo em Saúde
A Vitta Care é uma healthtech que desenvolve uma plataforma de Inteligência Artificial aplicada à gestão de serviços de saúde, com foco na predição e redução do absenteísmo em consultas, otimização de agendas, automação da comunicação com pacientes e melhor utilização da capacidade assistencial.
Este repositório reúne evidências técnicas do desenvolvimento da solução, incluindo arquitetura, componentes implementados, pipeline de dados, modelo preditivo, integrações, testes, exemplos anonimizados e histórico de evolução tecnológica.
As evidências institucionais e de validação externa — como cartas de intenção, registros de participação em eventos, demonstrações para gestores e documentos de piloto — são mantidas separadamente no repositório documental da startup.
---
3. Problema tecnológico
O absenteísmo em consultas médicas gera:
perda de capacidade assistencial;
aumento de filas de espera;
ociosidade de profissionais;
perda de receita em instituições privadas;
desperdício de recursos em instituições públicas;
dificuldade de reaproveitamento de vagas canceladas ou não utilizadas.
Grande parte das soluções existentes atua de forma reativa, utilizando lembretes padronizados, confirmações manuais ou reagendamentos após o cancelamento.
A proposta da Vitta Care é utilizar Inteligência Artificial e ciência de dados para antecipar o risco de ausência, permitindo que ações preventivas sejam executadas antes que a falta ocorra.
---
4. O que já foi desenvolvido
Registrar nesta seção apenas funcionalidades que já existam de fato.
Exemplo:
Plataforma para gestão de agendamentos;
Estrutura de cadastro e acompanhamento de consultas;
Pipeline inicial de preparação de dados;
Tratamento e transformação de dados históricos;
Engenharia de atributos para Machine Learning;
Modelo preditivo inicial para identificação de risco de ausência;
Geração de probabilidade de no-show;
Classificação de risco;
Dashboard de acompanhamento;
Integração entre dados de agendamento e camada de Inteligência Artificial;
Estrutura para automação de confirmações e comunicação;
Integrações com serviços externos;
Testes do modelo utilizando dados históricos;
Arquitetura preparada para evolução da inferência em nuvem.
> **Importante:** não declare como implementado algo que ainda esteja somente planejado.
---
5. Arquitetura da solução
Arquivo recomendado:
```text
docs/arquitetura.md
```
Descrever os principais componentes tecnológicos.
Exemplo de fluxo:
```text
Paciente / Agendamento
        ↓
Coleta de dados
        ↓
Preparação e tratamento
        ↓
Feature Engineering
        ↓
Modelo de Machine Learning
        ↓
Probabilidade de ausência
        ↓
Classificação de risco
        ↓
Motor de decisão
        ↓
Ações preventivas
        ↓
Confirmação / Reagendamento / Reaproveitamento de vaga
        ↓
Dashboard e acompanhamento
```
Adicionar também a imagem:
```text
diagrams/arquitetura-vitta-care.png
```
Componentes que podem ser documentados
Front-end da plataforma;
Back-end;
Banco de dados;
Serviços de autenticação;
Pipeline de dados;
Modelo de IA;
API de inferência;
Motor de automação;
Integrações de comunicação;
Monitoramento;
Segurança e auditoria.
---
6. Modelo Preditivo de Absenteísmo
Arquivo recomendado:
```text
docs/modelo-preditivo.md
```
Objetivo
O modelo preditivo tem como objetivo estimar a probabilidade de ausência associada a cada agendamento.
A previsão pode ser utilizada pelo sistema para direcionar ações preventivas e priorizar pacientes com maior probabilidade de falta.
Exemplo de variáveis
Utilizar somente variáveis efetivamente usadas no projeto.
Exemplos:
```text
dias_antecedencia
distancia_km
consultas_30d
taxa_hist
lembrete
feriado
is_weekend
periodo
idade
historico_faltas
```
Exemplo simplificado de código
> O exemplo abaixo deve ser apenas demonstrativo. Não é necessário publicar o código proprietário completo.
```python
features = [
    "dias_antecedencia",
    "distancia_km",
    "consultas_30d",
    "taxa_hist",
    "lembrete",
    "feriado",
    "is_weekend"
]

probabilidade = modelo.predict_proba(dados[features])[:, 1]
```
Resultado esperado
A saída da inferência pode ser convertida em uma classificação operacional de risco.
Exemplo:
```json
{
  "probabilidade_falta": 0.73,
  "classificacao": "RISCO_ELEVADO"
}
```
---
7. Pipeline de dados
Arquivo recomendado:
```text
docs/pipeline-dados.md
```
Estrutura sugerida:
```text
Dados históricos
      ↓
Validação dos registros
      ↓
Limpeza
      ↓
Tratamento de valores ausentes
      ↓
Normalização / transformação
      ↓
Feature Engineering
      ↓
Separação de treino e teste
      ↓
Treinamento
      ↓
Avaliação
      ↓
Modelo versionado
      ↓
Inferência
```
Documentar:
origem dos dados;
período analisado;
quantidade aproximada de registros;
processo de anonimização;
tratamento de campos inconsistentes;
criação das features;
separação de treino e validação;
métricas avaliadas;
versionamento do modelo.
> Não publicar dados pessoais ou informações que permitam identificar pacientes.
---
8. Exemplos anonimizados
Pasta recomendada:
```text
exemplos/
```
Exemplo de entrada
Arquivo:
```text
exemplo_inferencia.json
```
Conteúdo:
```json
{
  "dias_antecedencia": 14,
  "consultas_30d": 3,
  "taxa_hist": 0.27,
  "lembrete": true,
  "feriado": false,
  "is_weekend": false
}
```
Exemplo de saída
Arquivo:
```text
exemplo_resultado.json
```
Conteúdo:
```json
{
  "probabilidade_falta": 0.73,
  "classificacao": "RISCO_ELEVADO"
}
```
Dataset demonstrativo
Arquivo:
```text
exemplo_dados_anonimizados.csv
```
Utilizar apenas:
dados sintéticos;
dados anonimizados;
exemplos sem qualquer identificador pessoal;
dados sem CPF, nome, telefone, e-mail ou qualquer informação sensível.
---
9. Evidências visuais de desenvolvimento
Pasta:
```text
evidencias/
```
9.1 Screenshots
```text
evidencias/screenshots/
```
Sugestões:
tela de login;
agenda;
painel administrativo;
cadastro de agendamento;
classificação de risco;
confirmação de consulta;
reagendamento;
fila de espera;
automações;
telas da versão atual da plataforma.
Cada imagem deve possuir uma descrição curta.
Exemplo:
> **Figura 01 — Dashboard da plataforma Vitta Care.**  
> Tela utilizada para acompanhamento dos agendamentos e indicadores operacionais da instituição.
---
9.2 Dashboards
```text
evidencias/dashboards/
```
Podem ser apresentados:
número de consultas;
agendamentos confirmados;
faltas;
cancelamentos;
taxa de ocupação;
classificação de risco;
indicadores do modelo;
resultados de simulações.
---
9.3 Evidências do modelo de IA
```text
evidencias/modelo-ia/
```
Podem incluir:
prints do treinamento;
gráficos de métricas;
matriz de confusão;
ROC;
feature importance;
exemplos de inferência;
versões do modelo;
registros do ambiente de Machine Learning.
Somente incluir métricas realmente obtidas durante o desenvolvimento.
---
9.4 Testes
```text
evidencias/testes/
```
Registrar:
testes funcionais;
testes de API;
respostas de endpoints;
testes de integração;
logs anonimizados;
testes do pipeline;
testes de inferência.
---
10. Integrações
Arquivo:
```text
docs/integracoes.md
```
Documentar apenas integrações existentes ou efetivamente testadas.
Exemplos:
serviços de comunicação;
WhatsApp;
SMS;
e-mail;
APIs;
banco de dados;
ferramentas de automação;
serviços em nuvem;
autenticação;
Machine Learning.
Para cada integração, registrar:
```text
Nome:
Objetivo:
Status:
Forma de integração:
Resultado obtido:
Próxima evolução:
```
---
11. Testes e validação tecnológica
Arquivo:
```text
docs/testes-validacao.md
```
Estrutura sugerida:
Teste 01 — Pipeline de dados
Objetivo: validar processamento dos registros.
Entrada: dataset de teste.
Resultado: dados processados e preparados para o modelo.
Status: concluído / parcial / em evolução.
---
Teste 02 — Inferência
Objetivo: verificar geração da probabilidade de ausência.
Entrada: dados anonimizados de um agendamento.
Resultado: probabilidade e classificação de risco.
---
Teste 03 — Integração
Objetivo: validar comunicação entre plataforma e componente de IA.
Resultado esperado: previsão retornada e associada ao agendamento correspondente.
---
12. Evolução tecnológica
Arquivo:
```text
docs/evolucao-tecnologica.md
```
Esta seção é importante para demonstrar que a solução já existe, mas ainda possui desafios tecnológicos relevantes.
Modelo de texto:
> A primeira versão da Vitta Care permitiu validar os principais componentes da solução, incluindo preparação de dados, treinamento do modelo preditivo, geração de estimativas de risco e integração inicial com a plataforma.
>
> A próxima etapa de evolução tecnológica busca aumentar a robustez, escalabilidade, segurança, capacidade de integração, monitoramento e desempenho da solução, além de ampliar a validação em ambiente operacional relevante.
>
> Os desafios tecnológicos incluem evolução dos modelos de Inteligência Artificial, engenharia de dados, arquitetura de software, MLOps, explicabilidade, segurança da informação, interoperabilidade e validação em escala.
---
13. Desafios tecnológicos para a próxima etapa
Exemplos de desafios que podem ser apresentados ao ELDORADO:
evolução do modelo preditivo;
comparação entre diferentes algoritmos;
melhoria da qualidade e robustez das features;
explicabilidade das previsões;
monitoramento de drift;
reprocessamento e retreinamento;
arquitetura de inferência escalável;
versionamento de modelos;
MLOps;
segurança;
observabilidade;
integração com múltiplas instituições;
arquitetura multi-tenant;
interoperabilidade;
desempenho;
validação tecnológica em ambiente relevante;
testes de escalabilidade.
---
14. Histórico de evolução — CHANGELOG
Arquivo:
```text
CHANGELOG.md
```
Modelo:
```markdown
# Histórico de Evolução Tecnológica

## Versão 0.1
- Estrutura inicial da plataforma;
- Cadastro e gerenciamento de agendamentos;
- Primeiras telas operacionais.

## Versão 0.2
- Pipeline inicial de dados;
- Limpeza e preparação dos registros;
- Desenvolvimento inicial do modelo preditivo.

## Versão 0.3
- Integração das previsões à plataforma;
- Classificação de risco;
- Desenvolvimento de dashboards.

## Versão 0.4
- Evolução das automações;
- Melhorias na arquitetura;
- Integrações;
- Preparação para validação tecnológica ampliada.

## Próxima etapa
- Modelo preditivo v2;
- Arquitetura de inferência escalável;
- Engenharia de dados;
- MLOps;
- Segurança;
- Monitoramento;
- Validação ampliada em ambiente operacional.
```
Adapte as versões ao histórico real da Vitta Care.
---
15. Privacidade, LGPD e propriedade intelectual
Adicionar ao README:
> ## Privacidade e propriedade intelectual
>
> Por se tratar de uma plataforma aplicada ao setor de saúde, este repositório possui finalidade exclusivamente demonstrativa e documental.
>
> São disponibilizados somente materiais técnicos não sensíveis, documentação, exemplos anonimizados, diagramas, evidências de desenvolvimento e componentes demonstrativos.
>
> Não são disponibilizados publicamente:
>
> - dados pessoais de pacientes;
> - dados pessoais sensíveis;
> - bases de produção;
> - credenciais;
> - chaves de API;
> - tokens;
> - arquivos `.env`;
> - senhas;
> - segredos de infraestrutura;
> - código proprietário considerado estratégico;
> - informações protegidas por confidencialidade.
>
> Exemplos de dados são sintéticos ou anonimizados.
---
16. Segurança do repositório
Antes de tornar o repositório público, verificar se os seguintes arquivos estão no `.gitignore`:
```gitignore
.env
.env.*
*.key
*.pem
credentials.json
serviceAccount.json
firebase-adminsdk*.json
secrets/
private/
dados_reais/
datasets_producao/
```
Nunca publicar:
```text
API_KEY
OPENAI_API_KEY
AZURE_KEY
DATABASE_PASSWORD
FIREBASE_PRIVATE_KEY
JWT_SECRET
ZAPI_TOKEN
SMTP_PASSWORD
```
---
17. Separação entre GitHub e Google Drive
GitHub
Utilizar para:
desenvolvimento tecnológico;
arquitetura;
pipeline de dados;
modelo de IA;
screenshots;
testes;
exemplos anonimizados;
histórico de evolução;
integrações;
documentação técnica.
Google Drive
Utilizar para:
carta de intenção da Prefeitura / UBS;
evidências do piloto;
fotos do 68º Congresso de Municípios;
participação pelo Sebrae for Startups;
demonstrações para gestores;
certificados;
documentos institucionais;
apresentações;
relatórios complementares;
demais evidências externas.
---
18. Evidências externas
No README, deixar apenas uma referência às evidências externas.
Modelo:
```markdown
## Evidências externas e institucionais

As evidências institucionais e de validação externa da solução estão reunidas separadamente em ambiente documental controlado.

Incluem:

- carta de intenção para realização de piloto em UBS;
- registros de demonstração da solução;
- participação em programas de inovação;
- evidências de interação com gestores públicos;
- participação da Vitta Care no 68º Congresso de Municípios por meio do Sebrae for Startups;
- documentação complementar de validação.

Acesso:
[LINK DO GOOGLE DRIVE]
```
---
19. Links principais
Adicionar ao final do README:
```markdown
## Links

**Evidências técnicas / desenvolvimento**
GitHub: [LINK DO REPOSITÓRIO]

**Evidências institucionais / validação externa**
Google Drive: [LINK DA PASTA]

**Demonstração da plataforma**
Vídeo: [LINK]

**Site**
[LINK DA VITTA CARE]
```
---
20. Texto para o formulário do Programa ELDORADO
No campo:
25. Evidências do TRL (Links)
utilizar uma estrutura semelhante a:
> **Evidências de desenvolvimento tecnológico — GitHub:**  
> [LINK DO GITHUB]
>
> Repositório contendo documentação da arquitetura, evolução do software, modelo preditivo de absenteísmo, pipeline de dados, integrações, testes, exemplos anonimizados e evidências de implementação da plataforma Vitta Care.
>
> **Evidências de maturidade e validação externa — Google Drive:**  
> [LINK DO GOOGLE DRIVE]
>
> Pasta contendo documentação complementar, carta de intenção para piloto em UBS, registros de demonstração da solução, participação em ações do Sebrae for Startups e evidências de apresentação da plataforma a gestores públicos.
---
21. Checklist antes de publicar
README
[ ] Descrição clara da Vitta Care;
[ ] Problema apresentado;
[ ] Solução apresentada;
[ ] O que já está desenvolvido;
[ ] Arquitetura;
[ ] IA preditiva;
[ ] Pipeline de dados;
[ ] Integrações;
[ ] Testes;
[ ] Evolução tecnológica;
[ ] Próximos desafios;
[ ] Links externos.
Evidências
[ ] Screenshots atuais;
[ ] Dashboard;
[ ] Evidências do modelo;
[ ] Testes;
[ ] Diagramas;
[ ] Histórico de evolução;
[ ] Exemplos anonimizados.
Segurança
[ ] Nenhum dado pessoal;
[ ] Nenhum dado sensível;
[ ] Nenhuma senha;
[ ] Nenhum token;
[ ] Nenhuma chave de API;
[ ] Nenhum arquivo `.env`;
[ ] Nenhuma credencial de produção;
[ ] Nenhum código estratégico que a empresa não queira divulgar.
Links
[ ] GitHub público e acessível;
[ ] Drive configurado como “qualquer pessoa com o link pode visualizar”;
[ ] Vídeos acessíveis;
[ ] Links testados em janela anônima;
[ ] Arquivos com nomes claros.
---
22. Recomendações finais
Não transforme o GitHub em um depósito de arquivos.  
O README deve contar a história tecnológica da Vitta Care.
Não publique o código-fonte completo apenas para comprovar TRL.  
Documentação, exemplos e evidências técnicas podem ser suficientes.
Mostre evolução.  
O avaliador precisa perceber que houve desenvolvimento real ao longo do tempo.
Mostre o que já funciona e o que ainda é desafio tecnológico.  
Isso é particularmente importante para um programa de aceleração tecnológica.
Não declare funcionalidades futuras como já implementadas.
Não exponha informações de pacientes.
Use diagramas e screenshots.  
Eles tornam a avaliação muito mais rápida.
Coloque data ou versão nas evidências quando possível.
Mantenha o GitHub técnico e o Drive institucional.
Teste todos os links antes da submissão.
---
23. Resumo da estratégia de comprovação
```text
                    EVIDÊNCIAS TRL
                         │
          ┌──────────────┴──────────────┐
          │                             │
       GitHub                       Google Drive
          │                             │
 Desenvolvimento                Validação externa
 tecnológico                    e institucional
          │                             │
 Arquitetura                    Carta da Prefeitura
 IA / Machine Learning          UBS / piloto
 Pipeline de dados              Congresso de Municípios
 Integrações                    Sebrae for Startups
 Testes                         Demonstrações
 Screenshots                    Documentos
 Evolução                       Evidências de mercado
```
A combinação dos dois conjuntos de evidências deve mostrar que a Vitta Care possui:
desenvolvimento tecnológico real + solução funcional + evolução documentada + aplicação em contexto de saúde + caminho concreto para validação em ambiente operacional.
---
Vitta Care
VITTA CARE SOLUTIONS INOVA SIMPLES (I.S.)
Plataforma de Inteligência Artificial para predição e redução de absenteísmo, otimização de agendas e automação da jornada do paciente.
