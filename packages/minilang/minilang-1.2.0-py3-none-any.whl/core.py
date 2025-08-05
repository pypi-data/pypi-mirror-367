import re

# ───── TOKENS ─────
TOKEN_REGEX = [
    ('NUMBER', r'\d+'),
    ('PRINT', r'print'),   # MUST come before 'ID'
    ('ID', r'[a-zA-Z_]\w*'),
    ('ASSIGN', r'='),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('MULT', r'\*'),
    ('DIV', r'/'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('SEMICOLON', r';'),
    ('WHITESPACE', r'[ \t\n]+'),
]

def tokenize(code):
    tokens = []
    pos = 0
    while pos < len(code):
        match = None
        for token_type, regex in TOKEN_REGEX:
            pattern = re.compile(regex)
            match = pattern.match(code, pos)
            if match:
                text = match.group(0)
                if token_type != 'WHITESPACE':
                    tokens.append((token_type, text))
                pos = match.end(0)
                break
        if not match:
            raise SyntaxError(f'Unknown character: {code[pos]}')
    return tokens

# ───── AST Nodes ─────
class Number:
    def __init__(self, value):
        self.value = int(value)

class Variable:
    def __init__(self, name):
        self.name = name

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Assignment:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class Print:
    def __init__(self, expr):
        self.expr = expr

class Call:
    def __init__(self, name):
        self.name = name


# ───── PARSER ─────
class Parser:
    def __init__(self, tokens): self.tokens, self.pos = tokens, 0

    def consume(self, expected_type=None):
        if self.pos < len(self.tokens):
            tok = self.tokens[self.pos]
            if expected_type and tok[0] != expected_type:
                raise SyntaxError(f'Expected {expected_type}, got {tok[0]}')
            self.pos += 1
            return tok
        raise SyntaxError('Unexpected end of input')

    def peek(self, offset=0):
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return None

    def parse(self):
        stmts = []
        while self.pos < len(self.tokens):
            stmts.append(self.statement())
        return stmts

    def statement(self):
        tok = self.peek()
        if tok[0] == 'ID':
            next_tok = self.peek(1)
            if next_tok and next_tok[0] == 'ASSIGN':
                return self.assignment()
            elif next_tok and next_tok[0] == 'LPAREN':
                return self.call_stmt()
            else:
                return self.call_shortcut()
        elif tok[0] == 'PRINT':
            return self.print_stmt()
        else:
            raise SyntaxError(f'Unexpected token: {tok}')

    def assignment(self):
        name = self.consume('ID')[1]
        self.consume('ASSIGN')
        expr = self.expr()
        self.consume('SEMICOLON')
        return Assignment(name, expr)

    def call_stmt(self):
        name = self.consume('ID')[1]
        self.consume('LPAREN')
        self.consume('RPAREN')
        self.consume('SEMICOLON')
        return Call(name)

    def call_shortcut(self):
        name = self.consume('ID')[1]
        self.consume('SEMICOLON')
        return Call(name)

    def print_stmt(self):
        self.consume('PRINT')
        expr = self.expr()
        self.consume('SEMICOLON')
        return Print(expr)

    def expr(self):
        left = self.term()
        while self.peek() and self.peek()[0] in ('PLUS', 'MINUS'):
            op = self.consume()[0]
            right = self.term()
            left = BinOp(left, op, right)
        return left

    def term(self):
        left = self.factor()
        while self.peek() and self.peek()[0] in ('MULT', 'DIV'):
            op = self.consume()[0]
            right = self.factor()
            left = BinOp(left, op, right)
        return left

    def factor(self):
        tok = self.consume()
        if tok[0] == 'NUMBER': return Number(tok[1])
        elif tok[0] == 'ID': return Variable(tok[1])
        elif tok[0] == 'LPAREN':
            expr = self.expr()
            self.consume('RPAREN')
            return expr
        else:
            raise SyntaxError(f'Unexpected token: {tok}')

# ───── INTERPRETER ─────
class Interpreter:
    def __init__(self):
        self.env = {}
        self.functions = {}

    def add_function(self, name, func):
        self.functions[name] = func

    def eval(self, node):
        if isinstance(node, list):
            for stmt in node:
                self.eval(stmt)
        elif isinstance(node, Number):
            return node.value
        elif isinstance(node, Variable):
            if node.name in self.env: return self.env[node.name]
            raise NameError(f'Undefined variable: {node.name}')
        elif isinstance(node, BinOp):
            left = self.eval(node.left)
            right = self.eval(node.right)
            if node.op == 'PLUS': return left + right
            if node.op == 'MINUS': return left - right
            if node.op == 'MULT': return left * right
            if node.op == 'DIV': return left // right
        elif isinstance(node, Assignment):
            value = self.eval(node.expr)
            self.env[node.name] = value
        elif isinstance(node, Print):
            print(self.eval(node.expr))
        elif isinstance(node, Call):
            if node.name in self.functions:
                return self.functions[node.name]()
            raise NameError(f'Function not defined: {node.name}')
        else:
            raise TypeError(f'Unknown node type: {node}')

# ───── PUBLIC API ─────
class MiniLang:
    def __init__(self):
        self.interpreter = Interpreter()

    def add_function(self, name, func):
        self.interpreter.add_function(name, func)

    def run(self, code):
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        self.interpreter.eval(ast)
        
if __name__=='__main__':
    lang = MiniLang()
    lang.add_function("greet", lambda: print("Hello from MiniLang!"))
    lang.run("""
    x = 3 * 4;
    print x;
    greet;
    """)
