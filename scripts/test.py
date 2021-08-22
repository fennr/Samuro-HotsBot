from functools import reduce
def f(s): return len(reduce(lambda acc, x: acc[:-1] if acc and acc[-1]+x in ('{}', '[]', '()') else acc+x, s))

test_bad  = '{[(]}'
test_good = '{[()]}'

print(f(test_bad))
print(f(test_good))