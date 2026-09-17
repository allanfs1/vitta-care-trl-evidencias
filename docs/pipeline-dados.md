# Pipeline de Dados e Engenharia de Features

O pipeline de dados da **Vitta Care** foi estruturado para processar volumes contínuos de agendamentos ambulatoriais, garantindo integridade analítica, governança e conformidade estrita com a LGPD (Lei Geral de Proteção de Dados).

---

## 1. Fluxograma do Pipeline

```text
[ Dados Brutos de Agendamento (EHR / Sistema da Clínica) ]
                         │
                         ▼
[ 1. Validação de Esquema e Tipagem ]
                         │
                         ▼
[ 2. Higienização e Desidentificação PHI Guard ]
                         │
                         ▼
[ 3. Tratamento de Outliers e Valores Ausentes ]
                         │
                         ▼
[ 4. Feature Engineering (Janelas Temporais, Taxas Históricas) ]
                         │
                         ▼
[ 5. Divisão Temporal (Out-of-Time Split - sem vazamento) ]
                         │
                         ▼
[ 6. Treinamento e Calibração Probabilística ]
                         │
                         ▼
[ 7. Versionamento do Artefato (MLflow / Registry) ]
                         │
                         ▼
[ 8. Serviço de Inferência (API REST / Batch Diário) ]
```

---

## 2. Etapas Detalhadas

### 2.1 Higienização e PHI Guard (Privacy-Preserving)
- Remoção determinística de identificadores diretos: Nome completo, CPF, RG, número de telefone, endereço residencial e prontuário físico.
- Transformação de endereço em distância euclidiana/manhattan agregada (`distancia_km`) e classificação de turno (`periodo`).
- Anonimização de chaves primárias utilizando hashing irreversível (SHA-256 com salt) antes de qualquer persistência no repositório analítico.

### 2.2 Engenharia de Atributos (Feature Engineering)
- **Janelas Móveis:** Cálculo da taxa de absenteísmo individual nas últimas 3, 5 e 10 consultas.
- **Sazonalidade Calendárica:** Identificação de vésperas de feriados, pontes de emendas e dias atípicos.
- **Interação Multicanal:** Métricas de tempo de resposta da mensagem de confirmação no WhatsApp (ex.: respondeu em <15 min vs sem resposta).

### 2.3 Estratégia de Particionamento (Split Temporal)
Para prevenir vazamento de dados (*data leakage*):
- O particionamento é estritamente **temporal (Out-of-Time)**, onde os modelos são treinados com meses anteriores $M_{1} \dots M_{k}$ e validados nos meses subsequentes $M_{k+1}$.
- Garantia de que informações futuras sobre desfechos de consultas não influenciem o treinamento.

### 2.4 Versionamento e Monitoramento Contínuo
- Rastreabilidade de cada modelo gerado com metadados de treino, hiperparâmetros e métricas de corte.
- Monitoramento de deriva de dados (*data drift*) e deriva de conceito (*concept drift*) para re-treinamento adaptativo.
