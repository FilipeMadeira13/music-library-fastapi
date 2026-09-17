# BACKLOG — Biblioteca de Álbuns de Música (API FastAPI)

## 1. Contexto e Objetivo

Sistema para uso pessoal, com um único usuário (sem autenticação/multiusuário nesta fase), que permite catalogar uma coleção de álbuns de música organizados por artista e sortear um álbum aleatoriamente da biblioteca.

## 2. Decisões Arquiteturais Pré-Definidas

Com base nas respostas de escopo, ficam definidas as seguintes decisões técnicas para o MVP:

- **Framework de API:** FastAPI
- **Persistência:** SQLite (arquivo único em disco, não em memória — os dados devem sobreviver a reinicializações da aplicação)
- **Cadastro de dados:** manual, via endpoints CRUD da própria API (sem importação automática de fontes externas nesta fase)
- **Autenticação:** não há, nesta fase (sistema single-user)
- **Interface:** apenas API (sem front-end nesta fase); documentação interativa via OpenAPI/Swagger, nativa do FastAPI

## 3. Escopo do MVP

Está dentro do escopo desta primeira entrega:

- CRUD completo de Artistas
- CRUD completo de Álbuns, sempre vinculados a um Artista existente
- Listagem da biblioteca organizada/agrupada por artista
- Endpoint de sorteio aleatório de álbum, considerando toda a biblioteca
- Endpoint de sorteio aleatório de álbum restrito a um artista específico
- Validações de dados de entrada e de integridade referencial
- Tratamento padronizado de erros (recurso não encontrado, dados inválidos, etc.)
- Documentação automática da API

## 4. Fora de Escopo (nesta fase)

- Autenticação e autorização / múltiplos usuários
- Integração com serviços externos (Spotify, MusicBrainz, Discogs etc.)
- Front-end ou interface gráfica
- Upload/armazenamento de arquivos de áudio ou de imagens de capa (campo de capa, se existir, será apenas um texto/URL, sem upload)
- Deploy em nuvem, containerização e pipeline de CI/CD
- Histórico de sorteios, recomendações ou qualquer "inteligência" sobre o que sortear (o sorteio é puramente aleatório e uniforme)
- Paginação avançada, busca textual e filtros complexos (podem entrar em versões futuras)

## 5. Modelo Conceitual de Dados

### Entidade: Artista
| Campo | Obrigatório | Observações |
|---|---|---|
| id | Sim | Identificador único, gerado pelo sistema |
| nome | Sim | Não pode ser vazio |
| país de origem | Não | — |
| ano de início de carreira | Não | Se informado, deve ser um ano válido |
| data de criação/atualização | Sim | Preenchido automaticamente pelo sistema (auditoria) |

### Entidade: Álbum
| Campo | Obrigatório | Observações |
|---|---|---|
| id | Sim | Identificador único, gerado pelo sistema |
| título | Sim | Não pode ser vazio |
| artista_id | Sim | Deve referenciar um Artista existente |
| ano de lançamento | Não | Se informado, deve ser um ano válido e não pode ser futuro |
| gênero musical | Não | — |
| número de faixas | Não | Se informado, deve ser um número inteiro positivo |
| data de criação/atualização | Sim | Preenchido automaticamente pelo sistema (auditoria) |

### Relacionamento
- Um Artista possui zero ou muitos Álbuns (1:N).
- Um Álbum pertence a exatamente um Artista.
- Regra de exclusão de Artista com álbuns vinculados: **decisão pendente** — ver seção 9.

## 6. Épicos e Requisitos de Negócio

### Épico 1 — Gestão de Artistas
- **RN1.1** Como usuário, quero cadastrar um novo artista, para poder associar álbuns a ele.
- **RN1.2** Como usuário, quero listar todos os artistas cadastrados.
- **RN1.3** Como usuário, quero consultar os detalhes de um artista específico.
- **RN1.4** Como usuário, quero atualizar os dados de um artista.
- **RN1.5** Como usuário, quero remover um artista da biblioteca.

### Épico 2 — Gestão de Álbuns
- **RN2.1** Como usuário, quero cadastrar um álbum vinculado a um artista já existente.
- **RN2.2** Como usuário, quero listar todos os álbuns da biblioteca.
- **RN2.3** Como usuário, quero consultar os detalhes de um álbum específico.
- **RN2.4** Como usuário, quero atualizar os dados de um álbum.
- **RN2.5** Como usuário, quero remover um álbum da biblioteca.

### Épico 3 — Organização por Artista
- **RN3.1** Como usuário, quero visualizar minha biblioteca agrupada por artista, para navegar pela coleção de forma organizada.
- **RN3.2** Como usuário, quero listar todos os álbuns de um artista específico.

### Épico 4 — Sorteio Aleatório
- **RN4.1** Como usuário, quero sortear um álbum aleatório entre toda a minha biblioteca, para decidir o que ouvir.
- **RN4.2** Como usuário, quero sortear um álbum aleatório restrito aos álbuns de um artista específico.

### Épico 5 — Qualidade e Confiabilidade
- **RN5.1** O sistema não deve aceitar dados inválidos ou incompletos.
- **RN5.2** O sistema deve retornar mensagens de erro claras e em formato padronizado.
- **RN5.3** A API deve possuir documentação automática e sempre atualizada.

## 7. Critérios de Aceitação Técnicos

### 7.1 Cadastro de Artista (RN1.1)
- Dado que envio os dados de um novo artista com nome válido, quando a requisição é processada, então o artista é persistido e a resposta retorna o recurso criado com seu identificador.
- Dado que envio os dados de um artista sem nome (ou nome vazio), quando a requisição é processada, então o sistema rejeita a operação e retorna um erro de validação, sem persistir nada.

### 7.2 Consulta e Listagem de Artistas (RN1.2, RN1.3)
- Dado que existem artistas cadastrados, quando solicito a listagem, então recebo todos os artistas com seus dados básicos.
- Dado que solicito um artista por um identificador inexistente, quando a requisição é processada, então o sistema retorna um erro de "não encontrado", sem expor detalhes internos do sistema.

### 7.3 Atualização e Remoção de Artista (RN1.4, RN1.5)
- Dado que altero os dados de um artista existente com valores válidos, quando a requisição é processada, então os dados são atualizados e refletidos nas próximas consultas.
- Dado que solicito a remoção de um artista, quando ele possui álbuns vinculados, então o sistema aplica a regra definida na seção 9 (bloquear ou remover em cascata) de forma consistente e documentada.

### 7.4 Cadastro de Álbum (RN2.1)
- Dado que envio os dados de um álbum válido vinculado a um artista existente, quando a requisição é processada, então o álbum é persistido e associado corretamente ao artista.
- Dado que envio um álbum vinculado a um artista inexistente, quando a requisição é processada, então o sistema rejeita a operação e informa que o artista referenciado não existe.
- Dado que envio um álbum com ano de lançamento futuro ou número de faixas negativo, quando a requisição é processada, então o sistema rejeita a operação por dados inválidos.

### 7.5 Consulta, Atualização e Remoção de Álbum (RN2.2, RN2.3, RN2.4, RN2.5)
- Dado que existem álbuns cadastrados, quando solicito a listagem geral, então recebo todos os álbuns com seus dados e o artista associado identificável.
- Dado que solicito um álbum por identificador inexistente, quando a requisição é processada, então o sistema retorna um erro de "não encontrado".
- Dado que atualizo ou removo um álbum existente, quando a requisição é processada, então a alteração é refletida imediatamente nas consultas seguintes.

### 7.6 Organização por Artista (RN3.1, RN3.2)
- Dado que existem artistas com álbuns cadastrados, quando solicito a biblioteca agrupada, então recebo os artistas cada um com a lista de seus respectivos álbuns.
- Dado que solicito os álbuns de um artista específico que não possui nenhum álbum cadastrado, quando a requisição é processada, então recebo uma lista vazia (não um erro).
- Dado que solicito os álbuns de um artista inexistente, quando a requisição é processada, então o sistema retorna um erro de "não encontrado".

### 7.7 Sorteio Aleatório (RN4.1, RN4.2)
- Dado que existem álbuns cadastrados na biblioteca, quando solicito um sorteio geral, então recebo um único álbum escolhido de forma aleatória e uniforme (todo álbum tem a mesma probabilidade de ser sorteado).
- Dado que a biblioteca está vazia, quando solicito um sorteio, então o sistema retorna um erro claro informando que não há álbuns disponíveis, em vez de uma falha não tratada.
- Dado que solicito um sorteio filtrado por um artista específico que possui álbuns, quando a requisição é processada, então recebo um álbum aleatório apenas entre os álbuns daquele artista.
- Dado que solicito um sorteio filtrado por um artista sem álbuns cadastrados, quando a requisição é processada, então o sistema retorna um erro claro informando a ausência de álbuns para aquele artista.
- Dado que solicito um sorteio filtrado por um artista inexistente, quando a requisição é processada, então o sistema retorna um erro de "não encontrado" para o artista.

### 7.8 Tratamento de Erros (RN5.1, RN5.2)
- Todo erro de validação de entrada deve resultar em uma resposta com estrutura padronizada e consistente em toda a API (mesmo formato de mensagem de erro, independentemente do endpoint).
- Todo erro de recurso não encontrado deve ser diferenciável de um erro de dado inválido, tanto pelo código de status HTTP quanto pela mensagem retornada.
- Nenhuma exceção interna do sistema deve vazar detalhes técnicos (stack trace, nomes de tabelas, etc.) na resposta ao cliente.

### 7.9 Documentação (RN5.3)
- A documentação interativa da API deve estar acessível e refletir automaticamente todos os endpoints, parâmetros e modelos de dados existentes, sem necessidade de manutenção manual.

## 8. Requisitos Não Funcionais

- **Persistência durável:** os dados devem ser gravados em um arquivo SQLite em disco; reiniciar a aplicação não pode causar perda de dados.
- **Desempenho:** operações de listagem e sorteio devem responder rapidamente para o volume esperado de uma coleção pessoal (até alguns milhares de registros), sem necessidade de otimizações avançadas nesta fase.
- **Padrão de API:** os endpoints devem seguir convenções REST (recursos bem definidos, verbos HTTP semanticamente corretos, códigos de status HTTP apropriados para cada situação).
- **Validação centralizada:** toda entrada de dados deve ser validada antes de qualquer tentativa de persistência.
- **Testabilidade:** as regras de negócio críticas (cadastro, vínculo artista/álbum, sorteio e seus casos de borda) devem ser cobertas por testes automatizados.
- **Portabilidade do ambiente:** o projeto deve poder ser executado localmente a partir de instruções simples de setup, sem dependências de infraestrutura externa.
- **Organização do código:** a estrutura do projeto deve separar claramente camadas de API, regras de negócio e acesso a dados, para facilitar manutenção e evolução futura.

## 9. Perguntas em Aberto / Decisões Pendentes

Como Tech Lead, sinalizo os seguintes pontos que precisam da sua decisão como dono do produto antes (ou durante) da implementação:

1. **Exclusão de artista com álbuns vinculados:** bloquear a exclusão enquanto houver álbuns associados, ou excluir os álbuns automaticamente junto com o artista (cascade)?
2. **Duplicidade:** deve ser proibido cadastrar dois álbuns com o mesmo título para o mesmo artista? E dois artistas com o mesmo nome?
3. **Campos adicionais:** vale incluir, já no MVP, campos como "avaliação/nota" ou "favorito", já que a biblioteca é para uso pessoal? Ou isso fica para uma versão futura?
4. **Colaborações:** um álbum pode ter mais de um artista (ex.: colaborações, coletâneas), ou o modelo simples de um artista por álbum é suficiente?
5. **Paginação:** mesmo sendo uma coleção pessoal, deseja paginação nas listagens desde já, ou isso pode ser tratado apenas se a coleção crescer muito?

## 10. Definition of Done (DoD) do MVP

O projeto pode ser considerado pronto para esta fase quando:

- Todos os requisitos de negócio (seção 6) estiverem implementados e validados manualmente.
- Todos os critérios de aceitação técnicos (seção 7) estiverem cobertos por testes automatizados e passando.
- A documentação interativa da API estiver disponível e coerente com os endpoints implementados.
- As decisões pendentes (seção 9) estiverem resolvidas e refletidas no comportamento do sistema.
- Existir um README com instruções claras de como instalar dependências e executar o projeto localmente.
