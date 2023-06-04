icons = {'key1': 12, 'key2': 123, 'key3': None}

# Obtener la longitud del diccionario filtrado
length = len({key: value for key, value in icons.items() if value is not None})

print(length)  # Imprime: 2
