class AST:
    """Abstract Syntax Tree class that represents the hierarchical structure of parsed code."""
    
    def __init__(self, root = None):
        """Initialize AST with an optional root node."""
        self.root = root

    def set_root(self, root):
        """Set the root node of the AST."""
        self.root = root

    def get_root(self):
        """Get the root node of the AST."""
        return self.root

    def standardize(self):
        """Standardize the AST by applying standardization rules starting from root."""
        if not self.root.is_standardized:
            self.root.standardize()

    def pre_order_traverse(self, node, i):
        """
        Perform pre-order traversal of the AST.
        Args:
            node: Current node to process
            i: Current indentation level
        """
        print("." * i + str(node.get_data()))
        for child in node.children:
            self.pre_order_traverse(child, i + 1)

    def print_ast(self):
        """Print the AST structure using pre-order traversal with indentation."""
        self.pre_order_traverse(self.get_root(), 0)
