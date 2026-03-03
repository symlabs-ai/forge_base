# ForgeBase — Guia de Documentação

> "Código que não explica seu propósito é código que não pensa."

Este guia estabelece os padrões e práticas de documentação para o ForgeBase, garantindo que cada componente carregue **intenção**, **contexto** e **capacidade de auto-explicação**.

---

## 🎯 Filosofia de Documentação

### Princípio Fundamental

**Documentação não é anotação — é pensamento materializado.**

No ForgeBase, documentação vai além de descrever *o que* o código faz. Ela deve explicar:
- **Por quê** foi implementado desta forma
- **Qual decisão arquitetural** foi tomada
- **Que problema** resolve
- **Como se relaciona** com outros componentes
- **Quando e onde** deve ser usado

### Reflexividade Documental

Assim como o código, a documentação deve ser **reflexiva**:
- Auto-explicativa
- Contextualizada
- Evolutiva (atualizada com o código)
- Útil para humanos e sistemas

---

## 📐 Padrão de Docstrings: reST Format

ForgeBase utiliza **reStructuredText (reST)** como formato padrão, compatível com Sphinx para geração automática de documentação.

### Anatomia de uma Docstring

```python
def method(self, param1: str, param2: int = 0) -> bool:
    """
    [LINHA 1: Resumo conciso em uma linha, presente do indicativo]

    [PARÁGRAFO 2+: Explicação detalhada do PORQUÊ, contexto arquitetural,
    decisões de design, e relação com outros componentes. Esta seção
    responde: Por que este método existe? Que problema resolve? Como
    se encaixa na arquitetura cognitiva?]

    [PARÁGRAFO OPCIONAL: Detalhes de implementação importantes,
    limitações conhecidas, casos especiais]

    :param param1: Descrição do parâmetro incluindo valores esperados
    :type param1: str
    :param param2: Descrição do segundo parâmetro com valor default
    :type param2: int
    :return: Descrição clara do que é retornado e quando
    :rtype: bool
    :raises ValueError: Quando param1 está vazio
    :raises TypeError: Quando param2 não é inteiro

    Example::

        >>> obj = MyClass()
        >>> obj.method("test", 42)
        True

    Note::

        Este método é thread-safe e pode ser chamado concorrentemente.

    Warning::

        Não usar em loops de alta performance (overhead de 50ms).

    See Also::

        :meth:`other_method` : Método relacionado para caso X
        :class:`RelatedClass` : Classe que usa este método
    """
```

---

## 📚 Templates por Tipo de Componente

### 1. Classes Base (EntityBase, UseCaseBase, PortBase, etc.)

```python
class EntityBase(ABC):
    """
    Classe base abstrata para todas as entidades de domínio no ForgeBase.

    Esta classe implementa o padrão de identidade única para entidades conforme
    Domain-Driven Design. Cada entidade possui um ID único que define sua
    identidade, independentemente de outros atributos. Esta abstração garante
    que entidades de domínio permaneçam isoladas de infraestrutura, mantendo
    a pureza do domain layer na Clean Architecture.

    A decisão de usar uma classe base abstrata (em vez de protocolo ou duck typing)
    foi tomada para enforçar contratos explícitos e facilitar validação em tempo
    de desenvolvimento. Isso reflete o princípio de Autonomia do ForgeBase:
    módulos com contratos bem definidos.

    :ivar id: Identificador único da entidade
    :vartype id: str

    Example::

        class User(EntityBase):
            def __init__(self, id: str, name: str):
                super().__init__(id)
                self.name = name

            def validate(self) -> None:
                if not self.name:
                    raise ValueError("Name cannot be empty")

        user = User("user-123", "Alice")
        user.validate()

    Note::

        Subclasses devem implementar o método validate() para enforçar
        invariantes específicas da entidade.

    Warning::

        Não usar EntityBase para objetos sem identidade própria. Para esses
        casos, use ValueObjectBase.

    See Also::

        :class:`ValueObjectBase` : Base para objetos sem identidade
        :class:`UseCaseBase` : Orquestração usando entidades
    """

    def __init__(self, id: Optional[str] = None):
        """
        Inicializa a entidade com um ID único.

        Se nenhum ID é fornecido, um UUID4 é gerado automaticamente. A escolha
        de UUID4 garante unicidade global sem necessidade de coordenação central,
        alinhado com o princípio de Autonomia.

        :param id: Identificador único da entidade (opcional)
        :type id: Optional[str]

        Example::

            # Com ID explícito
            entity = EntityBase("entity-123")

            # ID gerado automaticamente
            entity = EntityBase()
        """
        self.id = id or str(uuid.uuid4())

    @abstractmethod
    def validate(self) -> None:
        """
        Valida as invariantes da entidade.

        Este método abstrato deve ser implementado por todas as subclasses para
        enforçar as regras de negócio específicas da entidade. A validação deve
        lançar exceções específicas (preferencialmente do módulo domain.exceptions)
        quando invariantes são violadas.

        A decisão de usar um método explícito (em vez de validação automática
        no __init__) permite controle fino sobre quando validação ocorre, útil
        em cenários de reconstrução de entidades do banco de dados.

        :raises InvariantViolation: Quando uma regra de negócio é violada
        :raises ValidationError: Quando dados são inválidos

        Example::

            class Product(EntityBase):
                def validate(self) -> None:
                    if self.price < 0:
                        raise InvariantViolation("Price cannot be negative")

        See Also::

            :mod:`domain.exceptions` : Exceções de domínio
            :mod:`domain.validators` : Validadores reutilizáveis
        """
        pass
```

### 2. Casos de Uso (UseCases)

```python
class CreateUserUseCase(UseCaseBase):
    """
    Caso de uso para criação de novos usuários no sistema.

    Este UseCase implementa a lógica de aplicação para registrar um novo usuário,
    orquestrando validações de domínio, verificações de duplicidade, e persistência.
    Seguindo Clean Architecture, este UseCase permanece independente de frameworks
    e infraestrutura, comunicando-se apenas através de Ports.

    O fluxo de execução segue o padrão:
    1. Validar dados de entrada (DTO)
    2. Verificar se email já existe (via UserRepositoryPort)
    3. Criar entidade User com invariantes validados
    4. Persistir via repositório
    5. Retornar DTO de resposta

    Este UseCase está instrumentado com observabilidade nativa via decorator
    @track_metrics, coletando automaticamente duração, sucesso/falha, e contexto.

    :ivar user_repository: Port para acesso ao repositório de usuários
    :vartype user_repository: UserRepositoryPort
    :ivar logger: Port para logging estruturado
    :vartype logger: LoggerPort

    Example::

        # Injeção de dependências
        repository = JSONUserRepository("data/users.json")
        logger = StdoutLogger()
        usecase = CreateUserUseCase(repository, logger)

        # Execução
        input_dto = CreateUserInputDTO(
            email="alice@example.com",
            name="Alice"
        )
        output_dto = usecase.execute(input_dto)

        print(f"User created: {output_dto.user_id}")

    Note::

        Este UseCase é idempotente: se chamado múltiplas vezes com mesmo email,
        retornará erro após primeira criação bem-sucedida.

    Warning::

        Não chamar este UseCase diretamente em loops. Use batch operations
        para criação de múltiplos usuários.

    See Also::

        :class:`User` : Entidade de domínio
        :class:`UserRepositoryPort` : Contrato do repositório
        :class:`CreateUserInputDTO` : DTO de entrada
    """

    def __init__(
        self,
        user_repository: UserRepositoryPort,
        logger: LoggerPort
    ):
        """
        Inicializa o caso de uso com dependências injetadas.

        A injeção de dependências via construtor (Dependency Injection) é o
        padrão do ForgeBase, garantindo testabilidade e desacoplamento. Todos
        os colaboradores são recebidos como abstrações (Ports), nunca como
        implementações concretas.

        :param user_repository: Repositório para persistência de usuários
        :type user_repository: UserRepositoryPort
        :param logger: Logger para registro de eventos
        :type logger: LoggerPort
        """
        self.user_repository = user_repository
        self.logger = logger

    @track_metrics(name="create_user")
    def execute(self, input_dto: CreateUserInputDTO) -> CreateUserOutputDTO:
        """
        Executa a criação de um novo usuário.

        Este método implementa toda a lógica de orquestração para criação
        de usuário, incluindo validações, verificações de negócio, e persistência.

        Decisões de design:
        - Validação de entrada ocorre no DTO antes de chegar aqui
        - Verificação de duplicidade usa repositório (não cache) para garantir
          consistência mesmo em ambientes distribuídos
        - Invariantes da entidade são validados antes de persistir

        :param input_dto: Dados de entrada validados
        :type input_dto: CreateUserInputDTO
        :return: DTO com resultado da operação
        :rtype: CreateUserOutputDTO
        :raises UserAlreadyExistsError: Quando email já está cadastrado
        :raises ValidationError: Quando dados de entrada são inválidos
        :raises RepositoryError: Quando falha ao persistir

        Example::

            input_dto = CreateUserInputDTO(
                email="bob@example.com",
                name="Bob"
            )

            try:
                output = usecase.execute(input_dto)
                print(f"Success: {output.user_id}")
            except UserAlreadyExistsError:
                print("Email already registered")

        Note::

            Métricas coletadas automaticamente:
            - create_user.duration (ms)
            - create_user.success (counter)
            - create_user.errors (counter)

        See Also::

            :meth:`_validate_email_unique` : Validação de unicidade
            :meth:`_create_user_entity` : Criação da entidade
        """
        self.logger.info("Creating new user", email=input_dto.email)

        # Verificar se email já existe
        if self.user_repository.find_by_email(input_dto.email):
            raise UserAlreadyExistsError(f"Email {input_dto.email} already exists")

        # Criar entidade
        user = User(
            id=None,  # Auto-generated
            email=input_dto.email,
            name=input_dto.name
        )
        user.validate()

        # Persistir
        self.user_repository.save(user)

        self.logger.info("User created successfully", user_id=user.id)

        return CreateUserOutputDTO(
            user_id=user.id,
            email=user.email,
            created_at=datetime.now()
        )
```

### 3. Ports (Interfaces de Comunicação)

```python
class UserRepositoryPort(PortBase, ABC):
    """
    Port (interface) para acesso ao repositório de usuários.

    Este Port define o contrato de comunicação entre a camada de aplicação
    e a camada de infraestrutura para persistência de usuários. Seguindo
    o padrão Hexagonal Architecture (Ports & Adapters), este Port é uma
    abstração que permite múltiplas implementações (JSON, SQL, MongoDB, etc)
    sem afetar a lógica de aplicação.

    Decisões de design:
    - Métodos retornam Optional[User] em vez de lançar exceções quando não
      encontrado, para diferenciar "não encontrado" de "erro"
    - Usa User (entidade) e não DTO, pois este Port está na fronteira entre
      application e domain (ainda não cruzou para fora do sistema)
    - Métodos são síncronos; versão async seria UserRepositoryAsyncPort

    Este é um "driven port" (secundário) pois é chamado pela aplicação,
    não a chama.

    Example::

        # Implementação concreta
        class JSONUserRepository(UserRepositoryPort):
            def save(self, user: User) -> None:
                # Implementação com JSON
                pass

        # Uso no UseCase
        class CreateUserUseCase:
            def __init__(self, repo: UserRepositoryPort):
                self.repo = repo  # Depende da abstração, não da implementação

    Note::

        Este Port segue o Repository Pattern do Domain-Driven Design,
        fornecendo uma abstração de coleção para entidades.

    See Also::

        :class:`User` : Entidade manipulada pelo repositório
        :class:`RepositoryBase` : Base genérica para repositórios
        :class:`JSONUserRepository` : Implementação em JSON
    """

    @abstractmethod
    def save(self, user: User) -> None:
        """
        Persiste um usuário no repositório.

        Implementações devem ser idempotentes: salvar o mesmo usuário (mesmo ID)
        múltiplas vezes deve atualizar, não criar duplicatas. Esta decisão
        simplifica lógica de aplicação e previne inconsistências.

        :param user: Entidade de usuário a ser persistida
        :type user: User
        :raises RepositoryError: Quando falha ao persistir

        Example::

            user = User(id="user-123", email="alice@example.com")
            repository.save(user)

        Note::

            Este método deve validar se user.validate() passa antes de persistir.
        """
        pass

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        """
        Busca um usuário por ID.

        Retorna None se não encontrado (em vez de lançar exceção), permitindo
        que camada de aplicação decida como lidar com ausência.

        :param user_id: ID único do usuário
        :type user_id: str
        :return: Usuário encontrado ou None
        :rtype: Optional[User]
        :raises RepositoryError: Quando erro de infraestrutura ocorre

        Example::

            user = repository.find_by_id("user-123")
            if user:
                print(f"Found: {user.name}")
            else:
                print("User not found")
        """
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """
        Busca um usuário por email.

        Email é tratado como campo único (invariante de negócio). Implementações
        devem garantir que apenas um usuário pode ter determinado email.

        :param email: Email do usuário (case-insensitive)
        :type email: str
        :return: Usuário encontrado ou None
        :rtype: Optional[User]
        :raises RepositoryError: Quando erro de infraestrutura ocorre

        Note::

            Comparação de email deve ser case-insensitive.

        Example::

            user = repository.find_by_email("ALICE@example.com")
            # Encontra "alice@example.com"
        """
        pass

    def info(self) -> dict:
        """
        Retorna informações sobre este Port para introspecção.

        Implementação padrão do PortBase, fornece metadados sobre o contrato.

        :return: Dicionário com metadados do Port
        :rtype: dict

        Example::

            port_info = repository.info()
            print(f"Port: {port_info['name']}")
            print(f"Methods: {port_info['methods']}")
        """
        return {
            "name": "UserRepositoryPort",
            "type": "driven",
            "methods": ["save", "find_by_id", "find_by_email"],
            "entity": "User"
        }
```

### 4. Adapters

```python
class JSONUserRepository(UserRepositoryPort):
    """
    Implementação de UserRepositoryPort usando persistência em JSON.

    Este Adapter implementa o contrato UserRepositoryPort persistindo dados
    em arquivo JSON no filesystem. É uma implementação simples adequada para
    desenvolvimento, testes, e aplicações de pequeno porte.

    Decisões de implementação:
    - Usa file locking para garantir thread-safety
    - Carrega arquivo inteiro em memória (não adequado para grandes volumes)
    - Serializa User para dict usando padrão to_dict()/from_dict()
    - Cria arquivo automaticamente se não existir

    Limitações conhecidas:
    - Não adequado para >10k usuários (performance)
    - Não suporta transações multi-operação
    - Não é adequado para ambientes distribuídos (arquivo local)

    :ivar file_path: Caminho do arquivo JSON
    :vartype file_path: str
    :ivar _lock: Lock para sincronização de acesso
    :vartype _lock: threading.Lock

    Example::

        # Inicialização
        repository = JSONUserRepository("data/users.json")

        # Uso
        user = User(id="user-123", email="alice@example.com")
        repository.save(user)

        found = repository.find_by_email("alice@example.com")
        assert found.id == "user-123"

    Note::

        Para ambientes de produção com múltiplos processos, use
        SQLUserRepository ou MongoUserRepository.

    Warning::

        Arquivo JSON pode crescer indefinidamente. Implementar lógica de
        arquivamento/limpeza se necessário.

    See Also::

        :class:`UserRepositoryPort` : Interface implementada
        :class:`SQLUserRepository` : Implementação para produção
        :class:`User` : Entidade persistida
    """

    def __init__(self, file_path: str):
        """
        Inicializa o repositório JSON.

        Cria o arquivo se não existir. Cria diretórios intermediários se necessário.

        :param file_path: Caminho completo do arquivo JSON
        :type file_path: str
        :raises PermissionError: Quando não tem permissão para criar/escrever

        Example::

            repo = JSONUserRepository("/var/data/users.json")
        """
        self.file_path = file_path
        self._lock = threading.Lock()
        self._ensure_file_exists()
```

### 5. DTOs (Data Transfer Objects)

```python
class CreateUserInputDTO(DTOBase):
    """
    DTO de entrada para criação de usuário.

    Este DTO encapsula todos os dados necessários para criar um novo usuário,
    com validação automática de estrutura e tipos. DTOs são usados para
    transferir dados entre camadas (ex: de Adapter para UseCase) mantendo
    isolamento de responsabilidades.

    Decisão de usar dataclass + validação explícita em vez de Pydantic:
    - Evita dependência externa no core
    - Validação mais explícita e documentada
    - Melhor controle sobre mensagens de erro

    :ivar email: Email do novo usuário (deve ser único)
    :vartype email: str
    :ivar name: Nome completo do usuário
    :vartype name: str
    :ivar age: Idade do usuário (opcional, deve ser ≥18 se fornecido)
    :vartype age: Optional[int]

    Example::

        # Criação válida
        dto = CreateUserInputDTO(
            email="alice@example.com",
            name="Alice Silva",
            age=25
        )

        # Validação automática
        dto.validate()  # OK

        # Criação inválida
        dto = CreateUserInputDTO(email="invalid", name="")
        dto.validate()  # Raises ValidationError

    Note::

        Validação ocorre em validate(), não em __init__, permitindo
        construção parcial para testes ou parsing gradual.

    See Also::

        :class:`CreateUserOutputDTO` : DTO de resposta
        :class:`CreateUserUseCase` : UseCase que consome este DTO
    """

    def __init__(self, email: str, name: str, age: Optional[int] = None):
        """
        Inicializa o DTO com dados de entrada.

        :param email: Email do usuário
        :type email: str
        :param name: Nome do usuário
        :type name: str
        :param age: Idade do usuário (opcional)
        :type age: Optional[int]
        """
        self.email = email
        self.name = name
        self.age = age

    def validate(self) -> None:
        """
        Valida a estrutura e valores do DTO.

        Validações aplicadas:
        - Email deve ter formato válido (regex)
        - Nome não pode estar vazio
        - Idade, se fornecida, deve ser ≥18

        :raises ValidationError: Quando alguma validação falha

        Example::

            dto = CreateUserInputDTO(email="test", name="", age=15)
            dto.validate()  # Raises ValidationError com múltiplas mensagens
        """
        errors = []

        if not self.email or "@" not in self.email:
            errors.append("Email must be valid")

        if not self.name or not self.name.strip():
            errors.append("Name cannot be empty")

        if self.age is not None and self.age < 18:
            errors.append("Age must be at least 18")

        if errors:
            raise ValidationError("; ".join(errors))
```

### 6. Funções Utilitárias

```python
def validate_email(email: str) -> bool:
    """
    Valida formato de email usando regex.

    Esta função implementa validação básica de email, verificando presença
    de @ e domínio. Não é validação completa segundo RFC 5322 (que é
    extremamente complexa), mas cobre 99% dos casos práticos.

    Decisão de usar regex simples em vez de biblioteca externa:
    - Evita dependência para funcionalidade básica
    - Performance superior para validação simples
    - Controle total sobre regras

    Para validação completa (ex: verificar MX records), use biblioteca
    externa como email-validator.

    :param email: String de email a validar
    :type email: str
    :return: True se formato é válido, False caso contrário
    :rtype: bool

    Example::

        >>> validate_email("alice@example.com")
        True
        >>> validate_email("invalid")
        False
        >>> validate_email("test@")
        False

    Note::

        Esta função NÃO verifica se email existe, apenas formato.

    Warning::

        Não usar para validação de segurança crítica sem validação adicional.

    See Also::

        :mod:`domain.validators` : Outros validadores de domínio
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

---

## ✅ Checklist de Qualidade de Docstring

Antes de considerar uma docstring completa, verifique:

### Conteúdo Essencial
- [ ] **Linha 1**: Resumo conciso e claro
- [ ] **Parágrafo explicativo**: Explica o PORQUÊ, não apenas o QUE
- [ ] **Todos os parâmetros**: Documentados com :param e :type
- [ ] **Retorno**: Documentado com :return e :rtype
- [ ] **Exceções**: Todas as exceções possíveis documentadas
- [ ] **Exemplo**: Pelo menos um exemplo de uso funcional

### Contexto Arquitetural
- [ ] Explica onde o componente se encaixa na arquitetura
- [ ] Menciona decisões de design relevantes
- [ ] Relaciona com outros componentes (See Also)
- [ ] Identifica limitações conhecidas

### Usabilidade
- [ ] Exemplos podem ser copiados e executados
- [ ] Warnings para armadilhas comuns
- [ ] Notes para informações importantes
- [ ] Links para documentação relacionada

### Formato
- [ ] Usa sintaxe reST correta
- [ ] Indentação consistente
- [ ] Sem erros de ortografia
- [ ] Código de exemplo com syntax highlight

---

## 🎨 Diretrizes de Estilo

### Tom e Voz

**Faça:**
- Use voz ativa: "Este método valida..."
- Seja direto e claro
- Explique decisões: "Escolhemos X porque Y..."
- Use exemplos práticos

**Não faça:**
- Voz passiva: "A validação é feita..."
- Jargão sem explicação
- Documentação óbvia: "Este método retorna um bool" (se já está no type hint)

### Estrutura de Parágrafos

```python
"""
[Linha 1: O QUE faz - presente do indicativo, conciso]

[Parágrafo 2: POR QUE existe - contexto, problema que resolve]

[Parágrafo 3: COMO funciona - detalhes de implementação importantes]

[Parágrafo 4: QUANDO/ONDE usar - casos de uso, relação com arquitetura]
"""
```

### Exemplos de Código

```python
Example::

    >>> # Caso simples e direto
    >>> result = function(param)
    >>> assert result == expected

    >>> # Caso com contexto
    >>> obj = MyClass(config)
    >>> try:
    ...     obj.method()
    ... except ValueError:
    ...     print("Handled error")

    >>> # Caso real de uso
    >>> with open("data.json") as f:
    ...     data = json.load(f)
    >>> processor = DataProcessor()
    >>> output = processor.process(data)
```

---

## 🔍 Documentando por Camada

### Domain Layer
**Foco:** Regras de negócio, invariantes, conceitos de domínio

```python
"""
Esta entidade representa [conceito de negócio].

No contexto de [domínio], [conceito] é definido como [definição clara].
Invariantes fundamentais:
- [Invariante 1]
- [Invariante 2]

Esta implementação garante [garantia] através de [mecanismo].
"""
```

### Application Layer
**Foco:** Orquestração, fluxo de casos de uso, coordenação

```python
"""
Este UseCase orquestra [fluxo de negócio].

Fluxo de execução:
1. [Passo 1]
2. [Passo 2]
3. [Passo 3]

Decisões de orquestração:
- [Decisão 1]: [Razão]
- [Decisão 2]: [Razão]

Integra-se com [outros componentes] para [propósito].
"""
```

### Infrastructure Layer
**Foco:** Detalhes técnicos, limitações, performance

```python
"""
Implementação de [contrato] usando [tecnologia].

Características técnicas:
- Performance: [O(n), limites, benchmarks]
- Thread-safety: [sim/não, mecanismo]
- Limitações: [limite 1, limite 2]

Adequado para [cenário]. Para [outro cenário], use [alternativa].
"""
```

### Adapters Layer
**Foco:** Interface externa, conversão, integração

```python
"""
Adapter para integração com [sistema externo].

Este adapter converte entre [formato interno] e [formato externo],
garantindo [garantia] durante a tradução.

Responsável por:
- [Responsabilidade 1]
- [Responsabilidade 2]

Protocolo de comunicação: [detalhes do protocolo]
"""
```

---

## 📦 Documentação de Módulos

Cada arquivo Python deve ter docstring no topo:

```python
"""
Domain validators for ForgeBase.

Este módulo fornece validadores reutilizáveis para enforçar regras de
negócio e invariantes em entidades de domínio. Validadores são funções
puras que retornam bool ou lançam ValidationError.

Filosofia de validação:
- Fail fast: Validar na construção da entidade
- Mensagens claras: Erros explicam o que está errado e por quê
- Composição: Validadores podem ser combinados

Validadores disponíveis:
- not_null: Verifica presença de valor
- not_empty: Verifica string/lista não vazia
- in_range: Verifica valor numérico em range
- matches_pattern: Verifica regex

Example::

    from forge_base.domain.validators import not_empty, in_range

    class Product(EntityBase):
        def validate(self):
            not_empty(self.name, "Product name")
            in_range(self.price, 0, 1000000, "Price")

Author: Jorge, The Forge
Created: 2025-11-03
"""
```

---

## 🚀 Ferramentas e Automação

### Validação de Docstrings

```bash
# Verificar docstrings presentes
pydocstyle src/forge_base/

# Gerar documentação com Sphinx
cd docs
make html

# Verificar links quebrados
sphinx-build -b linkcheck . _build
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-docstrings
        name: Check docstrings
        entry: pydocstyle
        language: system
        types: [python]
        args: ['--convention=google']
```

---

## 📊 Métricas de Documentação

### Alvos de Qualidade

| Métrica | Alvo | Atual |
|---------|------|-------|
| Classes com docstring | 100% | 0% |
| Métodos públicos documentados | 100% | 0% |
| Exemplos de código | ≥1 por classe | 0 |
| Links See Also | ≥2 por componente | 0 |
| Docstrings com "porquê" | 100% | 0% |

### Como Medir

```python
# Script: scripts/check_documentation.py
def count_documented_classes():
    """Conta classes com docstrings adequadas."""
    pass

def check_docstring_quality():
    """Verifica qualidade de docstrings (comprimento, seções)."""
    pass
```

---

## 🎓 Princípios de Documentação ForgeBase

### 1. Reflexividade
> "Documentação que explica seu próprio propósito"

- Docstrings devem documentar não só código, mas também **por que existem**
- Meta-documentação: "Esta classe existe porque [razão arquitetural]"

### 2. Autonomia
> "Documentação auto-contida e completa"

- Cada docstring deve ser compreensível isoladamente
- Contexto suficiente sem precisar ler outros arquivos
- Links para conceitos relacionados quando necessário

### 3. Coerência Cognitiva
> "Documentação alinhada com intenção"

- O que o código faz deve refletir o que documentação diz
- Atualizar documentação junto com código (não depois)
- Documentação de teste explica intenção do teste

---

## 📝 Templates Rápidos

### Método Simples
```python
def method(param: str) -> int:
    """
    [O que faz].

    [Por que existe / quando usar].

    :param param: [Descrição]
    :type param: str
    :return: [O que retorna]
    :rtype: int
    """
```

### Classe Simples
```python
class MyClass:
    """
    [O que é / propósito].

    [Como se encaixa na arquitetura / decisões de design].

    :ivar attr: [Descrição]
    :vartype attr: type
    """
```

### Função com Exemplo
```python
def function(x: int) -> bool:
    """
    [O que faz].

    :param x: [Descrição]
    :type x: int
    :return: [Descrição]
    :rtype: bool

    Example::

        >>> function(42)
        True
    """
```

---

## 🔗 Referências

- **reST Primer**: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
- **Google Python Style Guide**: https://google.github.io/styleguide/pyguide.html
- **PEP 257**: https://www.python.org/dev/peps/pep-0257/
- **Sphinx Domains**: https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html

---

## ✅ Critérios de "Done" para Documentação

Uma classe/método está completamente documentado quando:

- [x] Possui docstring reST formatada
- [x] Explica **o porquê**, não apenas o quê
- [x] Todos os parâmetros e retorno documentados
- [x] Todas as exceções documentadas
- [x] Pelo menos 1 exemplo funcional
- [x] Links para componentes relacionados
- [x] Warnings para armadilhas comuns
- [x] Validado por pydocstyle
- [x] Revisado por humano (não apenas auto-gerado)

---

*"Documentação não é tarefa final — é pensamento contínuo materializado em texto."*

**— Jorge, The Forge**
