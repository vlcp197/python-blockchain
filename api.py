from classes.blockchain import Blockchain
from uuid import uuid4
from flask import Flask, jsonify, request
from typing import List


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
