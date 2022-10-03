import copy
from collections import defaultdict


class ActionsCommunication:

    def __init__(self, node):
        self.socketCommunication = node

    def PEERREGISTER(self, data, connected_node):
        """
        Регистрация нового пира. Выполняется при подключении и когда необходимо обновление пиров
        :param data:  Блок данных сообщения
        :param connected_node: Нода, от которой пришло сообщение
        """
        if data.get("is_peer"):
            self.socketCommunication.peerDiscovery.peer_register(connected_node)
        host = '{}:{}'.format(connected_node.host, connected_node.port)
        peers = copy.copy(self.socketCommunication.peerDiscovery.peers)
        if host in peers:
            peers.remove(host)
        self.socketCommunication.peerDiscoveryHandler.handshake_receive_common(connected_node, 'PEERSREFRESH', peers)

    def PEERSREFRESH(self, data, connected_node):
        """
        Получение списка пиров
        :param data:  Блок данных сообщения
        :param connected_node: Нода, от которой пришло сообщение
        """
        self.socketCommunication.peerDiscoveryHandler.disconnect_peers()
        self.socketCommunication.peerDiscovery.refresh_peers(data)
        self.socketCommunication.peerDiscoveryHandler.connect_peers()
        self.socketCommunication.peerDiscovery.have_peers = True

    def PING(self, data, connected_node):
        self.socketCommunication.peerDiscoveryHandler.handshake_receive_common(connected_node, 'PONG')

    def PONG(self, data, connected_node):
        host = '{}:{}'.format(connected_node.host, connected_node.port)
        self.socketCommunication.pong.append(host)

    def GETAMOUNTSUFFIXES(self, data, connected_node):
        """
        Запрос на получение вида валют в сети. Необходим для удаленного блокчейна. Выполняется при подключении
        :param data:  Блок данных сообщения
        :param connected_node: Нода, от которой пришло сообщение
        """
        send_data = self.socketCommunication.node.blockchain.AMOUNT_SUFFIXES
        self.socketCommunication.peerDiscoveryHandler.handshake_receive_common(connected_node, 'RECEIVEAMOUNTSUFFIXES',
                                                                               send_data)

    def RECEIVEAMOUNTSUFFIXES(self, data, connected_node):
        """
        Получение вида валют в сети. Необходим для удаленного блокчейна
        :param data:  Блок данных сообщения
        :param connected_node: Нода, от которой пришло сообщение
        """
        self.socketCommunication.node.blockchain.AMOUNT_SUFFIXES = data

    def GETAMOUNTS(self, data, connected_node):
        """
        Запрос на получение баланса по аккаунту. Необходим для удаленного блокчейна. Выполняется при подключении
        """
        send_data = self.socketCommunication.node.blockchain.get_amounts(data)
        self.socketCommunication.peerDiscoveryHandler.handshake_receive_common(connected_node, 'RECEIVEAMOUNTS',
                                                                               send_data)

    def RECEIVEAMOUNTS(self, data, connected_node):
        """
        Получение баланса по аккаунту. Необходим для удаленного блокчейна
        :param data:  Блок данных сообщения
        :param connected_node: Нода, от которой пришло сообщение
        """
        self.socketCommunication.node.blockchain.amounts = data

    def GETFEERATES(self, data, connected_node):
        """
        Запрос на получение комиссии. Необходим для удаленного блокчейна. Выполняется при подключении
        """
        send_data = self.socketCommunication.node.blockchain.getFeeRate(data)
        self.socketCommunication.peerDiscoveryHandler.handshake_receive_common(connected_node, 'RECEIVEFEERATES',
                                                                               send_data)

    def RECEIVEFEERATES(self, data, connected_node):
        """
        Получение комиссии. Необходим для удаленного блокчейна
        :param data:  Блок данных сообщения
        :param connected_node: Нода, от которой пришло сообщение
        """
        self.socketCommunication.node.blockchain.FEE_RATES = data

    def GETBLOCKID(self, data, connected_node):
        """
        Запрос на получение номера последнего блока. Выполняется при подключении
        :param data:  Блок данных сообщения
        :param connected_node: Нода, от которой пришло сообщение
        """
        send_data = self.socketCommunication.node.blockchain.lastKnownBlockID
        self.socketCommunication.peerDiscoveryHandler.handshake_receive_common(connected_node, 'RECEIVEBLOCKID',
                                                                               send_data)

    def RECEIVEBLOCKID(self, data, connected_node):
        """
        Получение нового блока.
        :param data:  Блок данных сообщения
        :param connected_node: Нода, от которой пришло сообщение
        """
        self.socketCommunication.node.blockchain.lastKnownBlockID = data
        if not self.socketCommunication.node.blockchain.is_synchronized():
            self.socketCommunication.node.blockchain.synchronize_blocks = defaultdict(list)  # list()
            self.socketCommunication.peerDiscoveryHandler.start_synchronize()
        else:
            print('Blockchain has been successfully synced and is ready to go!')

    def GETBLOCKBYID(self, data, connected_node):
        """
        Запрос на получение блока по ID.
        :param data:  Блок данных сообщения
        :param connected_node: Нода, от которой пришло сообщение
        """
        send_data = {'block_id': data, 'block': self.socketCommunication.node.blockchain.read_block(data)}
        self.socketCommunication.peerDiscoveryHandler.handshake_receive_common(connected_node, 'RECEIVEBLOCKBYID',
                                                                               send_data)

    def RECEIVEBLOCKBYID(self, data, connected_node):
        """
        Получение нового блока.
        :param data:  Блок данных сообщения
        :param connected_node: Нода, от которой пришло сообщение
        """
        block_id = int(data.get('block_id'))
        block = data.get('block')
        self.socketCommunication.node.blockchain.synchronize_blocks[block_id].append(block)

    def PUTTRANSACTION(self, data, connected_node):
        """
        Добавление новой транзакции в локальный пул
        :param data:  Блок данных сообщения
        :param connected_node: Нода, от которой пришло сообщение
        """
        add_to_pull = self.socketCommunication.node.blockchain.put_transaction(data)
        self.socketCommunication.peerDiscoveryHandler.handshake_receive_common(connected_node, 'RECEIVETRANSACTION',
                                                                               add_to_pull)
        if add_to_pull[0]:
            self.socketCommunication.peerDiscoveryHandler.handshake_broadcast('NEWTRANSACTION', data)

    def RECEIVETRANSACTION(self, data, connected_node):
        """
        Добавление новой транзакции в пул
        :param data:  Блок данных сообщения
        :param connected_node: Нода, от которой пришло сообщение
        """
        self.socketCommunication.node.blockchain.add_to_pull = data

    def NEWTRANSACTION(self, data, connected_node):
        """
        Добавление новой транзакции в пул
        :param data:  Блок данных сообщения
        :param connected_node: Нода, от которой пришло сообщение
        """
        self.socketCommunication.node.blockchain.put_transaction(data)

    def PEERSTOP(self, data, connected_node):
        """
        Остановка ноды
        :param data:  Блок данных сообщения
        :param connected_node: Нода, от которой пришло сообщение
        """
        host = '{}:{}'.format(connected_node.host, connected_node.port)
        self.socketCommunication.peerDiscovery.remove_peer(host)
