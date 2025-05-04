from src.rpal_ast import ASTNode

class Standardizer:
    def standardize(self, node):
        if node is None:
            return None

        node.left = self.standardize(node.left)
        node.right = self.standardize(node.right)

        if node.label == "let":
            return self._standardize_let(node)
        elif node.label == "where":
            return self._standardize_where(node)
        elif node.label == "function_form":
            return self._standardize_function_form(node)
        elif node.label == "lambda":
            return self._standardize_lambda(node)
        elif node.label == "within":
            return self._standardize_within(node)
        elif node.label == "@":
            return self._standardize_at(node)
        elif node.label == "and":
            return self._standardize_and(node)
        elif node.label == "rec":
            return self._standardize_rec(node)

        return node

    def _copy_subtree(self, node):
        if node is None:
            return None
        new_node = ASTNode(node.label)
        new_node.left = self._copy_subtree(node.left)
        new_node.right = self._copy_subtree(node.right)
        return new_node

    def _standardize_let(self, node):
        equal = node.left
        expr = self._copy_subtree(equal.right)
        var = self._copy_subtree(equal.left)

        lambda_node = ASTNode("lambda")
        lambda_node.left = var
        var.right = expr

        gamma_node = ASTNode("gamma")
        gamma_node.left = lambda_node
        lambda_node.right = self._copy_subtree(node.left.right)

        return gamma_node

    def _standardize_where(self, node):
        expr = self._copy_subtree(node.left)
        equal = self._copy_subtree(expr.right)
        let_node = ASTNode("let")
        let_node.left = equal
        equal.right = expr
        return self._standardize_let(let_node)

    def _standardize_function_form(self, node):
        # Traverse all children
        children = []
        curr = node.left  # Start from first child (e.g., <ID:Sum>)
        while curr:
            children.append(self._copy_subtree(curr))
            curr = curr.right

        name = children[0]
        params = children[1:-1]
        expr = children[-1]

        # Build nested lambdas
        current_lambda = ASTNode("lambda")
        current_lambda.left = params[0]
        temp = current_lambda

        for param in params[1:]:
            new_lambda = ASTNode("lambda")
            param_node = param
            temp.left.right = new_lambda
            new_lambda.left = param_node
            temp = new_lambda

        temp.left.right = expr  # Attach the expression at the end

        equal = ASTNode("=")
        equal.left = name
        name.right = current_lambda

        return equal

    def _standardize_lambda(self, node):
        param = self._copy_subtree(node.left)
        expr = param
        while expr.right:
            expr = expr.right

        expr = self._copy_subtree(expr)

        current_lambda = ASTNode("lambda")
        current_lambda.left = param
        temp = current_lambda

        param = param.right
        while param and param.label != expr.label:
            new_lambda = ASTNode("lambda")
            new_lambda.left = self._copy_subtree(param)
            temp.left.right = new_lambda
            temp = new_lambda
            param = param.right

        temp.left.right = expr

        return current_lambda

    def _standardize_within(self, node):
        equal1 = node.left
        equal2 = equal1.right
        x1 = self._copy_subtree(equal1.left)
        e1 = self._copy_subtree(x1.right)
        x2 = self._copy_subtree(equal2.left)
        e2 = self._copy_subtree(x2.right)

        lambda_node = ASTNode("lambda")
        lambda_node.left = x1
        x1.right = e2

        gamma_node = ASTNode("gamma")
        gamma_node.left = lambda_node
        lambda_node.right = e1

        equal_node = ASTNode("=")
        equal_node.left = x2
        x2.right = gamma_node

        return equal_node

    def _standardize_at(self, node):
        e1 = self._copy_subtree(node.left)
        n = self._copy_subtree(e1.right)
        e2 = self._copy_subtree(n.right)

        gamma1 = ASTNode("gamma")
        gamma1.left = n
        n.right = e1

        gamma2 = ASTNode("gamma")
        gamma2.left = gamma1
        gamma1.right = e2

        return gamma2

    def _standardize_and(self, node):
        comma = ASTNode(",")
        tau = ASTNode("tau")
        comma_curr = comma
        tau_curr = tau

        equal = node.left
        while equal:
            x = self._copy_subtree(equal.left)
            e = self._copy_subtree(x.right)

            if comma_curr.left:
                comma_curr.right = ASTNode(",")
                comma_curr = comma_curr.right
            comma_curr.left = x

            if tau_curr.left:
                tau_curr.right = ASTNode("tau")
                tau_curr = tau_curr.right
            tau_curr.left = e

            equal = equal.right

        equal_node = ASTNode("=")
        equal_node.left = comma
        comma.right = tau

        return equal_node

    def _standardize_rec(self, node):
        equal = node.left
        x = self._copy_subtree(equal.left)
        e = self._copy_subtree(x.right)

        lambda_node = ASTNode("lambda")
        lambda_node.left = self._copy_subtree(x)
        lambda_node.left.right = self._copy_subtree(e)

        ystar = ASTNode("<Y*>")

        gamma_node = ASTNode("gamma")
        gamma_node.left = ystar
        ystar.right = lambda_node

        equal_node = ASTNode("=")
        equal_node.left = self._copy_subtree(x)
        equal_node.left.right = gamma_node

        return equal_node
