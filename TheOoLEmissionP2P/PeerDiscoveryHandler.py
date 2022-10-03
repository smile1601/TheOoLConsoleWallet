from threading import Thread
import time
from .Message import Message
from ToolkitBCH.tconst import MAX_PEERS


def get_message(message_type, message_text):
    message = Message(message_type, message_text)
    encoded_message = Message.encode(message)
    return encoded_message


class PeerDiscoveryHandler:

    def __init__(self, node):
        self.socketCommunication = node

    def start(self):
        """
        Запуск сетевого взаимодействия
        """
        if not (self.socketCommunication.seedDiscovery.is_seed(self.socketCommunication.ip)):
            self.connect_to_seed()
        else:
            self.start_as_seed()

    def start_as_seed(self):
        """
        Запуск сида
        """
        for host in self.socketCommunication.seedDiscovery.seeds:
            if host != self.socketCommunication.ip:
                self.socketCommunication.connect_with_node(host, self.socketCommunication.port)

            threads = list()
            threads.append(Thread(target=self.check_new_blockchain_items, args=(), daemon=True))
            for thread in threads:
                thread.start()
        print('Seed started!')

    def start_as_peer(self):
        """
        Запуск пира
        """
        thread = Thread(target=self.connect_to_seed, args=(), daemon=True)
        thread.start()

    def connect_to_seed(self):
        """
        Соединение с сидом
        """
        ip, port = self.socketCommunication.seedDiscovery.seed_ip(), self.socketCommunication.port
        self.socketCommunication.connect_with_node(ip, port, 4)
        # Если подключение уже было и нужно его обновить
        if len(self.socketCommunication.nodes_outbound) == 0:
            self.socketCommunication.seedDiscovery.remove_seed(ip)
            if len(self.socketCommunication.seedDiscovery.seeds) == 0:
                self.socketCommunication.no_seeds = True
                self.socketCommunication.stop()
            else:
                self.connect_to_seed()
        else:
            # Если новое подключение
            threads = list()
            threads.append(Thread(target=self.refresh_blockchain, args=(), daemon=True))
            threads.append(Thread(target=self.check_peers, args=(), daemon=True))
            if self.socketCommunication.is_peer:
                threads.append(Thread(target=self.check_new_blockchain_items, args=(), daemon=True))
            else:
                threads.append(Thread(target=self.refresh_variables, args=(), daemon=True))

            for thread in threads:
                thread.start()

    def start_synchronize(self):
        """
        Начало синхронизации. Необходим для удаленонго блокчейна
        """
        threads = list()
        threads.append(Thread(target=self.handshake_synchronize_blocks, args=(), daemon=True))
        threads.append(Thread(target=self.handshake_synchronize_blocks_check, args=(), daemon=True))

        for thread in threads:
            thread.start()

    def refresh_blockchain(self):
        """
        Обновление блоков
        """
        while True:
            if self.socketCommunication.peerDiscovery.have_peers:
                if self.socketCommunication.is_peer:
                    self.handshake_common('GETBLOCKID', '')
                    break
                else:
                    self.handshake_common('GETAMOUNTSUFFIXES', '')
                    break
            time.sleep(2)

    def check_new_blockchain_items(self):
        """
        Получение новых блоков от других участников сети
        """
        while True:
            if self.socketCommunication.node.blockchain is not None:
                if self.socketCommunication.node.blockchain.synchronize_pools:
                    pool_item = self.socketCommunication.node.blockchain.synchronize_pools.pop()
                    self.handshake_broadcast('NEWTRANSACTION', pool_item)
                if self.socketCommunication.node.blockchain.need_send_block_id:
                    self.handshake_broadcast('RECEIVEBLOCKID',
                                             self.socketCommunication.node.blockchain.lastKnownBlockID)
                    self.socketCommunication.node.blockchain.need_send_block_id = False
            time.sleep(2)

    def refresh_variables(self):
        """
        Обновление аккаунта для удаленного блокчейна. Выполняется 1 раз в час
        """
        while True:
            if not self.socketCommunication.is_updated:
                data = self.socketCommunication.node.wallet.accList
                self.handshake_common('GETAMOUNTS', data)
                time.sleep(60 * 60)
            else:
                time.sleep(1)

    def check_peers(self):
        """
        Проверка, все ли пиры в сети, Выполняется 1 раз в 20 минут. Если их меньше 50% - выполняется запрос на получение новых
        """
        while True:
            time.sleep(60 * 20)
            seed = '{}:{}'.format(self.socketCommunication.seed_connected_node.host,
                                  self.socketCommunication.seed_connected_node.port)
            for node in self.socketCommunication.nodes_outbound:
                host = '{}:{}'.format(node.host, node.port)
                if host != seed:
                    self.handshake_ping(host)
            if self.socketCommunication.is_peer and len(self.socketCommunication.nodes_outbound) < (MAX_PEERS / 2):
                self.handshake(self.socketCommunication.seed_connected_node)

    def connect_peers(self):
        """
        Соединение с новыми пирами
        """
        peers = self.socketCommunication.peerDiscovery.get_peers() \
            if self.socketCommunication.is_peer \
            else self.socketCommunication.peerDiscovery.get_peers(1)

        for peer in peers:
            host, port = peer.split(':', 1)
            self.socketCommunication.connect_with_node(host, port)

    def disconnect_peers(self):
        """
        Отключение от пиров
        """
        seed = '{}:{}'.format(self.socketCommunication.seed_connected_node.host,
                              self.socketCommunication.seed_connected_node.port)
        for node in self.socketCommunication.nodes_outbound:
            host = '{}:{}'.format(node.host, node.port)
            if host != seed:
                self.socketCommunication.disconnect_with_node(node)

    def handshake(self, connected_node):
        """
        Регистрация нового пира
        """
        if not (self.socketCommunication.seedDiscovery.is_seed(self.socketCommunication.ip)):
            message_type = 'PEERREGISTER'
            data = {'is_peer': self.socketCommunication.is_peer}
            message = get_message(message_type, data)
            self.socketCommunication.seed_connected_node = connected_node
            self.socketCommunication.send(connected_node, message)

    def handshake_broadcast(self, message_type, data=''):
        """
        Отправка сообщения всем соединенными нодам
        """
        message = get_message(message_type, data)
        self.socketCommunication.broadcast(message)

    def handshake_common(self, message_type, data=''):
        """
        Функция для отправки сообщения случайному пиру из списка подключенных
        """
        message = get_message(message_type, data)
        connected_node = self.socketCommunication.get_node()
        self.socketCommunication.send(connected_node, message)

    def handshake_receive_common(self, connected_node, message_type, data=''):
        """
        Отправка сообщения в ответ на полученное сообщение
        """
        message = get_message(message_type, data)
        self.socketCommunication.send(connected_node, message)

    def handshake_ping(self, host: str):
        """
        Проверка в сети ли нода
        """
        message_type = 'PING'
        data = ''
        message = get_message(message_type, data)
        connected_node = self.find_connected_node(host)
        if connected_node:
            self.socketCommunication.send(connected_node, message)
            index = 0
            while index < 4:
                if host in self.socketCommunication.pong:
                    self.socketCommunication.pong.remove(host)
                    #  print("{} connected".format(host))
                    return True
                time.sleep(1)
                index += 1
            #  print("{} not accessible".format(host))
            self.socketCommunication.peerDiscovery.remove_peer(host)
            return False
        else:
            if self.socketCommunication.peerDiscovery.check_peer(host):
                self.socketCommunication.peerDiscovery.remove_peer(host)
            #  print("{} not connected".format(host))

    def find_connected_node(self, host: str):
        """
        Поиск соединенной ноды
        """
        host_array = host.split(':')
        for node in self.socketCommunication.nodes_inbound:
            if node.host == host_array[0] and node.port == int(host_array[1]):
                return node

        for node in self.socketCommunication.nodes_outbound:
            if node.host == host_array[0] and node.port == int(host_array[1]):
                return node

        return False

    def handshake_synchronize_blocks(self):
        message_type = 'GETBLOCKBYID'
        while True:
            index = self.socketCommunication.node.blockchain.lastLocalBlockID
            while True:
                index += 1
                if index > self.socketCommunication.node.blockchain.lastKnownBlockID:
                    break
                blocks = self.socketCommunication.node.blockchain.synchronize_blocks
                if index not in blocks:
                    message = get_message(message_type, index)
                    connected_node = self.socketCommunication.get_node()
                    self.socketCommunication.send(connected_node, message)
            time.sleep(3)
            if self.socketCommunication.node.blockchain.lastLocalBlockID == \
                    self.socketCommunication.node.blockchain.lastKnownBlockID:
                self.handshake_common('GETBLOCKID', '')
                break

    def handshake_synchronize_blocks_check(self):
        """
        Запрос на получение новых блоков из сети по номеру не достающего
        """
        ck = 0
        while True:
            time.sleep(2)
            index = self.socketCommunication.node.blockchain.lastLocalBlockID + 1
            if index > self.socketCommunication.node.blockchain.lastKnownBlockID:
                break
            blocks = self.socketCommunication.node.blockchain.synchronize_blocks
            if index in blocks:
                self.socketCommunication.node.blockchain.put_block(blocks.get(index)[0])
                self.socketCommunication.node.blockchain.lastLocalBlockID = index
                self.socketCommunication.node.blockchain.save_local_data()
                del self.socketCommunication.node.blockchain.synchronize_blocks[index]
                ck = 0
            ck += 1
            if ck == 5:
                break
