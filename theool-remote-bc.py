import sys
import TheOoLEmissionP2P
from TheOoLEmissionBCH.RemoteAccessBlockchain import rblockchain
from TheOoLEmissionBCH.Wallet import Wallet
from ToolkitBCH.StartCmd import StartCmd


if __name__ == '__main__':
    node = TheOoLEmissionP2P.NodeBCH()
    node.p2p.is_peer = False
    node.start_p2p()
    if not node.p2p.no_seeds:
        node.blockchain = rblockchain(node.p2p)
        node.wallet = Wallet(node.blockchain)
        app = StartCmd()
        app.node = node
        app.intro = 'Welcome to the TheOoL remote emission blockchain. Type help or ? to list commands.\n'
        app.prompt = 'theool-remote-bc: '
        sys.exit(app.cmdloop())
    else:
        print('Exception: No seeds in network! Try later..')
