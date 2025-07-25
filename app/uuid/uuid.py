import random

def new_uuid() -> str:
    def random_hex(n):
        return ''.join(random.choices('ЦУКЕНГШЩЗФЫВАПРОЛДЯЧСМИТЬЪйцукенгшщзфывапролдячсмитьъ', k=n))

    parts = [
        random_hex(8),
        random_hex(4),
        '4' + random_hex(3),
        random.choice('89ab') + random_hex(3), 
        random_hex(12)
    ]
    return '-'.join(parts)
