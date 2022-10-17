from typing import List


class ParserException(Exception):
    ...


class StateException(Exception):
    ...


class State:
    def __init__(self, rem: dict = None):
        if rem is None:
            rem = {}
        self.rem = rem

    def set(self, pos, val):
        if pos not in self.rem:
            self.rem[pos] = val
        self.rem[pos] = min(self.rem[pos], val)

    def get_items(self):
        return self.rem.items()

    def concat(self, s: 'State', k):
        res = State()
        for rem, val in self.get_items():
            for rem_s, val_s in s.get_items():
                res.set((rem + rem_s) % k, val + val_s)
        return res

    def plus(self, s: 'State'):
        res = State()
        for rem, val in self.get_items():
            res.set(rem, val)
        for rem, val in s.get_items():
            res.set(rem, val)
        return res

    def klini(self, k) -> 'State':
        if not self.rem.keys():
            raise StateException('Invalid Klini. Empty expression')
        items = ['INF' for i in range(k)]
        for rem, val in self.get_items():
            for cnt in range(0, k):
                weight = (rem * cnt) % k
                cost = val * cnt
                if items[weight] == 'INF' or items[weight] > cost:
                    items[weight] = cost

        dp = [['INF' for i in range(k)] for j in range(len(items))]
        for weight, cost in enumerate(items):
            dp[weight][weight] = cost

        for weight in range(1, k):
            i = weight
            cost = items[weight]
            for w in range(k):
                if dp[i - 1][w] != 'INF':
                    dp[i][w] = dp[i - 1][w]
            if cost != 'INF':
                for w in range(k):
                    old_w = w - weight
                    if old_w < 0:
                        old_w += k
                    if dp[i - 1][old_w] != 'INF':
                        if dp[i][w] == 'INF' or dp[i][w] > dp[i - 1][old_w] + cost:
                            dp[i][w] = dp[i - 1][old_w] + cost

        res = State()
        for i in range(len(items)):
            for j in range(k):
                if dp[i][j] != 'INF':
                    res.set(j % k, dp[i][j])
        return res

    def get_ans(self, pos: int):
        if pos not in self.rem:
            return 'INF'
        return self.rem[pos]


class Parser:
    def __init__(self, regex, k):
        self.regex = regex
        self.k = k
        self.final_state = None

    def _calc(self):
        stack: List[State] = []
        regex = self.regex

        for c in regex:
            try:
                if c in 'abc':
                    stack.append(State({1: 1}))
                elif c == '1':
                    stack.append(State({0: 0}))
                elif c == '*':
                    current_state = stack.pop()
                    stack.append(current_state.klini(self.k))
                elif c == '+':
                    first_state = stack.pop()
                    second_state = stack.pop()
                    stack.append(first_state.plus(second_state))
                elif c == '.':
                    first_state = stack.pop()
                    second_state = stack.pop()
                    stack.append(first_state.concat(second_state, self.k))
            except Exception as e:
                raise ParserException(f"Error occurred while parsing regex expression: {repr(e)}")

        if len(stack) == 1:
            return stack[0]
        else:
            raise ParserException("Error occurred while parsing regex expression")

    def get_answer(self, pos: int):
        if self.final_state is None:
            self.final_state = self._calc()
        return self.final_state.get_ans(pos)
