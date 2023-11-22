from django import template


register = template.Library()


@register.filter()
def file_size_format(value):
    return f'{round(value / 1024 ** 2, 2)} MB\n'


@register.filter()
def used_space(values):
    used_size = sum(value.size for value in values if not hasattr(value, 'is_folder'))
    return round(used_size / 1024 ** 2, 2) if used_size > 0 else 0


@register.filter()
def user_premium(user):
    return True if user.groups.filter(name='Premium').exists() else False
