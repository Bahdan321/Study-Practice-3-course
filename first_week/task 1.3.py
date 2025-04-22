user_string = input("Введите строку: ")
if not user_string:
    raise ValueError("Строка не должна быть пустой!")


print(f"Ваша реверсированная строка: {user_string[::-1]}")
