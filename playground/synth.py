from sentence_transformers import SentenceTransformer, util

# Mean Pooling - Take attention mask into account for correct averaging


# def mean_pooling(model_output, attention_mask):
#     # First element of model_output contains all token embeddings
#     token_embeddings = model_output[0]
#     input_mask_expanded = attention_mask.unsqueeze(
#         -1).expand(token_embeddings.size()).float()
#     return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
# # Sentences we want sentence embeddings for
# sentences = ['This is an example sentence', 'Each sentence is converted']
# # Load model from HuggingFace Hub
# tokenizer = AutoTokenizer.from_pretrained(
#     'sentence-transformers/all-MiniLM-L12-v2')
# model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L12-v2')
# # Tokenize sentences
# encoded_input = tokenizer(sentences, padding=True,
#                           truncation=True, return_tensors='pt')
# # Compute token embeddings
# with torch.no_grad():
#     model_output = model(**encoded_input)
# # Perform pooling
# sentence_embeddings = mean_pooling(
#     model_output, encoded_input['attention_mask'])
# # Normalize embeddings
# sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
# print("Sentence embeddings:")
# print(sentence_embeddings)


model = SentenceTransformer('all-mpnet-base-v2')
# Our sentences we like to encode
sentences = ['This framework generates embeddings for each input sentence',
             'Sentences are passed as a list of string.',
             'The quick brown fox jumps over the lazy dog.']
# Sentences are encoded by calling model.encode()
embeddings = model.encode(sentences)
# Print the embeddings
for sentence, embedding in zip(sentences, embeddings):
    print("Sentence:", sentence)
    print("Embedding:", embedding)
    print("")


query_embedding = model.encode('How big is London')
passage_embedding = model.encode(['London has 9,787,426 inhabitants at the 2011 census',
                                  'London is known for its finacial district'])
print("Similarity:", util.dot_score(query_embedding, passage_embedding))
