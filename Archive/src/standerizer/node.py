class Node:
    """Represents a node in the Abstract Syntax Tree with data, depth, parent-child relationships, and standardization status."""
    
    def __init__(self):
        self.data = None
        self.depth = 0
        self.parent = None
        self.children = []
        self.is_standardized = False

    # Basic getters and setters
    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def get_degree(self):
        """Returns the number of children of this node."""
        return len(self.children)
    
    def get_children(self):
        return self.children

    def set_depth(self, depth):
        self.depth = depth

    def get_depth(self):
        return self.depth

    def set_parent(self, parent):
        self.parent = parent

    def get_parent(self):
        return self.parent

    def standardize(self):
        """
        Standardizes the AST node according to RPAL standardization rules.
        Applies different transformations based on node type (let, where, function_form, etc.).
        Each transformation converts the node into a standardized form using gamma and lambda nodes.
        """
        if not self.is_standardized:
            # First standardize all children
            for child in self.children:
                child.standardize()

            # Apply standardization rules based on node type
            if self.data == "let":
                # LET -> GAMMA transformation
                # Converts: LET(EQUAL(X,E), P) -> GAMMA(LAMBDA(X,P), E)
                temp1 = self.children[0].children[1]
                temp1.set_parent(self)
                temp1.set_depth(self.depth + 1)
                temp2 = self.children[1]
                temp2.set_parent(self.children[0])
                temp2.set_depth(self.depth + 2)
                self.children[1] = temp1
                self.children[0].set_data("lambda")
                self.children[0].children[1] = temp2
                self.set_data("gamma")

            elif self.data == "where":
                # WHERE -> LET transformation
                # Converts: WHERE(P, EQUAL(X,E)) -> LET(EQUAL(X,E), P)
                temp = self.children[0]
                self.children[0] = self.children[1]
                self.children[1] = temp
                self.set_data("let")
                self.standardize()

            elif self.data == "function_form":
                # FCN_FORM -> EQUAL transformation
                # Converts: FCN_FORM(P,V+,E) -> EQUAL(P,LAMBDA(V+,E))
                Ex = self.children[-1]
                current_lambda = NodeFactory.get_node_with_parent("lambda", self.depth + 1, self, [], True)
                self.children.insert(1, current_lambda)

                i = 2
                while self.children[i] != Ex:
                    V = self.children[i]
                    self.children.pop(i)
                    V.set_depth(current_lambda.depth + 1)
                    V.set_parent(current_lambda)
                    current_lambda.children.append(V)

                    if len(self.children) > 3:
                        current_lambda = NodeFactory.get_node_with_parent("lambda", current_lambda.depth + 1, current_lambda, [], True)
                        current_lambda.get_parent().children.append(current_lambda)

                current_lambda.children.append(Ex)
                self.children.pop(2)
                self.set_data("=")

            elif self.data == "lambda":
                # LAMBDA transformation
                # Converts: LAMBDA(V++,E) -> LAMBDA(V,LAMBDA(...))
                if len(self.children) > 2:
                    Ey = self.children[-1]
                    current_lambda = NodeFactory.get_node_with_parent("lambda", self.depth + 1, self, [], True)
                    self.children.insert(1, current_lambda)

                    i = 2
                    while self.children[i] != Ey:
                        V = self.children[i]
                        self.children.pop(i)
                        V.set_depth(current_lambda.depth + 1)
                        V.set_parent(current_lambda)
                        current_lambda.children.append(V)

                        if len(self.children) > 3:
                            current_lambda = NodeFactory.get_node_with_parent("lambda", current_lambda.depth + 1, current_lambda, [], True)
                            current_lambda.get_parent().children.append(current_lambda)

                    current_lambda.children.append(Ey)
                    self.children.pop(2)

            elif self.data == "within":
                # WITHIN -> EQUAL transformation
                # Converts: WITHIN(EQUAL(X1,E1), EQUAL(X2,E2)) -> EQUAL(X2,GAMMA(LAMBDA(X1,E2),E1))
                X1 = self.children[0].children[0]
                X2 = self.children[1].children[0]
                E1 = self.children[0].children[1]
                E2 = self.children[1].children[1]
                gamma = NodeFactory.get_node_with_parent("gamma", self.depth + 1, self, [], True)
                lambda_ = NodeFactory.get_node_with_parent("lambda", self.depth + 2, gamma, [], True)
                X1.set_depth(X1.get_depth() + 1)
                X1.set_parent(lambda_)
                X2.set_depth(X1.get_depth() - 1)
                X2.set_parent(self)
                E1.set_depth(E1.get_depth())
                E1.set_parent(gamma)
                E2.set_depth(E2.get_depth() + 1)
                E2.set_parent(lambda_)
                lambda_.children.append(X1)
                lambda_.children.append(E2)
                gamma.children.append(lambda_)
                gamma.children.append(E1)
                self.children.clear()
                self.children.append(X2)
                self.children.append(gamma)
                self.set_data("=")

            elif self.data == "@":
                # AT -> GAMMA transformation
                # Converts: @(E1,N,E2) -> GAMMA(GAMMA(N,E1),E2)
                gamma1 = NodeFactory.get_node_with_parent("gamma", self.depth + 1, self, [], True)
                e1 = self.children[0]
                e1.set_depth(e1.get_depth() + 1)
                e1.set_parent(gamma1)
                n = self.children[1]
                n.set_depth(n.get_depth() + 1)
                n.set_parent(gamma1)
                gamma1.children.append(n)
                gamma1.children.append(e1)
                self.children.pop(0)
                self.children.pop(0)
                self.children.insert(0, gamma1)
                self.set_data("gamma")

            elif self.data == "and":
                # AND -> EQUAL transformation
                # Converts: AND(EQUAL++) -> EQUAL(COMMA(X++), TAU(E++))
                comma = NodeFactory.get_node_with_parent(",", self.depth + 1, self, [], True)
                tau = NodeFactory.get_node_with_parent("tau", self.depth + 1, self, [], True)

                for equal in self.children:
                    equal.children[0].set_parent(comma)
                    equal.children[1].set_parent(tau)
                    comma.children.append(equal.children[0])
                    tau.children.append(equal.children[1])

                self.children.clear()
                self.children.append(comma)
                self.children.append(tau)
                self.set_data("=")

            elif self.data == "rec":
                # REC -> EQUAL transformation
                # Converts: REC(EQUAL(X,E)) -> EQUAL(X,GAMMA(YSTAR,LAMBDA(X,E)))
                X = self.children[0].children[0]
                E = self.children[0].children[1]
                F = NodeFactory.get_node_with_parent(X.get_data(), self.depth + 1, self, X.children, True)
                G = NodeFactory.get_node_with_parent("gamma", self.depth + 1, self, [], True)
                Y = NodeFactory.get_node_with_parent("<Y*>", self.depth + 2, G, [], True)
                L = NodeFactory.get_node_with_parent("lambda", self.depth + 2, G, [], True)

                X.set_depth(L.depth + 1)
                X.set_parent(L)
                E.set_depth(L.depth + 1)
                E.set_parent(L)
                L.children.append(X)
                L.children.append(E)
                G.children.append(Y)
                G.children.append(L)
                self.children.clear()
                self.children.append(F)
                self.children.append(G)
                self.set_data("=")

            self.is_standardized = True


class NodeFactory:
    """Factory class for creating Node instances with different configurations."""
    
    def __init__(self):
        pass

    @staticmethod
    def get_node(data, depth):
        """Creates a basic node with given data and depth."""
        node = Node()
        node.set_data(data)
        node.set_depth(depth)
        node.children = []
        return node

    @staticmethod
    def get_node_with_parent(data, depth, parent, children, is_standardized):
        """Creates a node with complete configuration including parent, children, and standardization status."""
        node = Node()
        node.set_data(data)
        node.set_depth(depth)
        node.set_parent(parent)
        node.children = children
        node.is_standardized = is_standardized
        return node