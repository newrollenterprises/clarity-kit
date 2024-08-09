import Levenshtein

def levenshtein_similarity(text1, text2):
    """
    Calculate the Levenshtein similarity between two texts.
    
    Args:
    text1 (str): The first text.
    text2 (str): The second text.
    
    Returns:
    float: The similarity score between 0 and 1.
    """
    lev_distance = Levenshtein.distance(text1, text2)
    similarity = 1 - lev_distance / max(len(text1), len(text2))
    return similarity

# Sample texts
text1 = "dollar"
text2 = "dollar"

# Calculate similarity
similarity_score = levenshtein_similarity(text1, text2)

print(f"Levenshtein Similarity: {similarity_score}")