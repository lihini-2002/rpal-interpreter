from .node import NodeFactory
from .ast import AST

#converting nodes from parser

class ASTFactory:
    """Factory class for creating Abstract Syntax Trees from parsed data."""
    
    def __init__(self):
        pass

    def get_abstract_syntax_tree(self, data):
        """
        Converts parsed data into an AST structure.
        Args:
            data: List of strings where each string represents a node with dots indicating depth
        Returns:
            AST object with properly structured nodes
        """
        root = NodeFactory.get_node(data[0], 0)  # Create root node
        previous_node = root
        current_depth = 0

        for s in data[1:]:
            # Calculate node depth by counting leading dots
            i = 0
            d = 0
            while s[i] == '.':
                d += 1
                i += 1

            current_node = NodeFactory.get_node(s[i:], d)

            # Handle node relationships based on depth
            if current_depth < d:
                # Add as child if deeper than previous node
                previous_node.children.append(current_node)
                current_node.set_parent(previous_node)  
            else:
                # Find appropriate parent at same depth
                while previous_node.get_depth() != d:
                    previous_node = previous_node.get_parent()
                previous_node.get_parent().children.append(current_node)  
                current_node.set_parent(previous_node.get_parent())  

            previous_node = current_node
            current_depth = d

        return AST(root)  
