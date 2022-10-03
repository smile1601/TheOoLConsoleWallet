"""
Created on 15 ���. 2021 �.

@author: Alex Nenashev
©TheOoL, Inc
"""
from datetime import datetime
from ToolkitBCH import getHash
from ToolkitBCH import getSign
from ToolkitBCH import verifySign
import json


class Transaction:
    """
    Общий класс транзакции на запись данных в базу данных блокчейна.
    Самостоятельно не используется и не долженпроходить проверку.
    Для каждого типа транзакций необходимо разработать модуль проверки
    на "кошерность".
    """
    def __init__(self, tra_type: str = None):
        """
        Constructor
        """
        self.version = '1.0'
        self.traType = tra_type
        self.traTimestamp = datetime.timestamp(datetime.now())
        self.transactionID = tra_type
        self.transactionSign = ''
        self.transactionPubKey = ''

    def to_dict(self):
        """
        возвращает транзакцию в виде словаря с полями транзакции
        """
        return {
            'ID': self.transactionID,
            'type': self.traType,
            'version': self.version,
            'timestamp': self.traTimestamp,
            'sign': self.transactionSign,
            'pubKey': self.transactionPubKey
            }

    @staticmethod
    def load_from_dict(transaction_dict: dict):
        """
        загружаем объект из словаря. возвращаем новую трансакцию.
        """
        tr = Transaction()
        tr.transactionID = transaction_dict.get('ID')
        tr.traType = transaction_dict.get('type')
        tr.traTimestamp = transaction_dict.get('timestamp')
        tr.transactionSign = transaction_dict.get('sign')
        tr.transactionPubKey = transaction_dict.get('pubKey')
        return tr
    
    def sign(self, ec_pub_key: str, ec_sec_key: str, pwd: str = None):
        """
        подпишем транзакцию
        на вход даем текстовое значение публичного ключа, секретного ключа и пароль (если есть)
        одновременно транзакции присваивается идентификатор путем хеширования тела транзакции
        вместе с публичным ключом, что исключает подмену транзакции.
        """
        self.transactionSign = ''
        self.transactionPubKey = ec_pub_key
        string_data = json.dumps(self.to_dict())
        self.transactionID = getHash(string_data)
        string_data = getHash(json.dumps(self.to_dict()))
        self.transactionSign = getSign(string_data, ec_sec_key, pwd)

    def sign_verify(self):
        """
        проверяем подпись транзакции
        и соответсвие идентификатора транзакции подписи транзакции.
        Таким образом подделка транзакции станосится невозможной
        без подбора приватного ключа к открытому ключу.
        """
        d = self.to_dict()
        d['sign'] = ''
        string_data = getHash(json.dumps(d))
        return verifySign(string_data, self.transactionSign, self.transactionPubKey)
    

class TokenSendTransaction(Transaction):
    """
    универсальный класс транзакции на перевод токенов
    """
    def __init__(self, moves_pool: list, fee: float, amount: float, suffix='TTG'):
        super().__init__(tra_type='token_send')
        self.fee = fee
        self.amount = amount
        self.suffix = suffix
        self.movesPool = moves_pool
        '''
        self.movesPool = [move1, move2, ..., moveN] move1 - N объекты move.toDict()
        '''

    def to_dict(self):
        d = super().to_dict()
        d['fee'] = self.fee
        d['amount'] = self.amount
        d['suffix'] = self.suffix
        d['moves'] = self.movesPool
        return d
    
    @staticmethod
    def load_from_dict(transaction_dict: dict):
        """
        возвращает объект класса tokenSendTransaction
        """
        tr = TokenSendTransaction(transaction_dict.get('moves'),
                                  transaction_dict.get('fee'),
                                  transaction_dict.get('amount'),
                                  transaction_dict.get('suffix')
                                  )
        tr.transactionID = transaction_dict.get('ID')
        tr.traType = transaction_dict.get('type')
        tr.traTimestamp = transaction_dict.get('timestamp')
        tr.transactionSign = transaction_dict.get('sign')
        tr.transactionPubKey = transaction_dict.get('pubKey')
        return tr
        
    def moves_sign_verify(self):
        """
        если все ходы транзакции подписаны верно, возвращаем True, иначе False
        """
        for i in self.movesPool:
            k = i.copy()
            k['sign'] = ''
            string_data = getHash(json.dumps(k))
            if not verifySign(string_data, i.get('sign'), i.get('pubKey')):
                return False
        return True


class FeeSendTransaction(TokenSendTransaction):
    """
    транзакция генерируется при создании блока и рассылает комиссию
    """
    def __init__(self,  move: dict,  amount, suffix='TTG'):
        move['mtype'] = 'fee_move'
        super().__init__([move], 0, amount, suffix)
        self.traType = 'fee_send'


class Move:
    """
    типовой ход (элемент транзакции) на передачу данных от sender к receiver.
    Под данными мы понимаем любую структуру. Например [fee:float , amount:float] для
    транзакций по передаче токенов
    """
    def __init__(self, sender: str, receiver: str, data=None):
        """
        sender - адрес отправителя
        receiver - адрес получателя
        data - данные
        """
        self.mtype = 'move'
        self.sender = sender
        self.receiver = receiver
        self.data = data
        self.pubKey = ''
        self.sign = ''

    def to_dict(self):
        """
        озвращает ход в виде словаря
        """
        return {
                'mtype': self.mtype, 
                'sender': self.sender, 
                'receiver': self.receiver,
                'data': self.data,
                'sign': self.sign,
                'pubKey': self.pubKey
                }

    @staticmethod
    def load_from_dict(move_dict: dict):
        """
        возвращает объект класса move
        """
        m = Move(move_dict.get('sender'), move_dict.get('receiver'))
        m.mtype = move_dict.get('mtype')
        m.data = move_dict.get('data')
        m.sign = move_dict.get('sign')
        m.pubKey = move_dict.get('pubKey')
        return m
    
    def sign_transaction(self, input_pub_key: str, input_sec_key: str, pwd: str = None):
        """
        подпишем ход
        на вход даем текстовое значение публичного ключа, секретного ключа и пароль (если есть)
        """
        self.sign = ''
        self.pubKey = input_pub_key
        string_data = getHash(json.dumps(self.to_dict()))
        self.sign = getSign(string_data, input_sec_key, pwd)
    
    def sign_verify(self):
        """
        проверяем подпись хода
        """
        d = self.to_dict()
        d['sign'] = ''
        string_data = getHash(json.dumps(d))
        return verifySign(string_data, self.sign, self.pubKey)


class TokenMove(Move):
    """
    ход с пересылкой токенов
    при записи ходов в транзакцию типа tokenSendTransaction в поле sender:str пишем адрес отправителя
    при записи ходов в транзакцию типа feeSendTransaction в поле sender:str пишем номер блока из которого
    происходит комиссия
    """
    
    def __init__(self, sender: str, receiver: str, amount: float, fee: float, data=None):
        super().__init__(sender, receiver, data)
        self.amount = amount
        self.fee = fee
        self.mtype = 'token_move'
        
    def to_dict(self):
        """
        возвращает словарь
        """
        dd = super().to_dict()
        dd['amount'] = self.amount
        dd['fee'] = self.fee
        return dd
    
    @staticmethod
    def load_from_dict(move_dict: dict):
        """
        возвращает объект класса tokenMove
        """
        m = TokenMove(move_dict.get('sender'), move_dict.get('receiver'), move_dict.get('amount'), move_dict.get('fee'))
        m.mtype = move_dict.get('mtype')
        m.data = move_dict.get('data')
        m.sign = move_dict.get('sign')
        m.pubKey = move_dict.get('pubKey')
        return m
