import socket
from decouple import config
from .SocketCommunication import SocketCommunication
from ToolkitBCH.tconst import PORT


def check_arg(arg):
    print(arg)
    if arg and arg != '':
        return arg
    return False


def parse(arg):
    return arg.split(' ')


class NodeBCH:

    def __init__(self):
        self.p2p = None
        self.blockchain = None
        self.validator = None
        self.wallet = None
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.ip = s.getsockname()[0]
        s.close()
        self.port = PORT
        self.p2p = SocketCommunication(self.ip, self.port)

    # Запуск сетевого протокола
    def start_p2p(self):
        self.p2p.start_socket_communication(self)

    # Остановка сетевого протокола
    def stop_p2p(self):
        self.p2p.stop_socket_communication()

    # делает устройство первым (lastKnownBlockID = lastLocalBlockID), выполнить после запуска первой ноды
    # удалить из релиза
    def do_first_node(self):
        self.blockchain.lastKnownBlockID = self.blockchain.lastLocalBlockID

    # Вывод списка соединенных нод
    def get_status(self):
        return self.p2p.print_connections()

    # Вывод списка входящих подключений
    def get_inbound(self):
        return self.p2p.nodes_inbound

    # Вывод списка исходящих подключений
    def get_outbound(self):
        return self.p2p.nodes_outbound

    # Вывод списка пиров
    def get_peers(self):
        return self.p2p.peerDiscovery.to_json()

    # Вывод сведений о локальном блокчейне
    def get_blocks(self):
        return "lastKnownBlockID = {}, lastLocalBlockID = {}; isSinchronized = {}".\
            format(self.blockchain.lastKnownBlockID,
                   self.blockchain.lastLocalBlockID,
                   self.blockchain.is_synchronized())

    # Вывод баланса
    def get_amounts(self):
        if self.p2p.is_peer:
            return self.blockchain.get_amounts(self.wallet.accList)
        return self.blockchain.get_amounts()
