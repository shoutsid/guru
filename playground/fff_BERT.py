from transformers import BertModel, BertConfig, BertTokenizer
import torch
import torch.nn as nn
import torch.nn.functional as F


class ConditionalMatrixMultiplication(nn.Module):
    def __init__(self, input_dim, output_dim, depth):
        super().__init__()
        self.depth = depth
        self.weight_matrices = nn.ParameterList(
            [nn.Parameter(torch.randn(input_dim, output_dim)) for _ in range(2**depth - 1)])

    def forward(self, x):
        logits = torch.zeros(
            x.size(0), self.weight_matrices[0].size(0), device=x.device)
        for i in range(x.size(0)):
            node_index = 0
            for depth in range(self.depth):
                weight_matrix = self.weight_matrices[node_index]
                logit = torch.matmul(x[i], weight_matrix)
                # Summing the logit tensor to get a scalar value
                next_direction = (logit.sum() > 0).long().item()
                node_index = 2 * node_index + 1 + next_direction
                if node_index >= len(self.weight_matrices):
                    break  # Prevent index out of range
            logits[i] = logit
        return logits


class FastFeedforwardNetwork(nn.Module):
    def __init__(self, input_dim, output_dim, depth):
        super().__init__()
        self.cmm = ConditionalMatrixMultiplication(
            input_dim, output_dim, depth)

    def forward(self, x):
        logits = self.cmm(x)
        output = F.relu(logits)
        return output


class UltraFastBERT(BertModel):
    def __init__(self, config):
        super().__init__(config)
        # Replace BERT's feedforward layers with FastFeedforwardNetwork
        for layer in self.encoder.layer:
            layer.output.dense = FastFeedforwardNetwork(
                config.hidden_size, config.hidden_size, depth=3)  # Example depth


if __name__ == "__main__":
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    sample_text = "Hello, this is a test sentence for UltraFastBERT."
    inputs = tokenizer(sample_text, return_tensors="pt")

    # Assuming CMM and FastFeedforwardNetwork are defined as before
    # Initialize test modules
    input_dim = output_dim = 768  # Typical size for BERT models
    depth = 3  # Example depth, adjust as needed
    cmm = ConditionalMatrixMultiplication(input_dim, output_dim, depth)
    ffn = FastFeedforwardNetwork(input_dim, output_dim, depth)

    # Test CMM
    with torch.no_grad():
        bert_model = BertModel.from_pretrained('bert-base-uncased')
        embeddings = bert_model.embeddings(inputs['input_ids'])

    cmm_output = cmm(embeddings)
    print("CMM Output Shape:", cmm_output.shape)
    # # Test FFN
    # ffn_output = ffn(inputs['input_ids'])
    # print("FFN Output Shape:", ffn_output.shape)

    # Example usage
    ultrafast_bert = UltraFastBERT(BertConfig())
    # Test UltraFastBERT
    with torch.no_grad():
        outputs = ultrafast_bert(**inputs)
        print("UltraFastBERT Output Shape:", outputs.last_hidden_state.shape)
