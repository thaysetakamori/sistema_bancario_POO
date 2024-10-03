from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self._endereco = endereco
        self._contas = []

    @property
    def contas(self):
        return self._contas

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self._nome = nome
        self._data_nascimento = data_nascimento
        self._cpf = cpf

    @property
    def nome(self):
        return self._nome

    @property
    def cpf(self):
        return self._cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
        self._limite_transacoes = 10

    @classmethod
    def nova_conta(cls, numero, cliente):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def verificar_limite_transacoes(self):
        numero_transacoes = len(self.historico.transacoes)
        if numero_transacoes >= self._limite_transacoes:
            print("\nFalha na operação! Você excedeu o número de transações permitidas para hoje.\n")
            return False

        return True

    def depositar(self, valor):
        if not self.verificar_limite_transacoes():
            return False

        if valor > 0:
            self._saldo += valor
            print("\nDepósito realizado com sucesso!\n")
        else:
            print("\nFalha na operação! O valor informado é inválido.\n")
            return False

        return True

    def sacar(self, valor):
        if not self.verificar_limite_transacoes():
            return False

        if valor > self._saldo:
            print("\nFalha na operação! Você não tem saldo suficiente.\n")

        elif valor > 0:
            self._saldo -= valor
            print("\nSaque realizado com sucesso!\n")
            return True

        else:
            print("\nFalha na operação! O valor informado é inválido.\n")

        return False


class ContaCorrente(Conta):
    def __init__(self, numero, cliente):
        super().__init__(numero, cliente)
        self._limite = 500
        self._limite_saques = 3

    def verificar_limite_saques(self):
        numero_saques = len([transacao for transacao in self.historico.transacoes if transacao['tipo'] == "Saque"])
        if numero_saques >= self._limite_saques:
            print("\nFalha na operação! Número máximo de saques excedido.\n")
            return False

        return True

    def sacar(self, valor):
        if not self.verificar_limite_saques():
            return False

        if valor > self._limite:
            print("\nFalha na operação! O valor do saque excede o limite.\n")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"Agência: {self.agencia}\nC/C:\t {self.numero}\nTitular: {self.cliente.nome}"


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({"tipo": transacao.__class__.__name__, "valor": transacao.valor, "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")})


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def menu():
    menu = """
Insira o número da operação desejada:
[1] Depositar
[2] Sacar
[3] Extrato
[4] Novo Cliente
[5] Nova Conta
[6] Listar Contas
[0] Sair
=> """
    return input(menu)


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\nFalha na operação! Cliente não possui conta cadastrada.\n")
        return

    if len(cliente.contas) == 1:
        return cliente.contas[0]

    print("\nEscolha o número da conta desejada para operação:")
    for i, conta in enumerate(cliente.contas):
        print(f"[{i + 1}] C/C: {conta.numero}")

    try:
        op = int(input("=> ")) - 1
        if op < 0 or op >= len(cliente.contas):
            print("\nEscolha inválida! Tente novamente.")
            return recuperar_conta_cliente(cliente)

        return cliente.contas[op]

    except ValueError:
        print("\nEntrada inválida! Tente novamente.")

        return recuperar_conta_cliente(cliente)


def validar_cpf():
    cpf = input("\nInforme seu CPF (somente números): ")
    
    while not (cpf.isdigit() and len(cpf) == 11):
        print("\nCPF inválido! Certifique-se de digitar 11 números.\n")
        cpf = input("Informe seu CPF (somente número): ")

    return cpf


def realizar_operacao(clientes, tipo_operacao):
    cpf = validar_cpf()
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nFalha na operação! Cliente não encontrado.\n")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    if tipo_operacao == Saque:
        if not conta.verificar_limite_saques():
            return

    if not conta.verificar_limite_transacoes():
        return

    valor = float(input(f"\nInforme o valor do {'depósito' if tipo_operacao == Deposito else tipo_operacao.__name__.lower()}: "))
    transacao = tipo_operacao(valor)

    cliente.realizar_transacao(conta, transacao)


def depositar(clientes):
    realizar_operacao(clientes, Deposito)


def sacar(clientes):
    realizar_operacao(clientes, Saque)


def exibir_extrato(clientes):
    cpf = validar_cpf()
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nFalha na operação! Cliente não encontrado.\n")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    transacoes = conta.historico.transacoes

    print()
    print(" EXTRATO ".center(45, "="))

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações\n"
    else:
        for transacao in transacoes:
            tipo_transacao = "Depósito" if transacao['tipo'] == "Deposito" else transacao['tipo']
            extrato += f"[{transacao['data']}] {tipo_transacao}:\tR$ {transacao['valor']:.2f}\n"

    print(extrato)
    print(f"Saldo: R$ {conta.saldo:.2f}")
    print("="*45)
    print()


def cadastrar_cliente(clientes):
    cpf = validar_cpf()
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\nFalha na operação! Já existe cliente com esse CPF cadastrado.\n")
        return

    nome = input("Nome completo: ")
    data_nascimento = input("Data de nascimento (dd/mm/aaaa): ")
    endereco = input("Endereço (Logradouro, Nº - Bairro - Cidade/UF): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\nCliente cadastrado com sucesso!\n")


def criar_conta(clientes, contas):
    cpf = validar_cpf()
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nCliente não encontrado! Fluxo de criação de conta encerrado.\n")
        return

    numero_conta = len(contas) + 1

    conta = ContaCorrente.nova_conta(numero=numero_conta, cliente=cliente)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\nConta criada com sucesso!\n")
    print(f"Agência: {conta.agencia}\nC/C:\t {conta.numero}\n")


def listar_contas(contas):
    print()
    if not contas:
        print("Não existem contas cadastradas!\n")
    for conta in contas:
        print("=" * 43)
        print((str(conta)))
        print()


def main():
    clientes = []
    contas = []

    print("\nBEM-VINDO!")

    while True:
        opcao = menu()

        if opcao == "1":
            depositar(clientes)

        elif opcao == "2":
            sacar(clientes)

        elif opcao == "3":
            exibir_extrato(clientes)

        elif opcao == "4":
            cadastrar_cliente(clientes)

        elif opcao == "5":
            criar_conta(clientes, contas)

        elif opcao == "6":
            listar_contas(contas)

        elif opcao == "0":
            print("\nVOLTE SEMPRE!\n")
            break

        else:
            print("\nOpção inválida! Tente novamente.\n")


main()