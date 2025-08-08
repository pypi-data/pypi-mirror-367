import os
import time
import inspect
import functools
import threading
from time import sleep
from pathlib import Path
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from .api import EnumBanco, EnumStatus, EnumProcesso, putStatusRobo, putTicket
from .funcoes import aguardarElemento, esperarElemento, clickarElemento, selectOption, aguardarAlert, mensagemTelegram


tokenTelegram = '8013361039:AAGBT5eMqYw3WdfxAdWsqgCySpuFPLHhl2Y'
chat_id = '-794597825'


headlessOptions = [
    'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36',
    '--no-sandbox',
    '--window-size=1920,1080',
    '--headless',
    '--disable-gpu',
    '--allow-running-insecure-content'
]


class ImportacaoOptions:
    def __init__(self, portabilidade: bool = False, crefisa_cp: bool = False, layout: str = "", empty: bool = False):
        self.PORTABILIDADE = portabilidade
        self.CREFISA_CP = crefisa_cp
        self.LAYOUT = layout
        self.VAZIO = empty


def checkEvent():
    """
    Decorator to check if an event is set before executing the decorated function.
    The event is dynamically retrieved from the function's arguments.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get the function's signature and parameter names
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            resetManager = bound_args.arguments.get("resetManager")
            
            if isinstance(resetManager, threading.Event):
                resetManager.set()

            return func(*args, **kwargs)
        return wrapper
    return decorator


@checkEvent()
def importacaoVirtaus(virtaus: Chrome, filepath: Path, nomeBanco: str, enumBanco: EnumBanco, options: ImportacaoOptions = ImportacaoOptions(), resetManager: threading.Event = None) -> int:
    """
    Realiza a rotina de importação de propostas no sistema Virtaus.

    Args:
        virtaus (Chrome): Instância do driver Selenium.
        filepath (Path): Caminho do arquivo a ser importado.
        nomeBanco (str): Nome do banco a ser selecionado.
        enumBanco (EnumBanco): Enum do banco.
        options (ImportacaoOptions): Opções específicas para a importação.
        resetManager (threading.Event, optional): Evento para controle de reinício/encerramento do bot.

    Returns:
        int: Código de status da operação (0 = sucesso, 1 = encerramento via resetManager).
    """
    putStatusRobo(EnumStatus.LIGADO, EnumProcesso.IMPORTACAO, enumBanco)
    
    portabilidade = "SIM" if options.PORTABILIDADE else "NÃO"
    crefisa_cp = "crefisa_cp" if options.CREFISA_CP else None
    layout = options.LAYOUT
    empty = options.VAZIO

    if empty:
        putStatusRobo(EnumStatus.SEM_PROPOSTA, EnumProcesso.IMPORTACAO, enumBanco)

    else:
        maxTry = 5
        tryCount = 0
        
        while tryCount <= maxTry:
            putStatusRobo(EnumStatus.IMPORTANDO, EnumProcesso.IMPORTACAO, enumBanco)
            tryCount += 1
            try:
                if resetManager:
                    if not resetManager.is_set():   # Finaliza o bot
                        virtaus.quit()
                        return 1
                time.sleep(5)
                virtaus.get('https://adpromotora.virtaus.com.br/portal/p/ad/pageworkflowview?processID=ImportacaoArquivoEsteira')
                aguardarAlert(virtaus)
                
                sleep(10)
                iframe = virtaus.find_elements('tag name','iframe')[0]
                virtaus.switch_to.frame(iframe)

                # Banco
                clickarElemento(virtaus, '/html/body/div/form/div/div[1]/div[2]/div/div[1]/span/span[1]/span/ul/li/input').click()
                esperarElemento(virtaus, '/html/body/div/form/div/div[1]/div[2]/div/div[1]/span/span[1]/span/ul/li/input').send_keys(nomeBanco)
                sleep(5)
                esperarElemento(virtaus, '/html/body/div/form/div/div[1]/div[2]/div/div[1]/span/span[1]/span/ul/li/input').send_keys(Keys.ENTER)

                # Layout
                if layout:
                    try:
                        selectOption(virtaus, '//*[@id="selectLayout"]', layout)
                    except Exception as e:
                        print(f"Error selecting option: {e}")

                # Portabilidade
                if portabilidade:
                    try:
                        selectOption(virtaus, '//*[@id="selectPortabilidade"]', portabilidade)
                    except Exception as e:
                        print(f"Error selecting option: {e}")
                        
                # Crefisa CP
                if crefisa_cp:
                    try:
                        selectOption(virtaus, '//*[@id="selectCrefisa"]', crefisa_cp)
                    except Exception as e:
                        print(f"Error selecting option: {e}")

                virtaus.switch_to.default_content()          

                clickarElemento(virtaus, '//*[@id="tab-attachments"]/a/span').click()
                sleep(5)
                esperarElemento(virtaus, '//*[@id="lb-input-upload"]')
                
                importarArquivo = aguardarElemento(virtaus, '//*[@id="ecm-navigation-inputFile-clone"]')
                importarArquivo.send_keys(str(filepath))
                sleep(5)
                
                # Upload arquivo
                clickarElemento(virtaus, '//*[@id="workflowActions"]/button[1]').click()
                sleep(5)

               
                elemento = esperarElemento(virtaus, '/html/body/div[1]/div[3]/div/div/div[2]/div/div/div/div[3]/div[1]/div/div[1]/span/a')
                numeroSolicitacao = elemento.text
                os.remove(str(filepath)) ## Só remover após ter certeza de que foi concluído
                putTicket(numeroSolicitacao, EnumProcesso.IMPORTACAO, enumBanco)
                mensagem = f"Importação Efetuada: <b> {nomeBanco} - {numeroSolicitacao}</b> ✅"
                
                if resetManager:
                    resetManager.set()              # Reseta countdown de restart do bot

                mensagemTelegram(tokenTelegram, chat_id, mensagem)
                putStatusRobo(EnumStatus.LIGADO, EnumProcesso.IMPORTACAO, enumBanco)
                return 0

            except Exception as e:
                print(e)
                print('Erro ao tentar importar no Virtaus')
                putStatusRobo(EnumStatus.ERRO, EnumProcesso.IMPORTACAO, enumBanco)