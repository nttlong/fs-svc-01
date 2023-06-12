import cy_kit
@cy_kit.parallel_loop([1,2,3])
def run(x):
    print(x)
run()