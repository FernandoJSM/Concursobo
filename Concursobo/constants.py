from enum import IntEnum


class AcquisitionStatus(IntEnum):
    """
        Indica o status da aquisição dos dados
    """
    ERROR = 0           # Não foi possível acessar a página
    UNCHANGED = 1       # A página foi acessada, mas os dados não foram alterados
    UPDATED = 2         # Os dados foram atualizados

class BotMessages:
    """
        Class to store standard messages from the bot.
    """

    git_hub_url = '<a href=\"https://github.com/FernandoJSM/MarinhoBot\">GitHub</a>'

    license_url = '<a href=\"https://github.com/FernandoJSM/MarinhoBot/blob/main/LICENSE\">licença GPL-2.0</a>'

    start = "Este é um bot desenvolvido para acompanhar as atualizações da página do concurso CP-CEM 2020 da Mar" \
                "inha do Brasil.\r\n\r\n/help - Apresenta a explicação dos comandos\r\n/last_update - Apresenta a úl" \
                "tima atualização da página do concurso\r\n/last_three_updates - Envia até as três últimas atualizaç" \
                "ões da página do concurso\r\n/subscribe - Adiciona este chat na lista de assinantes\r\n/unsubscribe" \
                " - Remove este chat da lista de assinantes\r\n/schedule - Apresenta os horários de disparo de mensa" \
                "gens para assinantes\r\n\r\nO bot foi programado na linguagem Python, todo o projeto está no " + \
                git_hub_url + " sob a " + license_url + "."

    help = start

    already_subscribed = "O chat já está na lista de contatos do bot"
    subscription_success = "O chat foi adicionado na lista de contatos do bot"

    unsubscription_success = "O chat foi removido da lista de contatos do bot"
    unsubscription_success = "O chat não está na lista de contatos do bot"

    schedule = "Disparo de mensagens de atualizações:\r\n\n- Segunda a Sexta, das 6h às 20h a cada 15 minutos: " \
                   "Caso haja alguma atualização no site, o bot envia mensagens para a lista de assinantes;\r\n\r\n" \
                   "- Segunda às 8h: Mensagem semanal, envia as últimas 3 atualizações do site mesmo que não haja n" \
                   "ada novo."
