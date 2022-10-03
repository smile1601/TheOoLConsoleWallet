import json
import os.path
import random
from ToolkitBCH.tconst import WORK_DIR, SEEDS_F, SEEDS_LIST


class SeedDiscovery:

    def __init__(self, node):
        self.socketCommunication = node
        self.seeds = list()
        self.load_seeds()

    def load_seeds(self):
        """
        Загружает список seeds
        """
        os.makedirs(WORK_DIR, exist_ok=True)
        if os.path.exists(SEEDS_F):
            with open(SEEDS_F) as f:
                self.seeds = json.load(f)
        else:
            with open(SEEDS_F, "w+") as f:
                self.seeds = SEEDS_LIST
                json.dump(self.seeds, f)

    def is_seed(self, ip: str):
        """
        Проверка, является ли устройство сидом
        :param ip:
        :return:
        """
        if ip in self.seeds:
            return True
        return False

    def seed_ip(self):
        """
        Возвращает случайный ip-адрес из списка seeds
        :return: String
        """
        return random.choice(self.seeds)

    def add_seed(self, data: str):
        """
        Добавляет seed в справочник. Сохраняет запись в seeds.json
        :param data: String
        """
        self.seeds.append(data)
        with open(SEEDS_F, "w+") as f:
            json.dump(self.seeds, f)

    def remove_seed(self, data: str):
        """
        Удаляет seed из справочника.
        :param data: String
        """
        self.seeds.remove(data)
