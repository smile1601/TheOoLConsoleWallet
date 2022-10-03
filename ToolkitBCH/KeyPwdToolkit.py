'''
Created on 15 ���. 2021 �.

@author: Alex Nenashev
©TheOoL, Inc


библиотека функций для работы с ключами, паролями и адресами (счетами) 
эмиссионного блокчейна TheOoL.
Написана на базе криптографического фреймворка cryptography: 
Python - обертка библиотеки OpenSSL. 

pip install cryptography
'''
import os
from cryptography.hazmat.primitives.asymmetric.ec import SECP521R1
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import keywrap
from cryptography.exceptions import InvalidSignature
from binascii import \
    unhexlify  # удобная функция для преобразования hex --> bytes из библиотеки для работы с разными кодировками м системами счисления

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.keywrap import InvalidUnwrap
from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)

'''
import json
import base58
import base64
'''


def getNewRandomAccount(pwd: str = None):
    """
    #Создает новую случайную сериализованную группу: секретный ключ, публичный ключ, адрес - счет
    Возвраimport ToolkitBCH словарь вида:
    {
        'secretkey': str,
        'isClosed': Boolean
        'publiczone': {'publickey': str,
                       'account': str
                       }
    }
    """
    return serializeKey(ec.generate_private_key(SECP521R1(), backend=None), pwd)


def getNewAccountByPrivateNum(privateNumbers: int, pwd: str = None):
    """
    #восстанавливает ключ по секретному целому числу. На вход параметр типа Integer
    Создает новую сериализованную группу: секретный ключ, публичный ключ, адрес - счет
    Возвращает структуру словарь вида:
    {
        'secretkey': str,
        'isClosed': Boolean
        'publiczone': {'publickey': str,
                       'account': str
                       }
    }
    """
    eckey = ec.derive_private_key(privateNumbers, SECP521R1(), backend=None)
    return serializeKey(eckey, pwd)


def getKeyPrivateNumber(eckey):
    """
    #извлекает секретное целое число из объекта ключа
    принимает объект типа EllipticCurvePrivateKey
    возвращает значение типа Integer
    """
    return eckey.private_numbers().private_value


def serializeKey(eckey, pwd: str = None):
    """
    #выгружает из обЪекта ключа секретный и публичный ключи и помещает их в словарь.
    #секретный ключ может быть сохранен в виде открытой строки либо зашифрован протоеолом AES по паролю.
    на вход принимает объект ключа (EllipticCurvePrivateKey) и пароль (String)
    Возвращает структуру словарь вида:
    {
        'secretkey': str,
        'isClosed': Boolean
        'publiczone': {'publickey': str,
                       'account': str
                       }
    }
    """
    pkey = eckey.public_key().public_bytes(serialization.Encoding.PEM,
                                           format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')
    if pwd is None:
        skey = eckey.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                   encryption_algorithm=serialization.NoEncryption()).decode('utf-8')
        isClosed = False
    else:
        isClosed = True
        skey = eckey.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                   encryption_algorithm=serialization.NoEncryption()).decode('utf-8')
        iterN = 8 - len(skey.encode('utf-8')) % 8
        if iterN < 8:
            switcher = {
                1: '0',
                2: '00',
                3: '000',
                4: '0000',
                5: '00000',
                6: '000000',
                7: '0000000'
            }
            skey += switcher.get(iterN)
        skey = keywrap.aes_key_wrap(pwdPreparator(pwd), skey.encode('utf-8')).hex()

    digest = hashes.Hash(hashes.SHA256())
    digest.update(pkey.encode('utf-8'))

    return {
        'secretkey': skey,
        'isClosed': isClosed,
        'publiczone': {'publickey': pkey,
                       'account': 'TheOoL' + digest.finalize().hex()
                       }
    }


def deserializeSecKey(ecKey: str, pwd: str = None):
    """
    #Принимает сериализрванный в строку приватный ключ (зашифрованный или нет)
    и пароль для расшифровки приватного ключа (если установлен)
    возвращает объект типа EllipticCurvePrivateKey
    """
    try:
        bk = ecKey.encode('utf-8')
        if pwd is None:
            return serialization.load_pem_private_key(bk, password=None, backend=None)
        else:
            ss = unhexlify(ecKey)
            ss = keywrap.aes_key_unwrap(pwdPreparator(pwd), ss)
            return serialization.load_pem_private_key(ss, password=None, backend=None)
    except InvalidUnwrap:
        raise Exception('Incorrect password')
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        raise Exception(message)


def deserializePubKey(ecPubKey: str):
    """
    #Принимает сериализованный в строку публичный ключ
    Возвращает Объект типа EllipticCurvePublicKey
    """
    ecPubKey = ecPubKey.encode('utf-8')
    return serialization.load_pem_public_key(ecPubKey)


def pwdPreparator(pwd: str):
    """
    #Принимает строку - пароль любой длинны и состава
    Выполняет однозначное одностороннее преобразование строки пароля к 32х
    байтовому ключу для шифрования/расшифрования секретного ключа по
    алгоритму AES
    Возвращает значение типа bytes длинной 32 бита.
    """
    if pwd == None:
        return None
    else:
        return getHash(pwd)[:32].encode('utf-8')


def getHash(data: str):
    """
    хешируем произвольный текст алгоритмом SHA256. На выходе получаем строку
    """
    digest = hashes.Hash(hashes.SHA256())
    digest.update(data.encode('utf-8'))
    return digest.finalize().hex()


def getSign(data: str, ecSecKey: str, pwd: str = None):
    """
    Принимает строковые переменные:
    data - данные, которые подписываем
    ecSecKey - Принимает сериализрванный в строку приватный ключ (зашифрованный или нет)
    pwd - пароль для расшифровки секретного ключа (если установлен)
    #возвращает цифровую подпись в виде строки
    """
    key = deserializeSecKey(ecSecKey, pwd)
    return key.sign(data.encode('utf-8'), ec.ECDSA(hashes.SHA256())).hex()


def verifySign(data: str, ecSign: str, ecPubKey: str):
    """
    #Принимает сериализованные в строку:
    data - данные, которые подписаны электронной подписью
    ecSign - электронную подпись
    ecPubKey - публичный ключ от аккаунта, который подписал данные
    #проверяет цифровую подпись
    Возвращает True если подпись валидна и False если нет
    """
    pkey = deserializePubKey(ecPubKey)
    try:
        pkey.verify(unhexlify(ecSign), data.encode('utf-8'), ec.ECDSA(hashes.SHA256()))
    except InvalidSignature:
        return False
    else:
        return True


def get_handshake_keys():
    private_key = ec.generate_private_key(ec.SECP384R1(), backend=None)

    serialized_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_key = private_key.public_key()

    serialized_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return serialized_private, serialized_public


def get_shared_key(ser_private_key, ser_public_key):
    private_key = deserializeSecKey(ser_private_key.decode())
    public_key = deserializePubKey(ser_public_key.decode())

    return private_key.exchange(ec.ECDH(), public_key)


def get_derived_key(shared_key, text):
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=text.encode('utf-8')
    ).derive(shared_key)


def derived_key(shared_key, message):
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=message.decode('utf-8')
    ).derive(shared_key)


def get_encrypt(key, message, associated_data):
    iv = os.urandom(12)

    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
    ).encryptor()

    encryptor.authenticate_additional_data(associated_data.encode('utf-8'))

    ciphertext = encryptor.update(message.encode('utf-8')) + encryptor.finalize()

    return iv, ciphertext, encryptor.tag


def get_decrypt(key, associated_data, iv, ciphertext, tag):
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
    ).decryptor()

    decryptor.authenticate_additional_data(associated_data.encode('utf-8'))

    return (decryptor.update(ciphertext) + decryptor.finalize()).decode('utf-8')
