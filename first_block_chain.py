"""
This module is used to create a blockchain

Link: http://ecomunsing.com/build-your-own-blockchain
"""
import hashlib, json, sys, random

class FirstBlockChain:
    """
    The basical rules of transactions are:
    1). The sum of deposits and withdrawals must be 0, which means the tokens are neither created nor destroyed
    2). One person's account must have enought funds to cover any withdrawals
    """

    def __init__(self):
        self.txnBuffer = [self.makeTransaction() for i in range(1000)]
        self.blockSizeLimit = 10 # arbitrary number of transactions per block
        random.seed(0)

    def createChain(self):
        # generate the first block, it's called genesis block, and we give Alice and Bob 100 coins each
        self.state = {u'Alice':100, u'Bob':100}
        genesisBlockTxns = [self.state]
        genesisBlockContents = {u'blockNumber':0, u'parentHash':None, u'txnCount':1, u'txns':genesisBlockTxns}
        genesisHash = self.HashMe(genesisBlockContents)
        genesisBlock = {u'hash':genesisHash, u'contents':genesisBlockContents}
        self.chain = [genesisBlock]

        # try to create the whole block chain
        while len(self.txnBuffer)>0:
            bufferStartSize = len(self.txnBuffer)

            # gather a set of valid transactions for inclusion
            txnList = []
            while (len(self.txnBuffer)>0) & (len(txnList)<self.blockSizeLimit):
                newTxn = self.txnBuffer.pop()
                validTxn = self.isValidTxn(newTxn)
                if validTxn:
                    # if we got a valid state, not False
                    txnList.append(newTxn)
                    self.state = self.updateState(newTxn)
                else:
                    print("Ignored transaction")
                    sys.stdout.flush()
                    continue
            #make a block
            myBlock = self.makeBlock(txnList)
            self.chain.append(myBlock)
        #print self.chain
        print '====='
        print self.state
        print 'start checking chain:'
        self.checkChain()

    def makeBlock(self, txns):
        parentBlock = self.chain[-1]
        parentHash = parentBlock[u'hash']
        blockNumber = parentBlock[u'contents'][u'blockNumber'] + 1
        txnCount = len(txns)
        blockContents = {u'blockNumber':blockNumber, u'parentHash':parentHash, u'txnCount':txnCount, 'txns': txns}
        blockHash = self.HashMe(blockContents)
        block = {u'hash':blockHash, u'contents':blockContents}
        return block

    def HashMe(self, msg=""):
        # function used to wrap hashing algorithm, we differenciate python 2 and python 3
        if type(msg) != str:
            msg = json.dumps(msg, sort_keys=True)
        if sys.version_info.major == 2:
            return unicode(hashlib.sha256(msg).hexdigest(), "utf-8")
        else:
            return hashlib.sha256(str(msg).encode("utf-8")).hexdigest()

    def makeTransaction(self, maxValue=3):
        # create transactions in between the range of (1, maxValue)
        sign = int(random.getrandbits(1))*2 - 1   # randomly gives 1 or -1
        amount = random.randint(1, maxValue)
        alicePay = sign*amount
        bobPay = -1 * alicePay
        return {u'Alice': alicePay, u'Bob': bobPay}

    def updateState(self, txn):
        # if the transaction is valid, then udpate the state
        state = self.state.copy()
        for key in txn:
            if key in state.keys():
                state[key] += txn[key]
            else:
                state[key] = txn[key]
        return state
    
    def isValidTxn(self, txn):
        # assume the transcation is dictionary keyed by account name
        # check the sum of the deposits and withdrawals is 0
        if sum(txn.values()) is not 0:
            return False
        
        # check that the transaction does not cause overdraft
        for key in txn.keys():
            if key in self.state.keys():
                acctBalance = self.state[key]
            else:
                acctBalance = 0
            if (acctBalance + txn[key]) < 0:
                return False
        return True
    


    # block chain validation
    def checkBlockHash(self, block):
        # raise an exception if the hash does not match the block contents
        expectedHash = self.HashMe(block['contents'])
        if block['hash'] != expectedHash:
            raise Exception('Hash does not match contents of block %s'%block['contents']['blockNumber'])
        return

    def checkBlockValidity(self, block, parent):
        # we want to check the following conditions:
        # - each of the transactions are valid updates to the system state
        # - block hash is valid for the block contents
        # - block number increments the parent block number by 1
        # - accurately references the parent block's hash
        parentNumber = parent['contents']['blockNumber']
        parentHash = parent['hash']
        blockNumber = block['contents']['blockNumber']
        # check transaction validity, throw an error if an invalid transaction was found
        for txn in block['contents']['txns']:
            if self.isValidTxn(txn):
                state = self.updateState(txn)
            else:
                raise Exception('Invalid transaction in block %s: %s'%(blockNumber, txn))
        self.checkBlockHash(block)

        if blockNumber != (parentNumber + 1):
            raise Exception('Hash does not match contents of block %s'%blockNumber)

        if block['contents']['parentHash'] != parentHash:
            raise Exception('Parent hash not accurate at block %s'%blockNumber)
        
        return state
    
    def checkChain(self):
        # work through the chain from the genesis block
        # checking that all transactions are internally valid,
        # that the transactions do not cause an overdraft
        # and that the blocks are linked by their hashes
        # Data input processing: make sure that our chain is a list of dicts
        if type(self.chain) == str:
            try:
                self.chain = json.loads(self.chain)
                assert(type(self.chain) == list)
            except:
                return False
        elif type(self.chain) != list:
            return False
        
        state = {}
        for txn in self.chain[0]['contents']['txns']:
            state = self.updateState(txn)
        self.checkBlockHash(self.chain[0])
        parent = self.chain[0]

        for block in self.chain[1:]:
            state = self.checkBlockValidity(block, parent)
            parent = block

        print state
        return state


    # end block chain validation


if __name__ == "__main__":
    FirstBlockChain().createChain()
