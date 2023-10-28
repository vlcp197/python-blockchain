# python-blockchain

## Overview
* Creating a blockchain from scratch to learn how one works.
* Working with flask API to access and manage the blockchain.

## Authentication

## Usage
To use the API, make HTTP requests to the following endpoint:

### To mine a new block
GET[http://127.0.0.1:5000/mine]

### To retrieve the full blockchain
GET[http://127.0.0.1:5000/chain]

### To implement the Consensus Algorithm
GET[http://127.0.0.1:5000/nodes/resolve]

### To create a new transaction to a block
POST[http://127.0.0.1:5000/transactions/new]  
Content-Type: application/json
{
    "sender": "" ,
    "recipient": "",
    "amount": 1
}

### To accept a list of new nodes in the form of URLs
POST[http://127.0.0.1:5000/nodes/register]
Content-Type: application/json
{
    "nodes": ["http://127.0.0.1:5001"]
}

## Each block needs to have:
* An index;
* A timestamp;
* A list of transactions with their sender, recipient, and the amount.
* Beyond that, a block needs to have its proof of work and the previous hash.

## Definitions:
- Proof of work algorithm = How new blocks are created or mined.
- Proof of work goal = Discover a number that solves a problem.
- The number must be very difficult to find but very easy to verify.
- Consensus Algorithm = Set of rules that help blockchain nodes to stay synchronized. It ensures that every node in the blockchain will have the same view of the blockchain. It is necessary, since the blockchain networks are decentralized.

## Endpoints:
- /transctions/new = To create a new transaction to a block.
- /mine = To mine a new block.
- /chain = To return the full blockchain.
- /nodes/register = To accept a list of new nodes in the form of URLs
- /nodes/resolve = to implement the Consensus Algorithm.

## Consensus Algorithm:
- The longest valid chain is Authoritative. In other words, the longest chain is the official and correct version of the blockchain, since it's the chain that is accepted by the majority of nodes in the network

## Tutorial:
https://hackernoon.com/learn-blockchains-by-building-one-117428612f46
