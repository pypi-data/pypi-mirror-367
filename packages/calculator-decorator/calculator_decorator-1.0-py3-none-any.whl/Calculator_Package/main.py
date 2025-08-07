


def show_message(func):
    def wrapper(*args,**kwargs):
        print("Before the function runs")
        result = func(*args,**kwargs)
        print(f'result = {result}')
        print("After the function runs")
        return result

    return wrapper

@show_message
def sum_numbers(num1,num2,name = "ss"):
    return num1 + num2

@show_message
def sub_numbers(num1,num2):
    return num1 - num2

@show_message
def mult_numbers(num1,num2):
    return num1 * num2

@show_message
def div_numbers(num1,num2):
    return num1 / num2
