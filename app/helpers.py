import random
from app.models import UserModel


def get_dict_data(data):
    from django.http import QueryDict

    if type(data) is QueryDict:
        return {
            k: data.getlist(k) if len(data.getlist(k)) > 1 else v
            for k, v in data.items()
        }
    elif type(data) is dict:
        return data
    return {}


def generate_username(name=''):
    
    username = "".join(name.split(' ')).lower()
    if username and not UserModel.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + str(random.randint(0, 1000))
        return generate_username(random_username)



# Pagination: page_size,page_num
def get_data(data: list, pagination: tuple = None):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    total_page_num = 1
    result = data
    if pagination:
        page_size, page_num = pagination
        paginator = Paginator(data, page_size)
        try:
            res = paginator.page(page_num)
        except PageNotAnInteger:
            res = paginator.page(2)
        except EmptyPage:
            res = paginator.page(paginator.num_pages)
        result = res.object_list
        total_page_num = res.paginator.num_pages

    return (result, total_page_num)
def get_response_data(request, queryset):
    if 'page_size' in request.query_params and request.query_params['page_size'] and \
                'page_num' in request.query_params and request.query_params['page_num']:
        _page_size = request.query_params['page_size']
        _page_num = request.query_params['page_num']
        _objects, _total_page_num = get_data(queryset,
                                             pagination=(_page_size,
                                                         _page_num))
    else:
        _objects, _total_page_num = get_data(queryset)

    return _objects, _total_page_num


def get_user(context):
    if context:
        try:
            if 'request' in context:
                _request = context['request']
                if _request:
                    if _request.auth:
                        return _request.auth.user
                    elif _request.user:
                        return _request.user
        except:
            _request = context
            if _request.auth:
                return _request.auth.user
            elif _request.user:
                return _request.user
    return None


def random_with_N_digits(n=8):
    range_start = 10**(n - 1)
    range_end = (10**n) - 1
    return random.randint(range_start, range_end)
def get_verfication_code(digit_num=5):
    return random_with_N_digits(digit_num)



def validate_phone_number(cellphone,country_code=None):
    #Regular expression: /^(\+98|0098|0)?(9[0-9]{9})$/
    import phonenumbers 
    if not country_code:
        country_code = "IR"
    cellphone_check = phonenumbers.parse(cellphone, country_code)
    return phonenumbers.is_valid_number(cellphone_check)

