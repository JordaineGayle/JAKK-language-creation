from Programming_Language_Making.project_parser import LambdaNode, VarNode, AppNode, parser


def reduce(expr, env=None):
    if env is None:
        env = {}

    if isinstance(expr, VarNode):
        return env.get(expr.name, expr)

    if isinstance(expr, LambdaNode):
        return expr

    if isinstance(expr, AppNode):
        func = reduce(expr.func, env)
        arg = reduce(expr.arg, env)
        if isinstance(func, LambdaNode):
            new_env = env.copy()
            new_env[func.var] = arg
            return reduce(func.body, new_env)
        else:
            return AppNode(func, arg)

    return expr


# Example usage
data = "#x.#y.xy"
result = parser.parse(data)
print("Initial expression:", result)
while True:
    new_result = reduce(result)
    if new_result == result:
        break
    result = new_result
    print("Reduced to:", result)
print("Normal form:", result)
