from string import Template
from my_func import is_cor_chr

# Функция для выдёргивания переменных хода алгоритма


def is_load_algoritm(controller, cells, sheet):
    sl_algoritm = {}
    # Для выдачи команд заполняем sl_algoritm парами алг.имя команды: (руское наименование команды, тип сигнала-BOOL)
    for p in cells:
        # Если установлен нужный контроллер и мы находимся в строке объявления режима
        if sheet[p[0].row][3].value == controller and p[0].value == 'Режим':
            cmd_eng, cmd_rus = (), ()
            # Добавляем дефолтные переменные для режима
            cmd_rus += ((f"Старт режима {sheet[p[0].row][2].value}", 'BOOL'),
                        (f"Оконачание режима {sheet[p[0].row][2].value}", 'BOOL'),
                        (f"Шаг режима {sheet[p[0].row][2].value}", 'INT'))
            cmd_eng += (f"GRH|{sheet[p[0].row][1].value}_START",
                        f"GRH|{sheet[p[0].row][1].value}_END",
                        f"GRH|{sheet[p[0].row][1].value}_Point")
            jj = 7
            while jj != sheet.max_column and sheet[p[0].row][jj].value and sheet[p[0].row + 1][jj].value:
                cmd_rus += ((sheet[p[0].row][jj].value, 'BOOL'),)
                cmd_eng += (sheet[p[0].row + 1][jj].value,)
                jj += 1
            sl_algoritm.update(dict(zip(cmd_eng, cmd_rus)))

    j = 0
    p = cells[0][0].value
    # пока не дошли до конца объявления режимов
    while p != 'STOP':
        j += 1
        p = cells[j][0].value
        # Если увидели объяление шагов алгоритма и алгоритм принадлежит текущему контроллеру
        if p == 'Шаг' and sheet[j][3].value == controller:
            mod_name = sheet[j][1].value
            mod_name_rus = sheet[j][2].value
            # cpu_name = sheet[j][3].value
            # print(cpu_name)
            while p is not None:
                j += 1
                p = cells[j][0].value
                # конструкции для условий перехода
                tuple_rus_step, tuple_eng_step = (), ()
                step_out_tmp = ()
                # конструкции для таймеров
                tuple_rus_step_timer, tuple_step_timer_value = (), ()
                step_timer_out_tmp = ()
                # конструкции для дополнительных параметров
                tuple_dop_par_rus = ()
                sl_dop_par_tmp = {}
                sl_dop_par_fragdigits_tmp = {}
                step_dop_par_out_tmp = ()
                step_dop_par_fragdigits_out_tmp = ()
                # конструкции для обратных таймеров
                sl_rev_timer_tmp = {}
                step_rev_timer_out_tmp = ()
                tuple_rev_timer_rus = ()
                if p is not None:
                    # sheet[j + 1][4].value - русское условие
                    # sheet[j + 1][3].value - алгоритмическое условие

                    # если на шаге есть какое-то условие перехода(смотрим по русскому тексту), то обрабатываем
                    if sheet[j + 1][4].value is not None:
                        # В данном виде в списках есть ИЛИ и OR. По ним делим в структуры
                        lst_rus_alg = sheet[j + 1][4].value.split('\n')
                        tuple_rus_step = ((lst_rus_alg[:lst_rus_alg.index('ИЛИ')] if 'ИЛИ' in lst_rus_alg
                                           else lst_rus_alg),
                                          (lst_rus_alg[lst_rus_alg.index('ИЛИ') + 1:] if 'ИЛИ' in lst_rus_alg else []))
                        # print(p, tuple_rus_step)
                        # print(p, [step for group_step in tuple_rus_step for step in group_step])
                        '''
                        lst_eng_alg = [f"{i.strip(' AND')}" if i != 'OR' else 'OR'
                                       for i in sheet[j + 1][3].value.split('\n')]
                        tuple_eng_step = ((lst_eng_alg[:lst_eng_alg.index('OR')] if 'OR' in lst_eng_alg 
                                           else lst_eng_alg),
                                          (lst_eng_alg[lst_eng_alg.index('OR') + 1:] if 'OR' in lst_eng_alg else []))
                        '''
                        # print(p, tuple_eng_step)
                        # print(p, [step for group_step in tuple_eng_step for step in group_step])

                        # В данном виде в списках НЕТ ИЛИ и OR. Возможно, пригодится
                        # print(p, mod_name, [i for i in sheet[j + 1][4].value.split('\n') if i != 'ИЛИ'])
                        # print(p, [f"{mod_name}-{p}-{i.strip(' AND')}" for
                        # i in sheet[j + 1][3].value.split('\n') if i != 'OR'])

                    # Если на шаге установлен какой-то таймер
                    if sheet[j + 1][1].value is not None:
                        # print(p, float(sheet[j + 1][1].value), sheet[j + 1][2].value)
                        # добавляем текст таймера и текст выхода таймера в кортеж русских таймеров
                        tuple_rus_step_timer += ([sheet[j + 1][2].value], [sheet[j + 1][2].value + '-Вых'],)
                        # добавляем значение таймера в кортеж
                        tuple_step_timer_value += ([sheet[j + 1][1].value],)
                    # Если на шаге не установлено таймера
                    else:
                        # добавляем прочерк-текст таймера в кортеж русских таймеров
                        tuple_rus_step_timer += (['-'],)
                        # добавляем нулевое значение таймера в кортеж
                        tuple_step_timer_value += (['0.0'],)

                    # Если на шаге указан дополнительный параметр(хотя бы один)
                    if sheet[j + 1][5].value is not None and sheet[j + 1][5].value.replace('\n', ''):
                        # формируем словарь соответствий условие перехода: дополнительный параметр,
                        # чтобы правильно сформировать префиксы на конце
                        sl_dop_par_tmp.update(dict(zip(sheet[j + 1][4].value.split('\n'),
                                                       tuple(sheet[j + 1][5].value.split('\n')))))
                        # формируем словарь соответствий условие перехода: количество знаков после запятой,
                        # чтобы правильно сформировать префиксы на конце
                        tuple_tmp = [a[a.find('{') + 1:a.find('}')] if '{' in a else '0'
                                     for a in sheet[j + 1][5].value.split('\n')]
                        sl_dop_par_fragdigits_tmp.update(dict(zip(sheet[j + 1][4].value.split('\n'), tuple_tmp)))

                    # Если на шаге указан хотя бы один обратный таймер
                    if sheet[j + 1][6].value is not None and sheet[j + 1][6].value.replace('\n', ''):
                        # формируем словарь соответствий условие перехода: обратный таймер,
                        # чтобы правильно сформировать префиксы на конце
                        sl_rev_timer_tmp.update(dict(zip(sheet[j + 1][4].value.split('\n'),
                                                         tuple(sheet[j + 1][6].value.split('\n')))))

                # Формируем алгоритмические имена шагов по правилам добавления префиксов на конце
                for a in range(len(tuple_rus_step)):
                    for b in range(len(tuple_rus_step[a])):
                        step_out_tmp += (f"GRH|{mod_name}_Cmd_In_{p}_{a + 1}_{b + 1}",)
                        # если есть в словаре соответствий допонительных параметров
                        if sl_dop_par_tmp.get(tuple_rus_step[a][b]):
                            # то формируем кортеж алгоритмических имён
                            # дополнительных параметров по правилам добавления префиксов,
                            step_dop_par_out_tmp += (f"GRH|{mod_name}_Par_In_{p}_{a + 1}_{b + 1}",)
                            # также формируем кортеж с русским описанием дополнительных параметров
                            tuple_dop_par_rus += (f"Дополнительный параметр режима {mod_name_rus} шага {p}",)
                            # также формируем кортеж с количеством знаков после запятой дополнительных параметров
                            step_dop_par_fragdigits_out_tmp += (sl_dop_par_fragdigits_tmp[tuple_rus_step[a][b]],)
                        # если есть в словаре соответствий обратных таймеров
                        if sl_rev_timer_tmp.get(tuple_rus_step[a][b]):
                            # формируем кортеж алгоритмических имён обратных таймеров
                            # по правилам добавления префиксов
                            step_rev_timer_out_tmp += (f"GRH|{mod_name}_Tmv_Rev_{p}_{a + 1}_{b + 1}",)
                            # также формируем кортеж с русским описанием обратных таймеров
                            tuple_rev_timer_rus += (f"Обратный таймер режима {mod_name_rus} шага {p}",)

                # Формируем алгоритмические имена шагов для таймеров
                for a in range(len(tuple_step_timer_value)):
                    # Если таймер ненулевой, то добавляем переменную для отображения
                    if tuple_step_timer_value[a] != ['0.0']:
                        step_timer_out_tmp += (f"GRH|{mod_name}_Tmv_In_{p}",)
                        step_timer_out_tmp += (f"GRH|{mod_name}_Tmv_Out_{p}",)
                    # Иначе просто добавляем переменную (возможно, незачем, но добавим!!!!!!!!!!!!!!!!!)
                    else:
                        step_timer_out_tmp += (f"GRH|{mod_name}_Tmv_In_{p}",)

                # Если в шаге только одно условие, то "убиваем" два последние цифры иначе оставляем
                step_out_tmp = ((step_out_tmp[0][:-4],) if len(step_out_tmp) == 1 else step_out_tmp)

                # Если в словаре дополнительных параметров только один,
                # то "убиваем" два последние цифры иначе оставляем
                step_dop_par_out_tmp = ((step_dop_par_out_tmp[0][:-4],) if len(sl_dop_par_tmp) == 1
                                        else step_dop_par_out_tmp)

                # Если в словаре обратных таймеров только один,
                # то "убиваем" два последние цифры иначе оставляем
                step_rev_timer_out_tmp = ((step_rev_timer_out_tmp[0][:-4],) if len(sl_rev_timer_tmp) == 1
                                          else step_rev_timer_out_tmp)

                # Условия перехода
                # В выходной словарь функции грузим алг.имя: (Русское имя, тип сигнала-BOOL)
                step_tmp = [(a, 'BOOL') for a in [step for group_step in tuple_rus_step for step in group_step]]
                sl_algoritm.update(dict(zip(step_out_tmp, step_tmp)))

                # Таймера
                # В выходной словарь функции грузим алг.имя: (Русское текст таймера, тип сигнала-FLOAT)
                sl_algoritm.update(dict(zip(step_timer_out_tmp, [(*a, 'FLOAT') for a in tuple_rus_step_timer])))

                # Дополнительный параметры
                # В выходной словарь функции грузим алг.имя: (Русское текст доп.параметра, тип сигнала-FLOAT, frag_dig)
                sl_algoritm.update(dict(zip(step_dop_par_out_tmp,
                                            tuple(zip(tuple_dop_par_rus, ('FLOAT',)*len(tuple_dop_par_rus),
                                                      step_dop_par_fragdigits_out_tmp)))))

                # Обратные таймера
                # В выходной словарь функции грузим алг.имя: (Русское текст обратного таймера, тип сигнала-FLOAT)
                sl_algoritm.update(dict(zip(step_rev_timer_out_tmp, [(a, 'FLOAT') for a in tuple_rev_timer_rus])))

    return sl_algoritm

# Функция для создания структуры для каждой переменной алгоритма


def is_create_objects_alogritm(sl_alogritm, template_text, template_text_dop_par):
    sl_type_alogritm = {
        'BOOL': 'Types.GRH.GRH_BOOL_PLC_View',
        'INT': 'Types.GRH.GRH_INT_PLC_View',
        'FLOAT': 'Types.GRH.GRH_FLOAT_PLC_View'
    }
    tmp_line_object = ''
    for key, value in sl_alogritm.items():
        if 'Дополнительный параметр режима' in value[0] and 'Par' in key:
            tmp_line_object += Template(template_text_dop_par).substitute(object_name=key[key.find('|') + 1:],
                                                                          object_type=sl_type_alogritm[value[1]],
                                                                          object_aspect='Types.PLC_Aspect',
                                                                          text_description=value[0],
                                                                          text_fracdigits=value[2])
        else:
            tmp_line_object += Template(template_text).substitute(object_name=key[key.find('|')+1:],
                                                                  object_type=sl_type_alogritm[value[1]],
                                                                  object_aspect='Types.PLC_Aspect',
                                                                  text_description=is_cor_chr(value[0]))
    return tmp_line_object.rstrip()
