# UtilsRPANAGEM

![Status](https://img.shields.io/badge/status-experimental-orange)
![License](https://img.shields.io/badge/license-MIT-blue)

Utilitário Python para automações e rotinas da Nagem. Criado para facilitar processos internos com foco em clareza, modularidade e reutilização.

## Objetivos do pacote
1. Incentivar o reuso;
2. Oferecer maior segurança ao desenvolvedor;
3. Tornar sua vida mais produtiva e fácil :)

Atenção: lembre-se de incrementar a versão e atualizar toda a documentação antes de gerar um novo pacote.

---

## ⚙️ Funcionalidades disponíveis no momento
1. 📈 conexao_banco
    - conectar_odbc
    - executar_select
    - conectar_sqlserver
    - executar_update_insert
2. 📤 enviar_email
    - conectar_smtp_server
    - enviar_email
3. 📅 manipula_datahora
    - obter_incluir_valor_data
    - converter_data
    - data_hora_para_binario
    - binario_para_data_hora
4. 📁📝 manipula_diretorios_arquivos
    - arquivos_existem
    - criar_arquivo
    - criar_xlsx_com_colunas
    - inserir_tabela_xlsx
    - formatar_xlsx
    - criar_logger_diario
    - mover_arquivo
    - diretorio_existe
    - criar_diretorio
5. 🧩 manipula_sap
    - start_sap_logon
    - procurar_campos
    - procurar_janela
    - verificar_mensagem_status
    - fechar_sessao_sap
    - run_transaction
    - anexar_sessao_sap


## 🚀 Instalação com poetry
    poetry add --source testpypi utilsrpanagem


## 🚀 Instalação com pip
    pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple utilsrpanagem



## Dúvidas?
Entre em contato com eduarda.lima@nagem.com.br ou desenvolvimentorpa@nagem.com.br.
