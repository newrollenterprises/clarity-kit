def levenshtein_distance(s1, s2):
    # Initialize matrix of size (len(s1)+1) x (len(s2)+1)
    rows = len(s1) + 1
    cols = len(s2) + 1
    distance_matrix = [[0 for x in range(cols)] for y in range(rows)]

    # Fill the first row and column with indices
    for i in range(1, rows):
        distance_matrix[i][0] = i
    for j in range(1, cols):
        distance_matrix[0][j] = j

    # Fill the matrix with Levenshtein distances
    for i in range(1, rows):
        for j in range(1, cols):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            distance_matrix[i][j] = min(
                distance_matrix[i - 1][j] + 1,    # Deletion
                distance_matrix[i][j - 1] + 1,    # Insertion
                distance_matrix[i - 1][j - 1] + cost  # Substitution
            )

    # The Levenshtein distance is the value in the bottom-right cell
    return distance_matrix[-1][-1]

def similarity_score(s1, s2):
    # Calculate Levenshtein distance
    distance = levenshtein_distance(s1, s2)

    # Compute the maximum possible distance (which is the length of the longer string)
    max_len = max(len(s1), len(s2))

    # Calculate the similarity score
    similarity = (1 - distance / max_len) * 100  # Similarity as a percentage

    return similarity

# Example usage
string1 = "kitten"
string2 = "sitting"

distance = levenshtein_distance(string1, string2)
similarity = similarity_score(string1, string2)

print(f"Levenshtein Distance: {distance}")
print(f"Similarity Score: {similarity:.2f}%")

def test_levenshtein_distance():
    # Test 1: Identical strings
    assert levenshtein_distance("abc", "abc") == 0

    # Test 2: Completely different strings
    assert levenshtein_distance("abc", "xyz") == 3

    # Test 3: One string is empty
    assert levenshtein_distance("", "abc") == 3

    # Test 4: Single character strings (same)
    assert levenshtein_distance("a", "a") == 0

    # Test 5: Single character strings (different)
    assert levenshtein_distance("a", "b") == 1

    # Test 6: One string is a prefix of the other
    assert levenshtein_distance("abc", "abcd") == 1

    # Test 7: One string is a suffix of the other
    assert levenshtein_distance("abc", "dabc") == 1

    # Test 8: Transposed characters
    assert levenshtein_distance("abcd", "abdc") == 2

    # Test 9: Insertion and deletion
    assert levenshtein_distance("kitten", "sitting") == 3

    # Test 10: Case sensitivity
    assert levenshtein_distance("abc", "ABC") == 3

    # Test 11: Large strings with minor differences
    assert levenshtein_distance("thisisaverylongstring", "thisisaverylongstrung") == 1

    # Test 12: Reversed strings
    assert levenshtein_distance("abcdef", "fedcba") == 6

    # Test 13: Strings with spaces
    assert levenshtein_distance("hello world", "hello  world") == 1

    # Test 14: Strings with special characters
    assert levenshtein_distance("hello!", "hello?") == 1

    # Test 15: Strings with numbers
    assert levenshtein_distance("123", "321") == 2

    # Test 16: Completely empty strings
    assert levenshtein_distance("", "") == 0

    # Test 17: Strings with repeated characters
    assert levenshtein_distance("aaa", "aaaa") == 1

    # Test 19: Substring
    assert levenshtein_distance("abc", "bc") == 1

    # Test 20: Very similar strings
    assert levenshtein_distance("abcdef", "abcdff") == 1

def test_similarity_score():
    # Test 1: Identical strings
    assert similarity_score("abc", "abc") == 100.0

    # Test 2: Completely different strings
    assert similarity_score("abc", "xyz") == 0.0

    # Test 3: One string is empty
    assert similarity_score("", "abc") == 0.0

    # Test 4: Single character strings (same)
    assert similarity_score("a", "a") == 100.0

    # Test 5: Single character strings (different)
    assert similarity_score("a", "b") == 0.0

    # Test 6: One string is a prefix of the other
    assert similarity_score("abc", "abcd") == 75.0

    # Test 7: One string is a suffix of the other
    assert similarity_score("abc", "dabc") == 75.0

    # Test 8: Transposed characters
    assert similarity_score("abcd", "abdc") == 50.0

    # Test 10: Case sensitivity
    assert similarity_score("abc", "ABC") == 0.0

    # Test 12: Reversed strings
    assert similarity_score("abcdef", "fedcba") == 0.0

    # Test 16: Completely empty strings
    assert similarity_score("", "") == 100.0

    # Test 17: Strings with repeated characters
    assert similarity_score("aaa", "aaaa") == 75.0

# Run the tests
test_levenshtein_distance()
test_similarity_score()

print("All tests passed!")