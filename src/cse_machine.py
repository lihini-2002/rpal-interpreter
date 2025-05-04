from collections import deque
from typing import List, Tuple, Any

# A Closure: (lambda index, param, env)
class Closure:
    def __init__(self, index: int, param: str, env: List[dict]):
        self.index = index
        self.param = param
        self.env = env  # Deep copy of the environment at closure creation

    def __repr__(self):
        return f"<Closure λ{self.index} {self.param}>"
    
class TupleValue:
    def __init__(self, elements):
        self.elements = elements

    def __repr__(self):
        return f"Tuple{self.elements}"


def lookup(name: str, env: List[dict]):
    # Normalize name like <ID:A> → A
    if name.startswith("<ID:") and name.endswith(">"):
        raw_name = name[4:-1]
    else:
        raw_name = name

    # Search in environment stack
    for scope in reversed(env):
        if raw_name in scope:
            return scope[raw_name]

    # Support built-in operators
    if raw_name in {"Order", "Print"}:
        return f"<ID:{raw_name}>"

    print("Env dump:", env)
    raise Exception(f"Unbound variable: {raw_name}")


def apply_operator(op: str, S: List):
    if op in {"+", "-", "*", "/", "**", "gr", "ge", "eq", "ne", "&", "or"}:
        b = S.pop()
        a = S.pop()
        S.append(eval_binary(op, a, b))
    elif op in {"not", "neg"}:
        a = S.pop()
        S.append(eval_unary(op, a))

def eval_binary(op: str, a, b):
    ops = {
        "+": a + b,
        "-": a - b,
        "*": a * b,
        "/": a // b,
        "**": a ** b,
        "gr": a > b,
        "ge": a >= b,
        "eq": a == b,
        "ne": a != b,
        "&": a and b,
        "or": a or b,
    }
    return ops[op]

def eval_unary(op: str, a):
    if op == "not":
        return not a
    if op == "neg":
        return -a

def evaluate(control: List, control_structures: List[Tuple[int, List]]):
    C = deque(control)
    S = []
    E = [{}]  # Environment: list of nested scopes (stack-like)

    while C:
        instr = C.popleft()

        if isinstance(instr, tuple) and instr[0] == "lambda":
            index, param = instr[1], instr[2]
            if param.startswith("<ID:") and param.endswith(">"):
                param = param[4:-1]
            closure = Closure(index, param, E.copy())
            S.append(closure)

        elif instr == "gamma":
            print("STACK BEFORE GAMMA:", S[-2:] if len(S) >= 2 else S)
            rand = S.pop()
            rator = S.pop()

            # Normalize rator if it's a built-in operator like <ID:Order>
            if isinstance(rator, str) and rator.startswith("<ID:") and rator.endswith(">"):
                raw_rator = rator[4:-1]
            else:
                raw_rator = rator

            # Handle built-in Order operator
            if raw_rator == "Order":
                # Try to handle nested tuple like Tuple[(tuple), index]
                if isinstance(rand, TupleValue) and len(rand.elements) == 2:
                    inner, idx = rand.elements
                    if isinstance(inner, TupleValue) and isinstance(idx, int):
                        S.append(len(inner.elements))
                        continue

                if isinstance(rand, TupleValue):
                    S.append(len(rand.elements))
                else:
                    raise Exception("Order applied to non-tuple")
                continue

            # Handle built-in Print operator
            if raw_rator == "Print":
                print(rand)
                S.append(rand)
                continue

            # Tuple projection: TupleValue applied to index
            if isinstance(rator, TupleValue) and isinstance(rand, int):
                if not (1 <= rand <= len(rator.elements)):
                    raise Exception(f"Tuple index out of bounds: {rand}")
                S.append(rator.elements[rand - 1])
                continue

            # Special case: Ystar combinator
            if raw_rator == "Ystar":
                if not isinstance(rand, Closure):
                    raise Exception("Ystar must be applied to a closure")
                
                # Create new closure with the same body and a fresh environment including a self-binding
                new_env = rand.env + [{rand.param: None}]  # Placeholder, will be updated
                recursive_closure = Closure(rand.index, rand.param, new_env)
                new_env[-1][rand.param] = recursive_closure  # self-binding

                S.append(recursive_closure)
                continue

            if isinstance(rator, Closure):
                # New environment: add binding of param to rand
                new_env = rator.env + [{rator.param: rand}]
                # Push new environment marker
                C.appendleft(("env_pop",))  # pop it later
                param_name = rator.param
                if param_name.startswith("<ID:") and param_name.endswith(">"):
                    param_name = param_name[4:-1]
                E.append({param_name: rand})
                print(f"Binding param {param_name} to value {rand}")
                print(f"Binding param {rator.param} to value {rand}")
                # Push function body to control
                body = next(cs[1] for cs in control_structures if cs[0] == rator.index)
                for op in reversed(body):
                    C.appendleft(op)
            else:
                print("DEBUG GAMMA TYPES:", type(rator), type(rand))
                raise Exception(f"Cannot apply non-closure: {rator} (trying to apply it to: {rand})")


        elif isinstance(instr, str) and instr.startswith("<ID:"):
            val = lookup(instr, E)  # Use the full string like "<ID:A>"
            S.append(val)

        elif isinstance(instr, str) and instr.startswith("<INT:"):
            val = int(instr[5:-1])
            S.append(val)

        elif isinstance(instr, str) and instr in {"+", "-", "*", "/", "**", "gr", "ge", "eq", "ne", "&", "or", "not", "neg"}:
            apply_operator(instr, S)

        elif isinstance(instr, tuple) and instr[0] == "env_pop":
            E.pop()
        
        elif isinstance(instr, str) and instr.startswith("tau "):
            count = int(instr.split()[1])
            elements = []
            for _ in range(count):
                elements.append(S.pop())
            elements.reverse()  # because stack pops right to left
            S.append(TupleValue(elements))

        else:
            S.append(instr)

    return S[-1]  # Final result
