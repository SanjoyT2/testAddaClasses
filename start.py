from prime import is_prime
from even import is_even
from odd import is_odd

def print_primes(limit):
    """Print all prime numbers up to the given limit."""
    print(f"Prime numbers up to {limit}:")
    for num in range(2, limit + 1):
        if is_prime(num):
            print(num, end=' ')
    print()

def print_evens(limit):
    """Print all even numbers up to the given limit."""
    print(f"Even numbers up to {limit}:")
    for num in range(2, limit + 1):
        if is_even(num):
            print(num, end=' ')
    print()

def print_odds(limit):
    """Print all odd numbers up to the given limit."""
    print(f"Odd numbers up to {limit}:")
    for num in range(1, limit + 1):
        if is_odd(num):
            print(num, end=' ')
    print()

if __name__ == "__main__":
    # The user is prompted to enter the upper limit for finding numbers.
    limit = int(input("Enter the upper limit: "))
    # The user is prompted to choose which type of numbers to print.
    print("Choose an option:")
    print("1. Print Prime Numbers")
    print("2. Print Even Numbers")
    print("3. Print Odd Numbers")
    choice = input("Enter your choice (1/2/3): ")

    if choice == '1':
        print_primes(limit)
    elif choice == '2':
        print_evens(limit)
    elif choice == '3':
        print_odds(limit)
    else:
        print("Invalid choice.")