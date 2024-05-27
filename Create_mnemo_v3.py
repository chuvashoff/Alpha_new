# import socket
import uuid
import sys
from math import floor  # , ceil
from func_for_v3 import *
from collections import ChainMap
from json import dumps as json_dumps, load as json_load
from tkinter import Tk, font
# from difflib import SequenceMatcher


def get_text_width(text, font_name, font_size):
    root = Tk()
    font_obj = font.Font(family=font_name, size=font_size)
    width = font_obj.measure(text)
    root.destroy()  # закрываем временный экземпляр Tk()
    return width


def check_diff_mnemo(new_data, check_path, file_name_check, message_print):
    def replace_uuid(input_string):
        pattern = r'uuid=".+?"'
        replacement = 'id'
        output_string = re.sub(pattern, replacement, input_string)
        return output_string

    # print(os.path.join(check_path, file_name_check))
    if os.path.exists(os.path.join(check_path, file_name_check)):
        # считываем имеющейся файл
        with open(os.path.join(check_path, file_name_check), 'r', encoding='UTF-8') as f_check:
            old_data = f_check.read()
        # differ = difflib.Differ()
        # diff = differ.compare(new_data.split('\n'), old_data.split('\n'))
        # matcher = SequenceMatcher(None, replace_uuid(new_data), replace_uuid(old_data))
        # print(matcher.ratio(), matcher.ratio() < 1.0)
        # Если данные отличаются
        # if matcher.ratio() < 1.0:
        if replace_uuid(new_data) != replace_uuid(old_data):
            # Если нет папки Old, то создаём её
            if not os.path.exists(os.path.join(check_path, 'Old')):
                os.mkdir(os.path.join(check_path, 'Old'))
            # Переносим старую файл в папку Old
            os.replace(os.path.join(check_path, file_name_check),
                       os.path.join(check_path, 'Old', file_name_check))
            sleep(0.5)
            # Записываем новый файл
            with open(os.path.join(check_path, file_name_check), 'w', encoding='UTF-8') as f_wr:
                f_wr.write(new_data)
            # пишем, что надо заменить
            print(message_print)
            with open('Required_change.txt', 'a', encoding='UTF-8') as f_change:
                f_change.write(f'{datetime.datetime.now()} - {message_print}\n')
    # Если в целевой(указанной) папке нет формируемого файла, то создаём его и пишем, что заменить
    else:
        with open(os.path.join(check_path, file_name_check), 'w', encoding='UTF-8') as f_wr:
            f_wr.write(new_data)
        print(message_print)
        with open('Required_change.txt', 'a', encoding='UTF-8') as f_change:
            f_change.write(f'{datetime.datetime.now()} - {message_print}\n')
    return


def multiple_replace_xml_mnemo(target_str):
    replace_values = {'access_modifier': 'access-modifier', 'display_name': 'display-name',
                      'type_id': 'type-id', 'base_': 'base-',
                      'frame_link': 'frame-link', 'form_action': 'form-action', 'form_by_id': 'form-by-id',
                      '<forCDATA/>': '<![CDATA[here.NameOpened]]>',
                      'yopta_on': '<', 'yopta_off': '>'}
    # получаем заменяемое: подставляемое из словаря в цикле
    for i, j in replace_values.items():
        # меняем все target_str на подставляемое
        target_str = target_str.replace(i, j)
    return target_str


# Функция создания мнемосхем параметров
def create_mnemo_param(name_list: str, name_group: str, name_page: str, base_type_param: str,
                       size_shirina: int, size_vysota: int, sl_param: dict, sl_object_all: dict, tuple_mnemo: tuple = ""):
    # print(sl_param)
    sl_page_uuid = {}
    # uuid.uuid4()
    if not os.path.exists(os.path.join('File_for_Import', 'Mnemo', f'{name_page}_Mnemo')):
        os.mkdir(os.path.join('File_for_Import', 'Mnemo', f'{name_page}_Mnemo'))
    if not os.path.exists(os.path.join('File_for_Import', 'Mnemo', f'{name_page}_Mnemo', 'Systemach')):
        os.mkdir(os.path.join('File_for_Import', 'Mnemo', f'{name_page}_Mnemo', 'Systemach'))

    # Чистим старые мнемосхемы ПЗ
    #  os.path.dirname(sys.argv[0])

    # for file in os.listdir(os.path.join(os.path.abspath(os.curdir), 'File_for_Import',
    #                                     'Mnemo', f'{name_page}_Mnemo')):
    #     if file.endswith('.omobj'):
    #         os.remove(os.path.join(os.path.abspath(os.curdir), 'File_for_Import',
    #                                'Mnemo', f'{name_page}_Mnemo', file))

    # СЛОВАРЬ УНИКАЛЬНЫХ ОБЪЕКТОВ
    # Формируем словарь вида {кортеж контроллеров: (Объект, рус имя объекта, индекс объекта)}
    # При этом, если есть полное совпадение контроллеров, то дублирования нет
    sl_cpus_object = {}
    for obj, sl_cpu in sl_object_all.items():
        cpus = tuple(sl_cpu.keys())  # cpus = tuple(sorted(sl_cpu.keys()))
        if cpus not in sl_cpus_object:
            sl_cpus_object[cpus] = obj

    sl_size = {
        '1920x900': (1780, 900, 780),
        '1920x780': (1780, 780, 780)
    }
    # Словарь ID для типовых структур, возможно потом будет считываться с файла или как-то по-другому
    sl_uuid_base_default = {
        '00_SubPage': '3fe01b7a-fed7-41d2-aa19-ca3e78391035',
        'Text': '21d59f8d-2ca4-4592-92ca-b4dc48992a0f',
        'S_A_INP_Param': '937a763e-eb58-4ded-b5a0-b58f4abd7ee7',
        'ApSource': '966603da-f05e-4b4d-8ef0-919efbf8ab2c',
        'string': '76403785-f3d5-41a7-9eb6-d19d2aa2d95d',
        'S_D_INP_Param': 'dbb862d3-e7bc-46b7-95bf-42819dd27277',
        'S_CNT': '6bd7cc8c-2d47-44cb-8e62-25b85831730b',
        '00_SubBase': '99471dea-1c95-471c-9960-b4f7a539d437',
        'Frame': '71f78e19-ef99-4133-a029-2968b14f02b6',
        'notifying_string': '14976fbf-36ab-415f-abc3-9f8fdc217351',
        'ExtPageButton': '2c2d6f3d-f500-4be6-b80c-620853cd99e3',
        'DebugTool': '43946044-139a-43f4-a7b8-19a6074ffc56',
        'S_CDO_Param': 'a3ddb55c-c549-4179-9564-f12cc1d85879'
    }
    try:
        if os.path.exists(os.path.join('Template_Alpha', 'Systemach', 'Mnemo', f'uuid_base_elements.json')):
            with open(os.path.join('Template_Alpha', 'Systemach', 'Mnemo', f'uuid_base_elements.json'), 'r',
                      encoding='UTF-8') as f_sig:
                text_json = json_load(f_sig)
            sl_uuid_base = text_json
        else:
            print('Файл Systemach/Mnemo/uuid_base_elements.json не найден, '
                  'uuid базовых элементов будут определены по умолчанию')
            sl_uuid_base = sl_uuid_base_default
    except Exception:
        print('Файл Systemach/Mnemo/uuid_base_elements.json заполнен некорректно, '
              'uuid базовых элементов будут определены по умолчанию')
        sl_uuid_base = sl_uuid_base_default

    # Словарь размеров элементов, тут по заполнению всё понятно
    sl_size_element = {'AI': {'size_el': ((591 + 2), (24 + 6)), 'size_text': (590.567, 24)},
                       'AE': {'size_el': ((591 + 2), (24 + 6)), 'size_text': (590.567, 24)},
                       'DI': {'size_el': ((525 + 50), (26 + 6)), 'size_text': (524.69, 26)},
                       'System.CNT': {'size_el': ((545 + 30), (24 + 6)), 'size_text': (545, 24)},
                       'System.CDO': {'size_el': ((591 + 2), (40 + 6)), 'size_text': (590.567, 24)},
                       }
    # Словарь расположения первого элемента, тут вроде всё понятно тоже - первый X, второй Y
    sl_start = {'AI': (3, 15),
                'AE': (3, 15),
                'DI': (50, 15),
                'System.CNT': (30, 15),
                'System.CDO': (3, 15)
                }
    gor_base = sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1780, 900))[0]
    vert_base = sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1780, 900))[1]
    window_height = sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1780, 900, 780))[2]
    # Узнаём, сколько целых параметров влезет по горизонтали
    # два пикселя по горизонтали между элементами
    par_gor_count = floor(gor_base / sl_size_element.get(name_group, {'size_el': (500, 0)})['size_el'][0])
    # Узнаём, сколько целых параметров влезет по вертикали
    # 6 пикселей по вертикали между элементами, 90 - запас для кнопок переключения
    par_vert_count = floor((vert_base - 90 - sl_start.get(name_group, (0, 500))[1]) /
                           sl_size_element.get(name_group, {'size_el': (0, 500)})['size_el'][1])
    # Узнаём количество параметров на один лист
    par_one_list = (par_gor_count * par_vert_count)
    # Узнаём количество требуемых листов, деля количество требуемых элементов на количество на одном листе
    # num_par = sum(len(i) for i in tuple(sl_param.values())) + len(tuple(sl_param.keys()))
    # number_list = ceil(num_par / par_one_list)
    # print(name_group, par_one_list)
    # Для каждого УНИКАЛЬНОГО объекта(уникального ранее определили по составу ПЛК) создаём мнемосхему 01_FormAlg
    # только в том случае, если у него определены какие-то режимы
    for cpus, obj in sl_cpus_object.items():
        sl_param_object = {}
        for plc in (_ for _ in cpus if _ in set(sl_param.keys())):  # sorted(set(set(cpus) & set(sl_param.keys())))
            for node in sl_param[plc]:
                if node not in sl_param_object:
                    sl_param_object[node] = sl_param[plc][node]
                else:
                    sl_param_object[node].extend(sl_param[plc][node])
            # sl_param_object.update(sl_param[plc])

        # Если параметров нет, то скипаем
        if not sl_param_object:
            continue
        # Если задан кортеж сортировки, то сортируем
        if tuple_mnemo:
            # print(name_list, '----------------')
            sl_param_object = {node: sl_param_object.get(node) for node in tuple_mnemo if sl_param_object.get(node)}
        # for i in sl_param_object:
        #     print(name_page, cpus, i, len(sl_param_object[i]))
        # # print(cpus, sl_param_object)
        start_list = 1
        count = 0
        # sl_list_par = {номер листа: {узел: кортеж параметров}}
        # При разбивке на листы учитывается количество параметров на листе, в том числе само наименование узла
        sl_list_par = {}
        for node in sl_param_object:
            count += 1
            if count == par_one_list:
                count = 0
                start_list += 1
            for j in range(len(sl_param_object[node])):
                count += 1
                sl_param_object[node][j] = (start_list, sl_param_object[node][j])
                if count == par_one_list:
                    count = 1
                    start_list += 1

        # for node in sl_param:
        #     print(node)
        #     print(sl_param[node])
        for node in sl_param_object:
            for par in sl_param_object[node]:
                # Если в словаре ещё нет данного листа, то создаём там пустой словарь
                if par[0] not in sl_list_par:
                    sl_list_par[par[0]] = {}
                # Если в словаре листа нет текущего узла, то добавляем туда узел с пустым кортежем будущих переменных
                if node not in sl_list_par[par[0]]:
                    sl_list_par[par[0]].update({node: tuple()})
                # После этого на соответствующем листе в соответствующий узел добавляем перебираемый параметр
                sl_list_par[par[0]][node] += (par[1],)

        if not os.path.exists(os.path.join('File_for_Import', 'Mnemo', f'{name_page}_Mnemo', 'Systemach', 'uuid')):
            with open(os.path.join('File_for_Import', 'Mnemo', f'{name_page}_Mnemo', 'Systemach', 'uuid'),
                      'w', encoding='UTF-8') as f_uuid_write:
                if sl_list_par:
                    generate_uuid = uuid.uuid4()
                    sl_page_uuid[f"{name_page}_0_{obj[0]}"] = f'{generate_uuid}'
                    f_uuid_write.write(f'{name_page}_0_{obj[0]}:{generate_uuid}\n')
                for number_list in sl_list_par:
                    generate_uuid = uuid.uuid4()
                    sl_page_uuid[f"{name_page}_{number_list}_{obj[0]}"] = f'{generate_uuid}'
                    f_uuid_write.write(f'{name_page}_{number_list}_{obj[0]}:{generate_uuid}\n')
        else:
            # Если файл существует, то считываем и записываем в словарь
            with open(os.path.join('File_for_Import', 'Mnemo', f'{name_page}_Mnemo', 'Systemach', 'uuid'),
                      'r', encoding='UTF-8') as f_uuid_read:
                for line in f_uuid_read:
                    lst_line = line.strip().split(':')
                    sl_page_uuid[lst_line[0]] = lst_line[1]
            # Если после вычитывания не обнаружили формы для отсутствующих объектов
            # (например, увеличилось количество объектов), то дозаписываем
            with open(os.path.join('File_for_Import', 'Mnemo', f'{name_page}_Mnemo', 'Systemach', 'uuid'),
                      'a', encoding='UTF-8') as f_uuid_write:
                if f"{name_page}_0_{obj[0]}" not in sl_page_uuid and sl_list_par:
                    generate_uuid = uuid.uuid4()
                    sl_page_uuid[f"{name_page}_0_{obj[0]}"] = f'{generate_uuid}'
                    f_uuid_write.write(f'{name_page}_0_{obj[0]}:{generate_uuid}\n')
                for number_list in sl_list_par:
                    if f"{name_page}_{number_list}_{obj[0]}" not in sl_page_uuid:
                        generate_uuid = uuid.uuid4()
                        sl_page_uuid[f"{name_page}_{number_list}_{obj[0]}"] = f'{generate_uuid}'
                        f_uuid_write.write(f'{name_page}_{number_list}_{obj[0]}:{generate_uuid}\n')
        # for li in sl_list_par:
        #     for node in sl_list_par[li]:
        #         print(li, node)
        #         print(li, sl_list_par[li][node])
        num_text = 0
        # sl_page_uuid = {}
        # Для каждого листа в словаре листов с параметрами...
        # print(cpus, sl_list_par)
        for page in sl_list_par:
            # Вносим инфу в словарь
            # ...создаём родительский узел листа
            # sl_page_uuid[f"{name_page}_{page}"] = uuid.uuid4()
            root_type = ET.Element(
                'type', access_modifier="private", name=f"{name_page}_{page}_{obj[0]}",
                display_name=f"{name_page}_{page}_{obj[0]}",
                uuid=f"{sl_page_uuid[f'{name_page}_{page}_{obj[0]}']}",
                base_type="00_SubPage",
                base_type_id=f"{sl_uuid_base.get('00_SubPage', '3fe01b7a-fed7-41d2-aa19-ca3e78391035')}",
                ver="3")
            # ...заполняем стандартную информацию
            ET.SubElement(root_type, 'designed', target='X', value="0", ver="3")
            ET.SubElement(root_type, 'designed', target='Y', value="0", ver="3")
            ET.SubElement(root_type, 'designed', target='ZValue', value="0", ver="3")
            ET.SubElement(root_type, 'designed', target='Rotation', value="0", ver="3")
            ET.SubElement(root_type, 'designed', target='Scale', value="1", ver="3")
            ET.SubElement(root_type, 'designed', target='Visible', value="true", ver="3")
            ET.SubElement(root_type, 'designed', target='Enabled', value="true", ver="3")
            ET.SubElement(root_type, 'designed', target='Tooltip', value="", ver="3")
            ET.SubElement(root_type, 'designed', target='Width', value=f"{gor_base}", ver="3")
            ET.SubElement(root_type, 'designed', target='Height', value=f"{vert_base}", ver="3")
            ET.SubElement(root_type, 'designed', target='PenColor', value="4278190080", ver="3")
            ET.SubElement(root_type, 'designed', target='PenStyle', value="0", ver="3")
            ET.SubElement(root_type, 'designed', target='PenWidth', value="1", ver="3")
            ET.SubElement(root_type, 'designed', target='BrushColor', value="0xffbfbfbf", ver="3")
            ET.SubElement(root_type, 'designed', target="BrushStyle", value="1", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowX", value="0", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowY", value="0", ver="3")

            # Вносим размеры мнемосхемы, пока так, позже может измениться
            ET.SubElement(root_type, 'designed', target="WindowWidth", value=f"{size_shirina}", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowHeight", value=f"{window_height}", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowCaption", value=f"{page}", ver="3")

            ET.SubElement(root_type, 'designed', target="ShowWindowCaption", value="true", ver="3")
            ET.SubElement(root_type, 'designed', target="ShowWindowMinimize", value="true", ver="3")
            ET.SubElement(root_type, 'designed', target="ShowWindowMaximize", value="true", ver="3")
            ET.SubElement(root_type, 'designed', target="ShowWindowClose", value="true", ver="3")
            ET.SubElement(root_type, 'designed', target="AlwaysOnTop", value="false", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowSizeMode", value="2", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowBorderStyle", value="1", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowState", value="0", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowScalingMode", value="0", ver="3")
            ET.SubElement(root_type, 'designed', target="MonitorNumber", value="0", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowPosition", value="1", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowCloseMode", value="0", ver="3")

            x_start = sl_start.get(name_group, (3, 10))[0]
            y_start = sl_start.get(name_group, (3, 10))[1]
            x_point = x_start
            y_point = y_start
            count_par = 0
            # Для каждого узла и его параметров делаем
            for node, pars in sl_list_par[page].items():
                num_text += 1
                # Добавляем оттекстовку узла
                name_sub_element = ET.SubElement(root_type, 'object', access_modifier="private",
                                                 name=f"Text_{num_text}",
                                                 display_name=f"Text_{num_text}",
                                                 uuid=f"{uuid.uuid4()}",
                                                 base_type="Text",
                                                 base_type_id=sl_uuid_base.get('Text', ''), ver="3")
                ET.SubElement(name_sub_element, 'designed', target="X", value=f"{x_point}", ver="3")
                ET.SubElement(name_sub_element, 'designed', target="Y", value=f"{y_point}", ver="3")
                y_point += sl_size_element.get(name_group, {'size_el': (0, 500)})['size_el'][1]
                count_par += 1
                if count_par == par_vert_count:
                    count_par = 0
                    y_point = y_start
                    x_point += sl_size_element.get(name_group, {'size_el': (500, 0)})['size_el'][0]
                ET.SubElement(name_sub_element, 'designed', target="ZValue", value="0", ver="3")
                ET.SubElement(name_sub_element, 'designed', target="Rotation", value="0", ver="3")
                ET.SubElement(name_sub_element, 'designed', target="Scale", value="1", ver="3")
                ET.SubElement(name_sub_element, 'designed', target="Visible", value="true", ver="3")
                ET.SubElement(name_sub_element, 'designed', target="Enabled", value="true", ver="3")
                ET.SubElement(name_sub_element, 'designed', target="Tooltip", value="", ver="3")

                # Размеры текста пока задаём жёстко
                width_text = sl_size_element.get(name_group, {'size_text': (500, 0)})['size_text'][0]
                height_text = sl_size_element.get(name_group, {'size_text': (0, 500)})['size_text'][1]
                ET.SubElement(name_sub_element, 'designed', target="Width", value=f"{width_text}", ver="3")
                ET.SubElement(name_sub_element, 'designed', target="Height", value=f"{height_text}", ver="3")

                ET.SubElement(name_sub_element, 'designed', target="Text", value=f"{node}", ver="3")
                ET.SubElement(name_sub_element, 'designed', target="Font",
                              value="PT Astra Sans,11,-1,5,50,0,0,0,0,0,Обычный", ver="3")
                ET.SubElement(name_sub_element, 'designed', target="FontColor", value="0xff000000", ver="3")
                ET.SubElement(name_sub_element, 'designed', target="TextAlignment", value="132", ver="3")
                ET.SubElement(name_sub_element, 'designed', target="Opacity", value="1", ver="3")

                # Для каждого параметра создаём узлы xml-ки
                for par in pars:
                    num_text += 1
                    num_sub_par = ET.SubElement(root_type, 'object', access_modifier="private",
                                                name=f"{par}_num{num_text}",
                                                display_name=f"{par}_num{num_text}",
                                                uuid=f"{uuid.uuid4()}",
                                                base_type=f"{base_type_param}",
                                                base_type_id=sl_uuid_base.get(f'{base_type_param}', ''), ver="3")
                    ET.SubElement(num_sub_par, 'designed', target="X", value=f"{x_point}", ver="3")
                    ET.SubElement(num_sub_par, 'designed', target="Y", value=f"{y_point}", ver="3")
                    y_point += sl_size_element.get(name_group, {'size_el': (0, 500)})['size_el'][1]
                    count_par += 1
                    if count_par == par_vert_count:
                        count_par = 0
                        y_point = y_start
                        x_point += sl_size_element.get(name_group, {'size_el': (500, 0)})['size_el'][0]
                    ET.SubElement(num_sub_par, 'designed', target="Rotation", value="0", ver="3")
                    # ET.SubElement(num_sub_par, 'init', target="_init_APSource", ver="3", ref="ApSource_CurrentForm")
                    ET.SubElement(num_sub_par, 'init', target="_init_Object", ver="3", value=f"{name_group}.{par}")
                    # ET.SubElement(num_sub_par, 'init', target="_AbonentName", ver="4", ref="here._init_GPAPath")
                    ET.SubElement(num_sub_par, 'init', target="_AbonentPath", ver="5", ref="here._init_GPAPath")

            # Ещё одна базовая информация
            ET.SubElement(root_type, 'designed', target="Opacity", value="1", ver="3")

            apsource_currentform = ET.SubElement(root_type, 'object', access_modifier="private",
                                                 name="ApSource_CurrentForm",
                                                 display_name="ApSource_CurrentForm",
                                                 uuid=f"{uuid.uuid4()}",
                                                 base_type="ApSource",
                                                 base_type_id=sl_uuid_base.get('ApSource', ''), ver="3")
            ET.SubElement(apsource_currentform, 'designed', target="Active", value="true", ver="3")
            ET.SubElement(apsource_currentform, 'designed', target="ReAdvise", value="0", ver="3")
            ET.SubElement(apsource_currentform, 'init', target="ParentSource", ver="3", ref="_init_ApSource")
            ET.SubElement(apsource_currentform, 'init', target="Path", ver="3", ref="_init_GPAPath")

            ET.SubElement(root_type, 'param', access_modifier="private", name="_init_ApSource",
                          display_name="_init_ApSource",
                          uuid=f"{uuid.uuid4()}",
                          base_type="ApSource", base_type_id=sl_uuid_base.get('ApSource', ''),
                          base_const="true", base_ref="true", ver="3")
            ET.SubElement(root_type, 'param', access_modifier="private", name="_init_GPAPath",
                          display_name="_init_GPAPath",
                          uuid=f"{uuid.uuid4()}",
                          base_type="string", base_type_id=sl_uuid_base.get('string', ''), ver="3")

            # Нормируем и записываем страницу мнемосхемы
            temp = ET.tostring(root_type).decode('UTF-8')
            check_diff_mnemo(new_data=multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                                     pretty_print=True,
                                                                                     encoding='unicode')),
                             check_path=os.path.join('File_for_Import', 'Mnemo', f'{name_page}_Mnemo'),
                             file_name_check=f'{name_page}_{page}_{obj[0]}.omobj',
                             message_print=f'Требуется заменить мнемосхему {name_page}_{page}_{obj[0]}.omobj'
                             )
            # with open(os.path.join('File_for_Import', 'Mnemo', f'{name_page}_Mnemo',
            #                        f'{name_page}_{page}_{obj[0]}.omobj'),
            #           'w', encoding='UTF-8') as f_out:
            #     f_out.write(multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
            #                                                                pretty_print=True, encoding='unicode')))

        # Создаём нулевую мнемосхему параметров
        if sl_list_par:
            root_list = ET.Element(
                'type', access_modifier="private", name=f"{name_page}_0_{obj[0]}",
                display_name=f"{name_page}_0_{obj[0]}",
                uuid=sl_page_uuid.get(f'{name_page}_0_{obj[0]}'),
                base_type="00_SubBase",
                base_type_id=f"{sl_uuid_base.get('00_SubBase', '99471dea-1c95-471c-9960-b4f7a539d437')}",
                ver="3"
            )
            # ...заполняем стандартную информацию
            ET.SubElement(root_list, 'designed', target='X', value="0", ver="3")
            ET.SubElement(root_list, 'designed', target='Y', value="0", ver="3")
            ET.SubElement(root_list, 'designed', target='ZValue', value="0", ver="3")
            ET.SubElement(root_list, 'designed', target='Rotation', value="0", ver="3")
            ET.SubElement(root_list, 'designed', target='Scale', value="1", ver="3")
            ET.SubElement(root_list, 'designed', target='Visible', value="true", ver="3")
            ET.SubElement(root_list, 'designed', target='Enabled', value="true", ver="3")
            ET.SubElement(root_list, 'designed', target='Tooltip', value="", ver="3")
            ET.SubElement(root_list, 'designed', target='Width', value=f"{gor_base}", ver="3")
            ET.SubElement(root_list, 'designed', target='Height', value=f"{vert_base}", ver="3")
            ET.SubElement(root_list, 'designed', target='PenColor', value="4278190080", ver="3")
            ET.SubElement(root_list, 'designed', target='PenStyle', value="0", ver="3")
            ET.SubElement(root_list, 'designed', target='PenWidth', value="1", ver="3")
            ET.SubElement(root_list, 'designed', target='BrushColor', value="0xffbfbfbf", ver="3")
            ET.SubElement(root_list, 'designed', target="BrushStyle", value="1", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowX", value="0", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowY", value="0", ver="3")

            # Вносим размеры мнемосхемы, пока так, позже может измениться
            ET.SubElement(root_list, 'designed', target="WindowWidth", value=f"{size_shirina}", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowHeight", value=f"{window_height}", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowCaption", value=f"{name_list}", ver="3")

            ET.SubElement(root_list, 'designed', target="ShowWindowCaption", value="true", ver="3")
            ET.SubElement(root_list, 'designed', target="ShowWindowMinimize", value="true", ver="3")
            ET.SubElement(root_list, 'designed', target="ShowWindowMaximize", value="true", ver="3")
            ET.SubElement(root_list, 'designed', target="ShowWindowClose", value="true", ver="3")
            ET.SubElement(root_list, 'designed', target="AlwaysOnTop", value="false", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowSizeMode", value="2", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowBorderStyle", value="1", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowState", value="0", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowScalingMode", value="0", ver="3")
            ET.SubElement(root_list, 'designed', target="MonitorNumber", value="0", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowPosition", value="1", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowCloseMode", value="0", ver="3")

            obj_frame = ET.SubElement(
                root_list, 'object', access_modifier="private", name="MainFrame",
                display_name="MainFrame",
                uuid=f"{uuid.uuid4()}",
                base_type=f"{name_page}_1",
                base_type_id=f"{sl_uuid_base.get('Frame', '71f78e19-ef99-4133-a029-2968b14f02b6')}",
                ver="3"
            )
            # ...заполняем стандартную информацию фрейма
            ET.SubElement(obj_frame, 'designed', target='X', value="0", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Y', value="0", ver="3")
            ET.SubElement(obj_frame, 'designed', target='ZValue', value="0", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Rotation', value="0", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Scale', value="1", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Visible', value="true", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Opacity', value="1", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Enabled', value="true", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Tooltip', value="", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Width', value=f"{gor_base}", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Height', value=f"{vert_base}", ver="3")
            ET.SubElement(obj_frame, 'designed', target='PenColor', value="4278190080", ver="3")
            ET.SubElement(obj_frame, 'designed', target='PenStyle', value="1", ver="3")
            ET.SubElement(obj_frame, 'designed', target='PenWidth', value="1", ver="3")
            ET.SubElement(obj_frame, 'designed', target='BrushColor', value="4278190080", ver="3")
            ET.SubElement(obj_frame, 'designed', target="BrushStyle", value="0", ver="3")
            ET.SubElement(obj_frame, 'designed', target="OverrideScaling", value="false", ver="3")
            ET.SubElement(obj_frame, 'designed', target="ShowScrollBars", value="true", ver="3")
            ET.SubElement(obj_frame, 'designed', target="MoveByMouse", value="false", ver="3")

            ET.SubElement(root_list, 'designed', target="Opacity", value="1", ver="3")

            do_on_action = ET.SubElement(root_list, 'do-on', access_modifier="private", name="Handler_1",
                                         display_name="Handler_1", ver="3", event="Opened", frame_link="MainFrame",
                                         form_action="open-in-frame",
                                         form_by_id="false")
            obj_do_on_action = ET.SubElement(do_on_action, 'object', access_modifier="private",
                                             uuid=f"{uuid.uuid4()}",
                                             base_type=f"{name_page}_1_{obj[0]}",
                                             base_type_id=f"{sl_page_uuid.get(f'{name_page}_1_{obj[0]}')}",
                                             ver="3")
            ET.SubElement(obj_do_on_action, 'init', target=f"Link_{name_page}", ver="3", ref="here")
            ET.SubElement(obj_do_on_action, 'init', target="_init_ApSource", ver="3", ref="here.ApSource_Main")
            ET.SubElement(obj_do_on_action, 'init', target="_init_GPAPath", ver="3", ref="here._pathToGPA")

            ET.SubElement(
                root_list, 'object', access_modifier="private",
                name="NameOpened", display_name="NameOpened",
                uuid=f"{uuid.uuid4()}", base_type="notifying_string",
                base_type_id=f"{sl_uuid_base.get('notifying_string', '14976fbf-36ab-415f-abc3-9f8fdc217351')}",
                ver="3"
            )

            # Добавляем кнопки переключения листов, если листов больше 1
            if len(sl_list_par) > 1:
                x_button_start = gor_base - (321 + 50 * len(sl_list_par))
                for page in sl_list_par:
                    x_swift = (page - 1) * 50
                    obj_button = ET.SubElement(
                        root_list, 'object', access_modifier="private",
                        name=f"ExtPageButton_{page}", display_name=f"ExtPageButton_{page}",
                        uuid=f"{uuid.uuid4()}",
                        base_type="ExtPageButton",
                        base_type_id=f"{sl_uuid_base.get('ExtPageButton', '2c2d6f3d-f500-4be6-b80c-620853cd99e3')}",
                        ver="3")
                    ET.SubElement(obj_button, 'designed', target='X', value=f"{x_button_start + x_swift}", ver="3")
                    ET.SubElement(obj_button, 'designed', target='Y', value=f"{vert_base - 60}", ver="3")
                    ET.SubElement(obj_button, 'designed', target='Rotation', value="0", ver="3")
                    ET.SubElement(obj_button, 'designed', target='Width', value="50", ver="3")
                    ET.SubElement(obj_button, 'designed', target='Height', value="40", ver="3")
                    ET.SubElement(obj_button, 'designed', target='Text', value=f"{page}", ver="3")
                    ET.SubElement(obj_button, 'designed', target='Font',
                                  value="PT Astra Sans,16,-1,5,75,0,0,0,0,0,Полужирный", ver="3")

                    tagret_name = ET.SubElement(obj_button, 'do-trace', access_modifier="private", target='_Name',
                                                ver="3")
                    body = ET.SubElement(tagret_name, 'body')
                    ET.SubElement(body, 'forCDATA')
                    ET.SubElement(obj_button, 'init', target='_IDtoOpen', ver="3",
                                  value=f"{sl_page_uuid.get(f'{name_page}_{page}')}")

                    do_on_action = ET.SubElement(obj_button, 'do-on', access_modifier="private", name="Handler_1",
                                                 display_name="Handler_1", ver="3", event="MouseClick",
                                                 frame_link="MainFrame",
                                                 form_action="open-in-frame",
                                                 form_by_id="false")
                    obj_do_on_action = ET.SubElement(do_on_action, 'object', access_modifier="private",
                                                     uuid=f"{uuid.uuid4()}",
                                                     base_type=f"{name_page}_{page}_{obj[0]}",
                                                     base_type_id=f"{sl_page_uuid.get(f'{name_page}_{page}_{obj[0]}')}",
                                                     ver="3")
                    ET.SubElement(obj_do_on_action, 'init', target=f"Link_{name_page}", ver="3", ref="here")
                    ET.SubElement(obj_do_on_action, 'init', target="_init_ApSource", ver="3", ref="here.ApSource_Main")
                    ET.SubElement(obj_do_on_action, 'init', target="_init_GPAPath", ver="3", ref="here._pathToGPA")

            # Добавляем ещё стандартной инфы
            apsource_currentform = ET.SubElement(root_list, 'object', access_modifier="private",
                                                 name="ApSource_CurrentForm",
                                                 display_name="ApSource_CurrentForm",
                                                 uuid=f"{uuid.uuid4()}",
                                                 base_type="ApSource",
                                                 base_type_id=sl_uuid_base.get('ApSource', ''), ver="3")
            ET.SubElement(apsource_currentform, 'designed', target="Active", value="true", ver="3")
            ET.SubElement(apsource_currentform, 'designed', target="ReAdvise", value="0", ver="3")
            ET.SubElement(apsource_currentform, 'init', target="ParentSource", ver="3", ref="_init_ApSource")
            ET.SubElement(apsource_currentform, 'init', target="Path", ver="3", ref="_init_GPAPath")
            ET.SubElement(apsource_currentform, 'designed', target="Path", value="", ver="3")

            ET.SubElement(root_list, 'param', access_modifier="private", name="_init_ApSource",
                          display_name="_init_ApSource",
                          uuid=f"{uuid.uuid4()}",
                          base_type="ApSource", base_type_id=sl_uuid_base.get('ApSource', ''),
                          base_const="true", base_ref="true", ver="3")
            ET.SubElement(root_list, 'param', access_modifier="private", name="_init_GPAPath",
                          display_name="_init_GPAPath",
                          uuid=f"{uuid.uuid4()}",
                          base_type="string", base_type_id=sl_uuid_base.get('string', ''), ver="3")

            ET.SubElement(root_list, 'object', access_modifier="private",
                          name="DebugTool_1", display_name="DebugTool_1",
                          uuid=f"{uuid.uuid4()}",
                          base_type="DebugTool",
                          base_type_id=sl_uuid_base.get('DebugTool', ''), ver="3")
            ET.SubElement(root_list, 'object', access_modifier="private",
                          name="_pathToGPA", display_name="_pathToGPA",
                          uuid=f"{uuid.uuid4()}",
                          base_type="notifying_string",
                          base_type_id=sl_uuid_base.get('notifying_string', ''), ver="3")
            apsource_main = ET.SubElement(root_list, 'object', access_modifier="private",
                                          name="ApSource_Main", display_name="ApSource_Main",
                                          uuid=f"{uuid.uuid4()}",
                                          base_type="ApSource",
                                          base_type_id=sl_uuid_base.get('ApSource', ''), ver="3")
            ET.SubElement(apsource_main, 'designed', target="Active", value="true", ver="3")
            ET.SubElement(apsource_main, 'designed', target="ReAdvise", value="0", ver="3")
            ET.SubElement(apsource_main, 'designed', target="Path", value="", ver="3")
            ET.SubElement(apsource_main, 'init', target="ParentSource", ver="3", ref="here._init_ApSource")

            ET.SubElement(root_list, 'init', target="_pathToGPA", ver="3", ref="here._init_GPAPath")

            # Нормируем и записываем страницу мнемосхемы
            temp = ET.tostring(root_list).decode('UTF-8')
            check_diff_mnemo(new_data=multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                                     pretty_print=True,
                                                                                     encoding='unicode')),
                             check_path=os.path.join('File_for_Import', 'Mnemo', f'{name_page}_Mnemo'),
                             file_name_check=f'{name_page}_0_{obj[0]}.omobj',
                             message_print=f'Требуется заменить мнемосхему {name_page}_0_{obj[0]}.omobj'
                             )
            # with open(os.path.join('File_for_Import', 'Mnemo', f'{name_page}_Mnemo', f'{name_page}_0_{obj[0]}.omobj'),
            #           'w', encoding='UTF-8') as f_out:
            #     f_out.write(multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
            #                                                                pretty_print=True, encoding='unicode')))
    return


# Функция создания мнемосхем проверки защит
def create_mnemo_pz(name_group: str, name_page: str, base_type_param: str,
                    size_shirina: int, size_vysota: int, sl_pz_xml: dict, sl_object_all: dict):

    if not os.path.exists(os.path.join('File_for_Import', 'Mnemo', f'PZ_Mnemo')):
        os.mkdir(os.path.join('File_for_Import', 'Mnemo', f'PZ_Mnemo'))
    if not os.path.exists(os.path.join('File_for_Import', 'Mnemo', f'PZ_Mnemo', 'Systemach')):
        os.mkdir(os.path.join('File_for_Import', 'Mnemo', f'PZ_Mnemo', 'Systemach'))

    # Чистим старые мнемосхемы ПЗ
    #  os.path.dirname(sys.argv[0])

    # for file in os.listdir(os.path.join(os.path.abspath(os.curdir), 'File_for_Import', 'Mnemo', 'PZ_Mnemo')):
    #     if file.endswith('.omobj'):
    #         os.remove(os.path.join(os.path.abspath(os.curdir), 'File_for_Import', 'Mnemo', 'PZ_Mnemo', file))

    # print(sl_with_check_pz)
    # param_pz = [_ for _ in param_pz if 'Проверяется при ПЗ - Да' in sl_with_check_pz[_]]

    # СЛОВАРЬ УНИКАЛЬНЫХ ОБЪЕКТОВ
    # Формируем словарь вида {кортеж контроллеров: (Объект, рус имя объекта, индекс объекта)}
    # При этом, если есть полное совпадение контроллеров, то дублирования нет
    sl_cpus_object = {}
    for obj, sl_cpu in sl_object_all.items():
        cpus = tuple(sl_cpu.keys())  # cpus = tuple(sorted(sl_cpu.keys()))
        if cpus not in sl_cpus_object:
            sl_cpus_object[cpus] = obj
    # print(sl_cpus_object)
    # uuid.uuid4()
    sl_size = {
        '1920x900': (1920, 900, 780),
        '1920x780': (1920, 780, 780)
    }
    # Словарь ID для типовых структур, возможно потом будет считываться с файла или как-то по-другому
    sl_uuid_base_default = {
        '00_SubPage': '3fe01b7a-fed7-41d2-aa19-ca3e78391035',
        'Text': '21d59f8d-2ca4-4592-92ca-b4dc48992a0f',
        'S_ALR': '401676e6-e678-4938-bc7a-8a3382258f93',
        'Line': '4dd08b15-1502-453f-a174-2c0a5aa850ba',
        'Point': '467f1af0-7bb4-4a61-b6fb-06e7bfd530d6',
        'ApSource': '966603da-f05e-4b4d-8ef0-919efbf8ab2c',
        'string': '76403785-f3d5-41a7-9eb6-d19d2aa2d95d',
        '00_SubBase': '99471dea-1c95-471c-9960-b4f7a539d437',
        'Frame': '71f78e19-ef99-4133-a029-2968b14f02b6',
        'notifying_string': '14976fbf-36ab-415f-abc3-9f8fdc217351',
        'ExtPageButton': '2c2d6f3d-f500-4be6-b80c-620853cd99e3',
        'DebugTool': '43946044-139a-43f4-a7b8-19a6074ffc56',
        '00_Base': '4f3aa327-d38a-4afe-8913-c7729acaafc0',
        'Button': '61e46e4a-827f-4dd2-ac8a-b68bcaddf442',
        'Alpha.Reports': '665556a0-5ea4-4768-8935-9ab18d0eb2a0'
    }
    try:
        if os.path.exists(os.path.join('Template_Alpha', 'Systemach', 'Mnemo', f'uuid_base_elements.json')):
            with open(os.path.join('Template_Alpha', 'Systemach', 'Mnemo', f'uuid_base_elements.json'), 'r',
                      encoding='UTF-8') as f_sig:
                text_json = json_load(f_sig)
            sl_uuid_base = text_json
        else:
            print('Файл Systemach/Mnemo/uuid_base_elements.json не найден, '
                  'uuid базовых элементов будут определены по умолчанию')
            sl_uuid_base = sl_uuid_base_default
    except Exception:
        print('Файл Systemach/Mnemo/uuid_base_elements.json заполнен некорректно, '
              'uuid базовых элементов будут определены по умолчанию')
        sl_uuid_base = sl_uuid_base_default

    # Словарь размеров элементов, тут по заполнению всё понятно
    sl_size_element = {'System.PZ': {'size_el': ((940 + 19.889), 30), 'size_text': (940, 30)}
                       }
    # Словарь расположения первого элемента, тут вроде всё понятно тоже - первый X, второй Y
    sl_start = {'System.PZ': (11.111, 92)
                }
    gor_base = sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1920, 900))[0]
    vert_base = sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1920, 900))[1]
    window_height = sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1920, 900, 780))[2]
    # Узнаём, сколько целых параметров влезет по горизонтали
    # два пикселя по горизонтали между элементами, 591 - ширина элемента параметра
    par_gor_count = floor(gor_base / sl_size_element.get(name_group, {'size_el': (500, 0)})['size_el'][0])
    # Узнаём, сколько целых параметров влезет по вертикали
    # 6 пикселей по вертикали между элементами, 92 - запас для кнопок переключения
    par_vert_count = floor((vert_base - sl_start.get(name_group, (0, 500))[1]) /
                           sl_size_element.get(name_group, {'size_el': (0, 500)})['size_el'][1])
    # Узнаём количество параметров на один лист
    par_one_list = (par_gor_count * par_vert_count)

    # Если не существует файла uuid_PZ, то создаём его и записываем uuid форм вызовов алгоритмов
    # для каждого объекта
    sl_page_uuid = {}
    if not os.path.exists(os.path.join('File_for_Import', 'Mnemo', 'PZ_Mnemo', 'Systemach', 'uuid_PZ')):
        with open(os.path.join('File_for_Import', 'Mnemo', 'PZ_Mnemo', 'Systemach', 'uuid_PZ'),
                  'w', encoding='UTF-8') as f_uuid_write:
            # Пробегаемся по УНИКАЛЬНЫМ объектам
            for cpus, obj in sl_cpus_object.items():
                # Если есть в уникальных объектах есть контроллеры с защитами
                if set(cpus) & set(sl_pz_xml.keys()):
                    generate_uuid = uuid.uuid4()
                    sl_page_uuid[f"ПЗ_0_{obj[0]}"] = f'{generate_uuid}'
                    f_uuid_write.write(f'ПЗ_0_{obj[0]}:{generate_uuid}\n')
    else:
        # Если файл существует, то считываем и записываем в словарь
        with open(os.path.join('File_for_Import', 'Mnemo', 'PZ_Mnemo', 'Systemach', 'uuid_PZ'),
                  'r', encoding='UTF-8') as f_uuid_read:
            for line in f_uuid_read:
                lst_line = line.strip().split(':')
                sl_page_uuid[lst_line[0]] = lst_line[1]
        # Если после вычитывания не обнаружили формы для отсутствующих объектов
        # (например, увеличилось количество объектов), то дозаписываем
        with open(os.path.join('File_for_Import', 'Mnemo', 'PZ_Mnemo', 'Systemach', 'uuid_PZ'),
                  'a', encoding='UTF-8') as f_uuid_write:
            # Пробегаемся по УНИКАЛЬНЫМ объектам
            for cpus, obj in sl_cpus_object.items():
                if set(cpus) & set(sl_pz_xml.keys()) and f"ПЗ_0_{obj[0]}" not in sl_page_uuid:
                    generate_uuid = uuid.uuid4()
                    sl_page_uuid[f"ПЗ_0_{obj[0]}"] = f'{generate_uuid}'
                    f_uuid_write.write(f'ПЗ_0_{obj[0]}:{generate_uuid}\n')

    # Для каждого УНИКАЛЬНОГО объекта(уникального ранее определили по составу ПЛК) создаём мнемосхему 01_FormAlg
    # только в том случае, если у него определены какие-то режимы
    for cpus, obj in sl_cpus_object.items():
        if set(cpus) & set(sl_pz_xml.keys()):
            param_pz = list()
            for plc in [i for i in cpus if i in sl_pz_xml]:
                param_pz += [j for j in sl_pz_xml[plc] if 'Проверяется при ПЗ - Да' in sl_pz_xml[plc][j]]
            # Узнаём количество требуемых листов, деля количество требуемых элементов на количество на одном листе
            start_list = 1
            count = 0
            # sl_list_par = {номер листа: кортеж защит листа}
            # При разбивке на листы учитывается количество параметров на листе, в том числе само наименование узла
            sl_list_par = {}
            for i in range(len(param_pz)):
                count += 1
                param_pz[i] = (start_list, param_pz[i])
                if count == par_one_list:
                    count = 0
                    start_list += 1

            for one_pz in param_pz:
                if one_pz[0] not in sl_list_par:
                    sl_list_par[one_pz[0]] = tuple()
                sl_list_par[one_pz[0]] += (one_pz[1],)
            # for i in sl_list_par:
            #     print(i)
            #     print(sl_list_par[i])
            num_text = 0

            # Для каждого листа в словаре листов с параметрами...
            for page, pars_pz in sl_list_par.items():
                # Вносим инфу в словарь
                # ...создаём родительский узел листа
                if f'{name_page}_{page}_{obj[0]}' not in sl_page_uuid:
                    generate_uuid_page = uuid.uuid4()
                    sl_page_uuid[f'{name_page}_{page}_{obj[0]}'] = f'{generate_uuid_page}'
                    with open(os.path.join('File_for_Import', 'Mnemo', 'PZ_Mnemo', 'Systemach', 'uuid_PZ'),
                              'a', encoding='UTF-8') as f_uuid_write:
                        f_uuid_write.write(f'{name_page}_{page}_{obj[0]}:{generate_uuid_page}\n')
                root_type = ET.Element(
                    'type', access_modifier="private", name=f"{name_page}_{page}_{obj[0]}",
                    display_name=f"{name_page}_{page}_{obj[0]}",
                    uuid=sl_page_uuid.get(f'{name_page}_{page}_{obj[0]}', ''),
                    base_type="00_SubPage",
                    base_type_id=f"{sl_uuid_base.get('00_SubPage', '3fe01b7a-fed7-41d2-aa19-ca3e78391035')}",
                    ver="3")
                # ...заполняем стандартную информацию
                ET.SubElement(root_type, 'designed', target='X', value="0", ver="3")
                ET.SubElement(root_type, 'designed', target='Y', value="0", ver="3")
                ET.SubElement(root_type, 'designed', target='ZValue', value="0", ver="3")
                ET.SubElement(root_type, 'designed', target='Rotation', value="0", ver="3")
                ET.SubElement(root_type, 'designed', target='Scale', value="1", ver="3")
                ET.SubElement(root_type, 'designed', target='Visible', value="true", ver="3")
                ET.SubElement(root_type, 'designed', target='Enabled', value="true", ver="3")
                ET.SubElement(root_type, 'designed', target='Tooltip', value="", ver="3")
                ET.SubElement(root_type, 'designed', target='Width', value=f"{gor_base}", ver="3")
                ET.SubElement(root_type, 'designed', target='Height', value=f"{vert_base}", ver="3")
                ET.SubElement(root_type, 'designed', target='PenColor', value="4278190080", ver="3")
                ET.SubElement(root_type, 'designed', target='PenStyle', value="0", ver="3")
                ET.SubElement(root_type, 'designed', target='PenWidth', value="1", ver="3")
                ET.SubElement(root_type, 'designed', target='BrushColor', value="0xffbfbfbf", ver="3")
                ET.SubElement(root_type, 'designed', target="BrushStyle", value="1", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowX", value="0", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowY", value="0", ver="3")

                # Вносим размеры мнемосхемы, пока так, позже может измениться
                ET.SubElement(root_type, 'designed', target="WindowWidth", value=f"{size_shirina}", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowHeight", value=f"{window_height}", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowCaption", value=f"{page}", ver="3")

                ET.SubElement(root_type, 'designed', target="ShowWindowCaption", value="true", ver="3")
                ET.SubElement(root_type, 'designed', target="ShowWindowMinimize", value="true", ver="3")
                ET.SubElement(root_type, 'designed', target="ShowWindowMaximize", value="true", ver="3")
                ET.SubElement(root_type, 'designed', target="ShowWindowClose", value="true", ver="3")
                ET.SubElement(root_type, 'designed', target="AlwaysOnTop", value="false", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowSizeMode", value="2", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowBorderStyle", value="1", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowState", value="0", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowScalingMode", value="0", ver="3")
                ET.SubElement(root_type, 'designed', target="MonitorNumber", value="0", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowPosition", value="1", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowCloseMode", value="0", ver="3")
                ET.SubElement(root_type, 'designed', target="Opacity", value="1", ver="3")

                # Добавляем Текст с описанием листа
                num_sub_text_discription = ET.SubElement(root_type, 'object', access_modifier="private",
                                                         name=f"Description_list",
                                                         display_name=f"Description_list",
                                                         uuid=f"{uuid.uuid4()}",
                                                         base_type="Text",
                                                         base_type_id=sl_uuid_base.get('Text', ''), ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='X', value="40.5", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Y', value="13", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='ZValue', value="0", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Rotation', value="0", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Scale', value="1", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Visible', value="true", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Enabled', value="true", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Tooltip', value="", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Width', value="535", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Height', value="30", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Text', value=f"Проверка защит лист {page}",
                              ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target="Font",
                              value="PT Astra Sans,20,-1,5,75,0,0,0,0,0,Полужирный", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target="FontColor", value="0xff000000", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target="TextAlignment", value="129", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target="Opacity", value="1", ver="3")

                # Добавляем параметры
                x_start = sl_start.get(name_group, (3, 10))[0]
                y_start = sl_start.get(name_group, (3, 10))[1]
                x_point = x_start
                y_point = y_start
                count_par = 0
                for one_pz in pars_pz:
                    num_text += 1
                    num_sub_par = ET.SubElement(root_type, 'object', access_modifier="private",
                                                name=f"Строка проверки защит_{num_text}_{one_pz}",
                                                display_name=f"Строка проверки защит_{num_text}_{one_pz}",
                                                uuid=f"{uuid.uuid4()}",
                                                base_type=f"{base_type_param}",
                                                base_type_id=sl_uuid_base.get(f'{base_type_param}', ''), ver="3")

                    ET.SubElement(num_sub_par, 'designed', target="X", value=f"{x_point}", ver="3")
                    ET.SubElement(num_sub_par, 'designed', target="Y", value=f"{y_point}", ver="3")
                    y_point += sl_size_element.get(name_group, {'size_el': (0, 500)})['size_el'][1]
                    count_par += 1
                    if count_par == par_vert_count:
                        count_par = 0
                        y_point = y_start
                        x_point += sl_size_element.get(name_group, {'size_el': (500, 0)})['size_el'][0]

                    ET.SubElement(num_sub_par, 'designed', target="Rotation", value="0", ver="3")
                    ET.SubElement(num_sub_par, 'init', target="_init_Object", ver="3", value=f"{name_group}.{one_pz}")
                    # ET.SubElement(num_sub_par, 'init', target="_init_APSource", ver="4",
                    # ref="here.ApSource_CurrentForm")
                    # ET.SubElement(num_sub_par, 'init', target="_AbonentName", ver="4", ref="here._init_GPAPath")
                    ET.SubElement(num_sub_par, 'init', target="_AbonentPath", ver="5", ref="here._init_GPAPath")

                # Добавляем табличку с текстом
                for table_i in range(par_gor_count):
                    gor_swift = table_i * sl_size_element.get(name_group, {'size_el': (0, 500)})['size_el'][0]
                    # Текста таблички
                    for table_text, attrib in {'Description': ('Название защиты', 11.5, 62, 535, 30),
                                               'Timer': ('Таймер (секунды)', 546.5, 62, 65, 30),
                                               'Delay': ('Задержка (секунды)', 611.5, 62, 65, 30),
                                               'Ustavka': ('Уставка', 676.5, 62, 65, 30),
                                               'Value': ('Значение', 741.5, 62, 65, 30),
                                               'E_Unit': ('Ед.изм', 806.5, 62, 50.6309, 30),
                                               'Check': ('Отметка о проверке', 858.5, 62, 92, 30),
                                               }.items():
                        name_pz_text = ET.SubElement(root_type, 'object', access_modifier="private",
                                                     name=f"{table_text}_{table_i}",
                                                     display_name=f"{table_text}_{table_i}",
                                                     uuid=f"{uuid.uuid4()}", base_type="Text",
                                                     base_type_id=sl_uuid_base.get('Text', ''), ver="3")
                        ET.SubElement(name_pz_text, 'designed', target="X", value=f"{attrib[1] + gor_swift}", ver="3")
                        ET.SubElement(name_pz_text, 'designed', target="Y", value=f"{attrib[2]}", ver="3")
                        ET.SubElement(name_pz_text, 'designed', target="ZValue", value="0", ver="3")
                        ET.SubElement(name_pz_text, 'designed', target="Rotation", value="0", ver="3")
                        ET.SubElement(name_pz_text, 'designed', target="Scale", value="1", ver="3")
                        ET.SubElement(name_pz_text, 'designed', target="Visible", value="true", ver="3")
                        ET.SubElement(name_pz_text, 'designed', target="Enabled", value="true", ver="3")
                        ET.SubElement(name_pz_text, 'designed', target="Tooltip", value="", ver="3")
                        ET.SubElement(name_pz_text, 'designed', target="Width", value=f"{attrib[3]}", ver="3")
                        ET.SubElement(name_pz_text, 'designed', target="Height", value=f"{attrib[4]}", ver="3")
                        ET.SubElement(name_pz_text, 'designed', target="Text", value=f"{attrib[0]}", ver="3")
                        ET.SubElement(name_pz_text, 'designed', target="Font",
                                      value="PT Astra Sans,10,-1,5,50,0,0,0,0,0,Обычный", ver="3")
                        ET.SubElement(name_pz_text, 'designed', target="FontColor", value="0xff000000", ver="3")
                        ET.SubElement(name_pz_text, 'designed', target="TextAlignment", value="132", ver="3")
                        ET.SubElement(name_pz_text, 'designed', target="Opacity", value="1", ver="3")

                    # Линии таблички
                    for line, attrib in {'Line_1': (1.5, 62, 0, vert_base - 70, 0, 0, 0, vert_base - 70, 0),
                                         'Line_2': (546.5, 62, 0, vert_base - 70, 0, 0, 0, vert_base - 70, 0),
                                         'Line_3': (611.5, 62, 0, vert_base - 70, 0, 0, 0, vert_base - 70, 0),
                                         'Line_4': (676.5, 62, 0, vert_base - 70, 0, 0, 0, vert_base - 70, 0),
                                         'Line_5': (741.5, 62, 0, vert_base - 70, 0, 0, 0, vert_base - 70, 0),
                                         'Line_6': (806.5, 62, 0, vert_base - 70, 0, 0, 0, vert_base - 70, 0),
                                         'Line_7': (476.7, -413, 0, 950.3, 0, 0, 0, 950.3, 270),
                                         'Line_8': (476.7, -383.5, 0, 950.3, 0, 0, 0, 950.3, 270),
                                         'Line_9': (476.7, (-413 + (vert_base - 70)), 0, 951, 0, 0, 0, 951, 270),
                                         'Line_10': (857.5, 62, 0, vert_base - 70, 0, 0, 0, vert_base - 70, 0),
                                         'Line_11': (952.5, 62, 0, vert_base - 70, 0, 0, 0, vert_base - 70, 0)
                                         }.items():
                        obj_pz_line = ET.SubElement(root_type, 'object', access_modifier="private",
                                                    name=f"{line}_{table_i}",
                                                    display_name=f"{line}_{table_i}",
                                                    uuid=f"{uuid.uuid4()}", base_type="Line",
                                                    base_type_id=sl_uuid_base.get('Line', ''), ver="3")
                        ET.SubElement(obj_pz_line, 'designed', target="X", value=f"{attrib[0] + gor_swift}", ver="3")
                        ET.SubElement(obj_pz_line, 'designed', target="Y", value=f"{attrib[1]}", ver="3")
                        ET.SubElement(obj_pz_line, 'designed', target="ZValue", value="0", ver="3")
                        ET.SubElement(obj_pz_line, 'designed', target="Rotation", value=f"{attrib[8]}", ver="3")
                        ET.SubElement(obj_pz_line, 'designed', target="Scale", value="1", ver="3")
                        ET.SubElement(obj_pz_line, 'designed', target="Visible", value="true", ver="3")
                        ET.SubElement(obj_pz_line, 'designed', target="Enabled", value="true", ver="3")
                        ET.SubElement(obj_pz_line, 'designed', target="Tooltip", value="", ver="3")
                        ET.SubElement(obj_pz_line, 'designed', target="Width", value=f"{attrib[2]}", ver="3")
                        ET.SubElement(obj_pz_line, 'designed', target="Height", value=f"{attrib[3]}", ver="3")
                        ET.SubElement(obj_pz_line, 'designed', target="PenColor", value="0xff818181", ver="3")
                        ET.SubElement(obj_pz_line, 'designed', target="PenStyle", value="1", ver="3")
                        ET.SubElement(obj_pz_line, 'designed', target="PenWidth", value="1", ver="3")
                        ET.SubElement(obj_pz_line, 'designed', target="BrushColor", value="0xff000000", ver="3")
                        ET.SubElement(obj_pz_line, 'designed', target="BrushStyle", value="0", ver="3")

                        obj_pz_point_1 = ET.SubElement(obj_pz_line, 'object', access_modifier="private",
                                                       name=f"Point_1", display_name=f"Point_1",
                                                       uuid=f"{uuid.uuid4()}", base_type="Point",
                                                       base_type_id=sl_uuid_base.get('Point', ''), ver="3")
                        ET.SubElement(obj_pz_point_1, 'designed', target="X", value=f"{attrib[4]}", ver="3")
                        ET.SubElement(obj_pz_point_1, 'designed', target="Y", value=f"{attrib[5]}", ver="3")

                        obj_pz_point_2 = ET.SubElement(obj_pz_line, 'object', access_modifier="private",
                                                       name=f"Point_2", display_name=f"Point_2",
                                                       uuid=f"{uuid.uuid4()}", base_type="Point",
                                                       base_type_id=sl_uuid_base.get('Point', ''), ver="3")
                        ET.SubElement(obj_pz_point_2, 'designed', target="X", value=f"{attrib[6]}", ver="3")
                        ET.SubElement(obj_pz_point_2, 'designed', target="Y", value=f"{attrib[7]}", ver="3")

                        ET.SubElement(obj_pz_line, 'designed', target="Opacity", value="1", ver="3")

                # Ещё одна базовая информация
                apsource_currentform = ET.SubElement(root_type, 'object', access_modifier="private",
                                                     name="ApSource_CurrentForm",
                                                     display_name="ApSource_CurrentForm",
                                                     uuid=f"{uuid.uuid4()}",
                                                     base_type="ApSource",
                                                     base_type_id=sl_uuid_base.get('ApSource', ''), ver="3")
                ET.SubElement(apsource_currentform, 'designed', target="Active", value="true", ver="3")
                ET.SubElement(apsource_currentform, 'designed', target="ReAdvise", value="0", ver="3")
                ET.SubElement(apsource_currentform, 'init', target="ParentSource", ver="3", ref="_init_ApSource")
                ET.SubElement(apsource_currentform, 'init', target="Path", ver="3", ref="_init_GPAPath")

                ET.SubElement(root_type, 'param', access_modifier="private", name="_init_ApSource",
                              display_name="_init_ApSource",
                              uuid=f"{uuid.uuid4()}",
                              base_type="ApSource", base_type_id=sl_uuid_base.get('ApSource', ''),
                              base_const="true", base_ref="true", ver="3")
                ET.SubElement(root_type, 'param', access_modifier="private", name="_init_GPAPath",
                              display_name="_init_GPAPath",
                              uuid=f"{uuid.uuid4()}",
                              base_type="string", base_type_id=sl_uuid_base.get('string', ''), ver="3")

                # Нормируем и записываем страницу мнемосхемы
                temp = ET.tostring(root_type).decode('UTF-8')
                check_diff_mnemo(new_data=multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                                         pretty_print=True,
                                                                                         encoding='unicode')),
                                 check_path=os.path.join('File_for_Import', 'Mnemo', 'PZ_Mnemo'),
                                 file_name_check=f'{name_page}_{page}_{obj[0]}.omobj',
                                 message_print=f'Требуется заменить мнемосхему {name_page}_{page}_{obj[0]}.omobj'
                                 )
                # with open(os.path.join('File_for_Import', 'Mnemo', 'PZ_Mnemo', f'{name_page}_{page}_{obj[0]}.omobj'),
                #           'w', encoding='UTF-8') as f_out:
                #     f_out.write(multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
                #                                                                pretty_print=True, encoding='unicode')))

            # Создаём главное окно ПЗ_0 ()
            root_list = ET.Element(
                'type', access_modifier="private", name=f"{name_page}_0_{obj[0]}",
                display_name=f"{name_page}_0_{obj[0]}",
                uuid=sl_page_uuid.get(f'{name_page}_0_{obj[0]}'),
                base_type="00_Base",
                base_type_id=f"{sl_uuid_base.get('00_Base', '4f3aa327-d38a-4afe-8913-c7729acaafc0')}",
                ver="3"
            )
            # ...заполняем стандартную информацию
            ET.SubElement(root_list, 'designed', target='X', value="0", ver="3")
            ET.SubElement(root_list, 'designed', target='Y', value="0", ver="3")
            ET.SubElement(root_list, 'designed', target='ZValue', value="0", ver="3")
            ET.SubElement(root_list, 'designed', target='Rotation', value="0", ver="3")
            ET.SubElement(root_list, 'designed', target='Scale', value="1", ver="3")
            ET.SubElement(root_list, 'designed', target='Visible', value="true", ver="3")
            ET.SubElement(root_list, 'designed', target='Enabled', value="true", ver="3")
            ET.SubElement(root_list, 'designed', target='Tooltip', value="", ver="3")
            ET.SubElement(root_list, 'designed', target='Width', value=f"{gor_base}", ver="3")
            ET.SubElement(root_list, 'designed', target='Height', value=f"{vert_base}", ver="3")
            ET.SubElement(root_list, 'designed', target='PenColor', value="4278190080", ver="3")
            ET.SubElement(root_list, 'designed', target='PenStyle', value="0", ver="3")
            ET.SubElement(root_list, 'designed', target='PenWidth', value="1", ver="3")
            ET.SubElement(root_list, 'designed', target='BrushColor', value="0xffbfbfbf", ver="3")
            ET.SubElement(root_list, 'designed', target="BrushStyle", value="1", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowX", value="0", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowY", value="0", ver="3")

            # Вносим размеры мнемосхемы, пока так, позже может измениться
            ET.SubElement(root_list, 'designed', target="WindowWidth", value=f"{size_shirina}", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowHeight", value=f"{window_height}", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowCaption", value=f"Проверка защит", ver="3")

            ET.SubElement(root_list, 'designed', target="ShowWindowCaption", value="true", ver="3")
            ET.SubElement(root_list, 'designed', target="ShowWindowMinimize", value="true", ver="3")
            ET.SubElement(root_list, 'designed', target="ShowWindowMaximize", value="true", ver="3")
            ET.SubElement(root_list, 'designed', target="ShowWindowClose", value="true", ver="3")
            ET.SubElement(root_list, 'designed', target="AlwaysOnTop", value="false", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowSizeMode", value="2", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowBorderStyle", value="1", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowState", value="0", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowScalingMode", value="0", ver="3")
            ET.SubElement(root_list, 'designed', target="MonitorNumber", value="0", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowPosition", value="1", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowCloseMode", value="0", ver="3")

            obj_frame = ET.SubElement(
                root_list, 'object', access_modifier="private", name="MainFrame",
                display_name="MainFrame",
                uuid=f"{uuid.uuid4()}",
                base_type=f"{name_page}_1",
                base_type_id=f"{sl_uuid_base.get('Frame', '71f78e19-ef99-4133-a029-2968b14f02b6')}",
                ver="3"
            )
            # ...заполняем стандартную информацию фрейма
            ET.SubElement(obj_frame, 'designed', target='X', value="0", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Y', value="0", ver="3")
            ET.SubElement(obj_frame, 'designed', target='ZValue', value="0", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Rotation', value="0", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Scale', value="1", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Visible', value="true", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Opacity', value="1", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Enabled', value="true", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Tooltip', value="", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Width', value=f"{gor_base}", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Height', value=f"{vert_base}", ver="3")
            ET.SubElement(obj_frame, 'designed', target='PenColor', value="4278190080", ver="3")
            ET.SubElement(obj_frame, 'designed', target='PenStyle', value="1", ver="3")
            ET.SubElement(obj_frame, 'designed', target='PenWidth', value="1", ver="3")
            ET.SubElement(obj_frame, 'designed', target='BrushColor', value="4278190080", ver="3")
            ET.SubElement(obj_frame, 'designed', target="BrushStyle", value="0", ver="3")
            ET.SubElement(obj_frame, 'designed', target="OverrideScaling", value="false", ver="3")
            ET.SubElement(obj_frame, 'designed', target="ShowScrollBars", value="true", ver="3")
            ET.SubElement(obj_frame, 'designed', target="MoveByMouse", value="false", ver="3")

            ET.SubElement(root_list, 'designed', target="Opacity", value="1", ver="3")

            do_on_action = ET.SubElement(root_list, 'do-on', access_modifier="private", name="Handler_1",
                                         display_name="Handler_1", ver="3", event="Opened", frame_link="MainFrame",
                                         form_action="open-in-frame",
                                         form_by_id="false")
            obj_do_on_action = ET.SubElement(do_on_action, 'object', access_modifier="private",
                                             uuid=f"{uuid.uuid4()}",
                                             base_type=f"{name_page}_1_{obj[0]}",
                                             base_type_id=f"{sl_page_uuid.get(f'{name_page}_1_{obj[0]}')}",
                                             ver="3")
            ET.SubElement(obj_do_on_action, 'init', target=f"Link_PZ", ver="3", ref="here")
            ET.SubElement(obj_do_on_action, 'init', target="_init_ApSource", ver="3", ref="here.ApSource_Main")
            ET.SubElement(obj_do_on_action, 'init', target="_init_GPAPath", ver="3", ref="here._pathToGPA")

            ET.SubElement(
                root_list, 'object', access_modifier="private",
                name="NameOpened", display_name="NameOpened",
                uuid=f"{uuid.uuid4()}", base_type="notifying_string",
                base_type_id=f"{sl_uuid_base.get('notifying_string', '14976fbf-36ab-415f-abc3-9f8fdc217351')}",
                ver="3"
            )

            # Добавляем кнопки переключения листов
            x_button_start = gor_base - (321 + 50 * len(sl_list_par))
            # Добавляем кнопку ПЕЧАТЬ на лист проверки защит
            obj_button_print = ET.SubElement(
                root_list, 'object', access_modifier="private",
                name=f"Button_print", display_name=f"Button_print",
                uuid=f"{uuid.uuid4()}",
                base_type="Button",
                base_type_id=f"{sl_uuid_base.get('Button', '61e46e4a-827f-4dd2-ac8a-b68bcaddf442')}",
                ver="3")
            ET.SubElement(obj_button_print, 'designed', target='X', value=f"{x_button_start - 107}", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='Y', value=f"{10}", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='ZValue', value=f"0", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='Rotation', value="0", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='Scale', value="1", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='Visible', value="true", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='Enabled', value="true", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='Width', value="107", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='Height', value="40", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='Checkable', value="false", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='Text', value=f"Печать", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='TextAlignment', value=f"132", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='Font',
                          value="PT Astra Sans,16,-1,5,75,0,0,0,0,0,Полужирный", ver="3")
            ET.SubElement(obj_button_print, 'designed', target="FontColor", value="0xff000000", ver="3")
            ET.SubElement(obj_button_print, 'designed', target="OnClickFontColor", value="0xff000000", ver="3")
            ET.SubElement(obj_button_print, 'designed', target="OnHoverFontColor", value="4278190080", ver="3")
            ET.SubElement(obj_button_print, 'designed', target="DisabledFontColor", value="4278190080", ver="3")
            ET.SubElement(obj_button_print, 'designed', target="BrushColor", value="0xfff0f0f0", ver="3")
            ET.SubElement(obj_button_print, 'designed', target="BrushStyle", value="1", ver="3")
            ET.SubElement(obj_button_print, 'designed', target="OnClickBrushColor", value="0xffa0a0a0", ver="3")
            ET.SubElement(obj_button_print, 'designed', target="OnClickBrushStyle", value="0", ver="3")
            ET.SubElement(obj_button_print, 'designed', target="OnHoverBrushColor", value="0xffffffff", ver="3")
            ET.SubElement(obj_button_print, 'designed', target="OnHoverBrushStyle", value="0", ver="3")
            ET.SubElement(obj_button_print, 'designed', target="DisabledBrushColor", value="0xffa0a0a0", ver="3")
            ET.SubElement(obj_button_print, 'designed', target="DisabledBrushStyle", value="0", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='PenColor', value="0xff000000", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='PenStyle', value="1", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='PenWidth', value="1", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='OnClickPenColor', value="0xff000000", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='OnClickPenStyle', value="1", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='OnClickPenWidth', value="1", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='OnHoverPenColor', value="4278190080", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='OnHoverPenStyle', value="1", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='OnHoverPenWidth', value="1", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='DisabledPenColor', value="4288716960", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='DisabledPenStyle', value="1", ver="3")
            ET.SubElement(obj_button_print, 'designed', target='DisabledPenWidth', value="1", ver="3")
            ET.SubElement(obj_button_print, 'designed', target="Opacity", value="1", ver="3")
            do_on_action = ET.SubElement(obj_button_print, 'do-on', access_modifier="private", name="Handler_1",
                                         display_name="Handler_1", ver="3", event="MouseClick",
                                         frame_link="MainFrame",
                                         form_action="open-in-frame",
                                         form_by_id="false")
            obj_do_on_action = ET.SubElement(do_on_action, 'object', access_modifier="private",
                                             uuid=f"{uuid.uuid4()}",
                                             base_type=f"Alpha.Reports",
                                             base_type_id=f"{sl_uuid_base.get(f'Alpha.Reports')}",
                                             ver="4")
            ET.SubElement(obj_do_on_action, 'init', target=f"_Report", ver="4", value="Протокол проверки защит")
            ET.SubElement(obj_do_on_action, 'init', target="GPA", ver="4", ref="here._pathToGPA")

            object_handler = ET.SubElement(obj_button_print, 'do-on', access_modifier="private",
                                           name=f"Handler_2", display_name=f"Handler_2", ver="5", event="MouseClick")
            el = ET.SubElement(object_handler, 'body', kind="om")
            add_text_action = ''
            for page in sl_list_par:
                add_text_action += f'ExtPageButton_{page}.Visible = false;\n'
            el.text = f'yopta_on![CDATA[me.Visible = false;\n{add_text_action}]]yopta_off'

            if len(sl_list_par) > 1:
                for page in sl_list_par:
                    x_swift = (page - 1) * 50
                    obj_button = ET.SubElement(
                        root_list, 'object', access_modifier="private",
                        name=f"ExtPageButton_{page}", display_name=f"ExtPageButton_{page}",
                        uuid=f"{uuid.uuid4()}",
                        base_type="ExtPageButton",
                        base_type_id=f"{sl_uuid_base.get('ExtPageButton', '2c2d6f3d-f500-4be6-b80c-620853cd99e3')}",
                        ver="3")
                    ET.SubElement(obj_button, 'designed', target='X', value=f"{x_button_start + x_swift}", ver="3")
                    ET.SubElement(obj_button, 'designed', target='Y', value=f"{10}", ver="3")  # vert_base - 60
                    ET.SubElement(obj_button, 'designed', target='Rotation', value="0", ver="3")
                    ET.SubElement(obj_button, 'designed', target='Width', value="50", ver="3")
                    ET.SubElement(obj_button, 'designed', target='Height', value="40", ver="3")
                    ET.SubElement(obj_button, 'designed', target='Text', value=f"{page}", ver="3")
                    ET.SubElement(obj_button, 'designed', target='Font',
                                  value="PT Astra Sans,16,-1,5,75,0,0,0,0,0,Полужирный", ver="3")

                    tagret_name = ET.SubElement(obj_button, 'do-trace', access_modifier="private", target='_Name',
                                                ver="3")
                    body = ET.SubElement(tagret_name, 'body')
                    ET.SubElement(body, 'forCDATA')
                    ET.SubElement(obj_button, 'init', target='_IDtoOpen', ver="3",
                                  value=f"{sl_page_uuid.get(f'{name_page}_{page}_{obj[0]}')}")

                    do_on_action = ET.SubElement(obj_button, 'do-on', access_modifier="private", name="Handler_1",
                                                 display_name="Handler_1", ver="3", event="MouseClick",
                                                 frame_link="MainFrame",
                                                 form_action="open-in-frame",
                                                 form_by_id="false")
                    obj_do_on_action = ET.SubElement(do_on_action, 'object', access_modifier="private",
                                                     uuid=f"{uuid.uuid4()}",
                                                     base_type=f"{name_page}_{page}_{obj[0]}",
                                                     base_type_id=f"{sl_page_uuid.get(f'{name_page}_{page}_{obj[0]}')}",
                                                     ver="3")
                    ET.SubElement(obj_do_on_action, 'init', target=f"Link_PZ", ver="3", ref="here")
                    ET.SubElement(obj_do_on_action, 'init', target="_init_ApSource", ver="3", ref="here.ApSource_Main")
                    ET.SubElement(obj_do_on_action, 'init', target="_init_GPAPath", ver="3", ref="here._pathToGPA")

            # Добавляем ещё стандартной инфы
            apsource_currentform = ET.SubElement(root_list, 'object', access_modifier="private",
                                                 name="ApSource_CurrentForm",
                                                 display_name="ApSource_CurrentForm",
                                                 uuid=f"{uuid.uuid4()}",
                                                 base_type="ApSource",
                                                 base_type_id=sl_uuid_base.get('ApSource', ''), ver="3")
            ET.SubElement(apsource_currentform, 'designed', target="Active", value="true", ver="3")
            ET.SubElement(apsource_currentform, 'designed', target="ReAdvise", value="0", ver="3")
            ET.SubElement(apsource_currentform, 'init', target="ParentSource", ver="3", ref="_init_ApSource")
            ET.SubElement(apsource_currentform, 'init', target="Path", ver="3", ref="_init_GPAPath")
            ET.SubElement(apsource_currentform, 'designed', target="Path", value="", ver="3")

            ET.SubElement(root_list, 'param', access_modifier="private", name="_init_ApSource",
                          display_name="_init_ApSource",
                          uuid=f"{uuid.uuid4()}",
                          base_type="ApSource", base_type_id=sl_uuid_base.get('ApSource', ''),
                          base_const="true", base_ref="true", ver="3")
            ET.SubElement(root_list, 'param', access_modifier="private", name="_init_GPAPath",
                          display_name="_init_GPAPath",
                          uuid=f"{uuid.uuid4()}",
                          base_type="string", base_type_id=sl_uuid_base.get('string', ''), ver="3")

            ET.SubElement(root_list, 'object', access_modifier="private",
                          name="DebugTool_1", display_name="DebugTool_1",
                          uuid=f"{uuid.uuid4()}",
                          base_type="DebugTool",
                          base_type_id=sl_uuid_base.get('DebugTool', ''), ver="3")
            ET.SubElement(root_list, 'object', access_modifier="private",
                          name="_pathToGPA", display_name="_pathToGPA",
                          uuid=f"{uuid.uuid4()}",
                          base_type="notifying_string",
                          base_type_id=sl_uuid_base.get('notifying_string', ''), ver="3")
            apsource_main = ET.SubElement(root_list, 'object', access_modifier="private",
                                          name="ApSource_Main", display_name="ApSource_Main",
                                          uuid=f"{uuid.uuid4()}",
                                          base_type="ApSource",
                                          base_type_id=sl_uuid_base.get('ApSource', ''), ver="3")
            ET.SubElement(apsource_main, 'designed', target="Active", value="true", ver="3")
            ET.SubElement(apsource_main, 'designed', target="ReAdvise", value="0", ver="3")
            ET.SubElement(apsource_main, 'designed', target="Path", value="", ver="3")
            ET.SubElement(apsource_main, 'init', target="ParentSource", ver="3", ref="here._init_ApSource")

            ET.SubElement(root_list, 'init', target="_pathToGPA", ver="3", ref="here._init_GPAPath")

            # Нормируем и записываем страницу мнемосхемы
            temp = ET.tostring(root_list).decode('UTF-8')
            check_diff_mnemo(new_data=multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                                     pretty_print=True,
                                                                                     encoding='unicode')),
                             check_path=os.path.join('File_for_Import', 'Mnemo', 'PZ_Mnemo'),
                             file_name_check=f'{name_page}_0_{obj[0]}.omobj',
                             message_print=f'Требуется заменить мнемосхему {name_page}_0_{obj[0]}.omobj'
                             )
            # with open(os.path.join('File_for_Import', 'Mnemo', 'PZ_Mnemo', f'{name_page}_0_{obj[0]}.omobj'),
            #           'w', encoding='UTF-8') as f_out:
            #     f_out.write(multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
            #                                                                pretty_print=True, encoding='unicode')))

    return


# Функция создания мнемосхем параметров
def create_mnemo_drv(name_group: str, name_page: str, name_pag_rus: str,
                     size_shirina: int, size_vysota: int, sl_one_driver_cpu: dict, sl_object_all: dict):
    sl_one_driver_par = ChainMap(*sl_one_driver_cpu.values())
    # print(sl_with_check_pz)
    # param_pz = [_ for _ in param_pz if 'Проверяется при ПЗ - Да' in sl_with_check_pz[_]]

    # СЛОВАРЬ УНИКАЛЬНЫХ ОБЪЕКТОВ
    # Формируем словарь вида {кортеж контроллеров: (Объект, рус имя объекта, индекс объекта)}
    # При этом, если есть полное совпадение контроллеров, то дублирования нет
    sl_cpus_object = {}
    for obj, sl_cpu in sl_object_all.items():
        cpus = tuple(sl_cpu.keys())  # cpus = tuple(sorted(sl_cpu.keys()))
        if cpus not in sl_cpus_object:
            sl_cpus_object[cpus] = obj
    # print(sl_cpus_object)
    # uuid.uuid4()
    sl_size = {
        '1920x900': (1780, 900, 780),
        '1920x780': (1780, 780, 780)
    }
    # Словарь ID для типовых структур, возможно потом будет считываться с файла или как-то по-другому
    sl_uuid_base_default = {
        '00_SubPage': '3fe01b7a-fed7-41d2-aa19-ca3e78391035',
        'Text': '21d59f8d-2ca4-4592-92ca-b4dc48992a0f',
        'S_ALR': '401676e6-e678-4938-bc7a-8a3382258f93',
        'Line': '4dd08b15-1502-453f-a174-2c0a5aa850ba',
        'Point': '467f1af0-7bb4-4a61-b6fb-06e7bfd530d6',
        'ApSource': '966603da-f05e-4b4d-8ef0-919efbf8ab2c',
        'string': '76403785-f3d5-41a7-9eb6-d19d2aa2d95d',
        '00_SubBase': '99471dea-1c95-471c-9960-b4f7a539d437',
        'Frame': '71f78e19-ef99-4133-a029-2968b14f02b6',
        'notifying_string': '14976fbf-36ab-415f-abc3-9f8fdc217351',
        'ExtPageButton': '2c2d6f3d-f500-4be6-b80c-620853cd99e3',
        'DebugTool': '43946044-139a-43f4-a7b8-19a6074ffc56',
        '00_Base': '4f3aa327-d38a-4afe-8913-c7729acaafc0',
        'Button': '61e46e4a-827f-4dd2-ac8a-b68bcaddf442',
        'Alpha.Reports': '665556a0-5ea4-4768-8935-9ab18d0eb2a0'
    }
    sl_base_drv_param_default = {
        'DRV_AI.DRV_AI_PLC_View': ('S_DRV_AI_Discription', '803e851d-f716-4341-a237-717afdf13c9b'),
        'DRV_DI.DRV_DI_PLC_View': ('S_DRV_DI_Discription', '16abad7a-2e37-4edd-ad30-7317f4832b95'),
        'DRV_INT.DRV_INT_PLC_View': ('S_DRV_INT_Discription', '3ab70fca-70f2-492f-a7a6-92d58d785afd'),
        'DRV_AI.DRV_AI_IMIT_PLC_View': ('S_DRV_AI_Discription', '803e851d-f716-4341-a237-717afdf13c9b'),
        'DRV_DI.DRV_DI_IMIT_PLC_View': ('S_DRV_DI_Discription', '16abad7a-2e37-4edd-ad30-7317f4832b95'),
        'DRV_INT.DRV_INT_IMIT_PLC_View': ('S_DRV_INT_Discription', '3ab70fca-70f2-492f-a7a6-92d58d785afd'),
    }
    try:
        if os.path.exists(os.path.join('Template_Alpha', 'Systemach', 'Mnemo', f'uuid_base_elements.json')):
            with open(os.path.join('Template_Alpha', 'Systemach', 'Mnemo', f'uuid_base_elements.json'), 'r',
                      encoding='UTF-8') as f_sig:
                text_json = json_load(f_sig)
            sl_uuid_base = text_json
            sl_base_drv_param = text_json
        else:
            print('Файл Systemach/Mnemo/uuid_base_elements.json не найден, '
                  'uuid базовых элементов будут определены по умолчанию')
            sl_uuid_base = sl_uuid_base_default
            sl_base_drv_param = sl_base_drv_param_default
    except Exception:
        print('Файл Systemach/Mnemo/uuid_base_elements.json заполнен некорректно, '
              'uuid базовых элементов будут определены по умолчанию')
        sl_uuid_base = sl_uuid_base_default
        sl_base_drv_param = sl_base_drv_param_default

    # Словарь размеров элементов, тут по заполнению всё понятно
    sl_size_element = {name_group: {'size_el': ((591 + 2), (24 + 6)), 'size_text': (590.567, 24)}
                       }
    # sl_size_element = {name_group: {'size_el': ((940 + 19.889), 30), 'size_text': (940, 30)}
    #                    }
    # sl_size_element = {'AI': {'size_el': ((591 + 2), (24 + 6)), 'size_text': (590.567, 24)},
    #                    'AE': {'size_el': ((591 + 2), (24 + 6)), 'size_text': (590.567, 24)},
    #                    'DI': {'size_el': ((525 + 50), (26 + 6)), 'size_text': (524.69, 26)},
    #                    'System.CNT': {'size_el': ((545 + 30), (24 + 6)), 'size_text': (545, 24)}
    #                    }
    # Словарь расположения первого элемента, тут вроде всё понятно тоже - первый X, второй Y
    sl_start = {name_group: (11.111, 92)
                }
    gor_base = sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1920, 900))[0]
    vert_base = sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1920, 900))[1]
    window_height = sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1920, 900, 780))[2]
    # Узнаём, сколько целых параметров влезет по горизонтали
    # два пикселя по горизонтали между элементами, 591 - ширина элемента параметра
    par_gor_count = floor(gor_base / sl_size_element.get(name_group, {'size_el': (500, 0)})['size_el'][0])
    # Узнаём, сколько целых параметров влезет по вертикали
    # 6 пикеселей по вертикали между элементами, 92 - запас для кнопок переключения
    par_vert_count = floor((vert_base - sl_start.get(name_group, (0, 500))[1]) /
                           sl_size_element.get(name_group, {'size_el': (0, 500)})['size_el'][1])
    # Узнаём количество параметров на один лист
    par_one_list = (par_gor_count * par_vert_count)

    # Если не существует файла uuid_drv, то создаём его и записываем uuid форм вызовов алгоритмов
    # для каждого объекта
    sl_page_uuid = {}
    if not os.path.exists(os.path.join('File_for_Import', 'Mnemo', 'DRV', 'Systemach', 'uuid_drv')):
        with open(os.path.join('File_for_Import', 'Mnemo', 'DRV', 'Systemach', 'uuid_drv'),
                  'w', encoding='UTF-8') as f_uuid_write:
            # Пробегаемся по УНИКАЛЬНЫМ объектам
            for cpus, obj in sl_cpus_object.items():
                # Если есть в уникальных объектах есть контроллеры с защитами
                if set(cpus) & set(sl_one_driver_cpu.keys()):
                    generate_uuid = uuid.uuid4()
                    sl_page_uuid[f"{name_page}_0_{obj[0]}"] = f'{generate_uuid}'
                    f_uuid_write.write(f'{name_page}_0_{obj[0]}:{generate_uuid}\n')
    else:
        # Если файл существует, то считываем и записываем в словарь
        with open(os.path.join('File_for_Import', 'Mnemo', 'DRV', 'Systemach', 'uuid_drv'),
                  'r', encoding='UTF-8') as f_uuid_read:
            for line in f_uuid_read:
                lst_line = line.strip().split(':')
                sl_page_uuid[lst_line[0]] = lst_line[1]
        # Если после вычитывания не обнаружили формы для отсутствующих объектов
        # (например, увеличилось количество объектов), то дозаписываем
        with open(os.path.join('File_for_Import', 'Mnemo', 'DRV', 'Systemach', 'uuid_drv'),
                  'a', encoding='UTF-8') as f_uuid_write:
            # Пробегаемся по УНИКАЛЬНЫМ объектам
            for cpus, obj in sl_cpus_object.items():
                if set(cpus) & set(sl_one_driver_cpu.keys()) and f"{name_page}_0_{obj[0]}" not in sl_page_uuid:
                    generate_uuid = uuid.uuid4()
                    sl_page_uuid[f"{name_page}_0_{obj[0]}"] = f'{generate_uuid}'
                    f_uuid_write.write(f'{name_page}_0_{obj[0]}:{generate_uuid}\n')

    # Для каждого УНИКАЛЬНОГО объекта(уникального ранее определили по составу ПЛК) создаём мнемосхему 01_FormAlg
    # только в том случае, если у него определены какие-то режимы
    for cpus, obj in sl_cpus_object.items():
        if set(cpus) & set(sl_one_driver_cpu.keys()):
            param_drv = list()
            for plc in [i for i in cpus if i in sl_one_driver_cpu]:
                param_drv += list(sl_one_driver_cpu[plc].keys())
            # Узнаём количество требуемых листов, деля количество требуемых элементов на количество на одном листе
            start_list = 1
            count = 0
            # sl_list_par = {номер листа: кортеж защит листа}
            # При разбивке на листы учитывается количество параметров на листе, в том числе само наименование узла
            sl_list_par = {}
            for i in range(len(param_drv)):
                count += 1
                param_drv[i] = (start_list, param_drv[i])
                if count == par_one_list:
                    count = 0
                    start_list += 1

            for one_pz in param_drv:
                if one_pz[0] not in sl_list_par:
                    sl_list_par[one_pz[0]] = tuple()
                sl_list_par[one_pz[0]] += (one_pz[1],)
            # for i in sl_list_par:
            #     print(i)
            #     print(sl_list_par[i])
            num_text = 0

            # Для каждого листа в словаре листов с параметрами...
            for page, pars_drv in sl_list_par.items():
                # Вносим инфу в словарь
                # ...создаём родительский узел листа
                if f'{name_page}_{page}_{obj[0]}' not in sl_page_uuid:
                    generate_uuid_page = uuid.uuid4()
                    sl_page_uuid[f'{name_page}_{page}_{obj[0]}'] = f'{generate_uuid_page}'
                    with open(os.path.join('File_for_Import', 'Mnemo', 'DRV', 'Systemach', 'uuid_drv'),
                              'a', encoding='UTF-8') as f_uuid_write:
                        f_uuid_write.write(f'{name_page}_{page}_{obj[0]}:{generate_uuid_page}\n')
                root_type = ET.Element(
                    'type', access_modifier="private", name=f"{name_page}_{page}_{obj[0]}",
                    display_name=f"{name_page}_{page}_{obj[0]}",
                    uuid=sl_page_uuid.get(f'{name_page}_{page}_{obj[0]}', ''),
                    base_type="00_SubPage",
                    base_type_id=f"{sl_uuid_base.get('00_SubPage', '3fe01b7a-fed7-41d2-aa19-ca3e78391035')}",
                    ver="3"
                )
                # ...заполняем стандартную информацию
                ET.SubElement(root_type, 'designed', target='X', value="0", ver="3")
                ET.SubElement(root_type, 'designed', target='Y', value="0", ver="3")
                ET.SubElement(root_type, 'designed', target='ZValue', value="0", ver="3")
                ET.SubElement(root_type, 'designed', target='Rotation', value="0", ver="3")
                ET.SubElement(root_type, 'designed', target='Scale', value="1", ver="3")
                ET.SubElement(root_type, 'designed', target='Visible', value="true", ver="3")
                ET.SubElement(root_type, 'designed', target='Enabled', value="true", ver="3")
                ET.SubElement(root_type, 'designed', target='Tooltip', value="", ver="3")
                ET.SubElement(root_type, 'designed', target='Width', value=f"{gor_base}", ver="3")
                ET.SubElement(root_type, 'designed', target='Height', value=f"{vert_base}", ver="3")
                ET.SubElement(root_type, 'designed', target='PenColor', value="4278190080", ver="3")
                ET.SubElement(root_type, 'designed', target='PenStyle', value="0", ver="3")
                ET.SubElement(root_type, 'designed', target='PenWidth', value="1", ver="3")
                ET.SubElement(root_type, 'designed', target='BrushColor', value="0xffbfbfbf", ver="3")
                ET.SubElement(root_type, 'designed', target="BrushStyle", value="1", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowX", value="0", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowY", value="0", ver="3")

                # Вносим размеры мнемосхемы, пока так, позже может измениться
                ET.SubElement(root_type, 'designed', target="WindowWidth", value=f"{size_shirina}", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowHeight", value=f"{window_height}", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowCaption",
                              value=f"{name_page}_{page}_{obj[0]}", ver="3")

                ET.SubElement(root_type, 'designed', target="ShowWindowCaption", value="true", ver="3")
                ET.SubElement(root_type, 'designed', target="ShowWindowMinimize", value="true", ver="3")
                ET.SubElement(root_type, 'designed', target="ShowWindowMaximize", value="true", ver="3")
                ET.SubElement(root_type, 'designed', target="ShowWindowClose", value="true", ver="3")
                ET.SubElement(root_type, 'designed', target="AlwaysOnTop", value="false", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowSizeMode", value="2", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowBorderStyle", value="1", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowState", value="0", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowScalingMode", value="0", ver="3")
                ET.SubElement(root_type, 'designed', target="MonitorNumber", value="0", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowPosition", value="1", ver="3")
                ET.SubElement(root_type, 'designed', target="WindowCloseMode", value="0", ver="3")
                ET.SubElement(root_type, 'designed', target="Opacity", value="1", ver="3")

                # Добавляем Текст с описанием листа
                num_sub_text_discription = ET.SubElement(root_type, 'object', access_modifier="private",
                                                         name=f"Description_list",
                                                         display_name=f"Description_list",
                                                         uuid=f"{uuid.uuid4()}",
                                                         base_type="Text",
                                                         base_type_id=sl_uuid_base.get('Text', ''), ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='X', value="40.5", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Y', value="13", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='ZValue', value="0", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Rotation', value="0", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Scale', value="1", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Visible', value="true", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Enabled', value="true", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Tooltip', value="", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Width', value="535", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Height', value="30", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target='Text',
                              value=f"Драйвер {name_pag_rus} страница {page}", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target="Font",
                              value="PT Astra Sans,20,-1,5,75,0,0,0,0,0,Полужирный", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target="FontColor", value="0xff000000", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target="TextAlignment", value="129", ver="3")
                ET.SubElement(num_sub_text_discription, 'designed', target="Opacity", value="1", ver="3")

                # Добавляем параметры
                x_start = sl_start.get(name_group, (3, 10))[0]
                y_start = sl_start.get(name_group, (3, 10))[1]
                x_point = x_start
                y_point = y_start
                count_par = 0
                for one_drv_par in pars_drv:
                    num_text += 1
                    base_type_param = sl_base_drv_param.get(sl_one_driver_par[one_drv_par][0], ('None', 'None'))
                    num_sub_par = ET.SubElement(root_type, 'object', access_modifier="private",
                                                name=f"Параметр_{num_text}_{one_drv_par}",
                                                display_name=f"Параметр_{num_text}_{one_drv_par}",
                                                uuid=f"{uuid.uuid4()}",
                                                base_type=f"{base_type_param[0]}",
                                                base_type_id=f"{base_type_param[1]}", ver="3")

                    ET.SubElement(num_sub_par, 'designed', target="X", value=f"{x_point}", ver="3")
                    ET.SubElement(num_sub_par, 'designed', target="Y", value=f"{y_point}", ver="3")
                    y_point += sl_size_element.get(name_group, {'size_el': (0, 500)})['size_el'][1]
                    count_par += 1
                    if count_par == par_vert_count:
                        count_par = 0
                        y_point = y_start
                        x_point += sl_size_element.get(name_group, {'size_el': (500, 0)})['size_el'][0]

                    ET.SubElement(num_sub_par, 'designed', target="Rotation", value="0", ver="3")
                    ET.SubElement(num_sub_par, 'init', target="_init_Object",
                                  ver="3", value=f"{name_group}.{one_drv_par}")
                    # ET.SubElement(num_sub_par, 'init', target="_init_APSource", ver="4",
                    # ref="here.ApSource_CurrentForm")
                    # ET.SubElement(num_sub_par, 'init', target="_AbonentName", ver="4", ref="here._init_GPAPath")
                    ET.SubElement(num_sub_par, 'init', target="_AbonentPath", ver="5", ref="here._init_GPAPath")

                # Ещё одна базовая информация
                apsource_currentform = ET.SubElement(root_type, 'object', access_modifier="private",
                                                     name="ApSource_CurrentForm",
                                                     display_name="ApSource_CurrentForm",
                                                     uuid=f"{uuid.uuid4()}",
                                                     base_type="ApSource",
                                                     base_type_id=sl_uuid_base.get('ApSource', ''), ver="3")
                ET.SubElement(apsource_currentform, 'designed', target="Active", value="true", ver="3")
                ET.SubElement(apsource_currentform, 'designed', target="ReAdvise", value="0", ver="3")
                ET.SubElement(apsource_currentform, 'init', target="ParentSource", ver="3", ref="_init_ApSource")
                ET.SubElement(apsource_currentform, 'init', target="Path", ver="3", ref="_init_GPAPath")

                ET.SubElement(root_type, 'param', access_modifier="private", name="_init_ApSource",
                              display_name="_init_ApSource",
                              uuid=f"{uuid.uuid4()}",
                              base_type="ApSource", base_type_id=sl_uuid_base.get('ApSource', ''),
                              base_const="true", base_ref="true", ver="3")
                ET.SubElement(root_type, 'param', access_modifier="private", name="_init_GPAPath",
                              display_name="_init_GPAPath",
                              uuid=f"{uuid.uuid4()}",
                              base_type="string", base_type_id=sl_uuid_base.get('string', ''), ver="3")

                # Нормируем и записываем страницу мнемосхемы
                temp = ET.tostring(root_type).decode('UTF-8')
                check_diff_mnemo(new_data=multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                                         pretty_print=True,
                                                                                         encoding='unicode')),
                                 check_path=os.path.join('File_for_Import', 'Mnemo', 'DRV'),
                                 file_name_check=f'{name_page}_{page}_{obj[0]}.omobj',
                                 message_print=f'Требуется заменить мнемосхему {name_page}_{page}_{obj[0]}.omobj'
                                 )
                # with open(os.path.join('File_for_Import', 'Mnemo', 'DRV', f'{name_page}_{page}_{obj[0]}.omobj'),
                #           'w', encoding='UTF-8') as f_out:
                #     f_out.write(multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
                #                                                                pretty_print=True, encoding='unicode')))

            # Создаём главное окно ПЗ_0 ()
            root_list = ET.Element(
                'type', access_modifier="private", name=f"{name_page}_0_{obj[0]}",
                display_name=f"{name_page}_0_{obj[0]}",
                uuid=sl_page_uuid.get(f'{name_page}_0_{obj[0]}'),
                base_type="00_SubBase",
                base_type_id=f"{sl_uuid_base.get('00_SubBase', '99471dea-1c95-471c-9960-b4f7a539d437')}",
                ver="3"
            )
            # ...заполняем стандартную информацию
            ET.SubElement(root_list, 'designed', target='X', value="0", ver="3")
            ET.SubElement(root_list, 'designed', target='Y', value="0", ver="3")
            ET.SubElement(root_list, 'designed', target='ZValue', value="0", ver="3")
            ET.SubElement(root_list, 'designed', target='Rotation', value="0", ver="3")
            ET.SubElement(root_list, 'designed', target='Scale', value="1", ver="3")
            ET.SubElement(root_list, 'designed', target='Visible', value="true", ver="3")
            ET.SubElement(root_list, 'designed', target='Enabled', value="true", ver="3")
            ET.SubElement(root_list, 'designed', target='Tooltip', value="", ver="3")
            ET.SubElement(root_list, 'designed', target='Width', value=f"{gor_base}", ver="3")
            ET.SubElement(root_list, 'designed', target='Height', value=f"{vert_base}", ver="3")
            ET.SubElement(root_list, 'designed', target='PenColor', value="4278190080", ver="3")
            ET.SubElement(root_list, 'designed', target='PenStyle', value="0", ver="3")
            ET.SubElement(root_list, 'designed', target='PenWidth', value="1", ver="3")
            ET.SubElement(root_list, 'designed', target='BrushColor', value="0xffbfbfbf", ver="3")
            ET.SubElement(root_list, 'designed', target="BrushStyle", value="1", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowX", value="0", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowY", value="0", ver="3")

            # Вносим размеры мнемосхемы, пока так, позже может измениться
            ET.SubElement(root_list, 'designed', target="WindowWidth", value=f"{size_shirina}", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowHeight", value=f"{window_height}", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowCaption", value=f"Драйвер {name_pag_rus} main", ver="3")

            ET.SubElement(root_list, 'designed', target="ShowWindowCaption", value="true", ver="3")
            ET.SubElement(root_list, 'designed', target="ShowWindowMinimize", value="true", ver="3")
            ET.SubElement(root_list, 'designed', target="ShowWindowMaximize", value="true", ver="3")
            ET.SubElement(root_list, 'designed', target="ShowWindowClose", value="true", ver="3")
            ET.SubElement(root_list, 'designed', target="AlwaysOnTop", value="false", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowSizeMode", value="2", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowBorderStyle", value="1", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowState", value="0", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowScalingMode", value="0", ver="3")
            ET.SubElement(root_list, 'designed', target="MonitorNumber", value="0", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowPosition", value="1", ver="3")
            ET.SubElement(root_list, 'designed', target="WindowCloseMode", value="0", ver="3")

            obj_frame = ET.SubElement(
                root_list, 'object', access_modifier="private", name="MainFrame",
                display_name="MainFrame",
                uuid=f"{uuid.uuid4()}",
                base_type=f"{name_page}_1",
                base_type_id=f"{sl_uuid_base.get('Frame', '71f78e19-ef99-4133-a029-2968b14f02b6')}",
                ver="3"
            )
            # ...заполняем стандартную информацию фрейма
            ET.SubElement(obj_frame, 'designed', target='X', value="0", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Y', value="0", ver="3")
            ET.SubElement(obj_frame, 'designed', target='ZValue', value="0", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Rotation', value="0", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Scale', value="1", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Visible', value="true", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Opacity', value="1", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Enabled', value="true", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Tooltip', value="", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Width', value=f"{gor_base}", ver="3")
            ET.SubElement(obj_frame, 'designed', target='Height', value=f"{vert_base}", ver="3")
            ET.SubElement(obj_frame, 'designed', target='PenColor', value="4278190080", ver="3")
            ET.SubElement(obj_frame, 'designed', target='PenStyle', value="1", ver="3")
            ET.SubElement(obj_frame, 'designed', target='PenWidth', value="1", ver="3")
            ET.SubElement(obj_frame, 'designed', target='BrushColor', value="4278190080", ver="3")
            ET.SubElement(obj_frame, 'designed', target="BrushStyle", value="0", ver="3")
            ET.SubElement(obj_frame, 'designed', target="OverrideScaling", value="false", ver="3")
            ET.SubElement(obj_frame, 'designed', target="ShowScrollBars", value="true", ver="3")
            ET.SubElement(obj_frame, 'designed', target="MoveByMouse", value="false", ver="3")

            ET.SubElement(root_list, 'designed', target="Opacity", value="1", ver="3")

            do_on_action = ET.SubElement(root_list, 'do-on', access_modifier="private", name="Handler_1",
                                         display_name="Handler_1", ver="3", event="Opened", frame_link="MainFrame",
                                         form_action="open-in-frame",
                                         form_by_id="false")
            obj_do_on_action = ET.SubElement(do_on_action, 'object', access_modifier="private",
                                             uuid=f"{uuid.uuid4()}",
                                             base_type=f"{name_page}_1_{obj[0]}",
                                             base_type_id=f"{sl_page_uuid.get(f'{name_page}_1_{obj[0]}')}",
                                             ver="3")
            ET.SubElement(obj_do_on_action, 'init', target=f"Link_DRV", ver="3", ref="here")
            ET.SubElement(obj_do_on_action, 'init', target="_init_ApSource", ver="3", ref="here.ApSource_Main")
            ET.SubElement(obj_do_on_action, 'init', target="_init_GPAPath", ver="3", ref="here._pathToGPA")

            ET.SubElement(
                root_list, 'object', access_modifier="private",
                name="NameOpened", display_name="NameOpened",
                uuid=f"{uuid.uuid4()}", base_type="notifying_string",
                base_type_id=f"{sl_uuid_base.get('notifying_string', '14976fbf-36ab-415f-abc3-9f8fdc217351')}",
                ver="3"
            )

            # Добавляем кнопки переключения листов
            x_button_start = gor_base - (321 + 50 * len(sl_list_par))
            for page in sl_list_par:
                x_swift = (page - 1) * 50
                obj_button = ET.SubElement(
                    root_list, 'object', access_modifier="private",
                    name=f"ExtPageButton_{page}", display_name=f"ExtPageButton_{page}",
                    uuid=f"{uuid.uuid4()}",
                    base_type="ExtPageButton",
                    base_type_id=f"{sl_uuid_base.get('ExtPageButton', '2c2d6f3d-f500-4be6-b80c-620853cd99e3')}",
                    ver="3")
                ET.SubElement(obj_button, 'designed', target='X', value=f"{x_button_start + x_swift}", ver="3")
                ET.SubElement(obj_button, 'designed', target='Y', value=f"{10}", ver="3")  # vert_base - 60
                ET.SubElement(obj_button, 'designed', target='Rotation', value="0", ver="3")
                ET.SubElement(obj_button, 'designed', target='Width', value="50", ver="3")
                ET.SubElement(obj_button, 'designed', target='Height', value="40", ver="3")
                ET.SubElement(obj_button, 'designed', target='Text', value=f"{page}", ver="3")
                ET.SubElement(obj_button, 'designed', target='Font',
                              value="PT Astra Sans,16,-1,5,75,0,0,0,0,0,Полужирный", ver="3")

                tagret_name = ET.SubElement(obj_button, 'do-trace', access_modifier="private", target='_Name', ver="3")
                body = ET.SubElement(tagret_name, 'body')
                ET.SubElement(body, 'forCDATA')
                ET.SubElement(obj_button, 'init', target='_IDtoOpen', ver="3",
                              value=f"{sl_page_uuid.get(f'{name_page}_{page}_{obj[0]}')}")

                do_on_action = ET.SubElement(obj_button, 'do-on', access_modifier="private", name="Handler_1",
                                             display_name="Handler_1", ver="3", event="MouseClick",
                                             frame_link="MainFrame",
                                             form_action="open-in-frame",
                                             form_by_id="false")
                obj_do_on_action = ET.SubElement(do_on_action, 'object', access_modifier="private",
                                                 uuid=f"{uuid.uuid4()}",
                                                 base_type=f"{name_page}_{page}_{obj[0]}",
                                                 base_type_id=f"{sl_page_uuid.get(f'{name_page}_{page}_{obj[0]}')}",
                                                 ver="3")
                ET.SubElement(obj_do_on_action, 'init', target=f"Link_PZ", ver="3", ref="here")
                ET.SubElement(obj_do_on_action, 'init', target="_init_ApSource", ver="3", ref="here.ApSource_Main")
                ET.SubElement(obj_do_on_action, 'init', target="_init_GPAPath", ver="3", ref="here._pathToGPA")

            # Добавляем ещё стандартной инфы
            apsource_currentform = ET.SubElement(root_list, 'object', access_modifier="private",
                                                 name="ApSource_CurrentForm",
                                                 display_name="ApSource_CurrentForm",
                                                 uuid=f"{uuid.uuid4()}",
                                                 base_type="ApSource",
                                                 base_type_id=sl_uuid_base.get('ApSource', ''), ver="3")
            ET.SubElement(apsource_currentform, 'designed', target="Active", value="true", ver="3")
            ET.SubElement(apsource_currentform, 'designed', target="ReAdvise", value="0", ver="3")
            ET.SubElement(apsource_currentform, 'init', target="ParentSource", ver="3", ref="_init_ApSource")
            ET.SubElement(apsource_currentform, 'init', target="Path", ver="3", ref="_init_GPAPath")
            ET.SubElement(apsource_currentform, 'designed', target="Path", value="", ver="3")

            ET.SubElement(root_list, 'param', access_modifier="private", name="_init_ApSource",
                          display_name="_init_ApSource",
                          uuid=f"{uuid.uuid4()}",
                          base_type="ApSource", base_type_id=sl_uuid_base.get('ApSource', ''),
                          base_const="true", base_ref="true", ver="3")
            ET.SubElement(root_list, 'param', access_modifier="private", name="_init_GPAPath",
                          display_name="_init_GPAPath",
                          uuid=f"{uuid.uuid4()}",
                          base_type="string", base_type_id=sl_uuid_base.get('string', ''), ver="3")

            ET.SubElement(root_list, 'object', access_modifier="private",
                          name="DebugTool_1", display_name="DebugTool_1",
                          uuid=f"{uuid.uuid4()}",
                          base_type="DebugTool",
                          base_type_id=sl_uuid_base.get('DebugTool', ''), ver="3")
            ET.SubElement(root_list, 'object', access_modifier="private",
                          name="_pathToGPA", display_name="_pathToGPA",
                          uuid=f"{uuid.uuid4()}",
                          base_type="notifying_string",
                          base_type_id=sl_uuid_base.get('notifying_string', ''), ver="3")
            apsource_main = ET.SubElement(root_list, 'object', access_modifier="private",
                                          name="ApSource_Main", display_name="ApSource_Main",
                                          uuid=f"{uuid.uuid4()}",
                                          base_type="ApSource",
                                          base_type_id=sl_uuid_base.get('ApSource', ''), ver="3")
            ET.SubElement(apsource_main, 'designed', target="Active", value="true", ver="3")
            ET.SubElement(apsource_main, 'designed', target="ReAdvise", value="0", ver="3")
            ET.SubElement(apsource_main, 'designed', target="Path", value="", ver="3")
            ET.SubElement(apsource_main, 'init', target="ParentSource", ver="3", ref="here._init_ApSource")

            ET.SubElement(root_list, 'init', target="_pathToGPA", ver="3", ref="here._init_GPAPath")

            # Нормируем и записываем страницу мнемосхемы
            temp = ET.tostring(root_list).decode('UTF-8')
            check_diff_mnemo(new_data=multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                                     pretty_print=True,
                                                                                     encoding='unicode')),
                             check_path=os.path.join('File_for_Import', 'Mnemo', 'DRV'),
                             file_name_check=f'{name_page}_0_{obj[0]}.omobj',
                             message_print=f'Требуется заменить мнемосхему {name_page}_0_{obj[0]}.omobj'
                             )
            # with open(os.path.join('File_for_Import', 'Mnemo', 'DRV', f'{name_page}_0_{obj[0]}.omobj'),
            #           'w', encoding='UTF-8') as f_out:
            #     f_out.write(multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
            #                                                                pretty_print=True, encoding='unicode')))

    return


def create_mnemo_drv_general(sl_object_all: dict, name_group: str, size_shirina: int, size_vysota: int,
                             sl_mnemo_drv: dict, sl_type_drv: dict, name_page: str, sl_all_drv: dict):
    sl_page_uuid = {}
    # uuid.uuid4()
    if not os.path.exists(os.path.join('File_for_Import', 'Mnemo', f'General_DRV_Mnemo')):
        os.mkdir(os.path.join('File_for_Import', 'Mnemo', f'General_DRV_Mnemo'))
    if not os.path.exists(os.path.join('File_for_Import', 'Mnemo', f'General_DRV_Mnemo', 'Systemach')):
        os.mkdir(os.path.join('File_for_Import', 'Mnemo', f'General_DRV_Mnemo', 'Systemach'))

    # СЛОВАРЬ УНИКАЛЬНЫХ ОБЪЕКТОВ
    # Формируем словарь вида {кортеж контроллеров: (Объект, рус имя объекта, индекс объекта)}
    # При этом, если есть полное совпадение контроллеров, то дублирования нет
    sl_cpus_object = {}
    for obj, sl_cpu in sl_object_all.items():
        cpus = tuple(sl_cpu.keys())  # cpus = tuple(sorted(sl_cpu.keys()))
        if cpus not in sl_cpus_object:
            sl_cpus_object[cpus] = obj

    sl_size = {
        '1920x900': (1780, 900, 780),
        '1920x780': (1780, 780, 780)
    }

    # Словарь ID для типовых структур, возможно потом будет считываться с файла или как-то по-другому
    sl_uuid_base_default = {
        '00_SubPage': '3fe01b7a-fed7-41d2-aa19-ca3e78391035',
        'Text': '21d59f8d-2ca4-4592-92ca-b4dc48992a0f',
        'S_ALR': '401676e6-e678-4938-bc7a-8a3382258f93',
        'Line': '4dd08b15-1502-453f-a174-2c0a5aa850ba',
        'Point': '467f1af0-7bb4-4a61-b6fb-06e7bfd530d6',
        'ApSource': '966603da-f05e-4b4d-8ef0-919efbf8ab2c',
        'string': '76403785-f3d5-41a7-9eb6-d19d2aa2d95d',
        '00_SubBase': '99471dea-1c95-471c-9960-b4f7a539d437',
        'Frame': '71f78e19-ef99-4133-a029-2968b14f02b6',
        'notifying_string': '14976fbf-36ab-415f-abc3-9f8fdc217351',
        'ExtPageButton': '2c2d6f3d-f500-4be6-b80c-620853cd99e3',
        'DebugTool': '43946044-139a-43f4-a7b8-19a6074ffc56',
        '00_Base': '4f3aa327-d38a-4afe-8913-c7729acaafc0',
        'Button': '61e46e4a-827f-4dd2-ac8a-b68bcaddf442',
        'Alpha.Reports': '665556a0-5ea4-4768-8935-9ab18d0eb2a0'
    }
    sl_base_drv_param_default = {
        'DRV_AI.DRV_AI_PLC_View': ('S_DRV_AI_Discription', '803e851d-f716-4341-a237-717afdf13c9b'),
        'DRV_DI.DRV_DI_PLC_View': ('S_DRV_DI_Discription', '16abad7a-2e37-4edd-ad30-7317f4832b95'),
        'DRV_INT.DRV_INT_PLC_View': ('S_DRV_INT_Discription', '3ab70fca-70f2-492f-a7a6-92d58d785afd'),
        'DRV_AI.DRV_AI_IMIT_PLC_View': ('S_DRV_AI_Discription', '803e851d-f716-4341-a237-717afdf13c9b'),
        'DRV_DI.DRV_DI_IMIT_PLC_View': ('S_DRV_DI_Discription', '16abad7a-2e37-4edd-ad30-7317f4832b95'),
        'DRV_INT.DRV_INT_IMIT_PLC_View': ('S_DRV_INT_Discription', '3ab70fca-70f2-492f-a7a6-92d58d785afd'),
    }
    try:
        if os.path.exists(os.path.join('Template_Alpha', 'Systemach', 'Mnemo', f'uuid_base_elements.json')):
            with open(os.path.join('Template_Alpha', 'Systemach', 'Mnemo', f'uuid_base_elements.json'), 'r',
                      encoding='UTF-8') as f_sig:
                text_json = json_load(f_sig)
            sl_uuid_base = text_json
            sl_base_drv_param = text_json
        else:
            print('Файл Systemach/Mnemo/uuid_base_elements.json не найден, '
                  'uuid базовых элементов будут определены по умолчанию')
            sl_uuid_base = sl_uuid_base_default
            sl_base_drv_param = sl_base_drv_param_default
    except (Exception, KeyError):
        print('Файл Systemach/Mnemo/uuid_base_elements.json заполнен некорректно, '
              'uuid базовых элементов будут определены по умолчанию')
        sl_uuid_base = sl_uuid_base_default
        sl_base_drv_param = sl_base_drv_param_default

    # Словарь размеров элементов, тут по заполнению всё понятно
    sl_size_element = {name_group: {'size_el': ((591 + 2), (24 + 6)), 'size_text': (590.567, 24)}
                       }

    # Словарь расположения первого элемента, тут вроде всё понятно тоже - первый X, второй Y
    sl_start = {name_group: (11.111, 158)
                }
    gor_base = sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1920, 900))[0]
    vert_base = sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1920, 900))[1]
    window_height = sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1920, 900, 780))[2]
    # Узнаём, сколько целых параметров влезет по горизонтали
    # два пикселя по горизонтали между элементами, 591 - ширина элемента параметра
    par_gor_count = floor(gor_base / sl_size_element.get(name_group, {'size_el': (500, 0)})['size_el'][0])
    # Узнаём, сколько целых параметров влезет по вертикали
    # 6 пикеселей по вертикали между элементами, 92 - запас для кнопок переключения
    par_vert_count = floor((vert_base - sl_start.get(name_group, (0, 500))[1]) /
                           sl_size_element.get(name_group, {'size_el': (0, 500)})['size_el'][1])
    # Узнаём количество параметров на один лист
    par_one_list = (par_gor_count * par_vert_count)

    # Если не существует файла uuid_drv, то создаём его и записываем uuid форм вызовов алгоритмов
    # для каждого объекта

    sl_page_uuid = {}

    # print(sl_mnemo_drv)
    # for name_driver in sl_mnemo_drv:
    #     print(f'---------------{name_driver}---------------')
    #     for name_plc in sl_mnemo_drv[name_driver]:
    #         print(f'========{name_plc}===========')
    #         print(sl_mnemo_drv[name_driver][name_plc])

    # Обрабатываем и создаём мнемосхемы только для тех уникальных объектов, контроллеры которых содержат драйвера
    set_cpu_with_drv = {j for _, i in sl_mnemo_drv.items() for j in i}
    # for cpus, obj in sl_cpus_object.items():
    for cpus, obj in {i: j for i, j in sl_cpus_object.items() if set(i) & set_cpu_with_drv}.items():
        # print(cpus)
        sl_param_object = {}
        for name_driver, sl_cpu_par in sl_mnemo_drv.items():
            if name_driver not in sl_param_object:
                sl_param_object[name_driver] = list()
            for plc in (_ for _ in cpus if _ in set(sl_cpu_par.keys())):
                sl_param_object[name_driver] += sl_cpu_par.get(plc, list())
        # print(sl_param_object)

        for node_drv in sl_param_object:
            start_list = 1
            count = 0
            for j in range(len(sl_param_object[node_drv])):
                count += 1
                sl_param_object[node_drv][j] = (start_list, sl_param_object[node_drv][j])
                if count == par_one_list:
                    count = 1
                    start_list += 1

        # print(sl_param_object)
        # for i in sl_param_object:
        #     print(i)
        #     print(sl_param_object[i])
        sl_list_par = {}
        for name_driver in sl_param_object:
            for par in sl_param_object[name_driver]:
                if f'{name_driver[0]}_{par[0]}' not in sl_list_par:
                    sl_list_par[f'{name_driver[0]}_{par[0]}'] = (par[1],)
                else:
                    sl_list_par[f'{name_driver[0]}_{par[0]}'] += (par[1],)

        # print(sl_list_par)
        # for li in sl_list_par:
        #     print(li)
        #     print(sl_list_par[li])

        if not os.path.exists(os.path.join('File_for_Import', 'Mnemo', f'General_DRV_Mnemo', 'Systemach', 'uuid')):
            with open(os.path.join('File_for_Import', 'Mnemo', f'General_DRV_Mnemo', 'Systemach', 'uuid'),
                      'w', encoding='UTF-8') as f_uuid_write:
                if sl_list_par:
                    generate_uuid = uuid.uuid4()
                    sl_page_uuid[f"{name_page}_0_{obj[0]}"] = f'{generate_uuid}'
                    f_uuid_write.write(f'{name_page}_0_{obj[0]}:{generate_uuid}\n')
                for number_list in sl_list_par:
                    generate_uuid = uuid.uuid4()
                    sl_page_uuid[f"{number_list}_{obj[0]}"] = f'{generate_uuid}'
                    f_uuid_write.write(f'{number_list}_{obj[0]}:{generate_uuid}\n')
        else:
            # Если файл существует, то считываем и записываем в словарь
            with open(os.path.join('File_for_Import', 'Mnemo', f'General_DRV_Mnemo', 'Systemach', 'uuid'),
                      'r', encoding='UTF-8') as f_uuid_read:
                for line in f_uuid_read:
                    lst_line = line.strip().split(':')
                    sl_page_uuid[lst_line[0]] = lst_line[1]
            # Если после вычитывания не обнаружили формы для отсутствующих объектов
            # (например, увеличилось количество объектов), то дозаписываем
            with open(os.path.join('File_for_Import', 'Mnemo', f'General_DRV_Mnemo', 'Systemach', 'uuid'),
                      'a', encoding='UTF-8') as f_uuid_write:
                if f"{name_page}_0_{obj[0]}" not in sl_page_uuid and sl_list_par:
                    generate_uuid = uuid.uuid4()
                    sl_page_uuid[f"{name_page}_0_{obj[0]}"] = f'{generate_uuid}'
                    f_uuid_write.write(f'{name_page}_0_{obj[0]}:{generate_uuid}\n')
                for number_list in sl_list_par:
                    if f"{number_list}_{obj[0]}" not in sl_page_uuid:
                        generate_uuid = uuid.uuid4()
                        sl_page_uuid[f"{number_list}_{obj[0]}"] = f'{generate_uuid}'
                        f_uuid_write.write(f'{number_list}_{obj[0]}:{generate_uuid}\n')

        # print(sl_all_drv)
        # print(sl_type_drv)
        first_page = ''
        # для подсчёта страниц, чтобы удалить номер страницы, если страница одна
        check_count_page = tuple([_[:_.rfind('_')] for _ in sl_list_par])
        # Для каждого листа в словаре листов с параметрами...
        for page, drv_pars in sl_list_par.items():
            if not first_page:
                first_page = page
            # На всякий случай ещё раз проверяем
            if f'{page}_{obj[0]}' not in sl_page_uuid:
                generate_uuid_page = uuid.uuid4()
                sl_page_uuid[f'{page}_{obj[0]}'] = f'{generate_uuid_page}'
                with open(os.path.join('File_for_Import', 'Mnemo', 'General_DRV_Mnemo', 'Systemach', 'uuid'),
                          'a', encoding='UTF-8') as f_uuid_write:
                    f_uuid_write.write(f'{page}_{obj[0]}:{generate_uuid_page}\n')

            # print(obj[0], page)
            name_drv_eng = page[:page.rfind('_')]
            name_drv_rus = sl_all_drv.get(name_drv_eng, 'Unknown driver')
            # ...создаём родительский узел листа
            root_type = ET.Element(
                'type', access_modifier="private", name=f"{page}_{obj[0]}",
                display_name=f"{page}_{obj[0]}",
                uuid=f"{sl_page_uuid[f'{page}_{obj[0]}']}",
                base_type="00_SubPage",
                base_type_id=f"{sl_uuid_base.get('00_SubPage', '3fe01b7a-fed7-41d2-aa19-ca3e78391035')}",
                ver="3")
            # ...заполняем стандартную информацию
            ET.SubElement(root_type, 'designed', target='X', value="0", ver="3")
            ET.SubElement(root_type, 'designed', target='Y', value="0", ver="3")
            ET.SubElement(root_type, 'designed', target='ZValue', value="0", ver="3")
            ET.SubElement(root_type, 'designed', target='Rotation', value="0", ver="3")
            ET.SubElement(root_type, 'designed', target='Scale', value="1", ver="3")
            ET.SubElement(root_type, 'designed', target='Visible', value="true", ver="3")
            ET.SubElement(root_type, 'designed', target='Enabled', value="true", ver="3")
            ET.SubElement(root_type, 'designed', target='Tooltip', value="", ver="3")
            ET.SubElement(root_type, 'designed', target='Width', value=f"{gor_base}", ver="3")
            ET.SubElement(root_type, 'designed', target='Height', value=f"{vert_base}", ver="3")
            ET.SubElement(root_type, 'designed', target='PenColor', value="4278190080", ver="3")
            ET.SubElement(root_type, 'designed', target='PenStyle', value="0", ver="3")
            ET.SubElement(root_type, 'designed', target='PenWidth', value="1", ver="3")
            ET.SubElement(root_type, 'designed', target='BrushColor', value="0xffbfbfbf", ver="3")
            ET.SubElement(root_type, 'designed', target="BrushStyle", value="1", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowX", value="0", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowY", value="0", ver="3")

            # Вносим размеры мнемосхемы, пока так, позже может измениться
            ET.SubElement(root_type, 'designed', target="WindowWidth", value=f"{size_shirina}", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowHeight", value=f"{window_height}", ver="3")
            count_list_drv = check_count_page.count(page[:page.rfind('_')])
            name_but = f"{name_drv_rus} {page[page.rfind('_') + 1:]}" if count_list_drv > 1 else f"{name_drv_rus}"
            ET.SubElement(root_type, 'designed', target="WindowCaption",
                          value=f"{name_but}", ver="3")

            ET.SubElement(root_type, 'designed', target="ShowWindowCaption", value="true", ver="3")
            ET.SubElement(root_type, 'designed', target="ShowWindowMinimize", value="true", ver="3")
            ET.SubElement(root_type, 'designed', target="ShowWindowMaximize", value="true", ver="3")
            ET.SubElement(root_type, 'designed', target="ShowWindowClose", value="true", ver="3")
            ET.SubElement(root_type, 'designed', target="AlwaysOnTop", value="false", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowSizeMode", value="2", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowBorderStyle", value="1", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowState", value="0", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowScalingMode", value="0", ver="3")
            ET.SubElement(root_type, 'designed', target="MonitorNumber", value="0", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowPosition", value="1", ver="3")
            ET.SubElement(root_type, 'designed', target="WindowCloseMode", value="0", ver="3")
            ET.SubElement(root_type, 'designed', target="Opacity", value="1", ver="3")

            # Добавляем Текст с описанием листа
            num_sub_text_discription = ET.SubElement(root_type, 'object', access_modifier="private",
                                                     name=f"Description_list",
                                                     display_name=f"Description_list",
                                                     uuid=f"{uuid.uuid4()}",
                                                     base_type="Text",
                                                     base_type_id=sl_uuid_base.get('Text', ''), ver="3")
            ET.SubElement(num_sub_text_discription, 'designed', target='X', value="40.5", ver="3")
            ET.SubElement(num_sub_text_discription, 'designed', target='Y', value="110", ver="3")
            ET.SubElement(num_sub_text_discription, 'designed', target='ZValue', value="0", ver="3")
            ET.SubElement(num_sub_text_discription, 'designed', target='Rotation', value="0", ver="3")
            ET.SubElement(num_sub_text_discription, 'designed', target='Scale', value="1", ver="3")
            ET.SubElement(num_sub_text_discription, 'designed', target='Visible', value="true", ver="3")
            ET.SubElement(num_sub_text_discription, 'designed', target='Enabled', value="true", ver="3")
            ET.SubElement(num_sub_text_discription, 'designed', target='Tooltip', value="", ver="3")
            ET.SubElement(num_sub_text_discription, 'designed', target='Width', value="535", ver="3")
            ET.SubElement(num_sub_text_discription, 'designed', target='Height', value="30", ver="3")

            ET.SubElement(num_sub_text_discription, 'designed', target='Text',
                          value=f"{name_drv_rus} страница {page[page.rfind('_')+1:]}", ver="3")  # f"Драйвер
            ET.SubElement(num_sub_text_discription, 'designed', target="Font",
                          value="PT Astra Sans,14,-1,5,75,0,0,0,0,0,Полужирный", ver="3")
            ET.SubElement(num_sub_text_discription, 'designed', target="FontColor", value="0xff000000", ver="3")
            ET.SubElement(num_sub_text_discription, 'designed', target="TextAlignment", value="129", ver="3")
            ET.SubElement(num_sub_text_discription, 'designed', target="Opacity", value="1", ver="3")

            # Добавляем параметры
            x_start = sl_start.get(name_group, (3, 10))[0]
            y_start = sl_start.get(name_group, (3, 10))[1]
            x_point = x_start
            y_point = y_start
            count_par = 0
            # num_text = 0
            for one_drv_par in drv_pars:
                # num_text += 1
                num_text = drv_pars.index(one_drv_par) + 1
                # print(name_drv_eng)
                # print(name_drv_rus)
                type_param_get = sl_type_drv.get(name_drv_rus).get(one_drv_par)
                base_type_param = sl_base_drv_param.get(type_param_get, ('None', 'None'))

                num_sub_par = ET.SubElement(root_type, 'object', access_modifier="private",
                                            name=f"Параметр_{num_text}_{one_drv_par}",
                                            display_name=f"Параметр_{num_text}_{one_drv_par}",
                                            uuid=f"{uuid.uuid4()}",
                                            base_type=f"{base_type_param[0]}",
                                            base_type_id=f"{base_type_param[1]}", ver="3")

                ET.SubElement(num_sub_par, 'designed', target="X", value=f"{x_point}", ver="3")
                ET.SubElement(num_sub_par, 'designed', target="Y", value=f"{y_point}", ver="3")
                y_point += sl_size_element.get(name_group, {'size_el': (0, 500)})['size_el'][1]
                count_par += 1
                if count_par == par_vert_count:
                    count_par = 0
                    y_point = y_start
                    x_point += sl_size_element.get(name_group, {'size_el': (500, 0)})['size_el'][0]

                ET.SubElement(num_sub_par, 'designed', target="Rotation", value="0", ver="3")
                ET.SubElement(num_sub_par, 'init', target="_init_Object",
                              ver="3", value=f"{name_group}.{name_drv_eng}.{one_drv_par}")
                ET.SubElement(num_sub_par, 'init', target="_AbonentPath", ver="5", ref="here._init_GPAPath")

            # Ещё одна базовая информация
            apsource_currentform = ET.SubElement(root_type, 'object', access_modifier="private",
                                                 name="ApSource_CurrentForm",
                                                 display_name="ApSource_CurrentForm",
                                                 uuid=f"{uuid.uuid4()}",
                                                 base_type="ApSource",
                                                 base_type_id=sl_uuid_base.get('ApSource', ''), ver="3")
            ET.SubElement(apsource_currentform, 'designed', target="Active", value="true", ver="3")
            ET.SubElement(apsource_currentform, 'designed', target="ReAdvise", value="0", ver="3")
            ET.SubElement(apsource_currentform, 'init', target="ParentSource", ver="3", ref="_init_ApSource")
            ET.SubElement(apsource_currentform, 'init', target="Path", ver="3", ref="_init_GPAPath")

            ET.SubElement(root_type, 'param', access_modifier="private", name="_init_ApSource",
                          display_name="_init_ApSource",
                          uuid=f"{uuid.uuid4()}",
                          base_type="ApSource", base_type_id=sl_uuid_base.get('ApSource', ''),
                          base_const="true", base_ref="true", ver="3")
            ET.SubElement(root_type, 'param', access_modifier="private", name="_init_GPAPath",
                          display_name="_init_GPAPath",
                          uuid=f"{uuid.uuid4()}",
                          base_type="string", base_type_id=sl_uuid_base.get('string', ''), ver="3")

            # Нормируем и записываем страницу мнемосхемы
            temp = ET.tostring(root_type).decode('UTF-8')
            check_diff_mnemo(new_data=multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                                     pretty_print=True,
                                                                                     encoding='unicode')),
                             check_path=os.path.join('File_for_Import', 'Mnemo', 'General_DRV_Mnemo'),
                             file_name_check=f'{page}_{obj[0]}.omobj',
                             message_print=f'Требуется заменить мнемосхему {page}_{obj[0]}.omobj '
                                           f'(Mnemo/General_DRV_Mnemo/{page}_{obj[0]}.omobj)')
        # Создаём главное 0-окно
        root_list = ET.Element(
            'type', access_modifier="private", name=f"{name_page}_0_{obj[0]}",
            display_name=f"{name_page}_0_{obj[0]}",
            uuid=sl_page_uuid.get(f'{name_page}_0_{obj[0]}'),
            base_type="00_SubBase",
            base_type_id=f"{sl_uuid_base.get('00_SubBase', '99471dea-1c95-471c-9960-b4f7a539d437')}",
            ver="3"
        )
        # ...заполняем стандартную информацию
        ET.SubElement(root_list, 'designed', target='X', value="0", ver="3")
        ET.SubElement(root_list, 'designed', target='Y', value="0", ver="3")
        ET.SubElement(root_list, 'designed', target='ZValue', value="0", ver="3")
        ET.SubElement(root_list, 'designed', target='Rotation', value="0", ver="3")
        ET.SubElement(root_list, 'designed', target='Scale', value="1", ver="3")
        ET.SubElement(root_list, 'designed', target='Visible', value="true", ver="3")
        ET.SubElement(root_list, 'designed', target='Enabled', value="true", ver="3")
        ET.SubElement(root_list, 'designed', target='Tooltip', value="", ver="3")
        ET.SubElement(root_list, 'designed', target='Width', value=f"{gor_base}", ver="3")
        ET.SubElement(root_list, 'designed', target='Height', value=f"{vert_base}", ver="3")
        ET.SubElement(root_list, 'designed', target='PenColor', value="4278190080", ver="3")
        ET.SubElement(root_list, 'designed', target='PenStyle', value="0", ver="3")
        ET.SubElement(root_list, 'designed', target='PenWidth', value="1", ver="3")
        ET.SubElement(root_list, 'designed', target='BrushColor', value="0xffbfbfbf", ver="3")
        ET.SubElement(root_list, 'designed', target="BrushStyle", value="1", ver="3")
        ET.SubElement(root_list, 'designed', target="WindowX", value="0", ver="3")
        ET.SubElement(root_list, 'designed', target="WindowY", value="0", ver="3")

        # Вносим размеры мнемосхемы, пока так, позже может измениться
        ET.SubElement(root_list, 'designed', target="WindowWidth", value=f"{size_shirina}", ver="3")
        ET.SubElement(root_list, 'designed', target="WindowHeight", value=f"{window_height}", ver="3")
        ET.SubElement(root_list, 'designed', target="WindowCaption", value=f"Драйверы", ver="3")

        ET.SubElement(root_list, 'designed', target="ShowWindowCaption", value="true", ver="3")
        ET.SubElement(root_list, 'designed', target="ShowWindowMinimize", value="true", ver="3")
        ET.SubElement(root_list, 'designed', target="ShowWindowMaximize", value="true", ver="3")
        ET.SubElement(root_list, 'designed', target="ShowWindowClose", value="true", ver="3")
        ET.SubElement(root_list, 'designed', target="AlwaysOnTop", value="false", ver="3")
        ET.SubElement(root_list, 'designed', target="WindowSizeMode", value="2", ver="3")
        ET.SubElement(root_list, 'designed', target="WindowBorderStyle", value="1", ver="3")
        ET.SubElement(root_list, 'designed', target="WindowState", value="0", ver="3")
        ET.SubElement(root_list, 'designed', target="WindowScalingMode", value="0", ver="3")
        ET.SubElement(root_list, 'designed', target="MonitorNumber", value="0", ver="3")
        ET.SubElement(root_list, 'designed', target="WindowPosition", value="1", ver="3")
        ET.SubElement(root_list, 'designed', target="WindowCloseMode", value="0", ver="3")

        obj_frame = ET.SubElement(
            root_list, 'object', access_modifier="private", name="MainFrame",
            display_name="MainFrame",
            uuid=f"{uuid.uuid4()}",
            base_type=f"{first_page}",
            base_type_id=f"{sl_uuid_base.get('Frame', '71f78e19-ef99-4133-a029-2968b14f02b6')}",
            ver="3"
        )
        # ...заполняем стандартную информацию фрейма
        ET.SubElement(obj_frame, 'designed', target='X', value="0", ver="3")
        ET.SubElement(obj_frame, 'designed', target='Y', value="0", ver="3")
        ET.SubElement(obj_frame, 'designed', target='ZValue', value="0", ver="3")
        ET.SubElement(obj_frame, 'designed', target='Rotation', value="0", ver="3")
        ET.SubElement(obj_frame, 'designed', target='Scale', value="1", ver="3")
        ET.SubElement(obj_frame, 'designed', target='Visible', value="true", ver="3")
        ET.SubElement(obj_frame, 'designed', target='Opacity', value="1", ver="3")
        ET.SubElement(obj_frame, 'designed', target='Enabled', value="true", ver="3")
        ET.SubElement(obj_frame, 'designed', target='Tooltip', value="", ver="3")
        ET.SubElement(obj_frame, 'designed', target='Width', value=f"{gor_base}", ver="3")
        ET.SubElement(obj_frame, 'designed', target='Height', value=f"{vert_base}", ver="3")
        ET.SubElement(obj_frame, 'designed', target='PenColor', value="4278190080", ver="3")
        ET.SubElement(obj_frame, 'designed', target='PenStyle', value="1", ver="3")
        ET.SubElement(obj_frame, 'designed', target='PenWidth', value="1", ver="3")
        ET.SubElement(obj_frame, 'designed', target='BrushColor', value="4278190080", ver="3")
        ET.SubElement(obj_frame, 'designed', target="BrushStyle", value="0", ver="3")
        ET.SubElement(obj_frame, 'designed', target="OverrideScaling", value="false", ver="3")
        ET.SubElement(obj_frame, 'designed', target="ShowScrollBars", value="true", ver="3")
        ET.SubElement(obj_frame, 'designed', target="MoveByMouse", value="false", ver="3")

        ET.SubElement(root_list, 'designed', target="Opacity", value="1", ver="3")

        do_on_action = ET.SubElement(root_list, 'do-on', access_modifier="private", name="Handler_1",
                                     display_name="Handler_1", ver="3", event="Opened", frame_link="MainFrame",
                                     form_action="open-in-frame",
                                     form_by_id="false")
        obj_do_on_action = ET.SubElement(do_on_action, 'object', access_modifier="private",
                                         uuid=f"{uuid.uuid4()}",
                                         base_type=f"{first_page}_{obj[0]}",
                                         base_type_id=f"{sl_page_uuid.get(f'{first_page}_{obj[0]}')}",
                                         ver="3")
        ET.SubElement(obj_do_on_action, 'init', target=f"Link_DRV", ver="3", ref="here")
        ET.SubElement(obj_do_on_action, 'init', target="_init_ApSource", ver="3", ref="here.ApSource_Main")
        ET.SubElement(obj_do_on_action, 'init', target="_init_GPAPath", ver="3", ref="here._pathToGPA")

        ET.SubElement(
            root_list, 'object', access_modifier="private",
            name="NameOpened", display_name="NameOpened",
            uuid=f"{uuid.uuid4()}", base_type="notifying_string",
            base_type_id=f"{sl_uuid_base.get('notifying_string', '14976fbf-36ab-415f-abc3-9f8fdc217351')}",
            ver="3"
        )

        # Добавляем кнопки переключения листов
        # x_button_start = gor_base - (500 + 50 * len(sl_list_par))
        x_button_start = 1.0
        y_button_start = 10.0
        height_button = 30
        page_number = 0
        x_swift = 0
        y_swift = 0

        for page in sl_list_par:
            page_number += 1
            name_drv_eng = page[:page.rfind('_')]
            name_drv_rus = sl_all_drv.get(name_drv_eng, 'Unknown driver')

            # print(page, name_drv_rus)
            # x_swift = (page_number - 1) * 50
            # print(name_drv_rus, x_swift, gor_base)
            obj_button = ET.SubElement(
                root_list, 'object', access_modifier="private",
                name=f"ExtPageButton_{page_number}", display_name=f"ExtPageButton_{page_number}",
                uuid=f"{uuid.uuid4()}",
                base_type="ExtPageButton",
                base_type_id=f"{sl_uuid_base.get('ExtPageButton', '2c2d6f3d-f500-4be6-b80c-620853cd99e3')}",
                ver="3")
            ET.SubElement(obj_button, 'designed', target='X', value=f"{x_button_start + x_swift}", ver="3")
            ET.SubElement(obj_button, 'designed', target='Y', value=f"{y_button_start + y_swift}", ver="3")  # vert_base - 60
            ET.SubElement(obj_button, 'designed', target='Rotation', value="0", ver="3")
            # ET.SubElement(obj_button, 'designed', target='Width', value=f"{50*(len(page)/3}", ver="3")
            count_list_drv = check_count_page.count(page[:page.rfind('_')])
            name_but = f"{name_drv_rus} {page[page.rfind('_')+1:]}" if count_list_drv > 1 else f"{name_drv_rus}"
            width_but = get_text_width(name_but, "PT Sans", 12) + 4
            # print(width)
            ET.SubElement(obj_button, 'designed', target='Width', value=f"{round(width_but, 2)}", ver="3")
            ET.SubElement(obj_button, 'designed', target='Height', value=f"{height_button}", ver="3")
            ET.SubElement(obj_button, 'designed', target='Text', value=f"{name_but}", ver="3")
            ET.SubElement(obj_button, 'designed', target='Font',
                          value="PT Astra Sans,12,-1,5,75,0,0,0,0,0,Полужирный", ver="3")

            tagret_name = ET.SubElement(obj_button, 'do-trace', access_modifier="private", target='_Name', ver="3")
            body = ET.SubElement(tagret_name, 'body')
            ET.SubElement(body, 'forCDATA')
            ET.SubElement(obj_button, 'init', target='_IDtoOpen', ver="3",
                          value=f"{sl_page_uuid.get(f'{page}_{obj[0]}')}")

            do_on_action = ET.SubElement(obj_button, 'do-on', access_modifier="private", name="Handler_1",
                                         display_name="Handler_1", ver="3", event="MouseClick",
                                         frame_link="MainFrame",
                                         form_action="open-in-frame",
                                         form_by_id="false")
            obj_do_on_action = ET.SubElement(do_on_action, 'object', access_modifier="private",
                                             uuid=f"{uuid.uuid4()}",
                                             base_type=f"{page}_{obj[0]}",
                                             base_type_id=f"{sl_page_uuid.get(f'{page}_{obj[0]}')}",
                                             ver="3")
            ET.SubElement(obj_do_on_action, 'init', target=f"Link_DRV", ver="3", ref="here")
            ET.SubElement(obj_do_on_action, 'init', target="_init_ApSource", ver="3", ref="here.ApSource_Main")
            ET.SubElement(obj_do_on_action, 'init', target="_init_GPAPath", ver="3", ref="here._pathToGPA")

            x_swift = x_swift + width_but
            if (x_swift + width_but) >= (gor_base - 20):
                x_swift = 0
                y_swift += height_button

        # Добавляем ещё стандартной инфы
        apsource_currentform = ET.SubElement(root_list, 'object', access_modifier="private",
                                             name="ApSource_CurrentForm",
                                             display_name="ApSource_CurrentForm",
                                             uuid=f"{uuid.uuid4()}",
                                             base_type="ApSource",
                                             base_type_id=sl_uuid_base.get('ApSource', ''), ver="3")
        ET.SubElement(apsource_currentform, 'designed', target="Active", value="true", ver="3")
        ET.SubElement(apsource_currentform, 'designed', target="ReAdvise", value="0", ver="3")
        ET.SubElement(apsource_currentform, 'init', target="ParentSource", ver="3", ref="_init_ApSource")
        ET.SubElement(apsource_currentform, 'init', target="Path", ver="3", ref="_init_GPAPath")
        ET.SubElement(apsource_currentform, 'designed', target="Path", value="", ver="3")

        ET.SubElement(root_list, 'param', access_modifier="private", name="_init_ApSource",
                      display_name="_init_ApSource",
                      uuid=f"{uuid.uuid4()}",
                      base_type="ApSource", base_type_id=sl_uuid_base.get('ApSource', ''),
                      base_const="true", base_ref="true", ver="3")
        ET.SubElement(root_list, 'param', access_modifier="private", name="_init_GPAPath",
                      display_name="_init_GPAPath",
                      uuid=f"{uuid.uuid4()}",
                      base_type="string", base_type_id=sl_uuid_base.get('string', ''), ver="3")

        ET.SubElement(root_list, 'object', access_modifier="private",
                      name="DebugTool_1", display_name="DebugTool_1",
                      uuid=f"{uuid.uuid4()}",
                      base_type="DebugTool",
                      base_type_id=sl_uuid_base.get('DebugTool', ''), ver="3")
        ET.SubElement(root_list, 'object', access_modifier="private",
                      name="_pathToGPA", display_name="_pathToGPA",
                      uuid=f"{uuid.uuid4()}",
                      base_type="notifying_string",
                      base_type_id=sl_uuid_base.get('notifying_string', ''), ver="3")
        apsource_main = ET.SubElement(root_list, 'object', access_modifier="private",
                                      name="ApSource_Main", display_name="ApSource_Main",
                                      uuid=f"{uuid.uuid4()}",
                                      base_type="ApSource",
                                      base_type_id=sl_uuid_base.get('ApSource', ''), ver="3")
        ET.SubElement(apsource_main, 'designed', target="Active", value="true", ver="3")
        ET.SubElement(apsource_main, 'designed', target="ReAdvise", value="0", ver="3")
        ET.SubElement(apsource_main, 'designed', target="Path", value="", ver="3")
        ET.SubElement(apsource_main, 'init', target="ParentSource", ver="3", ref="here._init_ApSource")

        ET.SubElement(root_list, 'init', target="_pathToGPA", ver="3", ref="here._init_GPAPath")

        # Нормируем и записываем страницу мнемосхемы
        temp = ET.tostring(root_list).decode('UTF-8')
        check_diff_mnemo(new_data=multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                                 pretty_print=True,
                                                                                 encoding='unicode')),
                         check_path=os.path.join('File_for_Import', 'Mnemo', 'General_DRV_Mnemo'),
                         file_name_check=f'{name_page}_0_{obj[0]}.omobj',
                         message_print=f'Требуется заменить мнемосхему {name_page}_0_{obj[0]}.omobj '
                                       f'(Mnemo/General_DRV_Mnemo/{name_page}_0_{obj[0]}.omobj)'
                         )
    return


