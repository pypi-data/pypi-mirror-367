def signhandlex(sinum):
    sinum = str(sinum)
    ans = None
    if sinum[0] == '-':
        val = [i for i in sinum]
        val.remove(val[0])
        for i in val:
            if ans is None:
                ans = i
            else:
                ans = ans + i
        return float(ans)
    else:
        return float(sinum)


def multiplier_handle(count: int, mul: str = 'neg' or 'pos'):
    val = '0.'
    temp = count
    while temp > 0:
        val = f'{val}0'
        temp -= 1
    unit = float(f'{val}1')
    stage = float(f'{val}9')
    if mul == 'neg':
        new_mul = 1 + stage
        return new_mul, unit
    elif mul == 'pos':
        if count == 0:
            new_mul = unit
            return new_mul, unit
        else:
            new_mul = 1 - stage
            return new_mul, unit
    else:
        return 'Invalid', 'multiplier'


def neg_mul_handle(neg: float, neg_mul: float, pos: float, unit: float, count: int):
    c = count
    while True:
        x = neg * neg_mul
        temp_x = str(x)
        position = temp_x.find('0000000000')
        if position != -1:
            x = round(x, position)
        if x > 90 or x >= pos:
            neg_mul -= unit
            neg_mul = round(neg_mul, c + 1)
            if neg_mul == 1 or neg_mul < 1:
                c += 1
                neg_mul, unit = multiplier_handle(c)
        else:
            return x, neg_mul, c


def pos_mul_handle(pos: float, pos_mul: float, neg: float, unit: float, count: int):
    c = count
    while True:
        x = pos * pos_mul
        temp_x = str(x)
        position = temp_x.find('0000000000')
        if position != -1:
            x = round(x, position)
        if x < 0 or x <= neg:
            pos_mul += unit
            pos_mul = round(pos_mul, c + 1)
            if pos_mul == 1 or pos_mul > 1:
                c += 1
                pos_mul, unit = multiplier_handle(c, 'pos')
        else:
            return x, pos_mul, c


def pi():
    p = 3.141592653589793
    return p


def e():
    p = 2.718281828459045
    return p


def fac(num: int):
    assert isinstance(num, int), f'Expected type is int, got: {type(num)}'
    if num < 0:
        return 'Math Error'
    num_fac = 1
    for i in range(1, num + 1):
        num_fac = num_fac * i
    return num_fac


def degtorad(deg: float):
    assert isinstance(deg, float) or isinstance(deg, int), f'Expected float or int, got {type(deg)}'
    pi = 3.141592653589793
    an = (pi * deg) / 180
    return an


def radtodeg(rad: float):
    assert isinstance(rad, float) or isinstance(rad, int), f'Expected float or int, got {type(rad)}'
    pi = 3.141592653589793
    an = (180 * rad) / pi
    return an


def decround(num: float, limit: int):
    assert isinstance(num, float) or isinstance(num, int), f'Expected float or int, got: {type(num)}'
    assert isinstance(limit, int), f'Expected int, got: {type(limit)}'
    if isinstance(num, int):
        return num, 'int'
    num = str(num)
    wh, dec = num.split('.')
    if len(dec) < limit:
        return num, 'short'
    elif len(dec) == limit:
        return num, None
    else:
        val = [j for i, j in enumerate(dec) if i < limit]
        num = f'{wh}.'
        for i in val:
            num = num + i
        return num, None


def fine_range(start: float, stop: float, step: float):
    str_step = str(step)
    wh, dec = str_step.split('.')
    check = None
    while start < stop:
        if check is None:
            check = True
            start = round(start, len(dec))
            yield start
        elif check is True:
            start = start + step
            start = round(start, len(dec))
            yield start


def co_terminal(angle: float, mode: str = 'rad' or 'deg', direction: str = 'default' or 'pos' or 'neg', length: int = 10):
    assert isinstance(angle, float) or isinstance(angle, int), f'Expected float or int, got: {type(angle)}'
    assert isinstance(mode, str), f'Expected str, got: {type(mode)}'
    assert isinstance(direction, str), f'Expected str, got: {type(direction)}'
    assert isinstance(length, int), f'Expected int, got: {type(length)}'
    if direction == 'default':
        length = None
    pi = 3.141592653589793
    val = []
    if mode == 'rad':
        if direction == 'default':
            an = angle
            val.append(an)
            if an > 2 * pi:
                while an > 2 * pi:
                    an = an - (2 * pi)
                    val.append(an)
            elif an < -(2 * pi):
                while an < -(2 * pi):
                    an = an + (2 * pi)
                    val.append(an)
            return val
        elif direction == 'pos':
            if length <= 0:
                return 'Invalid length for the list'
            an = angle
            val.append(an)
            while len(val) < length:
                an = an + (2 * pi)
                val.append(an)
            return val
        elif direction == 'neg':
            if length <= 0:
                return 'Invalid length for the list'
            an = angle
            val.append(an)
            while len(val) < length:
                an = an - (2 * pi)
                val.append(an)
            return val
        else:
            return 'Invalid direction'
    elif mode == 'deg':
        if direction == 'default':
            an = angle
            val.append(an)
            if an > 360:
                while an > 360:
                    an = an - 360
                    val.append(an)
            elif an < -360:
                while an < -360:
                    an = an + 360
                    val.append(an)
            return val
        elif direction == 'pos':
            if length <= 0:
                return 'Invalid length for the list'
            an = angle
            val.append(an)
            while len(val) < length:
                an = an + 360
                val.append(an)
            return val
        elif direction == 'neg':
            if length <= 0:
                return 'Invalid length for the list'
            an = angle
            val.append(an)
            while len(val) < length:
                an = an - 360
                val.append(an)
            return val
        else:
            return 'Invalid direction'
    else:
        return 'Invalid Mode'


def sin(angle: float, mode: str = 'rad' or 'deg'):
    assert isinstance(angle, float) or isinstance(angle, int), f'Expected float or int, got: {type(angle)}'
    assert isinstance(mode, str), f'Expected str, got: {type(mode)}'
    pi = 3.141592653589793
    if mode == 'rad':
        an = angle
        if an > 2 * pi:
            while an > 2 * pi:
                an = an - (2 * pi)
        elif an < -(2 * pi):
            while an < -(2 * pi):
                an = an + (2 * pi)
    elif mode == 'deg':
        an = (pi * angle)/180
        if an > 2 * pi:
            while an > 2 * pi:
                an = an - (2 * pi)
        elif an < -(2 * pi):
            while an < -(2 * pi):
                an = an + (2 * pi)
    else:
        return 'Invalid Mode'
    multi = 1
    check = 0
    count = 0
    n = 2
    sin_res = an * multi
    while count < 1000:
        if check == 0 or check == 1:
            multi = multi - 1
            check += 1
        elif check == 2:
            multi += 1
            check += 1
        elif check == 3:
            multi += 1
            check = 0
        num = an * multi
        try:
            stage = (num ** n) / fac(n)
        except OverflowError:
            break
        sin_res = sin_res + stage
        n += 1
        count += 1
    sin_res = round(sin_res, 12)
    test_res = str(sin_res)
    if test_res == '-0.0':
        sin_res = sin_res * (-1)
    return sin_res


def cos(angle: float, mode: str = 'rad' or 'deg'):
    assert isinstance(angle, float) or isinstance(angle, int), f'Expected float or int, got: {type(angle)}'
    assert isinstance(mode, str), f'Expected str, got: {type(mode)}'
    pi = 3.141592653589793
    if mode == 'rad':
        an = angle
        if an > 2 * pi:
            while an > 2 * pi:
                an = an - (2 * pi)
        elif an < -(2 * pi):
            while an < -(2 * pi):
                an = an + (2 * pi)
    elif mode == 'deg':
        an = (pi * angle)/180
        if an > 2 * pi:
            while an > 2 * pi:
                an = an - (2 * pi)
        elif an < -(2 * pi):
            while an < -(2 * pi):
                an = an + (2 * pi)
    else:
        return 'Invalid Mode'
    multi = 1
    check = 0
    count = 0
    n = 1
    cos_res = 1
    while count < 1000:
        if check == 0 or check == 1:
            multi = multi - 1
            check += 1
        elif check == 2:
            multi += 1
            check += 1
        elif check == 3:
            multi += 1
            check = 0
        try:
            stage = (multi * (an ** n)) / fac(n)
        except OverflowError:
            break
        cos_res = cos_res + stage
        n += 1
        count += 1
    cos_res = round(cos_res, 12)
    test_res = str(cos_res)
    if test_res == '-0.0':
        cos_res = cos_res * (-1)
    return cos_res


def tan(angle: float, mode: str = 'rad' or 'deg'):
    assert isinstance(angle, float) or isinstance(angle, int), f'Expected float or int, got: {type(angle)}'
    assert isinstance(mode, str), f'Expected str, got: {type(mode)}'
    pi = 3.141592653589793
    if mode == 'rad':
        an = angle
        if an > 2 * pi:
            while an > 2 * pi:
                an = an - (2 * pi)
        elif an < -(2 * pi):
            while an < -(2 * pi):
                an = an + (2 * pi)
    elif mode == 'deg':
        an = (pi * angle)/180
        if an > 2 * pi:
            while an > 2 * pi:
                an = an - (2 * pi)
        elif an < -(2 * pi):
            while an < -(2 * pi):
                an = an + (2 * pi)
    else:
        return 'Invalid Mode'
    if cos(an) == 0.0:
        return 'Undefined'
    tan_res = sin(an) / cos(an)
    tan_res = round(tan_res, 12)
    test_res = str(tan_res)
    if test_res == '-0.0':
        tan_res = tan_res * (-1)
    return tan_res


def csc(angle: float, mode: str = 'rad' or 'deg'):
    assert isinstance(angle, float) or isinstance(angle, int), f'Expected float or int got: {type(angle)}'
    assert isinstance(mode, str), f'Expected str got: {type(mode)}'
    pi = 3.141592653589793
    if mode == 'rad':
        an = angle
        if an > 2 * pi:
            while an > 2 * pi:
                an = an - (2 * pi)
        elif an < -(2 * pi):
            while an < -(2 * pi):
                an = an + (2 * pi)
    elif mode == 'deg':
        an = (pi * angle) / 180
        if an > 2 * pi:
            while an > 2 * pi:
                an = an - (2 * pi)
        elif an < -(2 * pi):
            while an < -(2 * pi):
                an = an + (2 * pi)
    else:
        return 'Invalid Mode'
    stage = sin(an)
    if stage == 0.0:
        return 'Undefined'
    csc_res = 1 / stage
    csc_res = round(csc_res, 12)
    return csc_res


def sec(angle: float, mode: str = 'rad' or 'deg'):
    assert isinstance(angle, float) or isinstance(angle, int), f'Expected float or int got: {type(angle)}'
    assert isinstance(mode, str), f'Expected str got: {type(mode)}'
    pi = 3.141592653589793
    if mode == 'rad':
        an = angle
        if an > 2 * pi:
            while an > 2 * pi:
                an = an - (2 * pi)
        elif an < -(2 * pi):
            while an < -(2 * pi):
                an = an + (2 * pi)
    elif mode == 'deg':
        an = (pi * angle) / 180
        if an > 2 * pi:
            while an > 2 * pi:
                an = an - (2 * pi)
        elif an < -(2 * pi):
            while an < -(2 * pi):
                an = an + (2 * pi)
    else:
        return 'Invalid Mode'
    stage = cos(an)
    if stage == 0.0:
        return 'Undefined'
    sec_res = 1 / stage
    sec_res = round(sec_res, 12)
    return sec_res


def cot(angle: float, mode: str = 'rad' or 'deg'):
    assert isinstance(angle, float) or isinstance(angle, int), f'Expected float or int got: {type(angle)}'
    assert isinstance(mode, str), f'Expected str got: {type(mode)}'
    pi = 3.141592653589793
    if mode == 'rad':
        an = angle
        if an > 2 * pi:
            while an > 2 * pi:
                an = an - (2 * pi)
        elif an < -(2 * pi):
            while an < -(2 * pi):
                an = an + (2 * pi)
    elif mode == 'deg':
        an = (pi * angle) / 180
        if an > 2 * pi:
            while an > 2 * pi:
                an = an - (2 * pi)
        elif an < -(2 * pi):
            while an < -(2 * pi):
                an = an + (2 * pi)
    else:
        return 'Invalid Mode'
    if sin(an) == 0.0:
        return 'Undefined'
    cot_res = cos(an) / sin(an)
    cot_res = round(cot_res, 12)
    return cot_res


def arcsin(val: float, mode: str = 'rad' or 'deg'):
    assert isinstance(val, float) or isinstance(val, int), f'Expected float or int, got: {type(val)}'
    assert isinstance(mode, str), f'Expected str, got: {type(mode)}'
    t_stage, extra = decround(val, 12)
    val = float(t_stage)
    if val > 1 or val < -1:
        return 'Invalid value'
    if val == 1 or val == 1.0:
        if mode == 'rad':
            return degtorad(90)
        elif mode == 'deg':
            return 90
        else:
            return 'Invalid mode'
    if val == -1 or val == -1.0:
        if mode == 'rad':
            return degtorad(-90)
        elif mode == 'deg':
            return -90
        else:
            return 'Invalid mode'
    if val == 0.5:
        if mode == 'rad':
            return degtorad(30)
        elif mode == 'deg':
            return 30
        else:
            return 'Invalid mode'
    if val == -0.5:
        if mode == 'rad':
            return degtorad(-30)
        elif mode == 'deg':
            return -30
        else:
            return 'Invalid mode'
    if val == 0:
        if mode == 'rad':
            return 0
        elif mode == 'deg':
            return 0
        else:
            return 'Invalid mode'
    temp = False
    if val < 0:
        val = signhandlex(val)
        temp = True
    given = val
    neg = 0
    pos = 90
    neg_mul_O = 1.9
    pos_mul_O = 0.9
    x = 30
    neg_unit = 0.1
    pos_unit = 0.1
    count_N = 0
    count_P = 0

    val1 = sin(x, 'deg')
    check = val1 - given
    if check == 0:
        if mode == 'rad':
            return degtorad(x)
        elif mode == 'deg':
            return x
        else:
            return 'Invalid mode'
    while check != 0:
        if check < 0:
            neg = x
            x, neg_mul, count = neg_mul_handle(neg, neg_mul_O, pos, neg_unit, count_N)
            neg_mul_O = neg_mul
            count_N = count
            val1 = sin(x, 'deg')
            check = val1 - given
        elif check > 0:
            pos = x
            x, pos_mul, count = pos_mul_handle(pos, pos_mul_O, neg, pos_unit, count_P)
            pos_mul_O = pos_mul
            count_P = count
            val1 = sin(x, 'deg')
            check = val1 - given
        else:
            break
    if mode == 'rad':
        temp_x = str(x)
        position9 = temp_x.find('9999999')
        position0 = temp_x.find('0000000')
        if position9 != -1:
            x = round(x, position9)
        if position0 != -1:
            x = round(x, position0)
        x = degtorad(x)
        if temp is True:
            x = str(x)
            res = f'-{x}'
            return float(res)
        else:
            return x
    elif mode == 'deg':
        temp_x = str(x)
        position9 = temp_x.find('9999999')
        position0 = temp_x.find('0000000')
        if position9 != -1:
            x = round(x, position9)
        if position0 != -1:
            x = round(x, position0)
        if temp is True:
            x = str(x)
            res = f'-{x}'
            return float(res)
        else:
            return x
    else:
        return 'Invalid mode'


def arccos(val: float, mode: str = 'rad' or 'deg'):
    assert isinstance(val, float) or isinstance(val, int), f'Expected float or int, got: {type(val)}'
    assert isinstance(mode, str), f'Expected str, got: {type(mode)}'
    t_stage, extra = decround(val, 12)
    val = float(t_stage)
    if val > 1 or val < -1:
        return 'Invalid value'
    if val == 1 or val == 1.0:
        if mode == 'rad':
            return 0
        elif mode == 'deg':
            return 0
        else:
            return 'Invalid mode'
    if val == -1 or val == -1.0:
        if mode == 'rad':
            return degtorad(180)
        elif mode == 'deg':
            return 180
        else:
            return 'Invalid mode'
    if val == 0.5:
        if mode == 'rad':
            return degtorad(60)
        elif mode == 'deg':
            return 60
        else:
            return 'Invalid mode'
    if val == -0.5:
        if mode == 'rad':
            return degtorad(120)
        elif mode == 'deg':
            return 120
        else:
            return 'Invalid mode'
    if val == 0:
        if mode == 'rad':
            return degtorad(90)
        elif mode == 'deg':
            return 90
        else:
            return 'Invalid mode'
    temp = False
    if val < 0:
        val = signhandlex(val)
        temp = True
    given = val
    neg = 0
    pos = 180
    neg_mul_O = 1.9
    pos_mul_O = 0.1
    x = 30
    neg_unit = 0.1
    pos_unit = 0.1
    count_N = 0
    count_P = 0

    val1 = cos(x, 'deg')
    check = given - val1
    if check == 0:
        if mode == 'rad':
            return degtorad(x)
        elif mode == 'deg':
            return x
        else:
            return 'Invalid mode'
    while check != 0:
        if check < 0:
            neg = x
            x, neg_mul, count = neg_mul_handle(neg, neg_mul_O, pos, neg_unit, count_N)
            neg_mul_O = neg_mul
            count_N = count
            val1 = cos(x, 'deg')
            check = given - val1
        elif check > 0:
            pos = x
            x, pos_mul, count = pos_mul_handle(pos, pos_mul_O, neg, pos_unit, count_P)
            pos_mul_O = pos_mul
            count_P = count
            val1 = cos(x, 'deg')
            check = given - val1
        else:
            break
    if mode == 'rad':
        temp_x = str(x)
        position9 = temp_x.find('9999999')
        position0 = temp_x.find('0000000')
        if position9 != -1:
            x = round(x, position9)
        if position0 != -1:
            x = round(x, position0)
        x = degtorad(x)
        if temp is True:
            stage = (pi() / 2) - x
            x = (pi() / 2) + stage
            return x
        else:
            return x
    elif mode == 'deg':
        temp_x = str(x)
        position9 = temp_x.find('9999999')
        position0 = temp_x.find('0000000')
        if position9 != -1:
            x = round(x, position9)
        if position0 != -1:
            x = round(x, position0)
        if temp is True:
            stage = 90 - x
            x = 90 + stage
            return x
        else:
            return x
    else:
        return 'Invalid mode'


def arctan(val: float, mode: str = 'rad' or 'deg'):
    assert isinstance(val, float) or isinstance(val, int), f'Expected float or int, got: {type(val)}'
    assert isinstance(mode, str), f'Expected str, got: {type(mode)}'
    if val == 1 or val == 1.0:
        if mode == 'rad':
            return degtorad(45)
        elif mode == 'deg':
            return 45
        else:
            return 'Invalid mode'
    elif val == -1 or val == -1.0:
        if mode == 'rad':
            return degtorad(-45)
        elif mode == 'deg':
            return -45
        else:
            return 'Invalid mode'
    elif val == 0:
        if mode == 'rad':
            return 0
        elif mode == 'deg':
            return 0
        else:
            return 'Invalid mode'
    x = val
    if x <= 1:
        if x >= -1:
            t_stage = (2 * x) / (1 + (x ** 2))
            t_stage, extra = decround(t_stage, 12)
            t_stage = float(t_stage)
            stage = arcsin(t_stage, 'deg')
            res = stage / 2
            if mode == 'rad':
                return degtorad(res)
            elif mode == 'deg':
                return res
            else:
                return 'Invalid mode'
        elif x < -1:
            t_stage = (1 - (x ** 2)) / (1 + (x ** 2))
            t_stage, extra = decround(t_stage, 12)
            t_stage = float(t_stage)
            stage = arccos(t_stage, 'deg')
            res = -stage / 2
            if mode == 'rad':
                return degtorad(res)
            elif mode == 'deg':
                return res
            else:
                return 'Invalid mode'
    elif x > 1:
        t_stage = (1 - (x ** 2)) / (1 + (x ** 2))
        t_stage, extra = decround(t_stage, 12)
        t_stage = float(t_stage)
        stage = arccos(t_stage, 'deg')
        res = stage / 2
        if mode == 'rad':
            return degtorad(res)
        elif mode == 'deg':
            return res
        else:
            return 'Invalid mode'


def arccsc(val: float, mode: str = 'rad' or 'deg'):
    assert isinstance(val, float) or isinstance(val, int), f'Expected float or int, got: {type(val)}'
    assert isinstance(mode, str), f'Expected str, got: {type(mode)}'
    if val > -1:
        if val < 1:
            return 'Invalid value'
    x = 1 / val
    t_stage, extra = decround(x, 12)
    t_stage = float(t_stage)
    res = arcsin(t_stage, 'deg')
    if mode == 'rad':
        return degtorad(res)
    elif mode == 'deg':
        return res
    else:
        return 'Invalid mode'


def arcsec(val: float, mode: str = 'rad' or 'deg'):
    assert isinstance(val, float) or isinstance(val, int), f'Expected float or int, got: {type(val)}'
    assert isinstance(mode, str), f'Expected str, got: {type(mode)}'
    if val > -1:
        if val < 1:
            return 'Invalid value'
    x = 1 / val
    t_stage, extra = decround(x, 12)
    t_stage = float(t_stage)
    res = arccos(t_stage, 'deg')
    if mode == 'rad':
        return degtorad(res)
    elif mode == 'deg':
        return res
    else:
        return 'Invalid mode'


def arccot(val: float, mode: str = 'rad' or 'deg'):
    assert isinstance(val, float) or isinstance(val, int), f'Expected float or int, got: {type(val)}'
    assert isinstance(mode, str), f'Expected str, got: {type(mode)}'
    x = 1 / val
    t_stage, extra = decround(x, 12)
    t_stage = float(t_stage)
    res = arctan(t_stage, 'deg')
    if mode == 'rad':
        return degtorad(res)
    elif mode == 'deg':
        return res
    else:
        return 'Invalid mode'


def ln(num: float):
    assert isinstance(num, float) or isinstance(num, int), f'Expected float or int, got {type(num)}'
    if num <= 0:
        return 'Math Error'
    c = 0
    while num >= 2:
        num = num / 2
        c += 1
    n = 1
    ans = 0
    while n <= 1000:
        if n == 1:
            ans = ((num - 1) ** n) / n
            n += 1
        elif n % 2 == 0:
            ans = ans - ((num - 1) ** n) / n
            n += 1
        elif n % 2 != 0:
            ans = ans + ((num - 1) ** n) / n
            n += 1
    ln2 = 0.69314718056
    stage_res = ans + c * ln2
    ln_res = round(stage_res, 9)
    return ln_res


def log(num: float, base: float = 10):
    assert isinstance(num, float) or isinstance(num, int), f'Expected float, got {type(num)}'
    assert isinstance(base, float) or isinstance(base, int), f'Expected float, got {type(base)}'
    if num <= 0:
        return 'Math Error'
    if base <= 0:
        return 'Math Error'
    stage_res = ln(num)/ln(base)
    log_res = round(stage_res, 9)
    return log_res


def n_root(num: float, root: int):
    assert isinstance(num, float) or isinstance(num, int), f'Expected float or int, got: {type(num)}'
    assert isinstance(root, int), f'Expected int, got: {type(root)}'
    ans = e() ** ((1 / root) * ln(num))
    temp_x = str(ans)
    position9 = temp_x.find('9999999')
    position0 = temp_x.find('0000000')
    if position9 != -1:
        ans = round(ans, position9)
    if position0 != -1:
        ans = round(ans, position0)
    ans, arg = decround(ans, 9)
    return float(ans)
