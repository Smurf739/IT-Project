import hashlib
import secrets


def generate_api_key(user_password, bit_length=1024):
    """
    Генерирует API ключ через двойной хэш

    Args:
        user_password (str): Пароль пользователя
        bit_length (int): Длина простого числа в битах

    Returns:
        tuple: (api_key, salt, prime_number)
    """

    def generate_large_prime(bit_length):
        """Генерирует большое простое число"""
        while True:
            # Генерируем случайное число с указанной битовой длиной
            candidate = secrets.randbits(bit_length)
            # Убеждаемся, что число нечетное и достаточно большое
            candidate |= (1 << bit_length - 1) | 1

            def is_prime(n, k=5):
                """Тест Миллера-Рабина на простоту"""
                if n == 2 or n == 3:
                    return True
                if n <= 1 or n % 2 == 0:
                    return False

                # Находим r и s
                s = 0
                r = n - 1
                while r & 1 == 0:
                    s += 1
                    r //= 2

                # Проводим k тестов
                for _ in range(k):
                    a = secrets.randbelow(n - 3) + 2
                    x = pow(a, r, n)
                    if x != 1 and x != n - 1:
                        j = 1
                        while j < s and x != n - 1:
                            x = pow(x, 2, n)
                            if x == 1:
                                return False
                            j += 1
                        if x != n - 1:
                            return False
                return True

            if is_prime(candidate):
                return candidate

    salt = secrets.token_hex(32)

    prime_number = generate_large_prime(bit_length)

    first_hash_input = user_password + salt
    first_hash = hashlib.sha512(first_hash_input.encode()).hexdigest()

    second_hash_input = first_hash + str(prime_number)
    api_key = hashlib.sha512(second_hash_input.encode()).hexdigest()

    return api_key

