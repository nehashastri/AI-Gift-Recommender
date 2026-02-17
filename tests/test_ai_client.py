from lib.ai_client import AIClient, cosine_similarity

ai = AIClient()

# Test embeddings
emb1 = ai.get_embedding("chocolate lover")
emb2 = ai.get_embedding("loves chocolate")
emb3 = ai.get_embedding("birthday party")

print(
    f"chocolate lover vs loves chocolate: {cosine_similarity(emb1, emb2)}"
)  # Should be high
print(
    f"chocolate lover vs birthday party: {cosine_similarity(emb1, emb3)}"
)  # Should be lower

# Test chat
response = ai.chat_completion(
    [{"role": "user", "content": "Say hello in JSON format with a 'message' field"}],
    response_format={"type": "json_object"},
)
print(response)
