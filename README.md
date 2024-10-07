# Configuração do Serviço systemd para FastAPI

Este guia descreve como configurar um serviço `systemd` para garantir que seu aplicativo FastAPI continue executando mesmo após reinicializações do sistema.

## Passos para Criar o Serviço

1. **Crie um arquivo de serviço**: Crie um arquivo de serviço em `/etc/systemd/system/` chamado `fastapi_app.service`.

    ```ini
    [Unit]
    Description=FastAPI Application
    After=network.target

    [Service]
    User=seu_usuario
    WorkingDirectory=/caminho/para/seu/app
    ExecStart=/usr/bin/uvicorn main:app --host 0.0.0.0 --port 8000
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

    - Substitua `seu_usuario` pelo nome do usuário que deve executar o serviço.
    - Substitua `/caminho/para/seu/app` pelo caminho para o diretório onde está o seu aplicativo.

2. **Atualize o `systemd`**: Após criar o arquivo de serviço, atualize o `systemd` para reconhecer o novo serviço.

    ```bash
    sudo systemctl daemon-reload
    ```

3. **Inicie o serviço**: Inicie o serviço para que ele comece a rodar.

    ```bash
    sudo systemctl start fastapi_app
    ```

4. **Habilite o serviço para iniciar no boot**: Isso garante que o serviço inicie automaticamente quando o sistema for reiniciado.

    ```bash
    sudo systemctl enable fastapi_app
    ```

## Comandos Úteis para Gerenciar o Serviço

- **Reiniciar o serviço**:

    ```bash
    sudo systemctl restart fastapi_app
    ```

- **Verificar o status do serviço**:

    ```bash
    sudo systemctl status fastapi_app
    ```

- **Parar o serviço**:

    ```bash
    sudo systemctl stop fastapi_app
    ```

Com isso, seu aplicativo FastAPI será gerenciado pelo `systemd`, garantindo que ele continue rodando após reinicializações e permitindo um gerenciamento fácil do ciclo de vida do serviço.