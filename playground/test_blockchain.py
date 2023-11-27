from blockchain import Blockchain

# Create blockchain instance
blockchain = Blockchain()

# Test genesis block creation
assert blockchain.chain[0].index == 0, "Genesis block has incorrect index"
assert blockchain.chain[0].previous_hash == "0", "Genesis block has incorrect previous hash"

# Test adding new blocks
blockchain.add_block("Block 1 Data")
blockchain.add_block("Block 2 Data")

assert len(blockchain.chain) == 3, "Incorrect number of blocks after additions"
assert blockchain.chain[1].data == "Block 1 Data", "Data in block 1 is incorrect"
assert blockchain.chain[2].data == "Block 2 Data", "Data in block 2 is incorrect"

# Test blockchain integrity
assert blockchain.is_valid(), "Blockchain integrity check failed"

# Test response to tampering
blockchain.chain[1].data = "Tampered Data"
assert not blockchain.is_valid(), "Blockchain did not detect tampering"

print("All tests passed.")
