# Concursobô

<p align="center">
<img src="readme_imgs/Concursobo.png" class="img-responsive" alt="Marinhobô" width="150px">
</p>

O Concursobô é um bot de Telegram criado para me manter atualizado com as informações de concursos, acessando as páginas
e enviando mensagens para o chat caso encontre alguma atualização. Inicialmente ele era o Marinhobô e me atualizava com
o site do CP-CEM, de forma que eu não precisava entrar várias vezes no site para ver se havia algo novo. A necessidade 
do bot surgiu por causa da pandemia, pois em 2020 estava sendo comum as datas serem alteradas. Devido a sua utilidade,
hoje ele é o Concursobô que foi atualizado para monitorar várias páginas diferentes, inclusive outras não relacionadas 
diretamente com o concurso em si.

O bot basicamente utiliza métodos de web scraping para obter os dados da página e caso ative um gatilho de mensagem 
(como por exemplo novas entradas na página, ou mensagens específicas) uma mensagem é enviada para uma lista de 
assinantes do bot.

**OBS**:
Apesar do token do bot aparecer em alguns commits, ele é recriado constantemente para evitar que outros tenham acesso 
ao bot na nuvem;

---

## 1. Funcionamento
*Em desenvolvimento*

### 2. Scrapers implementados
* Página de concursos da Marinha: A página dos concursos da Marinha possui o mesmo formato, então este scraper se aplica
em qualquer concurso da MB. Este scraper busca por mensagens de informação e também pela atualização da data do concurso
quando ela é publicada.
* Vagas da Fundep: A página de vagas da Fundep é uma bagunça, não é nem um pouco organizada e muito complicada de ver 
quais são as vagas novas. Este scraper lista todas as vagas e identifica o que foi adicionado e removido.
* Notícias do PCI Concursos: As notícias de concursos do PCI Concursos contém as vagas que estão sendo ofertadas, então
para agilizar o processo este scraper lê o conteúdo de cada notícia e caso ela contenha alguma palavra pré determinada,
a notícia é capturada pelo scraper.

### 3. Comandos do bot no Telegram
*Em desenvolvimento*

---

## 4. Instalação e execução
### 4.1 No Windows
### 4.2 No Linux
*Em desenvolvimento*

---

## Histórico de atualizações

### 1.0.0: Bot funcional
Serviço de resposta aos comandos do chat com o bot, manutenção básica de assinaturas e envio de mensagens
para os assinantes (envio baseado no chat_id).

### 2.0.0: Mudança para Concursobô
Bot reestruturado para ser modular, podendo conter mais de um scraper.
