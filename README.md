# Oficina Fácil

Sistema web acadêmico para gerenciamento de uma oficina mecânica. O projeto utiliza Python, Flask, SQLite, SQL nativo, Jinja2, HTML e CSS, seguindo a organização apresentada nos fascículos TaskFlow 01, 02 e 03 do curso.

## Funcionalidades

- Painel inicial com indicadores e últimas ordens de serviço.
- Cadastro, listagem, detalhe, edição e exclusão de clientes.
- Cadastro, listagem, edição e exclusão de veículos.
- Cadastro, listagem, edição e exclusão de serviços.
- Criação, consulta, atualização de status e exclusão de ordens de serviço.
- Relacionamentos entre clientes, veículos, ordens e serviços.
- Mensagens de sucesso e erro (`flash`) e página 404 personalizada.
- Consultas SQL parametrizadas para evitar SQL Injection.
- Scripts `.sql` para inclusão, testes de restrições, consultas e alterações.

## Requisitos

- Python 3.11 ou superior (recomendado pelo material do curso).
- pip.
- Git (para versionamento).
- VS Code (opcional, recomendado para acompanhar as aulas).
- DB Browser for SQLite (opcional, para visualizar o banco).

## Instalação no Windows (PowerShell)

Abra o terminal **dentro desta pasta**, onde estão `app.py` e `schema.sql`:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Caso o comando `py -3` não esteja disponível, use `python -m venv .venv`.

## Criar o banco e os dados iniciais

```powershell
flask --app app init-db
python executar.py inclusoes.sql
```

O ZIP já inclui `oficina.db` com dados fictícios para demonstração. O comando acima recria esse banco do zero; depois dele, execute o script de inclusões para carregar os exemplos.

**Atenção:** `flask --app app init-db` recria as tabelas e apaga os dados existentes. Use-o para a primeira configuração ou quando quiser reiniciar o banco. Depois, execute `python executar.py inclusoes.sql` novamente para carregar os dados fictícios.

## Executar o sistema

```powershell
flask --app app run --debug
```

Acesse http://127.0.0.1:5000 no navegador. Para testar a rota com parâmetro, abra, por exemplo, http://127.0.0.1:5000/ola/Maria.

Para encerrar o servidor, pressione `Ctrl + C` no terminal.

## Scripts SQL

Execute os comandos na pasta do projeto:

```powershell
python executar.py consultas.sql
python executar.py testes_regras.sql
python executar.py alteracoes.sql
```

- `schema.sql`: cria as tabelas, as chaves e as restrições.
- `inclusoes.sql`: adiciona dados fictícios (execute uma vez após inicializar o banco).
- `testes_regras.sql`: tenta inserir dados inválidos. As mensagens `ERRO` são esperadas, pois demonstram as restrições `NOT NULL`, `UNIQUE`, `CHECK` e `FOREIGN KEY`.
- `consultas.sql`: demonstra `INNER JOIN`, `LEFT JOIN`, `GROUP BY`, `LIKE` e `ORDER BY`.
- `alteracoes.sql`: demonstra `UPDATE` e `DELETE` em registros de exemplo.
- `executar.py`: ferramenta que executa um arquivo SQL e apresenta o resultado de cada comando. O caminho do banco é resolvido em relação à pasta do projeto.

## Estrutura do projeto

```text
oficina_facil/
├── app.py
├── db_sql.py
├── schema.sql
├── executar.py
├── inclusoes.sql
├── testes_regras.sql
├── consultas.sql
├── alteracoes.sql
├── requirements.txt
├── README.md
├── .gitignore
├── oficina.db (banco de demonstração com dados fictícios)
├── static/
│   └── style.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── ola.html
│   ├── clientes.html
│   ├── detalhe_cliente.html
│   ├── form_cliente.html
│   ├── veiculos.html
│   ├── form_veiculo.html
│   ├── servicos.html
│   ├── form_servico.html
│   ├── ordens.html
│   ├── form_ordem.html
│   ├── detalhe_ordem.html
│   ├── sobre.html
│   ├── contato.html
│   └── 404.html
└── tests/
    └── test_app.py
```

## Modelo de dados

- `clientes` 1:N `veiculos`.
- `veiculos` 1:N `ordens_servico`.
- `ordens_servico` N:N `servicos`, com a tabela associativa `os_servicos`.

As chaves estrangeiras usam `ON DELETE RESTRICT` quando um registro possui dependências que precisam ser preservadas. A tabela `os_servicos` usa `ON DELETE CASCADE`, pois os itens não fazem sentido sem a ordem de serviço. As conexões ativam `PRAGMA foreign_keys = ON`.

## Organização do código

- `app.py`: rotas, leitura de formulários, validações, mensagens e respostas HTTP.
- `db_sql.py`: conexão SQLite e todas as operações SQL.
- `schema.sql`: estrutura relacional e regras de integridade.
- `templates/`: HTML com herança Jinja2 a partir de `base.html`.
- `static/style.css`: aparência e responsividade.

As rotas não escrevem SQL diretamente. As consultas usam parâmetros `?`, e os formulários que alteram dados utilizam POST seguido de redirecionamento (POST-Redirect-GET).

## Git (checkpoint do projeto)

Depois de conferir a aplicação, registre a versão no Git:

```powershell
git init
git add .
git commit -m "Projeto Oficina Fácil com banco SQL e CRUD"
```

Não copie uma pasta `.venv` de outro computador ou projeto. O ambiente virtual guarda caminhos locais do Python; crie um novo com os comandos de instalação desta documentação.

## Testes automatizados

Com o ambiente virtual ativo e as dependências instaladas:

```powershell
python -m unittest discover -s tests -v
```

Os testes criam um banco temporário e não alteram o banco usado pela aplicação.
