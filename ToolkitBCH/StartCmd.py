import cmd2


class StartCmd(cmd2.Cmd):

    def __init__(self):
        cmd2.Cmd.__init__(self)
        self.node = None
        del cmd2.Cmd.do_alias
        del cmd2.Cmd.do_edit
        del cmd2.Cmd.do_history
        del cmd2.Cmd.do_run_pyscript
        del cmd2.Cmd.do_set
        del cmd2.Cmd.do_shortcuts
        del cmd2.Cmd.do_macro
        del cmd2.Cmd.do_quit
        del cmd2.Cmd.do_run_script
        del cmd2.Cmd.do_shell

    def base_status(self):
        self.poutput(self.node.get_status())

    def base_inbound(self):
        self.poutput(self.node.get_inbound())

    def base_outbound(self):
        self.poutput(self.node.get_outbound())

    def base_peers(self):
        self.poutput(self.node.get_peers())

    def base_amounts(self):
        self.poutput(self.node.get_amounts())

    def base_blocks(self):
        self.poutput(self.node.get_blocks())

    print_parser = cmd2.Cmd2ArgumentParser(
        description='Show information about node and blockchain',
        add_help=False
    )
    print_subparsers = print_parser.add_subparsers(help='sub-command help')

    print_subparsers_status = print_subparsers.add_parser('status', help='Show p2p network status')
    print_subparsers_status.set_defaults(func=base_status)

    print_subparsers_inbound = print_subparsers.add_parser('inbound', help='Show inbound connections')
    print_subparsers_inbound.set_defaults(func=base_inbound)

    print_subparsers_outbound = print_subparsers.add_parser('outbound', help='Show outbound connections')
    print_subparsers_outbound.set_defaults(func=base_outbound)

    print_subparsers_peers = print_subparsers.add_parser('peers', help='Show accessible peers list')
    print_subparsers_peers.set_defaults(func=base_peers)

    print_subparsers_amounts = print_subparsers.add_parser('amounts', help='Show amounts')
    print_subparsers_amounts.set_defaults(func=base_amounts)

    print_subparsers_blocks = print_subparsers.add_parser('blocks', help='Show blocks')
    print_subparsers_blocks.set_defaults(func=base_blocks)

    print_parser.set_defaults(func=base_status)

    @cmd2.with_argparser(print_parser)
    def do_print(self, args):
        func = getattr(args, 'func', None)
        if func is not None:
            func(self)

    def base_wallet_create(self, args):
        try:
            self.poutput(self.node.wallet.create(args.name))
        except Exception as ex:
            self.poutput(cmd2.style('Error: {}'.format(ex), fg=cmd2.fg.red))

    def base_wallets_list(self, args):
        self.poutput(self.node.wallet.get_wallets_list())

    def base_wallets_info(self, args):
        self.poutput(self.node.wallet.to_string())

    def base_wallets_accounts(self, args):
        self.poutput(self.node.wallet.get_accounts())

    def base_wallet_load(self, args):
        try:
            self.poutput(self.node.wallet.load(args.name))
        except Exception as ex:
            self.poutput(cmd2.style('Error: {}'.format(ex), fg=cmd2.fg.red))

    def base_wallet_rename(self, args):
        try:
            self.poutput(self.node.wallet.rename(args.name))
        except Exception as ex:
            self.poutput(cmd2.style('Error: {}'.format(ex), fg=cmd2.fg.red))

    def base_wallet_lock(self, args):
        try:
            self.poutput(self.node.wallet.wallet_lock(args.pwd))
        except Exception as ex:
            self.poutput(cmd2.style('Error: {}'.format(ex), fg=cmd2.fg.red))

    def base_wallet_unlock(self, args):
        try:
            self.poutput(self.node.wallet.wallet_unlock(args.pwd))
        except Exception as ex:
            self.poutput(cmd2.style('Error: {}'.format(ex), fg=cmd2.fg.red))

    def base_wallet_change_password(self, args):
        try:
            old_password, new_password, confirm_password = args.oldPassword, args.newPassword, args.confirmPassword
            self.poutput(self.node.wallet.change_password(old_password, new_password, confirm_password))
        except Exception as ex:
            self.poutput(cmd2.style('Error: {}'.format(ex), fg=cmd2.fg.red))

    def base_wallet_create_account(self, args):
        try:
            self.poutput(self.node.wallet.create_account(args.pwd))
        except Exception as ex:
            self.poutput(cmd2.style('Error: {}'.format(ex), fg=cmd2.fg.red))

    def base_wallet_move(self, args):
        try:
            output_account, output_amount, suffix, pwd = args.output_account, args.output_amount, args.suffix,\
                                                         args.password
            self.poutput(self.node.wallet.move(output_account, output_amount, suffix, pwd))
        except Exception as ex:
            self.poutput(cmd2.style('Error: {}'.format(ex), fg=cmd2.fg.red))

    wallet_parser = cmd2.Cmd2ArgumentParser(
        description="Interface for managing addresses and keys "
                    "and their interaction with the distributed registry base",
        add_help=False
    )

    wallet_subparsers = wallet_parser.add_subparsers(help='sub-command help')

    wallet_create = wallet_subparsers.add_parser('create', help='Creates a new wallet with the specified name')
    wallet_create.add_argument('-n', '--name', type=str, default='', help='Create new wallet')
    wallet_create.set_defaults(func=base_wallet_create)

    wallets_list = wallet_subparsers.add_parser('list', help='Show existing wallets')
    wallets_list.set_defaults(func=base_wallets_list)

    wallet_info = wallet_subparsers.add_parser('info', help='Show existing wallets')
    wallet_info.set_defaults(func=base_wallets_info)

    wallet_accounts = wallet_subparsers.add_parser('accounts', help='Show accounts')
    wallet_accounts.set_defaults(func=base_wallets_accounts)

    wallet_load = wallet_subparsers.add_parser('load', help='Load wallet by Name')
    wallet_load.add_argument('-n', '--name', type=str, default='', help='Wallet Name')
    wallet_load.set_defaults(func=base_wallet_load)

    wallet_rename = wallet_subparsers.add_parser('rename', help='Rename wallet')
    wallet_rename.add_argument('-n', '--name', type=str, default='', help='New wallet Name')
    wallet_rename.set_defaults(func=base_wallet_rename)

    wallet_change_password = wallet_subparsers.add_parser('changePassword', help='Change wallet password')
    wallet_change_password.add_argument('-op', '--oldPassword', type=str, default='', help='Old password')
    wallet_change_password.add_argument('-p', '--newPassword', type=str, default='', help='New password')
    wallet_change_password.add_argument('-cp', '--confirmPassword', type=str, default='', help='Confirm password')
    wallet_change_password.set_defaults(func=base_wallet_change_password)

    wallet_lock = wallet_subparsers.add_parser('lock',
                                               help='Blocks the wallet with a password (encrypts secret keys with '
                                                    'the AES protocol)')
    wallet_lock.add_argument('-p', '--pwd', type=str, default='', help='Wallet password')
    wallet_lock.set_defaults(func=base_wallet_lock)

    wallet_unlock = wallet_subparsers.add_parser('unlock',
                                                 help="""Разблокирует кошелек. Расшифровывает секретные ключи (все)
Предварительно проверяет кошелек на зашифрован/не зашифрован и корректность пароля""")
    wallet_unlock.add_argument('-p', '--pwd', type=str, default='', help='Wallet password')
    wallet_unlock.set_defaults(func=base_wallet_unlock)

    wallet_create_account = wallet_subparsers.add_parser('createAccount',
                                                         help="""Create new account""")
    wallet_create_account.add_argument('-p', '--pwd', type=str, default=None, help='Account password')
    wallet_create_account.set_defaults(func=base_wallet_create_account)

    wallet_move = wallet_subparsers.add_parser('move', help='Move amounts')
    wallet_move.add_argument('-a', '--output_account', type=str, default='', help='Output account')
    wallet_move.add_argument('-s', '--output_amount', type=float, default=0, help='Summa to move')
    wallet_move.add_argument('-t', '--suffix', type=str, default='TTG', help='Amount type, TTG default')
    wallet_move.add_argument('-p', '--password', type=str, default='', help='Account password')
    wallet_move.set_defaults(func=base_wallet_move)

    @cmd2.with_argparser(wallet_parser)
    def do_wallet(self, args):
        func = getattr(args, 'func', None)
        if func is not None:
            func(self, args)

    def do_ping(self, args):
        """
        Check host in p2p network.

            Usage:  ping [host]
                [host] - for example 62.77.154.93:58877

        """
        if args[1] and args[1] != '':
            self.node.p2p.peerDiscoveryHandler.handshake_ping(args[1])

    def do_exit(self, args):
        """
        Stop node and exit from blockchain

            Usage:  exit
        """
        self.node.stop_p2p()
        return -1
