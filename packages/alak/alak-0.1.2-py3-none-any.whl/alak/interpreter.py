"""
Developer: leetz-kowd
Project: alak
Date: 2025-07-21
Version: 1.0.0
"""
import random
import re
from lark import Lark, Transformer
class AlakInterpreter(Transformer):
    def __init__(self):
        self.vars = {}
        self.funcs = {}

    def start(self, items):
        for stmt in items:
            if callable(stmt):
                stmt()

    def statement(self, items):
        return items[0]

    def print_stmt(self, items):
        return lambda: print(items[0]())

    def assign_stmt(self, items):
        var_name = str(items[0])
        expr_fn = items[1]
        return lambda: self.vars.__setitem__(var_name, expr_fn())

    def var(self, name):
        return lambda: self.vars.get(str(name[0]), 0)

    def number(self, n):
        return lambda: float(n[0])

    def string(self, s):
        raw_string = s[0][1:-1]

        def interpolate():
            def eval_expr(expr):
                try:
                    return eval(expr, {}, self.vars)
                except Exception:
                    return f"{{{expr}}}"

            return re.sub(r'\{([^}]+)\}', lambda m: str(eval_expr(m.group(1))), raw_string)

        return interpolate

    
    # Boolean Values
    def false(self, _):
        return lambda: False

    def true(self, _):
        return lambda: True

    # Arithmetic Operations
    def add(self, items):
        return lambda: items[0]() + items[1]()

    def sub(self, items):
        return lambda: items[0]() - items[1]()

    def mul(self, items):
        return lambda: items[0]() * items[1]()

    def div(self, items):
        return lambda: items[0]() / items[1]()

    def comp_op(self, tokens):
        if not tokens:
            print(f"comp_op received no tokens {tokens}")
            return None
        return tokens[0].value


    def condition(self, items):
        left, op, right = items
        return lambda: (
            left() == right() if op == "==" else
            left() != right() if op == "!=" else
            left() > right() if op == ">" else
            left() < right()
        )

    def if_stmt(self, items):
        condition_fn = items[0]
        body = items[1:]
        return lambda: [stmt() for stmt in body] if condition_fn() else None

    def while_stmt(self, items):
        condition_fn = items[0]
        body = items[1:]
        def loop():
            while condition_fn():
                for stmt in body:
                    stmt()
        return loop

    # Function Definitions and Calls
    def func_def(self, items):
        name = str(items[0])
        param_names = [str(p) for p in items[1].children] if hasattr(items[1], 'children') else []
        body = items[2:] if param_names else items[1:]
        self.funcs[name] = (param_names, body)
        return lambda: None

    def func_call(self, items):
        name = str(items[0])
        args = items[1].children if len(items) > 1 and hasattr(items[1], 'children') else []

        def call():
            if name not in self.funcs:
                raise Exception(f"Undefined function '{name}'")

            param_names, body = self.funcs[name]
            if len(param_names) != len(args):
                raise Exception(f"Function '{name}' expected {len(param_names)} arguments, got {len(args)}")

            # Save current variable scope
            old_vars = self.vars.copy()

            # Bind args to params
            for pname, pval in zip(param_names, args):
                self.vars[pname] = pval()

            # Run function body
            for stmt in body:
                stmt()

            # Restore scope
            self.vars = old_vars

        return call
    
    
    # Array and List Handling
    def expr_list(self, items):
        return [item for item in items]
    
    def list_literal(self, items):
        if items:
            if isinstance(items[0], list):
                return lambda: [item() for item in items[0]]
            else:
                return lambda: [item() for item in items]
        return lambda: []
    
    def index_access(self, items):
        var_name = str(items[0])
        index_fn = items[1]
        return lambda: self.vars[var_name][int(index_fn())]
    
    
    # Hangover Statement (for loop)
    def hangover_stmt(self, items):
        init_fn = items[0]      # assign_stmt
        condition_fn = items[1] # condition
        step_fn = items[2]      # step_expr
        body = items[3:]        # statements

        def loop():
            init_fn()
            while condition_fn():
                for stmt in body:
                    stmt()
                step_fn()

        return loop

    def step_expr(self, items):
        var_name = str(items[0])
        value_fn = items[1]
        return lambda: self.vars.__setitem__(var_name, value_fn())

    def assign_expr(self, items):
        var_name = str(items[0])
        expr_fn = items[1]
        return lambda: self.vars.__setitem__(var_name, expr_fn())
    
    # Exit Program
    def patay_stmt(self, _):
        def exit_program():
            print("Exiting AlakLang... Patay na.")
            raise SystemExit()
        return exit_program
    
    
    # Ambag function get input from user
    def ambag_expr(self, items):
        prompt_fn = items[0]
        return lambda: input(prompt_fn())
    
    # Length of word
    def haba_expr(self, items):
        string_fn = items[0]
        return lambda: len(string_fn())

    # First letter uppercase
    def taas_expr(self, items):
        string_fn = items[0]
        return lambda: str(string_fn()).upper()
    
    # tropa.nahilo(x)    // push x to tropa array 
    def method_call_expr(self, items):
        obj_name = str(items[0])     # e.g. tropa
        method_name = str(items[1])  # e.g. nahilo
        args = items[2].children if len(items) > 2 and hasattr(items[2], 'children') else []

        def call():
            target = self.vars.get(obj_name)
            if not isinstance(target, list):
                raise Exception(f"'{obj_name}' is not a list")

            if method_name == "nahilo":
                if len(args) != 1:
                    raise Exception("nahilo() expects 1 argument")
                target.append(args[0]())
            else:
                raise Exception(f"Unknown method '{method_name}'")

        return call
    
    # Define custom function call here e.g: lagok()
    def method_call(self, items):
        method_name = str(items[0])
        args = items[1:] if len(items) > 1 else []

        # method logic here
        if method_name == "lagok":
            if len(args) == 2:
                return random.randint(args[0], args[1])
            elif len(args) == 1 and isinstance(args[0], list):
                return random.choice(args[0])
            else:
                raise ValueError("lagok() needs 2 numbers or a list")
        # Add more methods here
        else:
            raise Exception(f"Unknown method: {method_name}")









