# Concursobô

Concursobô é um bot do Telegram criado para me manter atualizado com as informações de concursos, a princípio criado
como Marinhobô que me atualizava apenas do CP-CEM da Marinha do Brasil, uma vez que o site do concurso é a única fonte
que a MB recomenda que o concurseiro acompanhe. Devido à pandemia está sendo comum as datas serem alteradas, então
este bot foi a melhor solução para que eu não fique acessando páginas de concurso com muita frequência.

O bot basicamente utiliza métodos de web scraping específicos para o layout da página de concursos, e a meta agora
é deixá-lo modular, onde para cada página de concurso terá um método específico retornando sua própria mensagem
padronizada via chat.

Além de monitorar a atualização dos sites definidos, todo o pacote é capaz de gerenciar e enviar dados para uma lista 
de assinantes do bot do Telegram, basicamente sendo necessário apenas a alteração da classe que realiza o web scraping.

<p align="center">
<img src="readme_imgs/Marinhobo.png" class="img-responsive" alt="Marinhobô" width="400px">
</p>

**OBS**:
* O bot está sendo utilizado para fins particulares, mas todo o código do repositório está sob a licença GPL 2.0;

* Apesar do token do bot aparecer em alguns commits, ele é recriado constantemente para evitar que outros tenham acesso
  ao bot na nuvem;

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

* Modularização do bot (conversão para Concursobô) a fim de fazer o web scraping de outras páginas
* Remoção de assinaturas duplicadas, pois hoje apenas o chat_id é considerado para a assinatura;
* Assinaturas temporárias, eliminando elas após um tempo pré-determinado e avisando o usuário;

---

## Histórico de atualizações

### 1.0.0: Bot funcional
Serviço de resposta aos comandos do chat com o bot, manutenção básica de assinaturas e envio de mensagens
para os assinantes (envio baseado no chat_id).

### 1.0.1: Mudança para Concursobô
Mudança de nome do repositório e atualização do readme.md
