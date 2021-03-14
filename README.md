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

**OBS**: Apesar do token do bot aparecer em alguns comits, ele é recriado constantemente, então não adianta tentar usar
ele :).

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
**EM DESENVOLVIMENTO, MAS É A INTENÇÃO DA PRIMEIRA VERSÃO:** Na sua primeira versão, todo o serviço de resposta aos comandos e manutenção de assinaturas está implementado.
