from string import Template
import os
import datetime
from time import sleep

# Функция для очистки русской строки от лишних символов в русской строке для json


def f_ind_json(target_str):
    replace_values = {'\"': '', '\'': ''}
    # получаем заменяемое: подставляемое из словаря в цикле
    for i, j in replace_values.items():
        # меняем все target_str на подставляемое
        target_str = target_str.replace(i, j)
    return target_str


# Функция для замены нескольких значений


def multiple_replace(target_str):
    replace_values = {'\n': ' ', '_x000D_': ''}
    # получаем заменяемое: подставляемое из словаря в цикле
    for i, j in replace_values.items():
        # меняем все target_str на подставляемое
        target_str = target_str.replace(i, j)
    return target_str

# функция для поиска индекса нужного столбца


def is_f_ind(cell, name_col):
    for i in range(len(cell)):
        if cell[i].value is None:
            break
        if multiple_replace(cell[i].value) == name_col:
            return i
    return 0


# Функция для замены в строке спецсимволов HTML

def is_cor_chr(st):
    sl_chr = {'<': '&lt;', '>': '&gt;', '"': '&quot;'}
    tmp = list()
    tmp.extend(st)
    for i in range(len(tmp)):
        if tmp[i] in sl_chr:
            tmp[i] = sl_chr[tmp[i]]
    return ''.join(tmp)


# Читаем и грузим в словарь, где ключ - алг имя, а в значении список(кортеж) - русское наименование
# ед. изм-я, короткое наименование и количество знаков после запятой

def is_load_ai_ae_set(controller, cell, alg_name, name_par, eunit, short_name, f_dig, cpu):
    tmp = {}
    reserve_cel = is_f_ind(cell[0], 'Резервный')
    for par in cell:
        if par[name_par].value is None:
            break
        if par[cpu].value == controller and par[reserve_cel].value == 'Нет':
            tmp['_'.join(par[alg_name].value.split('|'))] = (is_cor_chr(par[name_par].value),
                                                             par[eunit].value, par[short_name].value, par[f_dig].value)
    return tmp


# Функция для чтения обвеса DI, возможно потребуется в список грузить больше информации, пока читаем только алг имя,
# описание, цвет при наличии(color_on) и цвет при отсутствии(color_off)
# Также собираем словарь ПС -  текст сообщения и держим тип сообщения

def is_load_di(controller, cell, alg_name, im, name_par, c_on, c_off, ps, ps_msg, cpu):
    tmp = {}
    tmp_wrn = {}
    reserve_cel = is_f_ind(cell[0], 'Резервный')
    for par in cell:
        if par[name_par].value is None:
            break
        if par[cpu].value == controller and par[im].value == 'Нет' and par[reserve_cel].value == 'Нет':
            tmp['_'.join(par[alg_name].value.split('|'))] = (is_cor_chr(par[name_par].value),
                                                             par[c_on].fill.start_color.index,
                                                             par[c_off].fill.start_color.index)
            if par[ps].value != 'Нет':
                tmp_wrn['_'.join(par[alg_name].value.split('|'))] = (is_cor_chr(par[ps_msg].value), par[ps].value)
    return tmp, tmp_wrn

# добавлена функция для чтения дискретов НКУ


def is_load_di_nku(controller, cell, alg_name, im, name_par, c_on, c_off, ps, ps_msg, cpu):
    tmp = {}
    tmp_wrn = {}
    reserve_cel = is_f_ind(cell[0], 'Резервный')
    for par in cell:
        if par[name_par].value is None:
            break
        if par[cpu].value == controller and par[im].value == 'Нет' and par[reserve_cel].value == 'Нет':
            tmp['_'.join(par[alg_name].value.split('|'))] = (is_cor_chr(par[name_par].value),
                                                             par[c_on].fill.start_color.index,
                                                             par[c_off].fill.start_color.index)
            if par[ps].value != 'Нет':
                tmp_wrn['_'.join(par[alg_name].value.split('|'))] = (is_cor_chr(par[ps_msg].value), par[ps].value)
            else:
                tmp_wrn['_'.join(par[alg_name].value.split('|'))] = (is_cor_chr(par[ps_msg].value), 'Нет')
    return tmp, tmp_wrn


# Для им держим пока рус наименование, вид има, род, тип има по отображению, флаг наработки, флаг перестановки

def is_load_im(controller, cell, alg_name, name_par, type_im, gender, w_time, swap, cpu):
    tmp = {}
    for par in cell:
        if par[name_par].value is None:
            break
        if par[cpu].value == controller:
            tmp[par[alg_name].value] = (is_cor_chr(par[name_par].value), par[type_im].value,
                                        par[gender].value, par[19].value[0], par[w_time].value,
                                        par[swap].value)
    return tmp


def is_load_im_ao(controller, cell, alg_name, name_par, gender, im, cpu):
    tmp = {}
    for par in cell:
        if par[name_par].value is None:
            break
        if par[cpu].value == controller and par[im].value == 'Да':
            tmp[par[alg_name].value] = (is_cor_chr(par[name_par].value), 'ИМАО', par[gender].value, par[26].value[0])
    return tmp


def is_load_btn(controller, cell, alg_name, name_par, cpu):
    tmp = {}
    for par in cell:
        if par[name_par].value is None:
            break
        if par[cpu].value == controller:
            tmp['BTN_' + par[alg_name].value[par[alg_name].value.find('|')+1:]] = (is_cor_chr(par[name_par].value),)
    return tmp


# Для защит держим рус имя и ед. измерения

def is_load_pz(controller, cell, num_pz, name_par, type_protect, eunit, cpu):
    tmp = {}
    for par in cell:
        if par[name_par].value is None:
            break
        if par[type_protect].value not in 'АОссАОбсВОссВОбсАОНО':
            continue
        elif par[cpu].value == controller and par[type_protect].value in 'АОссАОбсВОссВОбсАОНО':
            '''обработка спецсимволов html в русском наименовании'''
            '''
            tmp_name = par[par_name].value.replace('<', '&lt;')
            tmp_name = tmp_name.replace('>', '&gt;')
            '''
            if par[eunit].value == '-999.0':
                tmp_eunit = str(par[eunit].comment)[str(par[eunit].comment).find(' ')+1:
                                                    str(par[eunit].comment).find('by')]
            else:
                tmp_eunit = par[eunit].value
            tmp['A' + str(num_pz).zfill(3)] = (par[type_protect].value + '. ' + is_cor_chr(par[name_par].value),
                                               tmp_eunit)
            num_pz += 1
    return tmp, num_pz


# словарь ПС -  текст сообщения и держим тип сообщения

def is_load_sig(controller, cell, alg_name, par_name, type_protect, cpu):
    tmp_wrn = {}
    tmp_ts = {}
    tmp_ppu = {}
    tmp_alr = {}
    tmp_modes = {}
    tmp_alg = {}
    for par in cell:
        if par[par_name].value is None:
            break
        if par[cpu].value == controller:
            if 'ПС' in par[type_protect].value:
                tmp_wrn[par[alg_name].value[par[alg_name].value.find('|')+1:]] = (is_cor_chr(par[par_name].value),
                                                                                  'Да (по наличию)')
            elif par[type_protect].value in 'АОссАОбсВОссВОбсАОНО' or 'АС' in par[type_protect].value:
                if 'АС' in par[type_protect].value:
                    tmp_alr[par[alg_name].value[par[alg_name].value.find('|') + 1:]] = ('АС. ' +
                                                                                        is_cor_chr(par[par_name].value),
                                                                                        'АС')
                else:
                    tmp_alr[par[alg_name].value[par[alg_name].value.find('|') + 1:]] = (par[type_protect].value + '. ' +
                                                                                        is_cor_chr(par[par_name].value),
                                                                                        'Защита')
            elif 'ТС' in par[type_protect].value:
                tmp_ts[par[alg_name].value[par[alg_name].value.find('|')+1:]] = (is_cor_chr(par[par_name].value), 'ТС')
            elif par[type_protect].value in ('ГР', 'ХР'):
                tmp_ppu[par[alg_name].value[par[alg_name].value.find('|') + 1:]] = (is_cor_chr(par[par_name].value),
                                                                                    'ППУ')
            elif 'Режим' in par[type_protect].value:
                tmp_modes[par[alg_name].value[par[alg_name].value.find('|') + 1:]] = ('Режим &quot;' +
                                                                                      is_cor_chr(par[par_name].value) +
                                                                                      '&quot;', 'Режим')
                tmp_modes['regNum'] = ['Номер режима', 'Номер режима']
            elif par[type_protect].value in ['BOOL', 'INT', 'FLOAT']:
                tmp_alg['_'.join(par[alg_name].value.split('|'))] = (is_cor_chr(par[par_name].value),
                                                                     'ALG_' + par[type_protect].value)
    return tmp_wrn, tmp_ts, tmp_ppu, tmp_alr, tmp_modes, tmp_alg


# Создаёт набор объектов возвращает его (ранее клала в промежуточный файл, теперь этого не делает, функция осталась
# в bk)

def is_create_objects_ai_ae_set(sl_cpu, template_text, object_type):
    tmp_line_object = ''
    for key, value in sl_cpu.items():
        tmp_line_object += Template(template_text).substitute(object_name=key, object_type=object_type,
                                                              object_aspect='Types.PLC_Aspect',
                                                              text_description=value[0], text_eunit=value[1],
                                                              short_name=value[2], text_fracdigits=value[3])

    return tmp_line_object.rstrip()


def is_create_objects_di(sl_cpu, template_text, object_type):
    sl_color_di = {'FF969696': '0', 'FF00B050': '1', 'FFFFFF00': '2', 'FFFF0000': '3'}
    tmp_line_object = ''
    for key, value in sl_cpu.items():
        tmp_line_object += Template(template_text).substitute(object_name=key, object_type=object_type,
                                                              object_aspect='Types.PLC_Aspect',
                                                              text_description=value[0], color_on=sl_color_di[value[1]],
                                                              color_off=sl_color_di[value[2]])

    return tmp_line_object.rstrip()


def is_create_objects_di_nku(sl_cpu, template_text, object_type, sl_wrn_nku):
    sl_color_di = {'FF969696': '0', 'FF00B050': '1', 'FFFFFF00': '2', 'FFFF0000': '3'}
    tmp_line_object = ''
    for key, value in sl_cpu.items():
        if sl_wrn_nku[key][1] == 'Нет':
            text_msg = 'Нет сообщения'
        else:
            text_msg = sl_wrn_nku[key][0]
        tmp_line_object += Template(template_text).substitute(object_name=key, object_type=object_type,
                                                              object_aspect='Types.PLC_Aspect',
                                                              text_description=value[0], color_on=sl_color_di[value[1]],
                                                              color_off=sl_color_di[value[2]],
                                                              text_msg=text_msg,
                                                              type_wrn=sl_wrn_nku[key][1])

    return tmp_line_object.rstrip()


def is_create_objects_drv(sl_drv_cpu, tuple_name_drv, template_text):
    sl_color_di = {'FF969696': '0', 'FF00B050': '1', 'FFFFFF00': '2', 'FFFF0000': '3'}
    sl_type_drv = {
        'FLOAT': 'Types.DRV_AI.DRV_AI_PLC_View',
        'INT': 'Types.DRV_INT.DRV_INT_PLC_View',
        'BOOL': 'Types.DRV_DI.DRV_DI_PLC_View'
    }
    tmp_line_object = ''
    for par in sl_drv_cpu[tuple_name_drv]:
        if par[2] == 'FLOAT':
            s_on = '0'
            s_off = '0'
            typ_msg = '-'
            unit = par[3]
            f_dig = par[4]
        elif par[2] == 'BOOL':
            s_on = sl_color_di[par[6]]
            s_off = sl_color_di[par[5]]
            typ_msg = par[7]
            unit = '-'
            f_dig = '0'
        else:
            s_on = '0'
            s_off = '0'
            typ_msg = '-'
            unit = par[3]
            f_dig = '0'
        tmp_line_object += Template(template_text).substitute(object_name=par[0], object_type=sl_type_drv[par[2]],
                                                              object_aspect='Types.PLC_Aspect',
                                                              text_description=par[1], type_msg=typ_msg,
                                                              color_off=s_off, color_on=s_on, text_eunit=unit,
                                                              text_fracdigits=f_dig)
    return tmp_line_object.rstrip()


# В словаре ДРВ - (драйвер, алг. имя) : рус наим, тип пер., ед. измер, чило знаков, цвет наличия, цвет отсутствия,
# тип сообщения

def is_load_drv(controller, cell, alg_name, name_par, eunit, type_sig, type_msg, c_on, c_off, f_dig, cpu):
    tmp = {}
    for par in cell:
        if par[name_par].value is None:
            break
        if par[cpu].value == controller:
            drv_name = par[is_f_ind(cell[0], 'Драйвер')].value
            drv_par = par[alg_name].value
            tmp[(drv_name, drv_par)] = [is_cor_chr(par[name_par].value), par[type_sig].value, par[eunit].value,
                                        par[f_dig].value, par[c_on].fill.start_color.index,
                                        par[c_off].fill.start_color.index, par[type_msg].value]

    return tmp


def is_create_objects_im(sl_cpu, template_text):
    sl_im_plc = {'ИМ1Х0': 'IM1x0.IM1x0_PLC_View', 'ИМ1Х1': 'IM1x1.IM1x1_PLC_View', 'ИМ1Х2': 'IM1x2.IM1x2_PLC_View',
                 'ИМ2Х2': 'IM2x2.IM2x2_PLC_View', 'ИМ2Х4': 'IM2x2.IM2x4_PLC_View', 'ИМ1Х0и': 'IM1x0.IM1x0_PLC_View',
                 'ИМ1Х1и': 'IM1x1.IM1x1_PLC_View', 'ИМ1Х2и': 'IM1x2.IM1x2_PLC_View', 'ИМ2Х2с': 'IM2x2.IM2x2_PLC_View',
                 'ИМАО': 'IM_AO.IM_AO_PLC_View'}

    sl_gender = {'С': '0', 'М': '1', 'Ж': '2'}

    tmp_line_object = ''
    for key, value in sl_cpu.items():
        tmp_line_object += Template(template_text).substitute(object_name=key,
                                                              object_type='Types.' + sl_im_plc[value[1]],
                                                              object_aspect='Types.PLC_Aspect',
                                                              text_description=value[0], gender=sl_gender[value[2]],
                                                              start_view=value[3])

    return tmp_line_object.rstrip()


def is_create_objects_btn_cnt(sl_cpu, template_text, object_type):
    tmp_line_object = ''
    for key, value in sl_cpu.items():
        tmp_line_object += Template(template_text).substitute(object_name=key, object_type=object_type,
                                                              object_aspect='Types.PLC_Aspect',
                                                              text_description=value[0])

    return tmp_line_object.rstrip()


def is_create_objects_pz(sl_cpu, template_text, object_type):
    tmp_line_object = ''
    for key, value in sl_cpu.items():
        tmp_line_object += Template(template_text).substitute(object_name=key, object_type=object_type,
                                                              object_aspect='Types.PLC_Aspect',
                                                              text_description=value[0],
                                                              text_eunit=value[1])

    return tmp_line_object.rstrip()


def is_create_objects_sig(sl_cpu, template_text):
    sl_type_sig = {
        'Да (по наличию)': 'Types.WRN_On.WRN_On_PLC_View',
        'Да (по отсутствию)': 'Types.WRN_Off.WRN_Off_PLC_View',
        'ТС': 'Types.TS.TS_PLC_View',
        'ППУ': 'Types.PPU.PPU_PLC_View',
        'Защита': 'Types.ALR.ALR_PLC_View',
        'АС': 'Types.ALR.ALR_PLC_View',
        'Режим': 'Types.MODES.MODES_PLC_View',
        'Номер режима': 'Types.MODES.regNum_PLC_View',
        'ALG_BOOL': 'Types.ALG.ALG_BOOL_PLC_View',
        'ALG_INT': 'Types.ALG.ALG_INT_PLC_View',
        'ALG_FLOAT': 'Types.ALG.ALG_FLOAT_PLC_View'
    }
    tmp_line_object = ''
    for key, value in sl_cpu.items():
        tmp_line_object += Template(template_text).substitute(object_name=key,
                                                              object_type=sl_type_sig[value[1]],
                                                              object_aspect='Types.PLC_Aspect',
                                                              text_description=value[0])
    return tmp_line_object.rstrip()


def is_create_objects_diag(sl):
    # Считываем файлы-шаблоны для диагностики модулей
    with open(os.path.join('Template', 'Temp_m547a'), 'r', encoding='UTF-8') as f:
        tmp_m547a = f.read()
    with open(os.path.join('Template', 'Temp_m537v_m932c_2n'), 'r', encoding='UTF-8') as f:
        tmp_m537v = f.read()
    with open(os.path.join('Template', 'Temp_m557d_m557o'), 'r', encoding='UTF-8') as f:
        tmp_m557d = f.read()
    with open(os.path.join('Template', 'Temp_cpu'), 'r', encoding='UTF-8') as f:
        template_text_cpu = f.read()

    sl_modules_temp = {
        'M547A': tmp_m547a,
        'M537V': tmp_m537v,
        'M557D': tmp_m557d,
        'M557O': tmp_m557d,
        'M932C_2N': tmp_m537v
    }
    sl_type_modules = {
        'M903E': 'Types.DIAG_CPU.DIAG_CPU_PLC_View',
        'M991E': 'Types.DIAG_CPU.DIAG_CPU_PLC_View',
        'M547A': 'Types.DIAG_M547A.DIAG_M547A_PLC_View',
        'M537V': 'Types.DIAG_M537V.DIAG_M537V_PLC_View',
        'M932C_2N': 'Types.DIAG_M932C2_N.DIAG_M932C2_N_PLC_View',
        'M557D': 'Types.DIAG_M557D.DIAG_M557D_PLC_View',
        'M557O': 'Types.DIAG_M557O.DIAG_M557O_PLC_View'
    }
    tmp_line_object = ''
    for key, value in sl.items():
        if value[0] in ('M903E', 'M991E'):
            tmp_line_object += Template(template_text_cpu).substitute(object_name=key,
                                                                      object_type=sl_type_modules[value[0]],
                                                                      object_aspect='Types.PLC_Aspect',
                                                                      text_description=f'Диагностика мастер-модуля {key} ({value[0]})',
                                                                      short_name=key)
        elif value[0] in ('M547A',):
            tmp_line_object += Template(sl_modules_temp[value[0]]).substitute(object_name=key,
                                                                              object_type=sl_type_modules[value[0]],
                                                                              object_aspect='Types.PLC_Aspect',
                                                                              text_description=f'Диагностика модуля {key} ({value[0]})',
                                                                              short_name=key,
                                                                              Channel_1=value[1][0],
                                                                              Channel_2=value[1][1],
                                                                              Channel_3=value[1][2],
                                                                              Channel_4=value[1][3],
                                                                              Channel_5=value[1][4],
                                                                              Channel_6=value[1][5],
                                                                              Channel_7=value[1][6],
                                                                              Channel_8=value[1][7],
                                                                              Channel_9=value[1][8],
                                                                              Channel_10=value[1][9],
                                                                              Channel_11=value[1][10],
                                                                              Channel_12=value[1][11],
                                                                              Channel_13=value[1][12],
                                                                              Channel_14=value[1][13],
                                                                              Channel_15=value[1][14],
                                                                              Channel_16=value[1][15])
        elif value[0] in ('M537V', 'M932C_2N'):
            tmp_line_object += Template(sl_modules_temp[value[0]]).substitute(object_name=key,
                                                                              object_type=sl_type_modules[value[0]],
                                                                              object_aspect='Types.PLC_Aspect',
                                                                              text_description=f'Диагностика модуля {key} ({value[0]})',
                                                                              short_name=key,
                                                                              Channel_1=value[1][0],
                                                                              Channel_2=value[1][1],
                                                                              Channel_3=value[1][2],
                                                                              Channel_4=value[1][3],
                                                                              Channel_5=value[1][4],
                                                                              Channel_6=value[1][5],
                                                                              Channel_7=value[1][6],
                                                                              Channel_8=value[1][7])
        elif value[0] in ('M557D', 'M557O'):
            tmp_line_object += Template(sl_modules_temp[value[0]]).substitute(object_name=key,
                                                                              object_type=sl_type_modules[value[0]],
                                                                              object_aspect='Types.PLC_Aspect',
                                                                              text_description=f'Диагностика модуля {key} ({value[0]})',
                                                                              short_name=key,
                                                                              Channel_1=value[1][0],
                                                                              Channel_2=value[1][1],
                                                                              Channel_3=value[1][2],
                                                                              Channel_4=value[1][3],
                                                                              Channel_5=value[1][4],
                                                                              Channel_6=value[1][5],
                                                                              Channel_7=value[1][6],
                                                                              Channel_8=value[1][7],
                                                                              Channel_9=value[1][8],
                                                                              Channel_10=value[1][9],
                                                                              Channel_11=value[1][10],
                                                                              Channel_12=value[1][11],
                                                                              Channel_13=value[1][12],
                                                                              Channel_14=value[1][13],
                                                                              Channel_15=value[1][14],
                                                                              Channel_16=value[1][15],
                                                                              Channel_17=value[1][16],
                                                                              Channel_18=value[1][17],
                                                                              Channel_19=value[1][18],
                                                                              Channel_20=value[1][19],
                                                                              Channel_21=value[1][20],
                                                                              Channel_22=value[1][21],
                                                                              Channel_23=value[1][22],
                                                                              Channel_24=value[1][23],
                                                                              Channel_25=value[1][24],
                                                                              Channel_26=value[1][25],
                                                                              Channel_27=value[1][26],
                                                                              Channel_28=value[1][27],
                                                                              Channel_29=value[1][28],
                                                                              Channel_30=value[1][29],
                                                                              Channel_31=value[1][30],
                                                                              Channel_32=value[1][31])
    return tmp_line_object.rstrip()


def check_diff_file(check_path, file_name, new_data, message_print):
    # Если в целевой(указанной) папке уже есть формируемый файл
    if os.path.exists(os.path.join(check_path, file_name)):
        # Формирурем новый
        # new_out_nku = Template(tmp_global).substitute(dp_node=tmp_group_nku)
        # считываем имеющейся файл
        with open(os.path.join(check_path, file_name), 'r', encoding='UTF-8') as f_check:
            old_data = f_check.read()
        # Если отличаются
        if new_data != old_data:
            # Если нет папки Old, то создаём её
            if not os.path.exists(os.path.join(check_path, 'Old')):
                os.mkdir(os.path.join(check_path, 'Old'))
            # Переносим старую файл в папку Old
            os.replace(os.path.join(check_path, file_name),
                       os.path.join(check_path, 'Old', file_name))
            sleep(0.1)
            # Записываем новый файл
            with open(os.path.join(check_path, file_name), 'w', encoding='UTF-8') as f_wr:
                f_wr.write(new_data)
            # пишем, что надо заменить
            print(message_print)
            with open('Required_change.txt', 'a', encoding='UTF-8') as f_change:
                f_change.write(f'{datetime.datetime.now()} - {message_print}\n')
    # Если в целевой(указанной) папке нет формируемого файла, то создаём его и пишем, что заменить
    else:
        with open(os.path.join(check_path, file_name), 'w', encoding='UTF-8') as f_wr:
            f_wr.write(new_data)
        print(message_print)
        with open('Required_change.txt', 'a', encoding='UTF-8') as f_change:
            f_change.write(f'{datetime.datetime.now()} - {message_print}\n')
