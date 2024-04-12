# ISSO NÃO É UM BOT, ISSO É UMA MÃE! 

O Projeto ISSO NÃO É UM BOT, ISSO É UMA MÃE!  é um bot do Telegram que fornece uma avaliação rápida do conteúdo de vídeos do YouTube, indicando se é adequado para crianças ou não. O bot é uma ferramenta simples e rápida para ajudar os pais a tomar decisões sobre o que seus filhos podem assistir online.

## Funcionalidades

- **Avaliação de Conteúdo**: Os usuários podem enviar o link de um vídeo do YouTube para o bot.
- **Classificação de Idade**: Com base na transcrição do vídeo, o bot classifica o conteúdo em duas categorias:
  - **Conteúdo Infantil**: Adequado para crianças.
  - **Inadequado para Crianças**: Conteúdo que pode não ser adequado para crianças.
- **Justificação da Classificação**: O bot fornece uma breve justificação para a classificação atribuída, ajudando os pais a entenderem por que o conteúdo foi avaliado dessa forma.
- **Integração com API OpenAI**: O bot utiliza a API OpenAI para transcrever o conteúdo dos vídeos do YouTube, o que permite uma avaliação precisa e rápida.

## Como Usar

1. Adicione o bot ao seu Telegram: [@maedeolhonoyoutube_bot].
2. Envie o link do vídeo do YouTube que deseja avaliar para o bot.
3. O bot retornará com uma classificação indicando se o conteúdo é adequado para crianças ou não, juntamente com uma breve justificação.

## Tecnologias Utilizadas

- **Flask**: Utilizado para construir o servidor web que se comunica com a API do Telegram.
- **API do Telegram**: Utilizada para receber e enviar mensagens para os usuários.
- **API OpenAI**: Utilizada para transcrever o conteúdo dos vídeos do YouTube e realizar a avaliação do conteúdo.

## Próximos Passos

- **Melhoria da Precisão da Avaliação**: Refinar o algoritmo de avaliação para aumentar a precisão na classificação do conteúdo.
- **Treinamento Adicional do Modelo**: Explorar a possibilidade de treinar o modelo para reconhecer características específicas de conteúdo educativo ou outros marcadores relevantes.
- **Integração com Outras Plataformas**: Expandir o suporte para avaliação de conteúdo de outras plataformas de vídeo além do YouTube.

## Contribuindo

- Se você tiver ideias para melhorar o bot ou deseja contribuir com código, sinta-se à vontade para abrir uma issue ou enviar uma solicitação de pull request.
- Se encontrar bugs ou problemas, por favor, relate-os na seção de issues do repositório.

Vamos juntos tornar a internet um lugar mais seguro e adequado para crianças! 🚀👨‍👩‍👧‍👦
