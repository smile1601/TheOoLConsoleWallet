'''
Created on 15 ���. 2021 �.

@author: Alex Nenashev
©TheOoL, Inc
'''


class excInvalidTransactionType(Exception):
    '''
    вызывается когда тип транзакции не входит в перечень допустимых типов транзакций
    '''
    pass

class excInvalidBlockType(Exception):
    '''
    вызывается когда тип транзакции не входит в перечень допустимых типов транзакций
    '''
    pass

class excInvalidTockenType(Exception):
    '''
    вызывается когда суффикс токена не входит в перечень допустимых типов токенов
    '''
    pass

class excGiveMePassword(Exception):
    '''
    вызываем если требуется пароль (например кошелек закрыт), но пользователь его не указал
    '''
    pass

class excWalletDoNotLocked(Exception):
    '''
    поднимаем если пароль для нового набора ключей введен, но wallet не заблокирован
    '''
    pass

class excIncorrectPassword(Exception):
    '''
    поднимаем если пароля не позволяет расшифровать кошелек
    '''
    pass