import datetime
import openpyxl
import logging
import warnings
import os
from func_for_v3 import *
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

try:
    # all_CPU = ()  # кортеж контроллеров
    pref_IP = ()  # кортеж префиксов IP
    sl_object_all = {}  # {(Объект, рус имя объекта, индекс объекта):
    # {контроллер: (ip основной, ip резервный, индекс объекта)} }

    # path_config = input('Укажите путь до конфигуратора\n')
    with open('Source_list_config.txt', 'r', encoding='UTF-8') as f:
        path_config = f.readline().strip()

    print(datetime.datetime.now(), '- Начало сборки файлов')

    file_config = 'UnimodCreate.xlsm'

    # Ищем файл конфигуратора в указанном каталоге
    for file in os.listdir(path_config):
        if file.endswith('.xlsm') or file.endswith('.xls'):
            file_config = file
            break

    # Считываем файл-шаблон для объекта IOS
    with open(os.path.join('Template', 'Temp_IOS'), 'r', encoding='UTF-8') as f:
        tmp_ios = f.read()

    # Считываем файл-шаблон для AI  AE SET
    with open(os.path.join('Template', 'Temp_AIAESET'), 'r', encoding='UTF-8') as f:
        tmp_object_AIAESET = f.read()
    # Считываем файл-шаблон для DI
    with open(os.path.join('Template', 'Temp_DI'), 'r', encoding='UTF-8') as f:
        tmp_object_DI = f.read()

    print(datetime.datetime.now(), '- Начало 1')
    book = openpyxl.open(os.path.join(path_config, file_config))  # , read_only=True
    # читаем список всех контроллеров
    print(datetime.datetime.now(), '- Начало 2')
    sheet = book['Настройки']  # worksheets[1]
    '''
    cells = sheet['B2': 'B22']
    for p in cells:
        if p[0].value is not None:
            all_CPU += (p[0].value,)
    '''
    # Читаем префиксы IP адреса ПЛК(нужно продумать про новые конфигураторы)
    cells = sheet['A1': 'B' + str(sheet.max_row)]
    for p in cells:
        if p[0].value == 'Cетевая часть адреса основной сети (связь с CPU)':
            pref_IP += (p[1].value + '.',)
        if p[0].value == 'Cетевая часть адреса резервной сети (связь с CPU)':
            pref_IP += (p[1].value + '.',)
            break
    # Читаем состав объектов и заполняем sl_object_all
    cells = sheet['A24': 'R38']
    for p in cells:
        if p[1].value is not None:
            # промежуточный словарь, для загрузки в общий
            # {контроллер: (ip основной, ip резервный)}
            sl_tmp = {}
            for i in range(12, 17):
                if p[i].value == 'ON':
                    last_dig_ip = p[i - 5].value
                    tmp_dig_ip1 = (last_dig_ip if '(' not in last_dig_ip else last_dig_ip[:last_dig_ip.find('(')])
                    tmp_dig_ip2 = (last_dig_ip if '(' not in last_dig_ip else last_dig_ip[last_dig_ip.find('(') + 1:-1])
                    sl_tmp[p[i - 10].value] = (tmp_dig_ip1, tmp_dig_ip2)
            sl_object_all[p[1].value, p[2].value, p[0].value.replace('Объект', '').strip()] = sl_tmp

    # Чистим файлы с прошлой сборки
    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера
        for cpu in sl_object_all[objects]:
            ff = open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'w', encoding='UTF-8')
            ff.close()
            ff = open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'w', encoding='UTF-8')
            ff.close()

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера
        for cpu in sl_object_all[objects]:
            # Записываем стартовую информацию ПЛК аспекта
            with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write('<omx xmlns="system" xmlns:dp="automation.deployment" xmlns:trei="trei" '
                        'xmlns:ct="automation.control">\n')
                f.write(f'  <trei:trei name="PLC_{cpu}_{objects[2]}" >\n')
                f.write('    <trei:master-module name="CPU" >\n')
                f.write(f'      <trei:ethernet-adapter name="Eth1" '
                        f'address="{pref_IP[0]}{sl_object_all[objects][cpu][0]}" />\n')
                f.write(f'      <trei:ethernet-adapter name="Eth2" '
                        f'address="{pref_IP[1]}{sl_object_all[objects][cpu][1]}" />\n')
                f.write(f'      <trei:unet-server name="UnetServer" '
                        f'address-map="PLC_{cpu}_{objects[2]}.CPU.Tree.UnetAddressMap" '
                        f'port="6001"/>\n')
                f.write('      <dp:application-object name="Tree" access-level="public" >\n')
        # Записываем стартовую информацию IOS-аспекта
        with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
            f.write('<omx xmlns="system" xmlns:dp="automation.deployment" xmlns:trei="trei" '
                    'xmlns:ct="automation.control">\n')
            f.write(f'    <ct:object name="{objects[0]}" access-level="public">\n')
            f.write(f'      <attribute type="unit.System.Attributes.Description" value="{objects[1]}" />\n')
            # Добавляем агрегаторы
            f.write(f'      <ct:object name="Agregator_Important_IOS" '
                    f'base-type="Types.MSG_Agregator.Agregator_Important_IOS" '
                    f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
            f.write(f'      <ct:object name="Agregator_LessImportant_IOS" '
                    f'base-type="Types.MSG_Agregator.Agregator_LessImportant_IOS" '
                    f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
            f.write(f'      <ct:object name="Agregator_N_IOS" '
                    f'base-type="Types.MSG_Agregator.Agregator_N_IOS" '
                    f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
            f.write(f'      <ct:object name="Agregator_Repair_IOS" '
                    f'base-type="Types.MSG_Agregator.Agregator_Repair_IOS" '
                    f'aspect="Types.IOS_Aspect" access-level="public"/>\n')

    # Измеряемые
    write_ai_ae(sheet=book['Измеряемые'], sl_object_all=sl_object_all, tmp_object_aiaeset=tmp_object_AIAESET,
                tmp_ios=tmp_ios, group_objects='AI')
    # Расчетные
    write_ai_ae(sheet=book['Расчетные'], sl_object_all=sl_object_all, tmp_object_aiaeset=tmp_object_AIAESET,
                tmp_ios=tmp_ios, group_objects='AE')
    # Дискретные
    write_di(sheet=book['Входные'], sl_object_all=sl_object_all, tmp_object_di=tmp_object_DI,
             tmp_ios=tmp_ios, group_objects='DI')

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Добавляем элемент адресной карты и закрываем стандартную информацию
            # Закрываем стандартную информацию
            with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write('	    <trei:unet-address-map name="UnetAddressMap" />\n')
                f.write('      </dp:application-object>\n')
                f.write('    </trei:master-module>\n')
                f.write(f'  </trei:trei>\n')
                f.write('</omx>\n')
        # Закрываем стартовую информацию IOS-аспекта
        with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
            f.write(f'    </ct:object>\n')
            f.write('</omx>\n')

    book.close()
    print(datetime.datetime.now(), 'Окончание сборки всех файлов')
except (Exception, KeyError):
    print('Произошла ошибка выполнения')
    logging.basicConfig(filename='error.log', filemode='a', datefmt='%d.%m.%y %H:%M:%S',
                        format='%(levelname)s - %(message)s - %(asctime)s')
    logging.exception("Ошибка выполнения")
