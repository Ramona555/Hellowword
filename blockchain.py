import hashlib
import json
from time import time

# 创建创世块
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.create_block(previous_hash='1', proof=100)  

    def create_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else None,
        }
         # 重置当前交易列表
        self.current_transactions = [] 
        self.chain.append(block)
        return block
# 创建一个新的交易并添加到交易列表中
    def new_transaction(self, sender, recipient, vnf_info):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'vnf_info': vnf_info,
        })
#生成区块的哈希值
    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof
    
# 以四个零开头作为简单的工作量证明

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"  

# 创建一个Flask应用程序来进行交互
from flask import Flask, jsonify, request

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.chain[-1]
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        sender="0",
        recipient="Your Address",
        vnf_info="Your VNF Info"
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.create_block(proof, previous_hash)

    response = {
        'message': "新块已经挖出",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required_fields = ['sender', 'recipient', 'vnf_info']
    if not all(k in values for k in required_fields):
        return '缺少必要字段', 400
#请求中必须包含JSON数据，包括sender（发送者地址）、recipient（接收者地址）和vnf_info（VNF信息）。如果缺少任何必要字段，将返回HTTP 400错误。
    blockchain.new_transaction(values['sender'], values['recipient'], values['vnf_info'])
    response = {'message': f'交易将添加到块 {blockchain.chain[-1]["index"]}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
#启动Flask应用：app.run(host='0.0.0.0', port=5000) 指定了Flask应用的运行参数。它告诉Flask应用在所有可用的网络接口上监听（0.0.0.0）并使用端口5000。通过浏览器HTTP客户端访问Flask应用。
