def fibonacci(n):
    # Initialize first two numbers
    a, b = 0, 1
    # Create empty list to store series
    fib_series = []
    
    # Generate fibonacci series
    for _ in range(n):
        fib_series.append(a)
        a, b = b, a + b
    
    return fib_series

# Get input from user
n = int(input("Enter how many Fibonacci numbers you want to generate: "))
result = fibonacci(n)
print(f"Fibonacci series with {n} numbers:")
print(result)