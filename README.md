# TheOoL-BCH

**TheOoL-BCH** (*blockchain*) is a database mechanism allowing to openly communicate as part of the business network. The blockchain database stores data in blocks linked together in a chain.

*The blockchain* is carried out using **P2P** networking mechanism.

**P2P Network** is an overlay computer network underpinned by equality of its members. Unlike the client-server architectures this setup enables uptime of the network with any number or combination of available nodes. All the nodes are members of the network. 



## Remote Node Networking Principle

Remote nodes have no offline blockchain database. They receive all the blockchain data from **peers** having the complete database.

When a request is executed from the **wallet** the entry is transmitted to one of the **peers** that, in turn, disseminates such data across the network. 

### Node Launching

1. **NodeBCH** class is launched; it contains the subsets blockchain,**wallet** and **p2p**
2. **start_p2p** function of **NodeBCH** class is perfomed; and it begins networking
3. Offline node is launched
4. **Seed** connection is executed (peerDiscoveryHandler.start())
5. If seed is not online an error is displayed
6. **TheOoLEmissionBCH.RemoteAccessBlockchain** is transmitted to **blockchain** subset
7. **Blockchain** is transmitted to **wallet** subset

After connection to seed the list of **peers** is received, in response, for networking; the list is saved in the file */theool/peers.dat*. All the blockchain enquiries are subsequently executed via them.

If */theool/peers.dat* becomes unavailable it gets deleted from the list. When the number of **peers** becomes less than 50% a request is generated to update them.

### Offline Wallet Transactions

Offline transactions (no data are transmitted to the network) include:
1. New **wallet** creation
2. Creation of a new account in the wallet
3. **Wallet** blocking, unblocking, and renaming
4. Switching between offline **wallets**

### Network Operations

In case of a **blockchain** update request (balance enquiry, transfer to another account, etc.) the request is first sent to one of the peers that, in response, sends the request execution result. 

## Содержание

* [Блокчейн](../docs/Блокчейн/README.md) 
    * [Блок](../docs/Блокчейн/Блок.md) 
    * [Кошелек](../docs/Блокчейн/Кошелек.md) 
    * [Пул транзакций](../docs/Блокчейн/Пул транзакций.md) 
    * [Транзакция](../docs/Блокчейн/Транзакция.md) 
    * [Удаленный блокчейн](../docs/Блокчейн/Удаленный блокчейн.md) 
* [Организация P2P-сети](../docs/Организация P2P-сети/README.md)
    * [Принцип сетевого взаимодействия полной ноды](../docs/Организация P2P-сети/Принцип сетевого взаимодействия полной ноды.md)
    * [Принцип сетевого взаимодействия удаленной ноды](../docs/Организация P2P-сети/Принцип сетевого взаимодействия удаленной ноды.md)
    * [Типы сетевых пакетов](../docs/Организация P2P-сети/Типы сетевых пакетов.md)
* Эксплорер
* Запуск ноды
    * [Запуск полной ноды](../docs/Запуск ноды/Запуск полной ноды.md)
    * [Запуск валидатора](../docs/Запуск ноды/Запуск валидатора.md)
    * [Запуск удаленной ноды](../docs/Запуск ноды/Запуск удаленной ноды.md)
    * [Запуск локального rest-api интерфейса](../docs/Запуск ноды/Запуск локального rest-api интерфейса.md)
    
## Remote Node Launching

```
pip install -r requirements.txt 
python3 theool-remote-bc.py
```