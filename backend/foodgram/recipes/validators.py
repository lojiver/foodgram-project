from django.core.exceptions import ValidationError


def validate_hex(val):
    if val[0] != '#' or len(val) != 7:
        raise ValidationError(
            'Введите значение в формате HEX: #112233'
        )
