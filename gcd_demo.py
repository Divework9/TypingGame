# 计算两个数的最大公约数
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a
# 测试最大公约数函数
def test_gcd():
    assert gcd(48, 18) == 6
    assert gcd(56, 98) == 14
    assert gcd(101, 10) == 1
    assert gcd(0, 5) == 5
    assert gcd(5, 0) == 5
    print("All tests passed.")  
if __name__ == "__main__":
    test_gcd()
    print(gcd(270, 192))
