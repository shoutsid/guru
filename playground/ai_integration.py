import json


class AIProcessor:
    def __init__(self):
        # Initialize AI processor with necessary parameters
        pass

    def process_instruction(self, instruction):
        # For demonstration, a simple decision-making process based on instruction content
        result = {"instruction": instruction, "outcome": "Processed"}
        return result


class BlockchainInterface:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def send_instruction_to_ai(self, instruction):
        # Convert instruction to a format that AI can process
        ai_processor = AIProcessor()
        result = ai_processor.process_instruction(instruction)
        self.record_ai_result_on_blockchain(result)

    def record_ai_result_on_blockchain(self, result):
        # Record the result of AI processing on the blockchain
        result_data = json.dumps(result)
        self.blockchain.add_block(result_data)


if __name__ == "__main__":
    from blockchain import Blockchain

    # Create blockchain instance
    blockchain = Blockchain()
    # Example usage
    # Assuming 'blockchain' is an instance of the Blockchain class from previous steps
    blockchain_interface = BlockchainInterface(blockchain)
    instruction = "Sample AI Instruction"
    print(blockchain_interface.send_instruction_to_ai(instruction))
