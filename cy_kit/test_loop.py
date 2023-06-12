import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_kit




def cal_all():
    m=1

    @cy_kit.parallel_loop([1,2,300])
    def test_run(x):
        fx = x + 12+m


        lst =[]
        @cy_kit.parallel_loop(range(0,fx))
        def run2(x):
            return x+3

        lst+=[run2()]
        return lst

    ret =test_run()
    return ret


fx= cal_all()
print(fx)


