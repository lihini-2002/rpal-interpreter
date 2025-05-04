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

def lookup(name: str, env: List[dict]):
    for scope in reversed(env):
        if name in scope:
            return scope[name]
    raise Exception(f"Unbound variable: {name}")

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
            closure = Closure(index, param, E.copy())
            S.append(closure)

        elif instr == "gamma":
            rator = S.pop()
            rand = S.pop()

            if isinstance(rator, Closure):
                # New environment: add binding of param to rand
                new_env = rator.env + [{rator.param: rand}]
                # Push new environment marker
                C.appendleft(("env_pop",))  # pop it later
                E.append({rator.param: rand})
                # Push function body to control
                body = next(cs[1] for cs in control_structures if cs[0] == rator.index)
                for op in reversed(body):
                    C.appendleft(op)
            else:
                raise Exception(f"Cannot apply non-closure: {rator}")

        elif isinstance(instr, str) and instr.startswith("<ID:"):
            name = instr[4:-1]
            val = lookup(name, E)
            S.append(val)

        elif isinstance(instr, str) and instr.startswith("<INT:"):
            val = int(instr[5:-1])
            S.append(val)

        elif isinstance(instr, str) and instr in {"+", "-", "*", "/", "**", "gr", "ge", "eq", "ne", "&", "or", "not", "neg"}:
            apply_operator(instr, S)

        elif isinstance(instr, tuple) and instr[0] == "env_pop":
            E.pop()

        else:
            S.append(instr)

    return S[-1]  # Final result
