# Formulário → PHP → Google Sheets

## Google Sheets e Apps Script

1. Na conta do cliente, crie uma planilha privada com uma aba chamada `Contatos`. Na primeira linha coloque: `Data e hora`, `Nome`, `WhatsApp`, `ID do envio`. A quarta coluna serve para evitar duplicação em tentativas de reenvio; pode ser ocultada.
2. Abra **Extensões → Apps Script** e cole o conteúdo de `Code.gs`.
3. Em **Configurações do projeto → Propriedades do script**, adicione:
   - `SPREADSHEET_ID`: o trecho entre `/d/` e `/edit` na URL da planilha.
   - `CONTACT_SECRET`: uma chave aleatória de pelo menos 32 caracteres. Gere com `php -r "echo bin2hex(random_bytes(32));"`.
4. Configure o fuso horário do projeto e da planilha como São Paulo e formate a coluna A como data e hora.
5. Em **Implantar → Nova implantação → Aplicativo da Web**, escolha executar como proprietário e acesso **Qualquer pessoa**. Autorize na conta do cliente. A chave é verificada pelo script antes de acessar a planilha. Contas Workspace podem restringir essa opção.
6. Copie a URL terminada em `/exec`. Ao alterar o script, atualize a implantação para uma nova versão.

## Hospedagem PHP

Requisitos: PHP 8.0 ou superior, extensão cURL, acesso HTTPS de saída ao Google e diretório temporário gravável.

1. Copie `liderseg-contact-config.example.php` para **fora da pasta pública**, com o nome `liderseg-contact-config.php`. Por exemplo, se o site estiver em `/home/cliente/public_html`, a configuração deve ficar em `/home/cliente/liderseg-contact-config.php`.
2. Preencha a URL `/exec` e a mesma chave `CONTACT_SECRET`. Não publique esse arquivo, nem coloque segredos no JavaScript. Se a estrutura da hospedagem for diferente, ajuste `$configPath` no endpoint PHP.
3. Rode `npm ci` e `npm run build` na pasta `liderseg`.
4. Envie o **conteúdo** de `dist` para a pasta pública da hospedagem. O build copia `public/captar-contato.php` para `dist/captar-contato.php`.
5. Confirme que a hospedagem executa PHP e não serve seu código como texto.

## Verificação antes de divulgar

- Envie um nome e celular com DDD no site publicado. Confira a nova linha e o redirecionamento ao WhatsApp da Liderseg, com uma mensagem contendo o nome informado. O redirecionamento só acontece após a confirmação da gravação; a pessoa ainda precisa enviar a mensagem no WhatsApp.
- Teste campos vazios, telefone incompleto e uma falha da integração. Nunca deve aparecer sucesso quando a gravação não for confirmada.
- Para verificar duplicação, envie duas requisições com o mesmo `submission_id`: deve existir apenas uma linha.
- O endpoint aceita até 10 tentativas por IP a cada 10 minutos. Há também um campo invisível contra bots simples; isso não elimina todo spam.
- O servidor de desenvolvimento do Astro e o preview estático **não executam PHP**. Para testar a integração local após o build, use `php -S localhost:8080 -t dist` e abra `http://localhost:8080`. Nesse caso, a configuração privada deve estar em `liderseg/liderseg-contact-config.php`.
- Não envie dados reais sem concluir a configuração. A planilha só deve ser compartilhada com quem precisa atender os contatos.

Documentação: https://developers.google.com/apps-script/guides/web
