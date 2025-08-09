
from flask import Flask, request, jsonify
from prime import is_prime
from even import is_even
from odd import is_odd

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

def get_primes(limit):
    return [num for num in range(2, limit + 1) if is_prime(num)]

def get_evens(limit):
    return [num for num in range(2, limit + 1) if is_even(num)]

def get_odds(limit):
    return [num for num in range(1, limit + 1) if is_odd(num)]

@app.route('/numbers', methods=['POST'])
def numbers():
    data = request.get_json()
    limit = int(data.get('limit', 0))
    choice = str(data.get('choice', ''))
    if choice == '1':
        result = get_primes(limit)
    elif choice == '2':
        result = get_evens(limit)
    elif choice == '3':
        result = get_odds(limit)
    else:
        return jsonify({'error': 'Invalid choice.'}), 400
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
