from django import forms


def validate_not_empty_or_less(value):
    """
    Функция-валидатор, которая проверяет получаемое значение на
    количество символов, и возвращает ошибку в форму,
    если это значение пустое или меньше 30 символов.

    :param value: str
    :return: None

    Doctest
    -------
    >>> validate_not_empty_or_less('01234567890qwertyuiop[]aggghhjjkkll;l;')

    """

    if value == '' or value is None:
        raise forms.ValidationError(
            'Статья не может быть пустой!',
            params={'value': value},
        )
    if len(value) <= 30:
        raise forms.ValidationError(
            f'Краткость, это прекрасно,'
            f'но может стоит написать больше {len(value)} символов?',
            params={'value': value},
        )


def validate_for_comment(value):
    if value == '' or value is None:
        raise forms.ValidationError(
            'Комментарий не может быть пустый!',
            params={'value': value},
        )
    if len(value) <= 5:
        raise forms.ValidationError(
            f'Краткость, это прекрасно,'
            f'но может стоит написать больше {len(value)} символов?',
            params={'value': value},
        )
