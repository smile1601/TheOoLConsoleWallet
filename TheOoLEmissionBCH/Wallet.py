import ToolkitBCH
import json
import os
from .Transaction import TokenSendTransaction, TokenMove
from ToolkitBCH import WALLETS_DIR, LOCAL_TRN_F


class Wallet(object):
    """
    класс - кошелек предназначен для управления адресами и ключами и их взаимодействием с базой распределенного реестра
    """

    def __init__(self, bch):
        """
        На вход ничего не подаем. Считаем, что все читается либо из файлов конфигурации либо из сохраненного кошелька
        """
        self.ID = ''
        self.Name = 'Default Wallet'
        self.isLocked = False
        self.accList = list()  # храним адреса (счета) и ключи, привязанные к кошельку
        self.accounts = list()  # адреса (счета)
        # храним доступные к расходованию средства с привязкой к счету и с учетом транзакций в пуле
        self.accAmounts = dict()
        self.accIndex = dict()  # храним моментальный результат индексирования блокчейна по счетам кошелька
        self.accTransactions = dict()  # сюда сохраняем индивидуальный индекс транзакций этого аккаунта
        self.wallets_list = list()  # список кошельков
        self.load_wallets_list()  # загружает список существующих кошелько
        """
        структура self.accAmounts типа: {
            счет 1 : {'TTG': 0, 'TU': 0}
            счет 2 : {'TTG': 0, 'TU': 0}
            ...
            счет N : {'TTG': 0, 'TU': 0}
        }
        """
        # храним итоговвые значения неизрасходованных сумм для каждого типа токенов по всем аккаунтам кошелька
        self.totalAmounts = dict()
        '''
        структура self.totalAmounts типа: 
        {
            'TTG': 0, 
            'TU': 0
        }
        '''
        self.blockchain = bch
        # self.amount_update()

    def load_wallets_list(self):
        self.wallets_list = list()
        if os.path.exists(WALLETS_DIR):
            files = os.listdir(WALLETS_DIR)
            for file in files:
                if file.find('.wal') != -1:
                    file = file.replace('.wal', '')
                    self.wallets_list.append(file)
        self.wallets_list.sort()
        if len(self.wallets_list) >= 1:
            self.load(self.wallets_list[0])

    def get_wallets_list(self):
        if len(self.wallets_list) == 0:
            return 'Wallets not exist'
        return '\n'.join(map(str, self.wallets_list))

    def to_string(self):
        data = {
            'ID': self.ID,
            'Name': self.Name,
            'isLocked': self.isLocked,
            'accList': self.accList
        }
        return json.dumps(data, indent=4)

    def get_accounts(self):
        self.accAmounts.clear()
        self.amount_update()
        return json.dumps(self.accAmounts, indent=4)

    '''
    ################################################
    ################################################
    ############## блок работы с ключами#############
    ################################################
    ################################################
    '''

    def create_account(self, pwd: str = None):
        """
        добавляет новый адрес с набором ключей к кошельку
        предварительно выполняется проверка пароля и блокировки кошелька
        """
        if pwd is None and self.isLocked:
            raise Exception('No password specified for locked wallet')
        elif pwd is not None and (len(self.accList) > 0 or self.isLocked):
            try:
                ToolkitBCH.deserializeSecKey(self.accList[0].get('secretkey'), pwd)
                key_data = ToolkitBCH.getNewRandomAccount(pwd)
                self.accList.append(key_data)
            except ValueError:
                raise Exception('Incorrect password')
        else:
            key_data = ToolkitBCH.getNewRandomAccount(pwd)
            self.accList.append(key_data)
        if pwd is not None:
            self.isLocked = True
        if self.save():
            self.accounts.append(key_data.get('publiczone').get('account'))
            return json.dumps(key_data, indent=4)

    # TODO
    def restore_account_by_sec_num(self, sec_num: int, pwd: str = None):
        """
        добавляет новый адрес с набором ключей к ToolkitBCHу по предопределенному секретному целому числу secNum
        предварительно выполняется проверка пароля и блокировки кошелька
        """
        if pwd is None and self.isLocked:
            raise ToolkitBCH.excGiveMePassword
        elif pwd is not None and not self.isLocked:
            raise ToolkitBCH.excWalletDoNotLocked
        elif len(self.accList) > 0:
            try:
                ToolkitBCH.deserializeSecKey(self.accList[0].get('secretkey'), pwd)
                key_data = ToolkitBCH.getNewAccountByPrivateNum(sec_num, pwd)
                self.accList.append(key_data)
                self.save()
            except Exception:
                raise ToolkitBCH.excIncorrectPassword
        else:
            key_data = ToolkitBCH.getNewAccountByPrivateNum(sec_num, pwd)
            self.accList.append(key_data)
            self.save()

    def check_password(self, pwd):
        ToolkitBCH.deserializeSecKey(self.accList[0].get('secretkey'), pwd)

    # TODO
    def upload_wallet_accounts_sec_nums(self, pwd: str = None):
        """
        выгружает секретные числа всех адресов и секретных ключей кошелька в словарь
        редварительно выполняется проверка пароля и блокировки кошелька
        """
        if pwd is None and self.isLocked:
            raise ToolkitBCH.excGiveMePassword
        elif pwd is not None and not self.isLocked:
            raise ToolkitBCH.excWalletDoNotLocked
        if len(self.accList) > 0:
            try:
                ToolkitBCH.deserializeSecKey(self.accList[0].get('secretkey'), pwd)
            except Exception:
                raise ToolkitBCH.excIncorrectPassword
        sec_nums = dict()
        for i in self.accList:
            sec_nums[i.get('publiczone').get('account')] = ToolkitBCH.getKeyPrivateNumber(
                ToolkitBCH.deserializeSecKey(i.get('secretkey'), pwd)
            )
        return sec_nums

    def create(self, name: str = None):
        """
        Создает новый кошелек в папку WALLETS_DIR с указанным наименованием
        """
        file_name = name.replace(' ', '_')
        if name is None or name == '':
            raise Exception('Name is required')
        if file_name in self.wallets_list:
            raise Exception('Wallet with name {} already exist'.format(file_name))
        self.ID = ''
        self.Name = name
        self.isLocked = False
        self.accList = list()
        if self.save():
            return 'Wallet {} was created successfully!'.format(file_name)

    def load(self, name: str = None):
        """
        загружает адреса и параметры кошелька из файла
        """
        file_name = name.replace(' ', '_')
        if name is None or name == '':
            raise Exception('Name is required')
        if file_name not in self.wallets_list:
            raise Exception('Wallet with name {} not exist'.format(file_name))
        try:
            with open(WALLETS_DIR + file_name + '.wal', 'r', encoding='utf-8') as w:
                load_wallet = json.load(w)
            self.ID = load_wallet.get('ID')
            self.Name = load_wallet.get('Name')
            self.isLocked = load_wallet.get('isLocked')
            self.accList = load_wallet.get('accList')

            self.accounts.clear()
            for account in self.accList:
                self.accounts.append(account.get('publiczone').get('account'))

            return self.to_string()
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            raise Exception(message)

    def save(self):
        """
        сохраняет кошелек в файл
        """
        try:
            data = {
                'ID': self.ID,
                'Name': self.Name,
                'isLocked': self.isLocked,
                'accList': self.accList
            }
            file_name = self.Name.replace(' ', '_')
            os.makedirs(WALLETS_DIR, exist_ok=True)
            with open(WALLETS_DIR + file_name + '.wal', 'w+', encoding='utf-8') as w:
                json.dump(data, w)
            self.load_wallets_list()

            return True
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            raise Exception(message)

    def rename(self, name: str = None):
        if name is None or name == '':
            raise Exception('New name is required')
        file_name = self.Name.replace(' ', '_')
        os.remove(WALLETS_DIR + file_name + '.wal')
        self.Name = name
        self.save()
        return 'Wallet was renamed to {} successfully!'.format(name)
    
    def update_transactions_data(self):
        """
        Передает в accTransactions структуру, содержащую все транзакции для конкретного набора адесов в структуре

        { 'inBCH':{account:{transaction: [[move_index (индекс размещения хода в списке ходов транзакции),
        payment_direction (1 - income/0 - outcome), timestamp (timestamp транзакции), amount (сумма движения),
        тип токена]]}} 'inPool':{account:{suffix:[[transaction, направление, сумма]]}} }
        """
        self.accTransactions = self.blockchain.get_transactions(self.accounts)

    def load_transactions_data(self):
        """
        загружает сведения о начислениях и списаниях из файла
        """
        try:
            with open(LOCAL_TRN_F, 'r', encoding='utf-8') as w:
                transactions_data = json.load(w)
            self.accAmounts = transactions_data.get('accAmounts')
            self.accTransactions = transactions_data.get('accTransactions')
            self.totalAmounts = transactions_data.get('totalAmounts')
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            raise Exception(message)

    def save_transactions_data(self):
        """
        сохраняет ведения о начислениях и списаниях в файл
        """
        try:
            data = {
                'accAmounts': self.accAmounts,
                'accTransactions': self.accTransactions,
                'totalAmounts': self.totalAmounts
            }
            with open(LOCAL_TRN_F, 'w+', encoding='utf-8') as w:
                json.dump(data, w)
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            raise Exception(message)
        else:
            return True

    def wallet_lock(self, pwd: str):
        """
        Блокирует кошелек паролем (шифрует секретные ключи протоколом AES)
        """
        if len(self.accList) == 0:
            return 'Nothing to lock here. Please create an account first!'
        elif self.isLocked:
            return 'Wallet Already Locked'
        else:
            self.isLocked = True
            for i in range(len(self.accList)):
                self.accList[i] = ToolkitBCH.serializeKey(
                    ToolkitBCH.deserializeSecKey(self.accList[i].get('secretkey')),
                    pwd
                )
            if self.save():
                return 'Wallet lock done!'

    def wallet_unlock(self, pwd: str,):
        """
        разблокирует кошелек. Расшифровывает секретные ключи (все.)
        предварительно проверяет кошелек на зашифрован/не зашифрован и корректность пароля
        """
        if len(self.accList) == 0:
            return 'Nothing to lock here. Please create an account first!'
        elif not self.isLocked:
            return 'Wallet Already UnLocked'
        else:
            try:
                self.isLocked = False
                for i in range(len(self.accList)):
                    self.accList[i] = ToolkitBCH.serializeKey(
                        ToolkitBCH.deserializeSecKey(self.accList[i].get('secretkey'), pwd)
                    )
                if self.save():
                    return 'Wallet unlock done!'
            except Exception as ex:  # надо сделать обработчики для конкретных исключений
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                raise Exception(message)

    def change_password(self, old_password: str, new_password: str, confirm_password: str):
        """
        меняет пароль кошелька
        """
        if not self.isLocked:
            return 'Wallet UnLocked'
        elif new_password != confirm_password:
            return 'New password does not match'
        elif self.wallet_unlock(old_password) == 'Wallet unlock done!':
            return self.wallet_lock(new_password)
        return 'Incorrect password'

    '''
    ##########################################################
    ##########################################################
    ############# блок работы со счетами и токенами############
    ##########################################################
    ##########################################################
    '''

    def amount_update(self):
        """
        обновляем остатки по счетам
        """
        self.accIndex = self.blockchain.get_amounts(self.accounts)
        '''
        получаем структуру self.accAmounts типа: {'inBCH' : {
            счет 1 : {'TTG': [[block], [transactionID],[amount]], 'TU': [[block], [transactionID],[amount]]}
            счет 2 : {'TTG': [[block], [transactionID],[amount]], 'TU': [[block], [transactionID],[amount]]}
            ...
            счет N : {'TTG': [[block], [transactionID],[amount]], 'TU': [[block], [transactionID],[amount]]}
        }
        'inPool':{
            счет 1 : {'TTG': [[transaction, направление, сумма, контрагент-аккаунт]], 'TU': [[transaction, направление, 
                               сумма, контрагент-аккаунт]]}
            счет 2 : {'TTG': [[transaction, направление, сумма, контрагент-аккаунт]], 'TU': [[transaction, направление, 
                               сумма, контрагент-аккаунт]]}
            ...
            счет N : {'TTG': [[transaction, направление, сумма, контрагент-аккаунт]], 'TU': [[transaction, направление, 
                               сумма, контрагент-аккаунт]]}
        }
        [block] - список блоков, где лежат вхдящие транзакции, [transactionID] - номера транзакций, [amount] - суммы
        так реализованы столбцы таблицы.
        '''
        if self.blockchain.debug_mode:
            print('Смотрим что в индексе')
            print(self.accIndex['inPool'])
        for i in self.blockchain.AMOUNT_SUFFIXES:
            self.totalAmounts[i] = [0, 0, 0]
        for i in self.accounts:
            self.accAmounts[i] = {}
            for j in self.blockchain.AMOUNT_SUFFIXES:
                self.accAmounts[i][j] = [0, 0, 0]
        if len(self.accIndex['inBCH']) != 0:
            for i, j in self.accIndex['inBCH'].items():
                for k in self.blockchain.AMOUNT_SUFFIXES:
                    if k in j:
                        for m in j[k][2]:
                            self.accAmounts[i][k][0] += m
                            self.totalAmounts[k][0] += m
        if len(self.accIndex['inPool']) != 0:
            for i, j in self.accIndex['inPool'].items():
                for k in self.blockchain.AMOUNT_SUFFIXES:
                    if k in j:
                        for m in j[k]:
                            if self.blockchain.debug_mode:
                                print('ндексные записи')
                                print(m)
                            # учитываем ожидаемые начисления из пула
                            if m[1] == 1:
                                self.accAmounts[i][k][1] += m[2]
                                self.totalAmounts[k][1] += m[2]
                            # учитываем неподтвержденные списания из пула
                            if m[1] == 0 and m[3] != i:
                                self.accAmounts[i][k][2] += m[2]
                                self.totalAmounts[k][2] += m[2]
        
        '''
        получаем структуру self.totalAmounts типа: 
        {
            'TTG': [0, 1, 2] 
            'TU': [0, 1, 2]
        }
        В позицию 0 записываем подтвержденный остаток, в позицию 1 - ожидаемые начисления, 
        в позицию 2 - ожидаемые списания. 
        Доступными считаем "подтвержденный остаток" - "ожидаемые списания"
        '''

    def search_account_data(self, account: str):
        """
        Субфункция для поиска набора данных (ключей) в списке аккаунтов по адресу
        """
        for i in self.accList:
            if i.get('publiczone').get('account') == account:
                return i
        else:
            return 'IncorrectAcc'

    def move(self, output_account, output_amount, fee_type='included', suffix: str = 'TTG', pwd: str = None):
        """
        output_account - адрес получателя
        output_amount - сумма перевода
        fee_type - параметр указывает тип комиссии (внутри суммы/берется сверху)
        suffix - Тип пересылаемого токена
        pwd - пароль доступа к кошельку. Указываем если кошелек запаролен.
        """
        if self.blockchain.debug_mode:
            print('Принты из Wallet.move')
        self.amount_update()
        suffix = ('TTG' if suffix == '' else suffix)
        available_limit = self.totalAmounts.get(suffix)[0] - self.totalAmounts.get(suffix)[2]
        if self.blockchain.debug_mode:
            print('av_limit = ' + str(available_limit))
        # получаем действующую ставку комиссии сети в %. Вернется ставка комиссии на момент создания транзакции.
        fee_rate = self.blockchain.getFeeRate(suffix)
        if self.blockchain.debug_mode:
            print('fee_rate = ' + str(fee_rate))
        moves_pool = list()

        if fee_type == 'included':
            total_fee = fee_rate * output_amount / (100 + fee_rate)
            output_amount -= total_fee  # выделяем комиссию
        else:
            total_fee = fee_rate * output_amount / 100

        fee_remainder = total_fee
        amount_remainder = output_amount
        if self.blockchain.debug_mode:
            print('fee_r_start = ' + str(fee_remainder))
            print('amount_r_start = ' + str(amount_remainder))
            print('finally_am = ' + str(fee_remainder + amount_remainder)
                  + ' процент комиссии:  ' + str(fee_remainder / amount_remainder))
        
        if (amount_remainder + total_fee) <= available_limit:
            '''
            если тотально токенов нужного типа в кошельке хватает, выполняем формирование транзакции
            иначе прерываем выполнение с ошибкой.
            Выдаем сообщение: Недостаточно токенов!!
            '''
            for k, j in self.accAmounts.items():
                '''
                Если на аккаунте k достаточно средств, сразу формируем ход и прерываем обход аккаунтов
                '''
                jj = 0
                if suffix in j:
                    jj = j[suffix][0] - j[suffix][2]
                if jj > 0:
                    if jj == (amount_remainder + fee_remainder):
                        m = TokenMove(k, output_account, amount_remainder, fee_remainder)
                        acc_dict = self.search_account_data(k)  # никак не обрабатываем вариант с кривым адресом
                        m.sign_transaction(acc_dict.get('publiczone').get('publickey'), acc_dict.get('secretkey'), pwd)
                        moves_pool.append(m.to_dict())
                        break
                    elif jj > (amount_remainder + fee_remainder):
                        m = TokenMove(k, output_account, amount_remainder, fee_remainder)
                        acc_dict = self.search_account_data(k)
                        m.sign_transaction(acc_dict.get('publiczone').get('publickey'), acc_dict.get('secretkey'), pwd)
                        moves_pool.append(m.to_dict())
                        '''
                        Кидаем обратно сдачу. Это абсолютно необходимо? Ну пусть пока так.
                        Это позволит относительно безнаказанно обрезать блокчейн и упростит подсчет неизрасходованных 
                        выходов в дальнейшем.
                        '''
                        m = TokenMove(k, k, jj - amount_remainder - fee_remainder, 0, data='change')
                        m.sign_transaction(acc_dict.get('publiczone').get('publickey'), acc_dict.get('secretkey'), pwd)
                        moves_pool.append(m.to_dict())
                        break
                    else:
                        '''
                        Иначе обрабатываем другие состояния. Сначала списываем amount, а потом fee
                        '''
                        if (jj >= amount_remainder) and (amount_remainder > 0):
                            m = TokenMove(k, output_account, amount_remainder, jj - amount_remainder)
                            acc_dict = self.search_account_data(k)
                            m.sign_transaction(acc_dict.get('publiczone').get('publickey'), acc_dict.get('secretkey'),
                                               pwd)
                            moves_pool.append(m.to_dict())
                            fee_remainder -= (jj - amount_remainder)
                            amount_remainder = 0
                        elif jj < amount_remainder:
                            m = TokenMove(k, output_account, jj, 0)
                            acc_dict = self.search_account_data(k)
                            m.sign_transaction(acc_dict.get('publiczone').get('publickey'), acc_dict.get('secretkey'),
                                               pwd)
                            moves_pool.append(m.to_dict())
                            amount_remainder -= jj
                        elif amount_remainder == 0 and fee_remainder > jj:
                            m = TokenMove(k, output_account, amount_remainder, jj)
                            acc_dict = self.search_account_data(k)
                            m.sign_transaction(acc_dict.get('publiczone').get('publickey'), acc_dict.get('secretkey'),
                                               pwd)
                            moves_pool.append(m.to_dict())
                            fee_remainder -= jj
            else:
                raise Exception('Not enough ' + suffix + ' tokens')
        # тестировочный код
        if self.blockchain.debug_mode:
            print('Распечатаем ходы:')
            for i in moves_pool:
                print(i)
            print('Ходы распечатаны')
            # конец тестировочного кода
        trn = TokenSendTransaction(moves_pool, total_fee, output_amount, suffix)
        trn.sign(self.accList[0].get('publiczone').get('publickey'), self.accList[0].get('secretkey'), pwd)
        try:
            add_to_pull = self.blockchain.put_transaction(trn.to_dict())
            if add_to_pull[0]:
                return 'Transaction created!'
            else:
                return 'Error: {}'.format(add_to_pull[2])
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            raise Exception(message)
