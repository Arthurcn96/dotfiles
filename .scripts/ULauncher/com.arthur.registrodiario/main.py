import os
import datetime
import logging
import traceback
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

# Configurar logging com mais detalhes
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('JournalExtension')

class JournalExtension(Extension):
    def __init__(self):
        super().__init__()
        logger.info("Extensão inicializada")
        self.subscribe(KeywordQueryEvent, JournalKeywordListener())
        
    def get_journal_dir(self):
        journal_dir = self.preferences.get('journal_dir', '/')
        logger.debug(f"Diretório do journal obtido das preferências: {journal_dir}")
        return journal_dir

    def get_idea_file(self):
        idea_file = self.preferences.get('idea_file', '/')
        logger.debug(f"Arquivo de ideias obtido das preferências: {idea_file}")
        return idea_file
    
    def get_lembrete_file(self):
        lembrete_file = self.preferences.get('lembrete_file', '/')
        logger.debug(f"Arquivo de lembretes obtido das preferências: {lembrete_file}")
        return lembrete_file

    def get_section_registro(self):
        section_name = self.preferences.get('section_registro_diario', '# Registros diários:')
        logger.debug(f"Nome da seção obtido das preferências: {section_name}")
        return section_name
    
    def get_keyword_registro(self):
        keyword = self.preferences.get('registro_todo', 'rd')
        logger.debug(f"Keyword de registro diário obtida das preferências: {keyword}")
        return keyword
    
    def get_section_todo(self):
        section_name = self.preferences.get('section_todo_diario', '# Tarefas:')
        logger.debug(f"Nome da seção de tarefas obtido das preferências: {section_name}")
        return section_name
    
    def get_keyword_todo(self):
        keyword = self.preferences.get('registro_todo', 'todo')
        logger.debug(f"Keyword de tarefas obtida das preferências: {keyword}")
        return keyword


# Processa a entrada e cria um item clicavel
class JournalKeywordListener(EventListener):
    def on_event(self, event, extension):
        keyword = event.get_keyword()
        mensagem = event.get_argument() or ""
        logger.debug(f"Evento KeywordQueryEvent recebido: query='{mensagem}'")
        
        logger.info(f'Texto recebido: "{mensagem}", criando ação personalizada')
        return RenderResultListAction([
            ExtensionResultItem(
                icon='images/icon.png',
                name='Digite um novo registro diário',
                description=mensagem,
                on_enter=ExtensionCustomAction({
                    'mensagem': mensagem,
                    'tipo': 'rd'
                }, keep_app_open=False)
            ),
            ExtensionResultItem(
                icon='images/icon.png',
                name='Digite uma nova tarefa diária',
                description=mensagem,
                on_enter=ExtensionCustomAction({
                    'mensagem': mensagem,
                    'tipo': 'todo'
                }, keep_app_open=False)
            ),
            ExtensionResultItem(
                icon='images/icon.png',
                name='Digite uma nova ideia',
                description=mensagem,
                on_enter=ExtensionCustomAction({
                    'mensagem': mensagem,
                    'tipo': 'idea'
                }, keep_app_open=False)
            ),
            ExtensionResultItem(
                icon='images/icon.png',
                name='Digite um novo lembrete',
                description=mensagem,
                on_enter=ExtensionCustomAction({
                    'mensagem': mensagem,
                    'tipo': 'lembrete'
                }, keep_app_open=False)
            )
        ])


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        logger.info("JournalEventHandler iniciado")

        data = event.get_data() 
        tipo = data['tipo']
        mensagem = data['mensagem']
        logger.debug(f"Mensagem recebida: {mensagem}")
        
        if not mensagem.strip():
            logger.warning("Mensagem vazia recebida, abortando operação")
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.png',
                    name='Erro: Mensagem vazia. Por favor, insira algum texto.',
                    description='Nenhum texto foi fornecido para o registro.',
                    on_enter=HideWindowAction()
                )
            ])
        
        else: 
            try:
                # Obter data e hora
                now = datetime.datetime.now()
                date_str = now.strftime("%d-%m-%Y")
                time_str = now.strftime("%H:%M")
                logger.debug(f"Data: {date_str}, Hora: {time_str}")

                # Preparar nova entrada e seção
                if tipo == 'rd':
                    new_entry = f"\n🕑 **{time_str}** | {mensagem}\n"
                    sessao = extension.get_section_registro()
                elif tipo == 'todo':
                    new_entry = f"\n- [ ] {mensagem}\n"
                    sessao = extension.get_section_todo()
                elif tipo == 'idea':
                    new_entry = f"\n**{date_str}** | **{time_str}** 👉 {mensagem}\n"
                    sessao = extension.get_idea_file()
                elif tipo == 'lembrete':
                    new_entry = f"\n**{date_str}** | **{time_str}** 🔔 {mensagem}\n"
                    sessao = extension.get_lembrete_file()
                else:
                    raise ValueError("Tipo desconhecido")

                # Verifica local do arquivo
                if tipo in ['rd', 'todo']:
                    directory = extension.get_journal_dir()
                    logger.debug(f"Diretório do journal: {directory}")
                    file_path = os.path.join(directory, f"{date_str}.md")
                elif tipo == 'idea':
                    file_path = extension.get_idea_file()
                    logger.debug(f"Caminho do arquivo de ideias: {file_path}")
                elif tipo == 'lembrete':
                    file_path = extension.get_lembrete_file()
                    logger.debug(f"Caminho do arquivo de lembretes: {file_path}")
                else:
                    raise ValueError("Tipo desconhecido para caminho de arquivo")

                logger.debug(f"Arquivo alvo: {file_path}")

                # Processar o arquivo
                logger.debug("Lendo arquivo...")
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    logger.debug(f"Arquivo lido com {len(lines)} linhas")

                new_lines = []
                inserted = False
                section_found = False
                
                logger.debug("Procurando pela seção especificada...")
                for i, line in enumerate(lines):
                    new_lines.append(line)
                    
                    # Verifica se a linha contém exatamente a seção
                    if line.strip() == sessao:
                        logger.debug(f"Seção encontrada na linha {i+1}")
                        
                        if not inserted:
                            new_lines.append(new_entry)
                            inserted = True
                            logger.debug(f"Mensagem inserida: {new_entry.strip()}")
                    
                    # Senão adiciona após a primeira seção encontrada
                    else:
                        if  line.startswith('# ') and not inserted:
                            new_lines.append(new_entry)
                            inserted = True
                            logger.debug(f"Mensagem inserida após seção (#): {new_entry.strip()}")

                # Escrever o novo conteúdo no arquivo
                logger.debug("Escrevendo arquivo modificado...")
                with open(file_path, 'w') as file:
                    file.writelines(new_lines)
                    logger.info("Arquivo salvo com sucesso")

                
            except Exception as e:
                error_msg = f"{str(e)}"
                logger.error(f"Exceção completa: {traceback.format_exc()}")
                return RenderResultListAction([
                    ExtensionResultItem(
                        icon='images/icon.png',
                        name='Erro ao adicionar registro. Verifique as preferências.',
                        description=error_msg,
                        on_enter=HideWindowAction()
                    )
                ])

if __name__ == '__main__':
    logger.info("Iniciando extensão...")
    ext = JournalExtension()
    ext.subscribe(KeywordQueryEvent, JournalKeywordListener())
    ext.subscribe(ItemEnterEvent, ItemEnterEventListener())
    ext.run()