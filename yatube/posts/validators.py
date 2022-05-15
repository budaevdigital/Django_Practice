from django import forms


def validate_not_empty_or_less(value):

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
