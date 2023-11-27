# blockchain.py

import hashlib
import time


class Block:
    def __init__(self, index, previous_hash, data, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        self.data = data
        self.timestamp = timestamp or time.time()
        self.nonce = 0  # For proof of work
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data_str = str(self.index) + self.previous_hash + \
            str(self.timestamp) + str(self.nonce) + str(self.data)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def mine_block(self, difficulty):
        while self.hash[:difficulty] != '0' * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block mined: {self.hash}")

    def __str__(self):
        return f"Block #{self.index}\nTimestamp: {self.timestamp}\nData: {self.data}\nHash: {self.hash}\n"


# Test the Block class
block = Block(0, "0", "Genesis Block")
print(block)

# blockchain.py (continued)


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4  # Adjust the difficulty as needed

    def create_genesis_block(self):
        return Block(0, "0", "Genesis Block")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.index = len(self.chain)
        new_block.previous_hash = self.get_latest_block().hash
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True


# Test the Blockchain class
blockchain = Blockchain()
blockchain.add_block(Block(1, "", "Data 1"))
blockchain.add_block(Block(2, "", "Data 2"))

print("Blockchain is valid:", blockchain.is_chain_valid())
