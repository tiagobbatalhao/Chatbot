# Facebook Messenger Bot

Esse é um app em Python com Flask que implementa um webhook para o Facebook Messenger.

O app é configurado para rodar dentro do ambiente Heroku (https://www.heroku.com/), um
serviço gratuito de host para aplicações web.

O comportamento do chatbot emula uma loja online de camisetas, em que o usuário
é guiado e pode verificar os modelos disponíveis e adicionar um carrinho de compras.

## Comportamento do bot

O bot simula uma loja de camisetas. Após uma mensagem de boas-vindas, o app direciona o usuário através de uma combinação de botões de resposta rápida, carrossel, listas e menu persistente para mostrar modelos de camisetas vendidas pela loja. A interação com o app se inicia através do menu persistente, ou de uma mensagem de início, contendo por exemplo um cumprimento ('oi', 'olá') ou um pedido de ajuda. A cada procura, uma lista aleatória de camisetas é mostrada (em um app real, um sistema de busca deveria ser implementado para retornar o que o usuário deseja). Se houver interesse, o produto é adicionado a um carrinho de compras. A qualquer momento, o usuário pode ver o carrinho através do menu persistente. Para finalizar a compra, o usuário seria redirecionado para outro site (essa função não foi ainda implementada).

## Arquivos

* 'Procfile' e 'runtime.txt': exigidos para a configuração do ambiente Heroku.
* 'requirements.txt': também exigido para a configuração do ambiente Heroku. Contém os pacotes necessários para o app.
* 'app.py': arquivo principal do app Flask. Define o comporamento do app. Aqui, recebe mensagens do Facebook através de webhook, salva as mensagens em uma base de dados e chama funções definidas em outros módulos.
* 'chatbot_store.py': funções do chatbot relativas a uma loja online.
* 'setup_database.py': define tabelas para uma base de dados Postgres. Chamado somente na primeira ativação do app, não necessário para o app em modo produção.
* 'Products.csv': uma lista de produtos para a loja, para abastecer a base de dados.  Necessário somente na primeira ativação do app, não necessário para o app em modo produção.
