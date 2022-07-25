import socket
import uuid
from math import floor, ceil
from func_for_v3 import *


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
                       size_shirina: int, size_vysota: int, sl_param: dict):
    # uuid.uuid4()
    sl_size = {
        '1920x900': (1780, 900, 780),
        '1920x780': (1780, 780, 780)
    }
    # Словарь ID для типовых структур, возможно потом будет считваться с файла или как-то по-другому
    sl_uuid_base = {
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
        'DebugTool': '43946044-139a-43f4-a7b8-19a6074ffc56'
    }
    # Словарь размеров элементов, тут по заполнению всё понятно
    sl_size_element = {'AI': {'size_el': ((591 + 2), (24 + 6)), 'size_text': (590.567, 24)},
                       'AE': {'size_el': ((591 + 2), (24 + 6)), 'size_text': (590.567, 24)},
                       'DI': {'size_el': ((525 + 50), (26 + 6)), 'size_text': (524.69, 26)},
                       'System.CNT': {'size_el': ((545 + 30), (24 + 6)), 'size_text': (545, 24)}
                       }
    # Словарь расположения первого элемента, тут вроде всё понятно тоже - первый X, второй Y
    sl_start = {'AI': (3, 15),
                'AE': (3, 15),
                'DI': (50, 15),
                'System.CNT': (30, 15)
                }
    gor_base = sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1780, 900))[0]
    vert_base = sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1780, 900))[1]
    window_height = sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1780, 900, 780))[2]
    # Узнаём, сколько целых параметров влезет по горизонтали
    # два пикселя по горизонтали между элементами
    par_gor_count = floor(gor_base / sl_size_element.get(name_group, {'size_el': (500, 0)})['size_el'][0])
    # Узнаём, сколько целых параметров влезет по вертикали
    # 6 пикеселей по вертикали между элементами, 90 - запас для кнопок переключения
    par_vert_count = floor((vert_base - 90 - sl_start.get(name_group, (0, 500))[1]) /
                           sl_size_element.get(name_group, {'size_el': (0, 500)})['size_el'][1])
    # Узнаём количество параметров на один лист
    par_one_list = (par_gor_count * par_vert_count)
    # Узнаём количество требуемых листов, деля количество требуемых элементов на количество на одном листе
    # num_par = sum(len(i) for i in tuple(sl_param.values())) + len(tuple(sl_param.keys()))
    # number_list = ceil(num_par / par_one_list)
    # print(name_group, par_one_list)
    start_list = 1
    count = 0
    # sl_list_par = {номер листа: {узел: кортеж параметров}}
    # При разбивке на листы учитывается количество параметров на листе, в том числе само наименование узла
    sl_list_par = {}
    for node in sl_param:
        count += 1
        if count == par_one_list:
            count = 0
            start_list += 1
        for j in range(len(sl_param[node])):
            count += 1
            sl_param[node][j] = (start_list, sl_param[node][j])
            if count == par_one_list:
                count = 1
                start_list += 1

    # for node in sl_param:
    #     print(node)
    #     print(sl_param[node])
    for node in sl_param:
        for par in sl_param[node]:
            # Если в словаре ещё нет данного листа, то создаём там пустой словарь
            if par[0] not in sl_list_par:
                sl_list_par[par[0]] = {}
            # Если в словаре листа нет текущего узла, то добавляем туда узел с пустым кортежем будущих переменных
            if node not in sl_list_par[par[0]]:
                sl_list_par[par[0]].update({node: tuple()})
            # После этого на соотвествующем листе в соответствующий узел добавляем перебираемый параметр
            sl_list_par[par[0]][node] += (par[1],)

    # for li in sl_list_par:
    #     for node in sl_list_par[li]:
    #         print(li, node)
    #         print(li, sl_list_par[li][node])
    num_text = 0
    sl_page_uuid = {}
    # Для каждого листа в словаре листов с параметрами...
    for page in sl_list_par:
        # Вносим инфу в словарь
        # ...создаём родительский узел листа
        sl_page_uuid[f"{name_page}_{page}"] = uuid.uuid4()
        root_type = ET.Element('type', access_modifier="private", name=f"{name_page}_{page}",
                               display_name=f"{name_page}_{page}",
                               uuid=f"{sl_page_uuid[f'{name_page}_{page}']}",
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

            # Для каждого параметра создаём узлы xmlки
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
                ET.SubElement(num_sub_par, 'init', target="_init_APSource", ver="3", ref="ApSource_CurrentForm")
                ET.SubElement(num_sub_par, 'init', target="_init_Object", ver="3", value=f"{name_group}.{par}")
                ET.SubElement(num_sub_par, 'init', target="_AbonentName", ver="4", ref="here._init_GPAPath")

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
        with open(os.path.join('File_for_Import', 'Mnemo', f'{name_page}_{page}.omobj'),
                  'w', encoding='UTF-8') as f_out:
            f_out.write(multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                       pretty_print=True, encoding='unicode')))

    # Если получилось больше одной мнемосхемы, то создаём главную мнемосхему с фреймом
    if len(sl_list_par) > 1:
        root_list = ET.Element('type', access_modifier="private", name=f"{name_page}_0",
                               display_name=f"{name_page}_0",
                               uuid=f"{uuid.uuid4()}",
                               base_type="00_SubBase",
                               base_type_id=f"{sl_uuid_base.get('00_SubBase', '99471dea-1c95-471c-9960-b4f7a539d437')}",
                               ver="3")
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

        obj_frame = ET.SubElement(root_list, 'object', access_modifier="private", name="MainFrame",
                                  display_name="MainFrame",
                                  uuid=f"{uuid.uuid4()}",
                                  base_type=f"{name_page}_1",
                                  base_type_id=f"{sl_uuid_base.get('Frame', '71f78e19-ef99-4133-a029-2968b14f02b6')}",
                                  ver="3")
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
                                         base_type=f"{name_page}_1",
                                         base_type_id=f"{sl_page_uuid.get(f'{name_page}_1')}",
                                         ver="3")
        ET.SubElement(obj_do_on_action, 'init', target=f"Link_{name_page}", ver="3", ref="here")
        ET.SubElement(obj_do_on_action, 'init', target="_init_ApSource", ver="3", ref="here.ApSource_Main")
        ET.SubElement(obj_do_on_action, 'init', target="_init_GPAPath", ver="3", ref="here._pathToGPA")

        ET.SubElement(root_list, 'object', access_modifier="private",
                      name="NameOpened", display_name="NameOpened",
                      uuid=f"{uuid.uuid4()}", base_type="notifying_string",
                      base_type_id=f"{sl_uuid_base.get('notifying_string', '14976fbf-36ab-415f-abc3-9f8fdc217351')}",
                      ver="3")

        # Добавляем кнопки переключения листов
        x_button_start = gor_base - (321 + 50*len(sl_list_par))
        for page in sl_list_par:
            x_swift = (page - 1)*50
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

            tagret_name = ET.SubElement(obj_button, 'do-trace', access_modifier="private", target='_Name', ver="3")
            body = ET.SubElement(tagret_name, 'body')
            ET.SubElement(body, 'forCDATA')
            ET.SubElement(obj_button, 'init', target='_IDtoOpen', ver="3",
                          value=f"{sl_page_uuid.get(f'{name_page}_{page}')}")

            do_on_action = ET.SubElement(obj_button, 'do-on', access_modifier="private", name="Handler_1",
                                         display_name="Handler_1", ver="3", event="MouseClick", frame_link="MainFrame",
                                         form_action="open-in-frame",
                                         form_by_id="false")
            obj_do_on_action = ET.SubElement(do_on_action, 'object', access_modifier="private",
                                             uuid=f"{uuid.uuid4()}",
                                             base_type=f"{name_page}_{page}",
                                             base_type_id=f"{sl_page_uuid.get(f'{name_page}_{page}')}",
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
        with open(os.path.join('File_for_Import', 'Mnemo', f'{name_page}_0.omobj'),
                  'w', encoding='UTF-8') as f_out:
            f_out.write(multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                       pretty_print=True, encoding='unicode')))


# Функция создания мнемосхем проверки защит
def create_mnemo_pz(name_group: str, name_page: str, base_type_param: str,
                    size_shirina: int, size_vysota: int, param_pz: list):
    # uuid.uuid4()
    sl_size = {
        '1920x900': (1920, 900, 780),
        '1920x780': (1920, 780, 780)
    }
    # Словарь ID для типовых структур, возможно потом будет считваться с файла или как-то по-другому
    sl_uuid_base = {
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
        'DebugTool': '43946044-139a-43f4-a7b8-19a6074ffc56'
    }
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
    # 6 пикеселей по вертикали между элементами, 92 - запас для кнопок переключения
    par_vert_count = floor((vert_base - sl_start.get(name_group, (0, 500))[1]) /
                           sl_size_element.get(name_group, {'size_el': (0, 500)})['size_el'][1])
    # Узнаём количество параметров на один лист
    par_one_list = (par_gor_count * par_vert_count)
    # Узнаём количество требуемых листов, деля количество требуемых элементов на количество на одном листе
    # num_par = sum(len(i) for i in tuple(sl_param.values())) + len(tuple(sl_param.keys()))
    # number_list = ceil(num_par / par_one_list)
    # print(name_group, par_one_list)
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
        root_type = ET.Element('type', access_modifier="private", name=f"{name_page}_{page}",
                               display_name=f"{name_page}_{page}",
                               uuid=f"{uuid.uuid4()}",
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

        # Добавляем Текст с описание листа
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
        ET.SubElement(num_sub_text_discription, 'designed', target='Text', value=f"Проверка защит лист {page}", ver="3")
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
            ET.SubElement(num_sub_par, 'init', target="_init_APSource", ver="4", ref="here.ApSource_CurrentForm")
            ET.SubElement(num_sub_par, 'init', target="_AbonentName", ver="4", ref="here._init_GPAPath")

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
                                 'Line_9': (476.7, (-413+(vert_base - 70)), 0, 951, 0, 0, 0, 951, 270),
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
        with open(os.path.join('File_for_Import', 'Mnemo', f'{name_page}_{page}.omobj'),
                  'w', encoding='UTF-8') as f_out:
            f_out.write(multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                       pretty_print=True, encoding='unicode')))
