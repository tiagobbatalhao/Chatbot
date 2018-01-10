# Facebook Messenger Bot

Esse � um app em Python com Flask que implementa um webhook para o Facebook Messenger.

O app � configurado para rodar dentro do ambiente Heroku (https://www.heroku.com/), um
servi�o gratuito de host para aplica��es web.

O comportamento do chatbot emula uma loja online de camisetas, em que o usu�rio
� guiado e pode verificar os modelos dispon�veis e adicionar um carrinho de compras.

## Comportamento do bot

O bot simula uma loja de camisetas. Ap�s uma mensagem de boas-vindas, o app direciona o usu�rio atrav�s de uma combina��o de bot�es de resposta r�pida, carrossel, listas e menu persistente para mostrar modelos de camisetas vendidas pela loja. A intera��o com o app se inicia atrav�s do menu persistente, ou de uma mensagem de in�cio, contendo por exemplo um cumprimento ('oi', 'ol�') ou um pedido de ajuda. A cada procura, uma lista aleat�ria de camisetas � mostrada (em um app real, um sistema de busca deveria ser implementado para retornar o que o usu�rio deseja). Se houver interesse, o produto � adicionado a um carrinho de compras. A qualquer momento, o usu�rio pode ver o carrinho atrav�s do menu persistente. Para finalizar a compra, o usu�rio seria redirecionado para outro site (essa fun��o n�o foi ainda implementada).

## Arquivos

* 'Procfile' e 'runtime.txt': exigidos para a configura��o do ambiente Heroku.
* 'requirements.txt': tamb�m exigido para a configura��o do ambiente Heroku. Cont�m os pacotes necess�rios para o app.
* 'app.py': arquivo principal do app Flask. Define o comporamento do app. Aqui, recebe mensagens do Facebook atrav�s de webhook, salva as mensagens em uma base de dados e chama fun��es definidas em outros m�dulos.
* 'chatbot_store.py': fun��es do chatbot relativas a uma loja online.
* 'setup_database.py': define tabelas para uma base de dados Postgres. Chamado somente na primeira ativa��o do app, n�o necess�rio para o app em modo produ��o.
* 'Products.csv': uma lista de produtos para a loja, para abastecer a base de dados.  Necess�rio somente na primeira ativa��o do app, n�o necess�rio para o app em modo produ��o.
