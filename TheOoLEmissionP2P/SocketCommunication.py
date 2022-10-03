from .PeerDiscovery import PeerDiscovery
from .PeerDiscoveryHandler import PeerDiscoveryHandler
from .SocketConnector import SocketConnector
from .SeedDiscovery import SeedDiscovery
from .Message import Message
from p2pnetwork.node import Node
import json
import copy
import random
import time
from collections import defaultdict
from.ActionsCommunication import ActionsCommunication


class SocketCommunication(Node):

    def __init__(self, ip: str, port: str):
        """
        :param ip:
        :param port:
        """
        self.ip = ip
        self.port = port
        self.is_peer = True
        self.no_seeds = False
        self.is_updated = True
        self.node = None
        self.pong = list()
        self.seed_connected_node = dict()
        super(SocketCommunication, self).__init__(ip, port, None)
        self.peerDiscovery = PeerDiscovery(self)
        self.seedDiscovery = SeedDiscovery(self)
        self.peerDiscoveryHandler = PeerDiscoveryHandler(self)
        self.socketConnector = SocketConnector(ip, port)
        self.actions_communication = ActionsCommunication(self)

    def start_socket_communication(self, node):
        """
        Запуск сетевого общения
        """
        self.node = node
        self.start()
        self.peerDiscoveryHandler.start()

    def stop_socket_communication(self):
        """
        Остановка сетевого общения
        """
        if self.is_peer:
            self.peerDiscoveryHandler.handshake_broadcast('PEERSTOP', )
        self.stop()

    def outbound_node_connected(self, connected_node):
        """
        Действие при подключении
        :param connected_node: Подключенная нода
        """
        self.peerDiscoveryHandler.handshake(connected_node)

    def node_message(self, connected_node, message):
        """
        Обработка полученного сообщения
        :param connected_node: Нода, от которой пришло сообщение
        :param message:  Текст сообщения
        """
        message = Message.decode(json.dumps(message))
        if self.node.blockchain.debug_mode:
            print('node_message = ', message.to_json())
        message_type = message.payload['messageType']
        data = message.payload['data']
        # Вызов функции обработчика из класса ActionsCommunication. Тип пакета совпадает с наименованием функции
        func = getattr(self.actions_communication, message_type)
        func(data, connected_node)

    def send(self, receiver, message):
        """
        Отправка сообщения указанной ноде
        :param receiver: Кому отправляется сообщение
        :param message: Текст сообщения
        """
        self.send_to_node(receiver, message)

    def broadcast(self, message):
        """
        Отправка сообщения всем подключенным нодам
        :param message: Текст сообщения
        """
        # self.send_to_nodes(message)
        for n in self.nodes_inbound:
            ip = n.host
            if self.seedDiscovery.is_seed(ip) or self.peerDiscovery.is_peer(ip):
                self.send_to_node(n, message)

        for n in self.nodes_outbound:
            ip = n.host
            if self.seedDiscovery.is_seed(ip) or self.peerDiscovery.is_peer(ip):
                self.send_to_node(n, message)

    def get_node(self):
        """
        Получение случайного пира для передачи запроса. Выполняется проверка, в сети ли пир и если нет - удаляется из списка
        """
        connected_node = None
        if len(self.nodes_inbound) > 0:
            connected_node = random.choice(list(self.nodes_inbound))
        elif len(self.nodes_outbound) > 0:
            connected_node = random.choice(list(self.nodes_outbound))

        if connected_node:
            host = '{}:{}'.format(connected_node.host, connected_node.port)
            if self.peerDiscoveryHandler.handshake_ping(host):
                return connected_node
            return self.get_node()
        print('Not connected nodes! Searching....')
        time.sleep(5)
        return self.get_node()
