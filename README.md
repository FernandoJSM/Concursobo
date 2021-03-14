# Marinhobô

Marinhobô é um bot do Telegram criado para me manter atualizado com as informações do concurso do CP-CEM da Marinha do
Brasil, uma vez que o site do concurso é a única fonte que a MB recomenda que o concurseiro acompanhe. Devido à 
pandemia está sendo comum as datas serem alteradas, então este bot é a melhor solução para que eu não fique acessando
a página do concurso com muita frequência.

Apesar dste bot utilizar métodos de web scraping específicos no layout da página de concursos da
Marinha do Brasil, todo o pacote é capaz de gerenciar e enviar dados para uma lista de assinantes do bot do Telegram, basicamente
sendo necessário apenas a alteração da classe que realiza o web scraping.

<p align="center">
<img src="readme_imgs/Marinhobo.png" class="img-responsive" alt="Marinhobô" width="400px">
</p>

Atualmente este bot está rodando na Google Cloud, com o usuário @marinhobo_bot.

**OBS**:
* O bot na nuvem pode cair sem aviso prévio, já que estou usando a parte gratuita do Google Cloud;

* A rotina do bot que está na nuvem é de fazer o check de segunda a sexta, das 6h as 20h em intervalos de 30 minutos. 
  Está com um limite de disparo de 120 mensagens por minuto caso haja alguma atualização no site. A cada segunda-feira 
  às 8h o bot envia uma mensagem para toda a lista de assinantes com os dados do site do concurso mesmo que não haja 
  atualização;

* Apesar do token do bot aparecer em alguns commits, ele é recriado constantemente para evitar que outros tenham acesso
  ao bot na nuvem;

* A lista de assinaturas pode ser apagada sem aviso prévio, até que eu implemente um gerenciamento de assinaturas mais 
  robusto.

---

## Funcionamento
*Em desenvolvimento*

### Programação
*Em desenvolvimento*

### Comandos do bot no Telegram
*Em desenvolvimento*

---

## Instalação e execução
*Em desenvolvimento*

---

## Implementações futuras

Algumas das possíveis implementações que poderão ou não serem feitas, mas que já pensei na possibilidade de implementar:

* Remoção de assinaturas duplicadas, pois hoje apenas o chat_id é considerado para a assinatura;
* Assinaturas temporárias, eliminando elas após um tempo pré-determinado e avisando o usuário;
* Gerenciamento de mais de um concurso da Marinha do Brasil, com o usuário poder assinar mais de uma lista.

---

## Histórico de atualizações

### 1.0.0: Bot funcional
Serviço de resposta aos comandos do chat com o bot, manutenção básica de assinaturas e envio de mensagens
para os assinantes (envio baseado no chat_id).
