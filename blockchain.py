import hashlib
import json
from time import time
from typing import Union, List
from uuid import uuid4
from flask import Flask, jsonify, request
import requests
from urllib.parse import urlparse


class Blockchain():
    """Class that will manage the chain"""
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
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
        return self.chain[-1]

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

    def register_node(self, address):
        """
            Add neighbouring nodes to the network.
            params:
                address: Address of the node.
                E.g.: http://192.168.0.5:5000
                return: None
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
            Determine if a given blockchain is valid.
            Params:
                chain: A chain in the blockchain.
                return: True if valid, False if not.
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'last_block: {last_block}')
            print(f'current_block: {block}')
            print('\n--------------\n')
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check if the proof of work is correct
            if not self.verify_valid_proof(
                    last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
            This is the Consensus Algorithm, it resolves conflicts by
            replacing our chain with the longest one in the network.
            Params:
                return: True if our chain was replaced, False if not.
        """

        neighbours = self.nodes
        new_chain = None

        # Comparing chains to know which is the longest
        max_length = len(self.chain)

        # Fetching the chains of all nodes in our network and verifying it
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False


# Instantiate our node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier: str = str(uuid4()).replace('-', '')

# Instantiate the blockchain
blockchain: Blockchain = Blockchain()


# This method will be split into other methods afterwards
@app.route('/mine', methods=['GET'])
def mine_block():
    """
        Mining Endpoint for the API.
        It calculates the proof of work;
        Rewards the miner giving 1 coin;
        Creates the new block and adds it to the chain.
    """

    # Run the proof of work algorithm to get the another proof
    last_block = blockchain.get_last_block
    last_proof = last_block['proof']
    proof = blockchain.run_proof_of_work(last_proof)

    # Receive the reward for the proof of work
    blockchain.add_new_transaction(
        sender='0',
        recipient=node_identifier,
        amount=1
    )

    # Forge the new block by adding it to the chain
    previous_hash = blockchain.hash_block(last_block)
    block = blockchain.create_new_block(proof, previous_hash)

    response = {
        'message': 'New forged block',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return jsonify(response), 200

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
        return f"Missing values{str(missing_values)}", 400

    index: str = blockchain.add_new_transaction(
        values['sender'],
        values['recipient'],
        values['amount']
    )

    response: dict = {'message': f'Transaction will be added to Block {index}'}

    return jsonify(response), 201


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


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    """
        Endpoint to register nodes in the blockchain.
    """
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New node have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def reachConsensusOnBlock():
    """
        Endpoint to apply the Consensus Algorithm.
    """
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain,
        }

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
