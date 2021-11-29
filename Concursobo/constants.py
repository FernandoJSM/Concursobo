class AcquisitionStatus:
    """
    Indica o status da aquisição dos dados
    """

    ERROR = 0  # Não foi possível acessar a página
    UNCHANGED = 1  # A página foi acessada, mas os dados não foram alterados
    UPDATED = 2  # Os dados foram atualizados


class BotMessages:
    """
    Class to store standard messages from the bot.
    """

    help = (
        "/ajuda - Como utilizar o bot\r\n"
        "/listar_concursos - Lista as páginas cadastradas e permite comandos interativos\r\n"
        "/cadastrar - Adiciona este chat na lista de assinantes\r\n"
        "/unsubscribe - Remove este chat da lista de assinantes\r\n"
        "/info - Informações do bot\r\n\n"
        "O bot faz checagens regulares nas páginas cadastradas e caso alguma alteração seja detectada,"
        "é enviado uma mensagem de atualização para a lista de assinantes cadastradas no bot."
    )

    git_hub_url = '<a href="https://github.com/FernandoJSM/MarinhoBot">GitHub</a>'

    start = (
        "Este é um bot desenvolvido para acompanhar as atualizações e informações de diferentes "
        "páginas cadastradas previamente no código, evitando a necessidade de acessá-las manualmente.\r\n\n"
        + help
        + "\r\n Código fonte: \r\n"
        + git_hub_url
    )

    license_url = '<a href="https://github.com/FernandoJSM/MarinhoBot/blob/main/LICENSE">licença GPL-2.0</a>'

    info = (
        "Este é um bot desenvolvido para acompanhar as atualizações e informações de diferentes "
        "páginas cadastradas previamente no código, evitando a necessidade de acessá-las manualmente.\r\n"
        "\r\n Código fonte: \r\n"
        + git_hub_url
        + "\r\n Licença de uso: \r\n"
        + git_hub_url
    )

    already_subscribed = "O chat já está na lista de contatos do bot"
    subscription_success = "O chat foi adicionado na lista de contatos do bot"

    unsubscription_success = "O chat foi removido da lista de contatos do bot"
    unsubscription_success = "O chat não está na lista de contatos do bot"
