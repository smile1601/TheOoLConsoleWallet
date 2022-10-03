import json
import os.path
import random
from ToolkitBCH.tconst import PEERS_F
from ToolkitBCH.tconst import MAX_PEERS


def clear_peers():
    """
    Удаляет peers.json если он существует
    """
    if os.path.isfile(PEERS_F):
        os.remove(PEERS_F)


class PeerDiscovery:

    def __init__(self, node):
        self.socketCommunication = node
        clear_peers()
        self.peers = list()
        self.have_peers = False

    def to_json(self):
        return '; '.join(self.peers)

    def is_peer(self, ip: str):
        """
        Проверка, является ли устройство пиром
        :param ip:
        :return:
        """
        if ip in self.peers:
            return True
        return False

    def peer_ip(self):
        """
        Возвращает случайный ip-адрес из списка peers
        :return: String
        """
        return random.choice(self.peers)

    def add_peer(self, host: str):
        """
        Добавляет peer в справочник. Сохраняет запись в peers.json
        :param host: String
        """
        self.peers.append(host)
        self.save()

    def refresh_peers(self, data: list):
        self.peers = data
        self.save()

    def remove_peer(self, host: str):
        """
        Удаляет peer из справочника.
        :param host: String
        """
        if host in self.peers:
            self.peers.remove(host)
            self.save()

    def save(self):
        with open(PEERS_F, "w+") as f:
            json.dump(self.peers, f)

    def peer_register(self, connected_node):
        """
        Регистрация пира
        :param connected_node
        """
        ip = '{}:{}'.format(connected_node.host, connected_node.port)
        if ip not in self.peers:
            self.add_peer(ip)

    def check_peer(self, host: str):
        if host in self.peers:
            return True
        return False

    def get_peers(self, peers_count: int = MAX_PEERS):
        """
        :return: Список пиров для подключения
        """
        peers = []
        if len(peers) > 0:
            while len(peers) < peers_count:
                peer = self.peer_ip()
                if peer not in peers:
                    peers.append(peer)
                if len(peers) == len(self.peers):
                    break
        return peers
