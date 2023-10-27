import hashlib
import json
from time import time
from typing import Union
from uuid import uuid4


class Blockchain():
    """Class that will manage the chain"""
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        self.create_new_block(previous_hash=1, proof=100)

    def create_new_block(self, proof: int, previous_hash: int = None):
        """
        Creates a new block and adds it to the chain.
        Params:
            proof: The proof given by the proof of work algorithm.
            previous_hash: The hash of previous block.
            return: New block.
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Adds the block to the chain
        self.chain.append(block)

        return block

    def add_new_transaction(self, sender: str, recipient: str, amount: int):
        """
        Adds a new transaction to the list of transactions.
        Params:
            sender: Address of the sender.
            recipient: Address of the recipient.
            amount: Quantity traded.
            return: Index of the block that will hold this transaction.
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.get_last_block['index'] + 1

    @staticmethod
    def hash_block(block: dict):
        """
        Creates a SHA-256 hash of a block
        Params:
            block: Block that will be hashed.
            return: Hash of a block.
        It is a static method, because it belongs to the class itself
        not to an specific object of that class.
        """
        block_json: Union[str, dict, float, int] = json.dumps(
            block, sort_keys=True).encode()
        return hashlib.sha256(block_json).hexdigest()

    @property
    def get_last_block(self):
        """Return the last block in the chain.
        It is a get method, so we use the decorator @property to
        encapsulate it.
        """
        return

# Each block needs to have:
# an index;
# a timestamp;
# a list of transactions with their sender, recipient, and the amount.
# Beyond that, a block needs to have its proof of work and the previous hash

# Proof of work algorithm = How new blocks are created or mined
# Proof of work goal = Discover a number that solves a problem.
# The number must be very difficult to find but very easy to verify.



