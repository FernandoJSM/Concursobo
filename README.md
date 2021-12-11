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

---

## 1. Funcionamento
O bot basicamente utiliza métodos de web scraping para obter os dados da página e caso ative um gatilho de mensagem 
(como por exemplo novas entradas na página, ou mensagens específicas) uma mensagem é enviada para uma lista de 
assinantes do bot. Ele foi estruturado da seguinte forma:

<p align="center">
<img src="readme_imgs/DiagramaBot.png" class="img-responsive" alt="Diagrama" width="500px">
</p>

A Base do bot contém a estrutura para o funcionamento com o Telegram:
* Comandos do chat: Aceita e gerencia os comandos do chat;
* Envio de mensagens: Envia mensagens para a lista de contatos ou como resposta do chat;
* Interface com os scrapers: Interfaceia o bot com os scrapers definidos pelo usuário, permitindo que cada scraper seja
independente do outro.

Os scrapers contém os métodos para capturar informação conforme ela está na fonte, a única restrição dos scrapers é que
eles tem de realizar três tipos de comandos:

* Identificar atualizações na página;
* Enviar uma mensagem resumida com os dados capturados;
* Enviar uma mensagem de todos os dados capturados.

Os scrapers também mantém salvos os dados capturados e uma das vantagens deles funcionarem de forma separada é que cada
scraper armazena seus dados da forma mais adequada para seu uso.

### 2. Scrapers implementados
* Página de concursos da Marinha: A página dos concursos da Marinha possui o mesmo formato, então este scraper se aplica
em qualquer concurso da MB. Este scraper busca por mensagens de informação e também pela atualização da data do concurso
quando ela é publicada;

* Página do concurso SMV da Marinha: Esse scraper é específico para esta página. Para este scraper, só estou extraindo
as informações da página "Nota Informativa";

* Vagas da Fundep: A página de vagas da Fundep é uma bagunça, não é nem um pouco organizada e muito complicada de ver 
quais são as vagas novas. Este scraper lista todas as vagas e identifica o que foi adicionado e removido;

* Notícias do PCI Concursos: As notícias de concursos do PCI Concursos contém as vagas que estão sendo ofertadas, então
para agilizar o processo este scraper lê o conteúdo de cada notícia e caso ela contenha alguma palavra pré determinada,
a notícia é capturada pelo scraper.

### 3. Comandos do bot no Telegram

Atualmente estão cadastrados os seguintes comandos pro bot:

* /ajuda: Mostra uma mensagem sobre como utilizar o bot;
* /listar_sites: Lista as páginas cadastradas e permite comandos interativos com botões de chat;
* /atualizar_tudo: Atualiza todas as páginas cadastradas;
* /cadastrar: Adiciona o chat na lista de assinantes do bot, de forma que quando houver atualizações de uma página, o
bot irá enviar a atualização para cada assinante da lista;
* /unsubscribe: Remove o chat da lista de assinantes;
* /info: Mostra uma mensagem com informações do bot

## 4. Execução

Primeiro é necessário configurar um ambiente Python 3.9+ com as bibliotecas definidas no arquivo ```requirements.txt```
para poder executar os scripts do bot.

Depois é necessário criar um bot no telegram através do @botfather para pegar um token. O token ficará no arquivo 
```data/config.cfg```. Existem outras coisas que só são possíveis de incluir pelo BotFather, como foto de perfil,
comandos e descrição.

**OBS**:
Apesar do token do bot aparecer em alguns commits, ele é recriado constantemente para evitar que outros tenham acesso 
ao bot.

O projeto contém dois scripts principais:
* ```concursobo.py```: inicializa o bot com os scrapers do projeto, de forma que o bot receba e responda pelos comandos
do chat
* ```regular_check.py```: Contém rotinas de checagem automática dos scrapers cadastrados através da biblioteca
APScheduler. Cada scraper tem um horário próprio de checagem declarado no formato do CRON. Recomendo que eles tenham
o minuto diferente para que não executem todos na mesma hora.

Já que o bot funciona só executando os scripts, basta manter os scripts ```concursobo.py``` e
 ```regular_check.py``` rodando no plano de fundo do sistema. Isso vai variar conforme o sistema operacional:

### 4.1 No Windows 10
No Windows 10 o bot pode ser executado pelo "Agendador de Tarefas" que é encontrado na pesquisa do Menu Iniciar. Após
abrir a janela, clique em "Criar Tarefa" e dê um nome e uma descrição para ela.

Na aba "Disparadores" coloque a opção "Ao Inicializar", assim o bot sempre estará ativo quando você ligar o computador.

Na aba "Ações" crie uma ação para cada script, onde na parte "Programa/script" deve conter o caminho para o arquivo
```pythonw.exe``` do ambiente python. Esse arquivo garante que não serão abertas telas do prompt de comando na execução
do código. Em "Argumentos", coloque o caminho do script a ser executado.

### 4.2 No Linux
Uma forma de colocar o bot para rodar no Linux é pelo [gerenciador de processos PM2](https://pm2.keymetrics.io), que 
roda os scripts como um serviço e os mantém em execução.

Após instalar o PM2 com o NPM, basta executar os comandos para colocar os scripts rodando.


* Inicializar os scripts:
```
pm2 start /caminho/do/script/concursobo.py --name Concursobo-Handler_manager --interpreter /caminho/do/interpretador/python
pm2 start /caminho/do/script/regular_check.py --name Concursobo-Handler_manager --interpreter /caminho/do/interpretador/python
```
* Salvar o ambiente (após o comando ```pm2 startup``` executar o comando sudo indicado pelo pm2)
```
pm2 save
pm2 startup
```
---

## Histórico de atualizações

### 1.0.0: Bot funcional
Serviço de resposta aos comandos do chat com o bot, manutenção básica de assinaturas e envio de mensagens
para os assinantes (envio baseado no chat_id).

### 2.0.0: Mudança para Concursobô
Bot reestruturado para ser modular, podendo conter mais de um scraper.
