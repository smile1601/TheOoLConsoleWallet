class rblockchain:

    def __init__(self, p2p):
        self.AMOUNT_SUFFIXES = list()
        self.p2p = p2p
        self.amounts = None
        self.FEE_RATES = None
        self.add_to_pull = None
        self.debug_mode = False

    def get_amounts(self, accounts_list: list):
        self.amounts = None
        self.p2p.peerDiscoveryHandler.handshake_common('GETAMOUNTS', accounts_list)
        while True:
            if self.amounts is not None:
                break

        return self.amounts

    def getFeeRate(self, suffix: str):
        self.FEE_RATES = None
        self.p2p.peerDiscoveryHandler.handshake_common('GETFEERATES', suffix)
        while True:
            if self.FEE_RATES is not None:
                break

        return self.FEE_RATES

    def put_transaction(self, trn: dict):
        self.add_to_pull = None
        self.p2p.peerDiscoveryHandler.handshake_common('PUTTRANSACTION', trn)
        while True:
            if self.add_to_pull is not None:
                break

        return self.add_to_pull
