from typing import Callable


class Test:
    Name: str
    Name1: int


# fx: Callable[[Test], bool] = lambda x: next(yield x)
# v = fx([1,3,5])
import ast

vx = ast.parse("a.contains(1)*b")
print(vx)


def __parse_compare__(x:ast.BinOp):
    pass


def __parse__(x):
    if isinstance(x,ast.Expr):
        return __parse__(x.value)
    if isinstance(x,ast.Compare):
        op = __parse__(x.ops[0])
        left = __parse__(x.left)

    if isinstance(x,ast.Eq):
        return "$eq"

    raise NotImplemented()


def to_b_tree(str_expr: str,args):
    _txt_ = str_expr
    for i in range(args):
        _txt_ = _txt_.replace("{"+i.__str__()+"}",f"__params__.p{i}")
    fx = ast.parse(_txt_)
    __parse__(fx.body[0])

to_b_tree("data_item.markdelete=={0}",True)