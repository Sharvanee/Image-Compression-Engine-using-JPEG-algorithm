from bitarray import bitarray

class HuffmanNode:
    def __init__(self, symbol=None, frequency=None):
        self.symbol = symbol  # Store symbol as integer (positive or negative)
        self.frequency = frequency
        self.left = None
        self.right = None

    def __lt__(self, other):
        # Compare nodes by frequency (used for sorting)
        return self.frequency < other.frequency

    def traverse(self, prefix=bitarray(), code_table=None):
        """
        Recursively traverse the Huffman tree to build the code table given
        prefix (bitarray): current prefix code (binary sequence) and code_table (dict): dictionary to store symbol-to-code mappings.
        """
        if code_table is None:
            code_table = {}

        if self.left is None and self.right is None:  # Leaf node
            code_table[self.symbol] = prefix
        else:
            if self.left:
                self.left.traverse(prefix + bitarray('0'), code_table)
            if self.right:
                self.right.traverse(prefix + bitarray('1'), code_table)

        return code_table

def extract_probs(array):
    """
    Returns a dictionary of symbols to their probabilities.
    """
    # Count occurrences of each symbol
    symbols_dict = {}
    for symbol in array:
        symbols_dict[symbol] = symbols_dict.get(symbol, 0) + 1

    # Calculate probabilities
    total_length = len(array)
    for symbol in symbols_dict:
        symbols_dict[symbol] /= total_length
    
    return symbols_dict

def generate_huffman_tree(array):
    """
    Generates the Huffman tree for a given array of symbols and returns the root node of the Huffman tree
    """
    # Extract probabilities and create nodes
    symbols_dict = extract_probs(array)
    sorted_nodes = [HuffmanNode(symbol=symbol, frequency=symbols_dict[symbol]) for symbol in symbols_dict]

    # Build the tree
    while len(sorted_nodes) > 1:
        # Sort nodes by frequency
        sorted_nodes = sorted(sorted_nodes)

        # Merge the two smallest nodes
        smallest, second_smallest = sorted_nodes[0], sorted_nodes[1]
        new_node = HuffmanNode(symbol=None, frequency=smallest.frequency + second_smallest.frequency)
        new_node.left = smallest
        new_node.right = second_smallest

        # Replace the two smallest nodes with the new node
        sorted_nodes = sorted_nodes[2:]
        sorted_nodes.append(new_node)

    # Return the root of the Huffman tree
    return sorted_nodes[0]

def encode_huffman(symbols, huffman_dict):
    """
    Encodes a sequence of symbols using a dictionary mapping symbols to their Huffman codes (bitarray objects) into a single Huffman-encoded bitarray.
    """
    encoded_stream = bitarray()
    for symbol in symbols:
        if symbol not in huffman_dict:
            raise ValueError(f"Symbol {symbol} not found in Huffman dictionary.")
        encoded_stream.extend(huffman_dict[symbol])  # Append the corresponding bitarray for the symbol
    return encoded_stream

def decode_huffman(encoded_string, huffman_dict):
    """
    Decodes a Huffman-encoded bitarray using dictionary mapping symbols to their Huffman codes (bitarray objects) into the original sequence of symbols.
    """
    # Create a reverse mapping from Huffman codes (as strings) to symbols
    reverse_dict = {code.to01(): symbol for symbol, code in huffman_dict.items()}

    decoded_symbols = []
    buffer = ""
    for bit in encoded_string:
        buffer += str(bit)  # Convert bit (int) to string before concatenation
        if buffer in reverse_dict:
            decoded_symbols.append(reverse_dict[buffer])
            buffer = ""  # Reset buffer after finding a match

    return decoded_symbols

