# 🔐 Sistema de Autenticação - Mapa de Despesas Automático

## Visão Geral

O sistema de autenticação foi implementado para proteger o acesso ao aplicativo de gestão de despesas, garantindo que apenas utilizadores autorizados possam aceder e gerar mapas de despesas.

## Funcionalidades de Segurança

### 🔑 Autenticação por Utilizador

- **Login seguro** com nome de utilizador e palavra-passe
- **Sessões controladas** com timeout automático (1 hora por defeito)
- **Logout seguro** que limpa todas as informações da sessão

### 👥 Controlo de Acesso Baseado em Papéis

#### Administrador (`admin`)

- **Acesso total** a todas as funcionalidades
- Pode **editar dados da empresa** e gestor
- Pode definir **valores acima dos limites legais**
- Acesso ao **log de auditoria**
- Valores máximos diários e totais aumentados

#### Gestor (`gestor`)

- **Acesso standard** às funcionalidades principais
- **Dados da empresa bloqueados** (só visualização)
- Limitado aos **valores legais** definidos
- Não tem acesso ao log de auditoria

### 📋 Log de Auditoria

O sistema regista automaticamente todas as atividades importantes:

- **Logins e logouts** (incluindo tentativas falhadas)
- **Geração de mapas de despesas**
- **Downloads de ficheiros Excel**
- **Alterações de configurações**

#### Informações Registadas

- Timestamp da ação
- Utilizador que executou a ação
- Papel do utilizador
- Detalhes da ação
- Identificador da sessão

### 🔒 Medidas de Segurança

1. **Gestão de Sessões**

   - Timeout automático de sessão
   - Limpeza segura do estado da sessão
   - Verificação contínua de validade

2. **Proteção de Dados**

   - Dados sensíveis marcados no audit log
   - Credenciais armazenadas em ficheiros de segredos
   - Ficheiros sensíveis excluídos do controlo de versão

3. **Controlo de Acesso**
   - Verificação de autenticação em cada ação
   - Restrições baseadas em papéis
   - Validação de permissões

## Configuração

### Credenciais de Teste

Por defeito, o sistema vem configurado com as seguintes credenciais:

```
Administrador:
- Utilizador: admin
- Palavra-passe: accounting2025!

Gestor:
- Utilizador: gestor
- Palavra-passe: gestor123!
```

### Configuração Personalizada

Para configurar credenciais personalizadas, edite o ficheiro `.streamlit/secrets.toml`:

```toml
[auth]
admin_username = "admin"
admin_password = "sua_palavra_passe_segura"
gestor_username = "gestor"
gestor_password = "outra_palavra_passe_segura"

[app]
session_timeout = 3600  # Timeout em segundos (1 hora)
```

## Estrutura de Ficheiros

```
├── auth.py                    # Módulo de autenticação
├── audit_log.py              # Sistema de auditoria
├── .streamlit/
│   └── secrets.toml          # Credenciais (NÃO incluir no Git)
├── audit_log.json            # Log de atividades (gerado automaticamente)
└── .gitignore                # Excluir ficheiros sensíveis
```

## Utilização

### Para Utilizadores

1. **Aceder à aplicação** - será solicitado login automático
2. **Inserir credenciais** no formulário de autenticação
3. **Utilizar a aplicação** normalmente
4. **Terminar sessão** quando terminar (recomendado)

### Para Administradores

1. Fazer login como administrador
2. Aceder ao **"Log de Auditoria"** através do sidebar
3. **Filtrar e analisar** atividades dos utilizadores
4. **Configurar dados da empresa** conforme necessário

## Segurança e Melhores Práticas

### ⚠️ Importante

- **Nunca** partilhe as credenciais
- **Sempre** termine a sessão quando terminar de usar
- **Altere** as palavras-passe por defeito em produção
- **Mantenha** o ficheiro `secrets.toml` seguro e fora do Git

### 🏭 Produção

Para um ambiente de produção, considere:

1. **Integração com SSO** (Single Sign-On)
2. **Autenticação multi-factor** (MFA)
3. **Palavras-passe mais complexas**
4. **Rotação regular de credenciais**
5. **Monitorização avançada** dos logs

## Resolução de Problemas

### Problemas Comuns

1. **"Sessão expirada"**

   - Faça login novamente
   - Verifique o timeout configurado

2. **"Credenciais incorretas"**

   - Verifique o nome de utilizador e palavra-passe
   - Consulte as credenciais de teste

3. **"Acesso negado"**
   - Verifique se tem as permissões necessárias
   - Contacte um administrador

### Logs de Debug

O sistema regista automaticamente tentativas de login falhadas e outras atividades suspeitas no ficheiro `audit_log.json`.

## Suporte

Para questões sobre o sistema de autenticação, consulte:

- Os logs de auditoria (administradores)
- Este documento
- O código-fonte nos módulos `auth.py` e `audit_log.py`
