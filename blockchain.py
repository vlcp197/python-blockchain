import hashlib
import json
from time import time
from typing import Union, List
from uuid import uuid4
from flask import Flask, jsonify, request
from textwrap import dedent


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
        """
            Return the last block in the chain.
            It is a get method, so we use the decorator @property to
            encapsulate it.
        """
        return

    def run_proof_of_work(self, last_proof: int):
        """
            Simple proof of work algorithm:
                - Find a number x' such that hash(xx') contains 4 leading
                zeroes, where p is the previous p'
                - p is the previous proof, and p' is the new proof
            Params:
                last_proof
                return: New proof
        """
        proof = 0
        while self.verify_valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def verify_valid_proof(last_proof: int, proof: int):
        """
            Validates the proof, verifying if hash(last_proof, proof) has
            4 leading zeroes.
            Params:
                last_proof
                proof
                return: True if correct, or False.
        """
        guess: str = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


# Instantiate our node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier: str = str(uuid4()).replace('-', '')

# Instantiate the blockchain
blockchain: Blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def get_mine_block():
    return "We'll mine a new block"


@app.route('/transactions/new', methods=['POST'])
def add_new_transaction():
    """
        Adds a new transction to the block.
    """
    values = request.get_json()

    missing_values = []
    # Check if the request contains all the required values
    required: List[str] = ['sender', 'recipient', 'amount']

    if not all(k in values for k in required):
        missing_values = [k for k in required if k not in values]
        # for k in required:
        #     if k not in values:
        #         missing_values.append(k)
        return f"Missing values{str(missing_values)}", 400

    index: str = blockchain.add_new_transaction(
        values['sender'],
        values['recipient'],
        values['amount']
    )

    response: dict = {'message': f'Transaction will be added to Block {index}'}

    return jsonify({response}), 200


@app.route('/chain', methods=['GET'])
def get_full_chain():
    """
        Get method to return the chain.
    """
    response: dict = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
