from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import re
from typing import List


class Confirmacao(Enum):
    SIM = "sim"
    NAO = "não"

@dataclass
class Compromisso:
    id: str
    nome: str
    telefone: str
    compromisso_data: datetime
    status: str = "Pendente"

class TelefoneValidator:
    @staticmethod
    def validar_formato_telefone(numero_telefone: str) -> bool:
        """Valida o formato do número de telefone."""
        pattern = re.compile(r'^\+\d{1,3}\d{8,14}$')  # Exemplo de expressão regular para validação de E.164
        return bool(pattern.match(numero_telefone))

class CPFValidator:
    @staticmethod
    def validar_formato_cpf(cpf: str) -> bool:
        """Valida o formato do CPF usando expressão regular."""
        pattern = re.compile(r'^\d{11}$')
        return bool(pattern.match(cpf))

class ConsultaBot:
    def __init__(self):
        self.compromissos: List[Compromisso] = []
        self.dados_usuario = {}
        self.logger = self.configurar_logger()
        self.telefone_validator = TelefoneValidator()
        self.cpf_validator = CPFValidator()

    def configurar_logger(self):
        """Configura o logger para o ConsultaBot."""
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)

    def comecar_conversa(self, id: str) -> None:
        """Inicia uma nova conversa com o usuário."""
        if id not in self.dados_usuario:
            self.dados_usuario[id] = {"nome": None, "cpf": None, "email": None}

        self.logger.info("Bem-vindo ao ConsultaBot! Como posso ajudar você hoje?")
        compromisso = self.verificar_identidade(id)
        self.confirmar_compromissos(compromisso)

    def verificar_identidade(self, id: str) -> Compromisso:
        """Verifica a identidade do usuário."""
        if self.dados_usuario[id]["nome"] is None:
            self.dados_usuario[id]["nome"] = input("Por favor, digite seu nome completo: ")

        if self.dados_usuario[id]["cpf"] is None:
            self.verificar_cpf(id)

        # Adapte para verificar outras informações, como e-mail, se necessário

        return self.pegar_detalhes(id)

    def verificar_cpf(self, id: str) -> None:
        """Verifica e solicita o CPF do usuário."""
        while True:
            cpf = input("Seu CPF não foi encontrado. Por favor, digite seu CPF: ")
            # Adapte para verificar o CPF em seu banco de dados
            if self.cpf_validator.validar_formato_cpf(cpf):
                self.dados_usuario[id]["cpf"] = cpf
                break
            else:
                print("CPF inválido. Tente novamente.")

    def pegar_detalhes(self, id: str) -> Compromisso:
        """Obtém detalhes adicionais do usuário."""
        nome = self.dados_usuario[id]["nome"]
        cpf = self.dados_usuario[id]["cpf"]

        print(f"\nOlá, {nome}!")
        while True:
            try:
                data_str = input("Quando você gostaria de marcar o compromisso? (Formato: DD/MM/YYYY): ")
                if self.validar_formato_data(data_str):
                    compromisso_data = datetime.strptime(data_str, "%d/%m/%Y")
                    if compromisso_data < datetime.now():
                        print("Por favor, insira uma data futura.")
                    else:
                        datas_validas = self.pegar_datas_validas(compromisso_data)
                        print("\nDatas disponíveis para compromisso:")
                        for i, date in enumerate(datas_validas, start=1):
                            print(f"{i}. {date.strftime('%d/%m/%Y')}")

                        indice_data_selecionada = int(input("Escolha uma data (número): "))
                        data_selecionada = datas_validas[indice_data_selecionada - 1]
                        return Compromisso(id, nome, cpf, data_selecionada)
                else:
                    print("Formato de data inválido. Tente novamente.")
            except ValueError:
                print("Formato de data inválido. Tente novamente.")

    def validar_formato_data(self, data_str: str) -> bool:
        """Valida o formato da data."""
        try:
            datetime.strptime(data_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def pegar_datas_validas(self, start_date: datetime) -> List[datetime]:
        """Obtém datas válidas para compromisso."""
        # Adapte para obter datas disponíveis a partir de sua base de dados ou lógica de agendamento
        return [start_date + timedelta(days=i) for i in range(7)]

    def confirmar_compromissos(self, compromisso: Compromisso) -> None:
        """Confirma os detalhes do compromisso."""
        print("\nConfirme os detalhes do compromisso:")
        print(f"Nome: {compromisso.nome}")
        print(f"CPF: {compromisso.telefone}")
        print(f"Data do Compromisso: {compromisso.compromisso_data.strftime('%d/%m/%Y')}")
        confirmacao = input("\nOs detalhes estão corretos? (Sim/Não): ").lower()
        if self.processar_confirmacao(confirmacao) == Confirmacao.SIM:
            if self.validar_e_adicionar_compromisso(compromisso):
                print("Compromisso marcado com sucesso! Aguardamos por você.")
            else:
                print("Erro ao adicionar compromisso. Por favor, tente novamente.")
        else:
            self.comecar_conversa(compromisso.id)

    def processar_confirmacao(self, confirmacao: str) -> Confirmacao:
        """Processa a confirmação do usuário."""
        if confirmacao == Confirmacao.SIM.value:
            return Confirmacao.SIM
        elif confirmacao == Confirmacao.NAO.value:
            return Confirmacao.NAO
        else:
            print("Opção inválida. Por favor, digite 'Sim' ou 'Não'.")
            return self.processar_confirmacao(input("Os detalhes estão corretos? (Sim/Não): ").lower())

    def validar_e_adicionar_compromisso(self, compromisso: Compromisso) -> bool:
        """Valida e adiciona o compromisso à lista."""
        try:
            # Lógica de validação aqui
            self.compromissos.append(compromisso)
            # Adicionar registro de compromisso bem-sucedido ao registro de eventos
            self.logger.info("Compromisso adicionado com sucesso!")
            return True
        except Exception as e:
            # Adicionar registro de compromisso com falha ao registro de eventos
            self.logger.error(f"Erro ao adicionar compromisso: {str(e)}")
            return False

    def verifica_telefone(self) -> str:
        """Solicita ao usuário o número de telefone e valida a entrada."""
        while True:
            numero_telefone = input("Por favor, digite seu número de telefone: ")
            if self.telefone_validator.validar_formato_telefone(numero_telefone):
                return numero_telefone
            else:
                print("Formato de número de telefone inválido. Tente novamente.")

if __name__ == "__main__":
    consulta_bot = ConsultaBot()
    numero_telefone = consulta_bot.verifica_telefone()
    consulta_bot.comecar_conversa(numero_telefone)

