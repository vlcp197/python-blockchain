import hashlib
import json
from time import time
from typing import Union
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
