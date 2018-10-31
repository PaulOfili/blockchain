from functools import reduce
# import hashlib as hl
# import hashlib
from collections import OrderedDict
import json
import pickle

from hash_util import hash_string_256, convert_to_hash

MINING_REWARD = 10
genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': [],
    'proof': 100
}
blockchain = [genesis_block]
open_transactions = []
continue_loop = True
owner = 'Paul'
participants = {'Paul'}


def load_data():
    with open('blockchain.txt', mode='r') as f:
        global blockchain
        global open_transactions

        file_content = f.readlines()
        blockchain = json.loads(file_content[0][:-1])
        open_transactions = json.loads(file_content[1])

        # file_content = pickle.loads(f.read())
        # # print(file_content)
        # blockchain = file_content['chain']
        # open_transactions = file_content['ot']

        """ CODE TO ENSURE ADDITION OF ORDERED-DICT INFORMATION INTO THE TRANSACTIONS DETAIL BECAUSE
        WHEN CONVERTING TO JSON USING 'json.dumps', IT LOSES THAT EXTRA INFORMATION. BUT PICKLE DOES NOT, PICKLE 
        PICKLE MAINTAINS THAT INFORMATION HENCE CODE BELOW BECOMES UNNECESSARY. USE THE CODE WHEN USING JSON LIBRARY"""

        blockchain = [{
            'previous_hash': block['previous_hash'],
            'index': block['index'],
            'proof': block['proof'],
            'transactions': [
                OrderedDict([
                    ('sender', tx['sender']),
                    ('recipient', tx['recipient']),
                    ('amount', tx['amount'])
                ])
                for tx in block['transactions']]
        } for block in blockchain]

        open_transactions = [
            OrderedDict([
                ('sender', tx['sender']),
                ('recipient', tx['recipient']),
                ('amount', tx['amount'])
            ]) for tx in open_transactions]


load_data()


def save_data():
    with open('blockchain.txt', mode='w') as f:
        # # json.dump(blockchain, f)
        f.write(json.dumps(blockchain))
        f.write('\n')
        f.write(json.dumps(open_transactions))
        # saved_data = {
        #     'chain': blockchain,
        #     'ot': open_transactions
        # }
        # f.write(pickle.dumps(saved_data))


def take_choice():
    allowed = list('12345hvq')
    while True:
        print('Please choose: ')
        print('1. Add new transaction value: ')
        print('2. Mine a new block')
        print('3. Output the blockchain blocks')
        print('4. Print out participants')
        print('5. Check transaction validity')
        print('h. Manipulate the chain')
        print('v. Verify blockchain')
        print('q. Quit program')
        choice = input("Your choice: ").strip()

        if choice in allowed:
            break

        print('Not allowed, YO!')
    return choice


def get_transaction_value():
    tx_recipient = input('Enter recipient of transaction: ')
    tx_amount = float(input('Your transaction amount please: '))
    return tx_recipient, tx_amount


def get_balance(participant):
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]

    tx_sender_amount = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in
                        blockchain]
    tx_sender_amount.append(open_tx_sender)
    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt), tx_sender_amount, 0)

    tx_recipient_amount = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in
                           blockchain]
    amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt), tx_recipient_amount, 0)

    return amount_received - amount_sent


def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])
    # for tx in open_transactions:
    #     if not verify_transaction(tx):
    #         return False
    # return True


def add_transaction(recipient, sender=owner, amount=1.0):
    # transaction = {
    #     'sender': sender,
    #     'recipient': recipient,
    #     'amount': amount
    # }
    transaction = OrderedDict(
        [('sender', sender), ('recipient', recipient), ('amount', amount)]
    )
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    return False


def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    print(guess_hash)
    return guess_hash[:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    last_block_hash = convert_to_hash(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_block_hash, proof):
        proof += 1
    return proof


def mine_block():
    last_block = blockchain[-1]
    hashed_block = convert_to_hash(last_block)
    proof = proof_of_work()

    # reward_transactions = {
    #     'sender': 'MINING',
    #     'recipient': owner,
    #     'amount': MINING_REWARD
    # }
    reward_transaction = OrderedDict(
        [('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)]
    )
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions,
        'proof': proof
    }
    blockchain.append(block)
    # open_transactions.clear()
    return True


def verify_chain():
    # MY WORK -- NOT SUFFICIENT
    # for index in range(len(blockchain) - 1):
    #     if not convert_to_hash(blockchain[index]) == blockchain[index + 1]['previous_hash']:
    #         return False
    # return True
    # # WHAT THE TUTOR USED
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != convert_to_hash(blockchain[index - 1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('Proof of work is invalid')
            return False
    return True


def print_blockchain_elements():
    for block in blockchain:
        print(block)
    for tx in open_transactions:
        print(tx)


while continue_loop:
    user_choice = take_choice()
    if user_choice == '1':
        recipient, amount = get_transaction_value()
        print(' Added transaction!' if add_transaction(recipient, amount=amount) else 'Transaction Failed')
        print(open_transactions)

    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
            print(blockchain)

    elif user_choice == '3':
        print_blockchain_elements()

    elif user_choice == '4':
        print(participants)

    elif user_choice == '5':
        print('All transactions are valid' if verify_transactions() else 'There are invalid transactions')

    elif user_choice == 'h':
        if len(blockchain) > 0:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [
                    {'sender': 'Vic',
                     'recipient': 'Pablo',
                     'amount': 100}
                ]
            }

    elif user_choice == 'q':
        continue_loop = False

    if not verify_chain():
        print_blockchain_elements()
        print('Invalid blockchain')
        continue_loop = False

    print('Balance of {}: {:6.2f}'.format('Paul', get_balance('Paul')))
else:
    print('User left!')

print('Done')
