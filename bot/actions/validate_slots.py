#========= Importações =========================================================
# Aqui ficam as importações de modulos e bibliotecas
from errno import errorcode
import re
import mysql.connector
from mysql.connector import errorcode
# import MySQLdb
from datetime import datetime
from typing import Text, List, Any, Dict
import time
from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import AllSlotsReset
from rasa_sdk.events import SlotSet

tentativas_cpf = 0
menu = 0
tipo_agendamento = ''
#============================== Actions =========================================
# Aqui ficam as ações que o bot pode executar

# Classe de não possui prontuário

class ValidateCisamForm(FormValidationAction):
    def name(self) -> Text:
            return "validate_cisam_form"

    def validate_user_lgpd(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate user_lgpd"""
        global tentativas_cpf
        #====== Caso o usuário concorde informando 1, o bot continua ============
        if slot_value == '1' or slot_value == 'um' or slot_value == 'número um':
            tentativas_cpf = 0
            dispatcher.utter_message(response="utter_user_lgpd_sim")
            dispatcher.utter_message(response="utter_form_dois") # chega até aqui
            return {"user_lgpd": slot_value}
        #===== Caso o usuário discorde informando 2, o bot para =================
        elif slot_value == '2' or slot_value == 'dois' or slot_value == 'número dois':
            dispatcher.utter_message(response="utter_user_lgpd_nao")
            return {"user_lgpd": None, "requested_slot": None}
        #===== Caso o usuário não informe sim ou não ============================
        else:
            dispatcher.utter_message(response="utter_user_lgpd_errado")
            return {"user_lgpd": None}

    def validate_user_cpf(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate user_cpf"""
        # volta pro dialogo anterior
        if slot_value == 'voltar':
            dispatcher.utter_message(response="utter_ask_user_lgpd")
            return {"user_cpf": None, "user_lgpd": None}
        # resposta negativa
        elif slot_value == 'n':
            dispatcher.utter_message(response="utter_cenario_um_menu_resp_dois")
            return {"user_lgpd": None,"user_cpf": None, "requested_slot": None}
        
        elif slot_value == 's':
            dispatcher.utter_message(response="utter_sem_prontuario_sim")
            global tentativas_cpf
            tentativas_cpf = 1
            return {"user_cpf": None}
        
        elif slot_value == 'sim':
            msg = 'nao tenho'
            dispatcher.utter_message(response="utter_sem_prontuario_2_sim")
            return {"user_cpf": msg, "requested_slot": None}
        
        # inseriu o cpf, passou pelo regex e esta valido
        else:
            if UtilsForm.validar_cpf(slot_value) == True:
                time.sleep(4)
                if len(slot_value) == 11:
                    cpf = f'{slot_value[0]}{slot_value[1]}{slot_value[2]}.{slot_value[3]}{slot_value[4]}{slot_value[5]}.{slot_value[6]}{slot_value[7]}{slot_value[8]}-{slot_value[9]}{slot_value[10]}'
                    resultado = ValidateCPFNaoProntuario.validate_cpf_nao_prontuario(cpf)
                    if resultado != None and resultado != [] and resultado != [(None,), (None,)]:
                        dispatcher.utter_message(response="utter_validate_cpf_prontuario_encontrado")
                        dispatcher.utter_message(response="utter_nome")
                        return {"user_cpf": slot_value}
                    else:
                        if tentativas_cpf == 0:
                            dispatcher.utter_message(response="utter_sem_prontuario")
                            return {"user_cpf": None}
                        else:
                            dispatcher.utter_message(response="utter_sem_prontuario_2")
                            return {"user_cpf": None}
                        
                elif len(slot_value) == 14:
                    resultado = ValidateCPFNaoProntuario.validate_cpf_nao_prontuario(slot_value)
                    if resultado != None and resultado != [] and resultado != [(None,), (None,)]:
                        dispatcher.utter_message(response="utter_validate_cpf_prontuario_encontrado")
                        dispatcher.utter_message(response="utter_nome")
                        return {"user_cpf": slot_value}
                    else:
                        if tentativas_cpf == 0:
                            dispatcher.utter_message(response="utter_sem_prontuario")
                            return {"user_cpf": None}
                        else:
                            dispatcher.utter_message(response="utter_sem_prontuario_2")
                            return {"user_cpf": None}

            else:
                dispatcher.utter_message(response="utter_user_cpf_invalido")
                return {"user_cpf": None}
            
    def validate_user_nome(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate user_nome"""
        global menu
        # volta pro dialogo anterior
        if slot_value == 'voltar':
            dispatcher.utter_message(response="utter_form_dois")
            return {"user_nome": None, "user_cpf": None}
        else:
            if len(slot_value) >= 2 and not slot_value.isdigit():
                menu = 0
                dispatcher.utter_message(response="utter_cenario_dois_menu")
                return {"user_nome": slot_value}
            else:
                dispatcher.utter_message(response="utter_nome_errado")
                return {"user_nome": None}          
    
    def validate_cenario_dois_menu(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        global tipo_agendamento
        global menu
        """Validate cenario_dois_menu"""
        # volta pro dialogo volta pro inicio do menu
        if slot_value == 'menu':
            menu = 0
            dispatcher.utter_message(response="utter_cenario_dois_menu")
            return {"cenario_dois_menu": None}
        
        # volta pro dialogo anterior
        if slot_value == 'voltar':
            dispatcher.utter_message(response="utter_user_email")
            return {"cenario_dois_menu": None, "user_email": None}
        # sair do menu
        if menu != 0 and slot_value == 'enviar':
            dispatcher.utter_message(response="utter_fim_form")
            return {"cenario_dois_menu": tipo_agendamento, "controle": 1}
        
        if slot_value == 'sair':
            dispatcher.utter_message(response="utter_terminar")
            return {"cenario_dois_menu": slot_value, "controle": 2}
        
        # continuar desenvolvendo a lógica ============= <

        elif menu != 0 and slot_value == 'continuar':
            dispatcher.utter_message(response="utter_gine_queixa")
            return {"cenario_dois_menu": None}

        elif slot_value == '1' or slot_value == 'número um':
            menu = 1
            dispatcher.utter_message(response="utter_cenario_dois_menu_resp_um")
            return {"cenario_dois_menu": None}
        elif menu == 1 and slot_value == 'número um a' or menu == 1 and slot_value== 'número 1 a' or menu == 1 and slot_value == 'número uma' or menu == 1 and slot_value == 'número 1A':
            dispatcher.utter_message(response="utter_repro_um")
            tipo_agendamento = 'Reproducao Humana'
            return {"cenario_dois_menu": None}
        elif menu == 1 and slot_value == 'número um b' or menu == 1 and slot_value== 'número 1 b' or menu == 1 and slot_value == 'número umb' or menu == 1 and slot_value == 'número 1B':
            dispatcher.utter_message(response="utter_repro_dois")
            tipo_agendamento = 'Laqueadura tubária'
            return {"cenario_dois_menu": None}
        
        elif menu == 1 and slot_value == 'número um c' or menu == 1 and slot_value== 'número 1 c' or menu == 1 and slot_value == 'número umc' or menu == 1 and slot_value == 'número 1C':
            dispatcher.utter_message(response="utter_repro_tres")
            tipo_agendamento = 'Teleconsulta para métodos contraceptivos'
            return {"cenario_dois_menu": None}
        
        elif slot_value == '2' or slot_value == 'número dois':
            menu = 2
            dispatcher.utter_message(response="utter_cenario_dois_menu_resp_dois")
            return {"cenario_dois_menu": None}
        elif menu == 2 and slot_value == 'número dois a' or menu == 2 and slot_value== 'número 2 a' or menu == 2 and slot_value == 'número doisa' or menu == 2 and slot_value == 'número 2A':
            dispatcher.utter_message(response="utter_dent_um")
            tipo_agendamento = 'Dentista da FOP'
            return {"cenario_dois_menu": None}
        elif menu == 2 and slot_value == 'número dois b' or menu == 2 and slot_value== 'número 2 b' or menu == 2 and slot_value == 'número doisb' or menu == 2 and slot_value == 'número 2B':
            dispatcher.utter_message(response="utter_dent_dois")
            tipo_agendamento = 'Dentista do Cisam'
            return {"cenario_dois_menu": None}
        
        elif slot_value == '3' or slot_value == 'número três':
            menu = 3
            dispatcher.utter_message(response="utter_cenario_dois_menu_resp_tres")
            return {"cenario_dois_menu": None}
        elif menu == 3 and slot_value == 'número três a' or menu == 3 and slot_value== 'número 3 a' or menu == 3 and slot_value == 'número trêsa' or menu == 3 and slot_value == 'número 3A':
            dispatcher.utter_message(response="utter_histe_um")
            tipo_agendamento = 'Exame histeroscopia diagnóstica'
            return {"cenario_dois_menu": None}
        elif menu == 3 and slot_value == 'número três b' or menu == 3 and slot_value== 'número 3 b' or menu == 3 and slot_value == 'número trêsb' or menu == 3 and slot_value == 'número 3B':
            dispatcher.utter_message(response="utter_histe_dois")
            tipo_agendamento = 'Exame histeroscopia diagnóstica'
            return {"cenario_dois_menu": None}
        

        elif slot_value == '4' or slot_value == 'número quatro':
            menu = 4
            dispatcher.utter_message(response="utter_cenario_dois_menu_resp_quatro")
            return {"cenario_dois_menu": None}
        elif menu == 4 and slot_value == 'número quatro a' or menu == 4 and slot_value== 'número 4 a' or menu == 4 and slot_value == 'número quatroa' or menu == 4 and slot_value == 'número 4A':
            dispatcher.utter_message(response="utter_gine_um")
            tipo_agendamento = 'Endocrinologia Ginecológica'
            return {"cenario_dois_menu": None}
        elif menu == 4 and slot_value == 'número quatro b' or menu == 4 and slot_value== 'número 4 b' or menu == 4 and slot_value == 'número quatrob' or menu == 4 and slot_value == 'número 4B':
            dispatcher.utter_message(response="utter_gine_dois")
            tipo_agendamento = 'Endometriose'
            return {"cenario_dois_menu": None}
        elif menu == 4 and slot_value == 'número quatro c' or menu == 4 and slot_value== 'número 4 c' or menu == 4 and slot_value == 'número quatroc' or menu == 4 and slot_value == 'número 4C':
            dispatcher.utter_message(response="utter_gine_tres")
            tipo_agendamento = 'Mastologia'
            return {"cenario_dois_menu": None}
        elif menu == 4 and slot_value == 'número quatro d' or menu == 4 and slot_value== 'número 4 d' or menu == 4 and slot_value == 'número quatrod' or menu == 4 and slot_value == 'número 4D':
            dispatcher.utter_message(response="utter_gine_quatro")
            tipo_agendamento = 'Climatério'
            return {"cenario_dois_menu": None}
        elif menu == 4 and slot_value == 'número quatro e' or menu == 4 and slot_value== 'número 4 e' or menu == 4 and slot_value == 'número quatroe' or menu == 4 and slot_value == 'número 4E':
            dispatcher.utter_message(response="utter_gine_cinco")
            tipo_agendamento = 'Ginecologia Geral'
            return {"cenario_dois_menu": None}

        # escolhas do menu ginecologia queixas
        elif menu == 4 and slot_value == 'quatro aa' or menu == 4 and slot_value== 'número 4 aa' or menu == 4 and slot_value == 'número quatroaa' or menu == 4 and slot_value == 'número 4AA':
            dispatcher.utter_message(response="utter_gine_confirma")
            return {"cenario_dois_menu": None, "queixa": 'Dor/Sangramento/Corrimento/Prurido'}
        elif menu == 4 and slot_value == 'quatro ab' or menu == 4 and slot_value== 'número 4 ab' or menu == 4 and slot_value == 'número quatroab' or menu == 4 and slot_value == 'número 4AB':
            dispatcher.utter_message(response="utter_gine_confirma")
            return {"cenario_dois_menu": None, "queixa": 'Mioma/Cisto/Pólipo'}
        elif menu == 4 and slot_value == 'quatro ac' or menu == 4 and slot_value== 'número 4 ac' or menu == 4 and slot_value == 'número quatroac' or menu == 4 and slot_value == 'número 4AC':
            dispatcher.utter_message(response="utter_gine_confirma")
            return {"cenario_dois_menu": None, "queixa": 'Resultado/Solicitação de exames'}
        elif menu == 4 and slot_value == 'quatro ad' or menu == 4 and slot_value== 'número 4 ad' or menu == 4 and slot_value == 'número quatroad' or menu == 4 and slot_value == 'número 4AD':
            dispatcher.utter_message(response="utter_gine_confirma")
            return {"cenario_dois_menu": None, "queixa":'Sem queixa, consulta de rotina'}
        elif menu == 4 and slot_value == 'quatro ae' or menu == 4 and slot_value== 'número 4 ae' or menu == 4 and slot_value == 'número quatroae' or menu == 4 and slot_value == 'número 4AE':
            dispatcher.utter_message(response="utter_gine_confirma")
            return {"cenario_dois_menu": None, "queixa": 'Nenhuma das opções'}

        elif slot_value == '5' or slot_value == 'número cinco':
            menu = 5
            dispatcher.utter_message(response="utter_cenario_dois_menu_resp_cinco")
            return {"cenario_dois_menu": None}
        elif menu == 5 and slot_value == 'cinco a' or menu == 5 and slot_value== 'número 5 a' or menu == 5 and slot_value == 'número cincoa' or menu == 5 and slot_value == 'número 5A':
            dispatcher.utter_message(response="utter_cirur_um")
            tipo_agendamento = 'Cirurgia geral em Ginecologia'
            return {"cenario_dois_menu": None}
        elif menu == 5 and slot_value == 'cinco b' or menu == 5 and slot_value== 'número 5 b' or menu == 5 and slot_value == 'número cincob' or menu == 5 and slot_value == 'número 5B':
            dispatcher.utter_message(response="utter_cirur_dois")
            tipo_agendamento = 'Cirurgia de Reversão Tubária'
            return {"cenario_dois_menu": None}

        elif slot_value == '6' or slot_value == 'número seis':
            menu = 6
            dispatcher.utter_message(response="utter_cenario_dois_menu_resp_seis")
            return {"cenario_dois_menu": None}
        elif menu == 6 and slot_value == 'seis a' or menu == 6 and slot_value== 'número 6 a' or menu == 6 and slot_value == 'número seisa' or menu == 6 and slot_value == 'número 6A':
            dispatcher.utter_message(response="utter_derma_um")
            tipo_agendamento = 'Dermatologia - Primeira Consulta'
            return {"cenario_dois_menu": None}
        elif menu == 6 and slot_value == 'seis b' or menu == 6 and slot_value== 'número 6 b' or menu == 6 and slot_value == 'número seisb' or menu == 6 and slot_value == 'número 6B':
            dispatcher.utter_message(response="utter_derma_dois")
            tipo_agendamento = 'Dermatologia - Consulta de Retorno'
            return {"cenario_dois_menu": None}

        else:
            dispatcher.utter_message(response="utter_cenario_dois_menu_resp_errado")
            return {"cenario_dois_menu": None}

class ValidateCisamFormDois(FormValidationAction):
    def name(self) -> Text:
            return "validate_cisam_form_dois"

    def validate_user_nome_completo(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate user_nome_completo"""
        # volta pro dialogo anterior
        
        if len(slot_value) >= 10 and not slot_value.isdigit():
            dispatcher.utter_message(response="utter_user_data_nasc")
            return {"user_nome_completo": slot_value}
        else:
            dispatcher.utter_message(response="utter_nome_completo_errado")
            return {"user_nome_completo": None}
    
    def validate_user_data_nasc(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate user_data_nasc"""
        # volta pro dialogo anterior
        if slot_value == 'voltar':
            dispatcher.utter_message(response="utter_user_nome_completo")
            return {"user_data_nasc": None, "user_nome_completo": None}
        else:
            if UtilsForm.check_data_nasc(slot_value) == 'valido':
                dispatcher.utter_message(response="utter_user_telefone")
                return {"user_data_nasc": slot_value}
            else:
                dispatcher.utter_message(response="utter_user_data_nasc_invalido")
                return {"user_data_nasc": None}
    
    def validate_user_telefone(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate user_telefone"""
        # volta pro dialogo anterior
        if slot_value == 'voltar':
            dispatcher.utter_message(response="utter_user_data_nasc")
            return {"user_telefone": None, "user_data_nasc": None}
        else:
            if UtilsForm.check_telefone(slot_value) == 'valido':
                dispatcher.utter_message(response="utter_user_email")
                return {"user_telefone": slot_value}
            else:
                dispatcher.utter_message(response="utter_user_telefone_invalido")
                return {"user_telefone": None}
              
    def validate_user_email(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate user_email"""
        # volta pro dialogo anterior
        global menu
        if slot_value == 'voltar':
            dispatcher.utter_message(response="utter_user_telefone")
            return {"user_email": None, "user_telefone": None}
        else:
            if UtilsForm.check_email(slot_value) == 'valido':
                menu = 0
                dispatcher.utter_message(response="utter_cenario_dois_menu_prontuario")
                return {"user_email": slot_value}
            else:
                dispatcher.utter_message(response="utter_user_email_invalido")
                return {"user_email": None}
    
    def validate_cenario_dois_menu(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        global tipo_agendamento
        global menu
        """Validate cenario_dois_menu"""
        # volta pro dialogo volta pro inicio do menu
        if slot_value == 'menu':
            menu = 0
            dispatcher.utter_message(response="utter_cenario_dois_menu_prontuario")
            return {"cenario_dois_menu": None}
        
        # volta pro dialogo anterior
        if slot_value == 'voltar':
            dispatcher.utter_message(response="utter_user_email")
            return {"cenario_dois_menu": None, "user_email": None}
        # sair do menu
        if menu != 0 and slot_value == 'enviar':
            dispatcher.utter_message(response="utter_fim_form")
            return {"cenario_dois_menu": tipo_agendamento, "controle": 1}
        
        if slot_value == 'sair':
            dispatcher.utter_message(response="utter_terminar")
            return {"cenario_dois_menu": slot_value, "controle": 2}
        
        # continuar desenvolvendo a lógica ============= <

        elif menu != 0 and slot_value == 'continuar':
            dispatcher.utter_message(response="utter_gine_queixa")
            return {"cenario_dois_menu": None}

        elif slot_value == '1' or slot_value == 'número um':
            menu = 1
            dispatcher.utter_message(response="utter_cenario_dois_menu_resp_um")
            return {"cenario_dois_menu": None}
        elif menu == 1 and slot_value == 'número um a' or menu == 1 and slot_value== 'número 1 a' or menu == 1 and slot_value == 'número uma' or menu == 1 and slot_value == 'número 1A':
            dispatcher.utter_message(response="utter_repro_um")
            tipo_agendamento = 'Reproducao Humana'
            return {"cenario_dois_menu": None}
        elif menu == 1 and slot_value == 'número um b' or menu == 1 and slot_value== 'número 1 b' or menu == 1 and slot_value == 'número umb' or menu == 1 and slot_value == 'número 1B':
            dispatcher.utter_message(response="utter_repro_dois")
            tipo_agendamento = 'Laqueadura tubária'
            return {"cenario_dois_menu": None}
        
        elif menu == 1 and slot_value == 'número um c' or menu == 1 and slot_value== 'número 1 c' or menu == 1 and slot_value == 'número umc' or menu == 1 and slot_value == 'número 1C':
            dispatcher.utter_message(response="utter_repro_tres")
            tipo_agendamento = 'Teleconsulta para métodos contraceptivos'
            return {"cenario_dois_menu": None}
        
        elif slot_value == '2' or slot_value == 'número dois':
            menu = 2
            dispatcher.utter_message(response="utter_cenario_dois_menu_resp_dois")
            return {"cenario_dois_menu": None}
        elif menu == 2 and slot_value == 'número dois a' or menu == 2 and slot_value== 'número 2 a' or menu == 2 and slot_value == 'número doisa' or menu == 2 and slot_value == 'número 2A':
            dispatcher.utter_message(response="utter_dent_um")
            tipo_agendamento = 'Dentista da FOP'
            return {"cenario_dois_menu": None}
        elif menu == 2 and slot_value == 'número dois b' or menu == 2 and slot_value== 'número 2 b' or menu == 2 and slot_value == 'número doisb' or menu == 2 and slot_value == 'número 2B':
            dispatcher.utter_message(response="utter_dent_dois")
            tipo_agendamento = 'Dentista do Cisam'
            return {"cenario_dois_menu": None}
        
        elif slot_value == '3' or slot_value == 'número três':
            menu = 3
            dispatcher.utter_message(response="utter_cenario_dois_menu_resp_tres")
            return {"cenario_dois_menu": None}
        elif menu == 3 and slot_value == 'número três a' or menu == 3 and slot_value== 'número 3 a' or menu == 3 and slot_value == 'número trêsa' or menu == 3 and slot_value == 'número 3A':
            dispatcher.utter_message(response="utter_histe_um")
            tipo_agendamento = 'Exame histeroscopia diagnóstica'
            return {"cenario_dois_menu": None}
        elif menu == 3 and slot_value == 'número três b' or menu == 3 and slot_value== 'número 3 b' or menu == 3 and slot_value == 'número trêsb' or menu == 3 and slot_value == 'número 3B':
            dispatcher.utter_message(response="utter_histe_dois")
            tipo_agendamento = 'Exame histeroscopia diagnóstica'
            return {"cenario_dois_menu": None}
        

        elif slot_value == '4' or slot_value == 'número quatro':
            menu = 4
            dispatcher.utter_message(response="utter_cenario_dois_menu_resp_quatro")
            return {"cenario_dois_menu": None}
        elif menu == 4 and slot_value == 'número quatro a' or menu == 4 and slot_value== 'número 4 a' or menu == 4 and slot_value == 'número quatroa' or menu == 4 and slot_value == 'número 4A':
            dispatcher.utter_message(response="utter_gine_um")
            tipo_agendamento = 'Endocrinologia Ginecológica'
            return {"cenario_dois_menu": None}
        elif menu == 4 and slot_value == 'número quatro b' or menu == 4 and slot_value== 'número 4 b' or menu == 4 and slot_value == 'número quatrob' or menu == 4 and slot_value == 'número 4B':
            dispatcher.utter_message(response="utter_gine_dois")
            tipo_agendamento = 'Endometriose'
            return {"cenario_dois_menu": None}
        elif menu == 4 and slot_value == 'número quatro c' or menu == 4 and slot_value== 'número 4 c' or menu == 4 and slot_value == 'número quatroc' or menu == 4 and slot_value == 'número 4C':
            dispatcher.utter_message(response="utter_gine_tres")
            tipo_agendamento = 'Mastologia'
            return {"cenario_dois_menu": None}
        elif menu == 4 and slot_value == 'número quatro d' or menu == 4 and slot_value== 'número 4 d' or menu == 4 and slot_value == 'número quatrod' or menu == 4 and slot_value == 'número 4D':
            dispatcher.utter_message(response="utter_gine_quatro")
            tipo_agendamento = 'Climatério'
            return {"cenario_dois_menu": None}
        elif menu == 4 and slot_value == 'número quatro e' or menu == 4 and slot_value== 'número 4 e' or menu == 4 and slot_value == 'número quatroe' or menu == 4 and slot_value == 'número 4E':
            dispatcher.utter_message(response="utter_gine_cinco")
            tipo_agendamento = 'Ginecologia Geral'
            return {"cenario_dois_menu": None}

        # escolhas do menu ginecologia queixas
        elif menu == 4 and slot_value == 'número quatro aa' or menu == 4 and slot_value== 'número 4 aa' or menu == 4 and slot_value == 'número quatroaa' or menu == 4 and slot_value == 'número 4AA':
            dispatcher.utter_message(response="utter_gine_confirma")
            return {"cenario_dois_menu": None, "queixa": 'Dor/Sangramento/Corrimento/Prurido'}
        elif menu == 4 and slot_value == 'número quatro ab' or menu == 4 and slot_value== 'número 4 ab' or menu == 4 and slot_value == 'número quatroab' or menu == 4 and slot_value == 'número 4AB':
            dispatcher.utter_message(response="utter_gine_confirma")
            return {"cenario_dois_menu": None, "queixa": 'Mioma/Cisto/Pólipo'}
        elif menu == 4 and slot_value == 'número quatro ac' or menu == 4 and slot_value== 'número 4 ac' or menu == 4 and slot_value == 'número quatroac' or menu == 4 and slot_value == 'número 4AC':
            dispatcher.utter_message(response="utter_gine_confirma")
            return {"cenario_dois_menu": None, "queixa": 'Resultado/Solicitação de exames'}
        elif menu == 4 and slot_value == 'número quatro ad' or menu == 4 and slot_value== 'número 4 ad' or menu == 4 and slot_value == 'número quatroad' or menu == 4 and slot_value == 'número 4AD':
            dispatcher.utter_message(response="utter_gine_confirma")
            return {"cenario_dois_menu": None, "queixa":'Sem queixa, consulta de rotina'}
        elif menu == 4 and slot_value == 'número quatro ae' or menu == 4 and slot_value== 'número 4 ae' or menu == 4 and slot_value == 'número quatroae' or menu == 4 and slot_value == 'número 4AE':
            dispatcher.utter_message(response="utter_gine_confirma")
            return {"cenario_dois_menu": None, "queixa": 'Nenhuma das opções'}

        elif slot_value == '5' or slot_value == 'número cinco':
            menu = 5
            dispatcher.utter_message(response="utter_cenario_dois_menu_resp_cinco")
            return {"cenario_dois_menu": None}
        elif menu == 5 and slot_value == 'cinco a' or menu == 5 and slot_value== 'número 5 a' or menu == 5 and slot_value == 'número cincoa' or menu == 5 and slot_value == 'número 5A':
            dispatcher.utter_message(response="utter_cirur_um")
            tipo_agendamento = 'Cirurgia geral em Ginecologia'
            return {"cenario_dois_menu": None}
        elif menu == 5 and slot_value == 'cinco b' or menu == 5 and slot_value== 'número 5 b' or menu == 5 and slot_value == 'número cincob' or menu == 5 and slot_value == 'número 5B':
            dispatcher.utter_message(response="utter_cirur_dois")
            tipo_agendamento = 'Cirurgia de Reversão Tubária'
            return {"cenario_dois_menu": None}

        elif slot_value == '6' or slot_value == 'número seis':
            menu = 6
            dispatcher.utter_message(response="utter_cenario_dois_menu_resp_seis")
            return {"cenario_dois_menu": None}
        elif menu == 6 and slot_value == 'seis a' or menu == 6 and slot_value== 'número 6 a' or menu == 6 and slot_value == 'número seisa' or menu == 6 and slot_value == 'número 6A':
            dispatcher.utter_message(response="utter_derma_um")
            tipo_agendamento = 'Dermatologia - Primeira Consulta'
            return {"cenario_dois_menu": None}
        elif menu == 6 and slot_value == 'seis b' or menu == 6 and slot_value== 'número 6 b' or menu == 6 and slot_value == 'número seisb' or menu == 6 and slot_value == 'número 6B':
            dispatcher.utter_message(response="utter_derma_dois")
            tipo_agendamento = 'Dermatologia - Consulta de Retorno'
            return {"cenario_dois_menu": None}

        else:
            dispatcher.utter_message(response="utter_cenario_dois_menu_resp_errado")
            return {"cenario_dois_menu": None}

#============================= Ação resetar todos os slots=======================
# Aqui os slots são resetados

class ActionResetAllSlots(Action):
    # reseta os slots
    def name(self):
        return "action_reset_all_slots"

    def run(self, dispatcher, tracker, domain):
        return [AllSlotsReset()]


class UtilsForm:
    # funcao que checka o email por regex
    def check_email(email):
        regex = '^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'
        if re.search(regex, email):
            return "valido"
        else:
            return "invalido"
     # funcao que checka o telefone por regex
    def check_telefone(telefone):
        regex = '^(?:[14689][1-9]|2[12478]|3[1234578]|5[1345]|7[134579])\-? ?(?:[2-8]|9[1-9])[0-9]{3}\-?[0-9]{4}$'
        if re.search(regex, telefone):
            return "valido"
        else:
            return "invalido"
  # funcao que checka a data
    def check_data_nasc(data_nasc):
        formatos = ('%d.%m.%Y', '%d-%m-%Y', '%d/%m/%Y')

        for formato in formatos:
            try:
                datetime.strptime(data_nasc, formato)
                return "valido"
            except ValueError:
                pass
        return "invalido"
     # funcao que checka o cpf por regex
    def check_cpf(cpf):
        regex = '^(\d{3})\.?(\d{3})\.?(\d{3})\-?(\d{2})$'
        if re.search(regex, cpf):
            return "valido"
        else:
            return "invalido"
        
    def validar_cpf(cpf):
        if len(cpf) > 11:
            cpf = cpf.replace(".", "").replace("-", "") # remove pontos e traço do CPF
            if not cpf.isnumeric() or len(cpf) != 11: # verifica se o CPF contém apenas números e tem 11 dígitos
                return False
            # calcula o primeiro dígito verificador
            soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
            resto = soma % 11
            digito1 = 0 if resto < 2 else 11 - resto
            # calcula o segundo dígito verificador
            soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
            resto = soma % 11
            digito2 = 0 if resto < 2 else 11 - resto
            # verifica se os dígitos verificadores são iguais aos do CPF
            return cpf[-2:] == str(digito1) + str(digito2)
        
        if len(cpf) == 11: # verifica se o CPF contém apenas números e tem 11 dígitos
            # calcula o primeiro dígito verificador
            soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
            resto = soma % 11
            digito1 = 0 if resto < 2 else 11 - resto
            # calcula o segundo dígito verificador
            soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
            resto = soma % 11
            digito2 = 0 if resto < 2 else 11 - resto
            # verifica se os dígitos verificadores são iguais aos do CPF
            return cpf[-2:] == str(digito1) + str(digito2)
        else:
            return False


#========= Conexão com banco de dados ==========================================
def DataUpdate(lgpd, nome, cpf, telefone, email, sexo, data_nasc):
    '''
    Entrada: dados do formulario
    Envia para o banco de dados: slots preenchidos
    '''
    config = {
                'user': 'root',
                'password': 'root',
                'host': 'mysqldb',
                'port': '3306',
                'database': 'Cisam',
                }
            
    mydb = mysql.connector.connect(**config)

    mycursor = mydb.cursor()
    # codigo sql
    sql = 'INSERT INTO UserCisam (user_lgpd, user_cpf, user_cpf, user_telefone, user_email, user_sexo, user_data_nasc) VALUES ("{0}","{1}","{2}","{3}","{4}","{5}","{6}");'.format(lgpd, nome, cpf, telefone, email, sexo, data_nasc)
    mycursor.execute(sql)
    mydb.commit()
    mydb.close()


#=========== Ação submeter ===============================================
class ActionSubmit(Action):
    '''
    Atribui os slots as variaveis
    Envia para a funcao data update
    '''
    def name(self) -> Text:
        return "action_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        controle = tracker.get_slot("controle")
        lgpd = tracker.get_slot("user_lgpd")
        if controle == 1 or controle == '1':
            try:
                dispatcher.utter_message(text="Enviando para o DB")
                
                # lgpd = tracker.get_slot("user_lgpd")
                # nome =  tracker.get_slot("user_cpf")
                # cpf = tracker.get_slot("user_cpf")
                # telefone = tracker.get_slot("user_telefone")
                # email = tracker.get_slot("user_email")
                # sexo = tracker.get_slot("user_sexo")
                # data_nasc = tracker.get_slot("user_data_nasc")

                # DataUpdate(lgpd, nome, cpf, telefone, email, sexo, data_nasc)
                return [AllSlotsReset()]
                #==============================================================
            except Exception as erro:
               dispatcher.utter_message(text=erro)
        elif controle == 2 or controle == '2':
            return [AllSlotsReset()]
        elif lgpd == 2 or lgpd == '2':
            return [AllSlotsReset()]

class ValidateCPFNaoProntuario:

    def validate_cpf_nao_prontuario(cpf):
        '''
        Recebe como parametro o cpf
        Retorna o campo encontrado ou vazio se nada foi encontrado
        '''
        try:
            config = {
                'user': 'root',
                'password': 'root',
                'host': 'mysqldb',
                'port': '3306',
                'database': 'Cisam',
                }
            
            mydb = mysql.connector.connect(**config)
            
            mycursor = mydb.cursor()
            sql = f"SELECT (cpf) FROM tb_UserCisam WHERE cpf = '{cpf}';"
            mycursor.execute(sql)
            confirmaCPF = mycursor.fetchall()
            mydb.close()
            return confirmaCPF    
        except mysql.connector.Error as err:
            return "Ops! Acho que algo deu errado, vamos resolver o mais rápido possível."
        
