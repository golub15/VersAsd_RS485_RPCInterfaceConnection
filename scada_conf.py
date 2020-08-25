import yaml
from collections import OrderedDict
import pybook

kor_shleif = '7'

states = {
    'error': 'НЕИСПР',
    '0': 'ОК',
    '-1': 'НЕТ СВЯЗИ',
    'not_resp': 'НЕТ ОТВЕТА',
    'on': 'ВКЛ',
    'fire_1': 'ПОЖ 1',
    'fire_2': 'ПОЖ 2',
    '10': 'СБРОС',
    '-5': 'ОТКЛ',
    'power_error': '27В',
    'open': 'ВКЛ',
    "not_con": 'НЕТ ОТВ',
    'con': 'ОК',
    'reset': 'СБРОС',
    'init': 'ОЖИДАНИЕ',
    'unavailable': 'unavailable'

}

m_states = {
    'error': 'НЕИСПР',
    '0': 'ОК',
    '-1': 'НЕТ СВЯЗИ',
    'not_resp': 'НЕТ ОТВЕТА',
    'on': 'ВКЛ',
    'fire_1': 'ПОЖ 1',
    'fire_2': 'ПОЖ 2',
    '10': 'СБРОС',
    '-5': 'ОТКЛ',
    'power_error': '27В'

}


# print(ordered_dump(get_sec_entities('01','14', '1' ,14)))
# print(ordered_dump(get_sec_customize('01', '14', '1', 14)))
# print(ordered_dump(get_lovelace('01', '14', '1', 14)))
def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


client_template = {
    'entity_type': '',
    'state_topic': 'con/client',
    'avb_topic': '',
    'name': 'Ядро опроса',
    'value_template': '{% if (value == "1") %}\nПОДКЛ\n{% else %}\nОТКЛ\n{% endif %}',
    'states': {},
    'show_state': 1,
    'entity_state_customize': {'ПОДКЛ': ('mdi:server-network', '#96ff2e', 0),
                               'ОТКЛ': ('mdi:server-network-off', 'red', 1),
                               'unavailable': ('mdi:server-network-off', '#771996', 0)},

    'bold': 1
}

com_port_template = {
    'entity_type': '',
    'state_topic': 'con/port',
    'avb_topic': 'con/client',
    'name': 'СOM Порт',
    'value_template': '{% if (value == "1") %}\nПОДКЛ\n{% elif (value == "0") %}\nОТКЛ\n{% endif %}\n',
    'states': {},
    'show_state': 1,
    'entity_state_customize': {'ПОДКЛ': ('mdi:serial-port', '#96ff2e', 0),
                               'ОТКЛ': ('mdi:serial-port', 'red', 1),
                               'unavailable': ('mdi:serial-port', 'gray', 0)},

    'bold': 1
}

mou_con_template = {
    'entity_type': '',
    'state_topic': 'con/mou',
    'avb_topic': 'con/client',
    'name': 'RS485',
    'value_template': "{% if (value == \"1\") %}ПОДКЛ{% elif (value == \"0\") %}НЕТ СВЯЗИ{% endif %}",
    'states': {},
    'show_state': 1,
    'entity_state_customize': {'ПОДКЛ': ('mdi:sitemap', '#96ff2e', 0),
                               'НЕТ СВЯЗИ': ('mdi:sitemap', 'red', 0),
                               'unavailable': ('mdi:sitemap', 'gray', 0)},

    'bold': 1
}

mou_state_template = {
    'entity_type': '',
    'state_topic': 'states/mou',
    'avb_topic': 'con/client',
    'name': 'Блок системы',
    'value_template': "{% if (value == \"not_con\") %}НЕТ ОТВ{% elif (value == \"init\") %} ОЖИДАНИЕ  {% elif (value == \"reset\") %} СБРОС  {% elif (value == \"con\") %} ОК {% elif (value == \"error\") %} ОШИБКА {% endif %}",
    'states': {},
    'show_state': 1,
    'entity_state_customize': {'НЕТ ОТВ': ('mdi:deskphone', 'red', 0),
                               'ОЖИДАНИЕ': ('mdi:deskphone', '#d500ff', 1),
                               'СБРОС': ('mdi:deskphone', '#fff235', 0),
                               'ОК': ('mdi:deskphone', '#96ff2e', 0),
                               'ОШИБКА': ('mdi:deskphone', 'orange', 0),
                               'unavailable': ('mdi:deskphone', 'gray', 0)},

    'bold': 1
}

mou_mode_template = {
    'entity_type': 'mou_mode',
    'state_topic': 'states/miru',
    'avb_topic': 'avb/miru',
    'name': 'Режим',
    'value_template': "{% if (value_json.mode == \"1\") %}АВТО{% elif (value_json.mode == \"2\") %} РУЧН  {% elif (value_json.mode == \"error\") %} ОШИБКА {% endif %}",
    'states': {},
    'show_state': 1,
    'entity_state_customize': {'АВТО': ('mdi:brightness-auto', '#96ff2e', 0),  # state : icon, color, error_anime
                               'РУЧН': ('mdi:cursor-move', 'red', 0),
                               'unavailable': ('mdi:alert-outline', 'gray', 0)},

    'bold': 1
}

mou_fire_template = {
    'entity_type': 'mou_fire',
    'state_topic': 'states/miru',
    'avb_topic': 'avb/miru',
    'name': 'Сработка',
    'value_template': "{% if (value_json.fire_2 == \"1\") %}ПОЖ 2{% elif (value_json.fire_1 == \"1\") %}ПОЖ 1{% else %}НЕТ{% endif %}",
    'states': {},
    'show_state': 1,
    'entity_state_customize': {'НЕТ': ('mdi:fire', '#96ff2e', 0),  # state : icon, color, error_anime
                               'ПОЖ 1': ('mdi:fire', 'yellow', 1),
                               'ПОЖ 2': ('mdi:fire', 'red', 1),
                               'unavailable': ('mdi:alert-outline', 'gray', 0)},

    'bold': 1
}

mou_errors_template = {
    'entity_type': 'mou_errors',
    'state_topic': 'states/miru',
    'avb_topic': 'avb/miru',
    'name': 'Ошибки',
    'value_template': "{% if (value_json.error == \"0\") %}НЕТ{% elif (value_json.error == \"1\") %} ЕСТЬ  {% endif %}",
    'states': {},
    'show_state': 1,
    'entity_state_customize': {'НЕТ': ('mdi:check-outline', '#96ff2e', 0),  # state : icon, color, error_anime
                               'ЕСТЬ': ('mdi:alert', 'orange', 0),
                               'unavailable': ('mdi:alert-outline', 'gray', 0)},

    'bold': 1
}

mou_power_template = {
    'entity_type': 'mou_power',
    'state_topic': 'states/miru',
    'avb_topic': 'avb/miru',
    'name': 'Питание',
    'value_template': "{% if (value_json.power == \"0\") %}ОК{% elif (value_json.power == \"1\") %}220В НЕИСПР{% elif (value_json.power == \"2\") %}АКБ НЕИСПР{% endif %}",
    'states': {},
    'show_state': 1,
    'entity_state_customize': {'ОК': ('mdi:flash', '#96ff2e', 0),  # state : icon, color, error_anime
                               '220В НЕИСПР': ('mdi:flash-alert-outline', 'orange', 0),
                               'АКБ НЕИСПР': ('mdi:car-battery', 'orange', 0),
                               'unavailable': ('mdi:alert-outline', 'gray', 0)},

    'bold': 1
}

shleif_template = {
    'entity_type': '',
    'state_topic': 'states/floors',
    'avb_topic': 'avb/floors',
    'num': 1,
    'name': '',
    'value_template': "",
    'states': {},
    'icon': '',
    'entity_state_customize': {states['0']: ('mdi:resistor-nodes', '#96ff2e', 0),  # state : icon, color, error_anime
                               states['-1']: ('mdi:resistor-nodes', 'white', 0),
                               states['error']: ('mdi:resistor-nodes', 'orange', 0),
                               states['power_error']: ('mdi:flash-alert-outline', 'orange', 0),
                               states['fire_1']: ('mdi:fire-extinguisher', 'yellow', 0),
                               states['fire_2']: ('mdi:fire', 'red', 0),
                               states['unavailable']: ('mdi:alert-outline', 'gray', 0)},

    'bold': 0
}

device_template = {
    'entity_type': 'device',
    'state_topic': 'states/floors',
    'avb_topic': 'avb/floors',
    'name': '',
    'value_template': "",
    'states': {},
    'entity_state_customize': {states['0']: ('mdi:server-network', '#96ff2e', 0),  # state : icon, color, error_anime
                               states['not_resp']: ('mdi:server-network-off', 'cyan', 0),
                               states['error']: ('mdi:server-remove', 'orange', 0),
                               states['fire_2']: ('mdi:fire', 'red', 0),
                               states['unavailable']: ('mdi:alert-outline', 'gray', 0)},

    'bold': 1
}

gate_template = {
    'entity_type': 'gate',
    'state_topic': 'states/floors',
    'avb_topic': 'avb/floors',
    'name': '',
    "elm_action": 1,
    'value_template': "",
    'states': {},
    'entity_state_customize': {states['0']: ('mdi:select-all', '#96ff2e', 0),  # state : icon, color, error_anime
                               states['-1']: ('mdi:select-off', 'white', 0),
                               states['error']: ('mdi:select-off', 'orange', 0),
                               states['on']: ('mdi:select', 'red', 0),
                               states['unavailable']: ('mdi:alert-outline', 'gray', 0)},

    'bold': 0
}

exit_panel_template = {
    'entity_type': 'exit_panel',
    'state_topic': 'states/floors',
    'avb_topic': 'avb/floors',
    'name': '',
    "elm_action": 1,
    'value_template': "",
    'states': {},
    'entity_state_customize': {states['0']: ('mdi:exit-run', '#96ff2e', 0),  # state : icon, color, error_anime
                               states['-1']: ('mdi:exit-run', 'white', 0),
                               states['error']: ('mdi:exit-run', 'orange', 0),
                               states['on']: ('mdi:exit-run', 'red', 0),
                               states['unavailable']: ('mdi:alert-outline', 'gray', 0)},

    'bold': 0
}

siren_template = {
    'entity_type': 'exit_panel',
    'state_topic': 'states/floors',
    'avb_topic': 'avb/floors',
    'name': '',
    "elm_action": 1,
    'value_template': "",
    'states': {},
    'entity_state_customize': {states['0']: ('mdi:speaker', '#96ff2e', 0),  # state : icon, color, error_anime
                               states['-1']: ('mdi:speaker-off', 'white', 0),
                               states['error']: ('mdi:speaker-off', 'orange', 0),
                               states['on']: ('mdi:speaker-wireless', 'red', 0),
                               states['unavailable']: ('mdi:alert-outline', 'gray', 0)},

    'bold': 0
}

fire_light_template = {
    'entity_type': 'exit_panel',
    'state_topic': 'states/floors',
    'avb_topic': 'avb/floors',
    'name': '',
    "elm_action": 1,
    'value_template': "",
    'states': {},
    'entity_state_customize': {states['0']: ('mdi:alarm-light-outline', '#96ff2e', 0),
                               # state : icon, color, error_anime
                               states['-1']: ('mdi:alarm-light-outline', 'white', 0),
                               states['error']: ('mdi:alarm-light-outline', 'orange', 0),
                               states['on']: ('mdi:alarm-light', 'red', 0),
                               states['unavailable']: ('mdi:alert-outline', 'gray', 0)},

    'bold': 0
}

fan_template = {
    'entity_type': 'fan',
    'state_topic': 'states/floors',
    'avb_topic': 'avb/floors',
    'name': '',
    "elm_action": 1,
    'value_template': "",
    'states': {},
    'entity_state_customize': {states['0']: ('mdi:fan-off', '#96ff2e', 0),  # state : icon, color, error_anime
                               states['-1']: ('mdi:fan-alert', 'white', 0),
                               states['error']: ('mdi:fan-alert', 'orange', 0),
                               states['on']: ('mdi:fan', 'red', 0),
                               states['unavailable']: ('mdi:alert-outline', 'gray', 0)},

    'bold': 0
}

sensor_entities_list = list()
switch_entities_list = list()
customize_list = OrderedDict()
input_select_entities_list = OrderedDict()


class Entity:
    def __init__(self, rcd, hcd, sec, flr, elm, conf):
        global sensor_entities_list, customize_list

        self.e = 'shleif'

        self.rcd = rcd
        self.hcd = hcd
        self.sec = sec
        self.flr = flr
        self.elm = elm

        self.conf = conf
        en = self.get_entity()
        if en not in sensor_entities_list:
            sensor_entities_list.append(en)
        for k, v in self.get_customize().items():
            if k not in customize_list:
                customize_list[k] = v
        # self.states = conf['states']

    def get_entity(self):
        data = OrderedDict()
        data['platform'] = 'mqtt'
        data['name'] = f'{self.rcd}_{self.hcd}_{self.sec}_floor_{self.flr}_{self.elm}'
        # print(self.conf)
        data['state_topic'] = f'{self.rcd}_{self.hcd}_{self.sec}/{self.conf["state_topic"]}'

        if self.conf['value_template'] != '':
            data['value_template'] = self.conf['value_template']
        else:
            data['value_template'] = '{{ value_json.iem_' + str(self.flr) + '.' + str(self.elm) + ' }}'

        if self.conf["avb_topic"] != "":
            data['availability_topic'] = f'{self.rcd}_{self.hcd}_{self.sec}/{self.conf["avb_topic"]}'
            data['payload_available'] = '1'
            data['payload_not_available'] = '0'

        return data

    def get_customize(self):
        res = OrderedDict()
        data = OrderedDict()

        data['friendly_name'] = self.conf['name']

        t = OrderedDict()
        si = ''
        for k, v in self.conf['entity_state_customize'].items():
            si += f" if (state == \"{k}\") return '{v[0]}';"
        si += f" else return 'mdi:alert-box';\n"

        t['icon'] = si

        ic = ''
        for k, v in self.conf['entity_state_customize'].items():
            ic += f" if (state == \"{k}\") return '{v[1]}';"
        ic += f" else return 'mdi:alert-box';\n"

        t['icon_color'] = ic
        data['templates'] = t

        en = OrderedDict()
        en[f'sensor.{self.rcd}_{self.hcd}_{self.sec}_floor_{self.flr}_{self.elm}'] = data

        return en

    def get_card(self):
        data = OrderedDict()
        data['type'] = 'custom:button-card'
        data['entity'] = f'sensor.{self.rcd}_{self.hcd}_{self.sec}_floor_{self.flr}_{self.elm}'
        data['color_type'] = 'card'

        if 'elm_action' in self.conf:
            data['hold_action'] = {
                "action": "call-service",
                "service": f"vers_asd_services.{self.rcd}_{self.hcd}_{self.sec}_execute_command",
                "service_data": {
                    "command": "entity_toggle_relay",
                    "data": {"id": self.elm,
                             "floor": self.flr}
                }

            }

        if 'show_state' in self.conf:
            data['show_state'] = self.conf['show_state']

        if self.conf['bold']:
            data['styles'] = OrderedDict({'card': [OrderedDict({'font-weight': 'bold'})]})

        card_states = []

        for x, y in self.conf['entity_state_customize'].items():
            st = OrderedDict()
            st['color'] = y[1]
            st['value'] = x

            if y[2] == 1:
                st['styles'] = OrderedDict({'card': [OrderedDict({'animation': 'blink 2s ease infinite'})]})

            card_states.append(st)

        data['state'] = card_states

        return data


def get_full_entity(rcd, hcd, sec, flr, elm):
    r = None
    conf = dict()

    if elm == 'device':
        conf = dict(device_template)
        if flr == 50:
            conf['name'] = 'Тех этаж'
        else:
            conf['name'] = f'Этаж {flr}'
            pass
    elif elm == 'air_gate_in':
        conf = dict(gate_template)
        conf['name'] = 'ПК'
    elif elm == 'air_gate_out':
        conf = dict(gate_template)
        conf['name'] = 'ВК'
    elif elm == 'exit_panel':
        conf = dict(exit_panel_template)
        conf['name'] = 'Табло'
    elif elm == 'fire_light':
        conf = dict(fire_light_template)
        conf['name'] = 'Лампа'
    elif elm == 'siren':
        conf = dict(siren_template)
        conf['name'] = 'Сирена'
    elif elm == 'fan_in':
        conf = dict(fan_template)
        conf['name'] = 'ПВ'
    elif elm == 'fan_out':
        conf = dict(fan_template)
        conf['name'] = 'ВВ'
    elif 'shleif' in elm:
        n = elm[-1]
        conf = dict(shleif_template)
        if flr == 50:
            conf['name'] = f'Маш отд'
        else:
            if n == kor_shleif:
                conf['name'] = f'Кор'
            else:
                conf['name'] = f'ШС {n}'

    r = Entity(rcd, hcd, sec, flr, elm, conf)
    # print(conf)
    return r


def rpc_more_card_ent(rcd, hcd, sec):
    def get_rpc_switch_entity_card(rcd, hcd, sec):
        global switch_entities_list
        en = OrderedDict({
            "platform": "mqtt",
            "name": f'{rcd}_{hcd}_{sec}_rpc_mode',
            "command_topic": f'{rcd}_{hcd}_{sec}/rpc/mode',
            "availability_topic": f'{rcd}_{hcd}_{sec}/avb/rpc',
            "payload_available": "1",
            "payload_not_available": "0"
        })
        cs = OrderedDict({
            f'switch.{rcd}_{hcd}_{sec}_rpc_mode': {
                "friendly_name": "Управление элементами",
                "icon": "mdi:dice"
            }

        })

        cr = OrderedDict({
            "type": "button",
            "tap_action": {
                "action": "toggle"
            },
            "hold_action": {
                "action": "more-info"
            },
            "show_icon": True,
            "show_name": True,
            "entity": f'switch.{rcd}_{hcd}_{sec}_rpc_mode'
        })

        # if en not in switch_entities_list:
        # print(en)
        switch_entities_list.append(en)
        for k, v in cs.items():
            if k not in customize_list:
                customize_list[k] = v
        return cr

    def get_rpc_device_input(rcd, hcd, sec):
        global switch_entities_list
        en = OrderedDict({
            f'{rcd}_{hcd}_{sec}_rpc_device_input': {
                "options": [
                    "Тех.Этаж",
                    "МОУ",
                    "1 Этаж",
                    "2 Этаж"
                ],
                "initial": "1 Этаж",
            }
        })
        cs = OrderedDict({
            f'input_select.{rcd}_{hcd}_{sec}_rpc_device_input': {
                "friendly_name": "Устройства",
                "icon": "mdi:deskphone"
            }

        })

        for k, v in en.items():
            if k not in input_select_entities_list:
                input_select_entities_list[k] = v

        for k, v in cs.items():
            if k not in customize_list:
                customize_list[k] = v
        return f"input_select.{rcd}_{hcd}_{sec}_rpc_device_input"

    rpc_reset_btn_template = OrderedDict({
        "type": "button",
        "tap_action": {
            "action": "more-info"
        },
        "hold_action": {
            "action": "call-service",
            "service": f"vers_asd_services.{rcd}_{hcd}_{sec}_execute_command",
            "service_data": {"command": "reset_system", "data": {}}
        },
        "show_icon": True,
        "show_name": True,
        "name": "Cброс",
        "icon": 'mdi:auto-fix'
    })

    rpc_sys_mode_btn_template = OrderedDict({
        "type": "button",
        "tap_action": {
            "action": "more-info"
        },
        "hold_action": {
            "action": "call-service",
            "service": f"vers_asd_services.{rcd}_{hcd}_{sec}_execute_command",
            "service_data": {"command": "switch_mode", "data": {"mode" : "T"}}
        },
        "show_icon": True,
        "show_name": True,
        "name": "Переключить режим",
        "icon": 'mdi:domain'
    })

    rpc_more_card_template = OrderedDict({
        "type": "vertical-stack",
        "cards": [
            {"type": "horizontal-stack",
             "cards": [Entity(rcd, hcd, sec, 0, "mou_state", mou_state_template).get_card(),
                       Entity(rcd, hcd, sec, 0, "mou_mode", mou_mode_template).get_card(),
                       Entity(rcd, hcd, sec, 0, "mou_fire", mou_fire_template).get_card()]
             },
            {"type": "horizontal-stack",
             "cards": [rpc_reset_btn_template,
                       rpc_sys_mode_btn_template,
                       get_rpc_switch_entity_card(rcd, hcd, sec)]
             },
            {"type": "entity",
             "entity": get_rpc_device_input(rcd, hcd, sec)
             }

        ]
    })

    return rpc_more_card_template


def view_card_ent(rcd, hcd, sec):
    def get_view_state_entity_card_btn(rcd, hcd, sec):
        global sensor_entities_list
        en = OrderedDict({
            "platform": "template",
            "sensors": {
                f"{rcd}_{hcd}_{sec}_view_state": {
                    "value_template": "{% if is_state('sensor.01_14_1_floor_0_mou_fire', 'ПОЖ 2') %}ПОЖАР 2{% elif is_state('sensor.01_14_1_floor_0_mou_fire', 'ПОЖ 1') %}ПОЖАР 1{% elif is_state('sensor.01_14_1_floor_0_mou_error', 'ЕСТЬ') %}НЕИСПРАВНОСТИ{% elif is_state('sensor.01_14_1_floor_0_mou_state', 'ОК') %}НОРМА{% elif is_state('sensor.01_14_1_floor_0_mou_state', 'СБРОС') %}СБРОС{% else %}НЕТ СВЯЗИ{% endif %}"
                }
            }

        })

        cs = OrderedDict({
            f'sensor.{rcd}_{hcd}_{sec}_view_state': {
                "friendly_name": "Состояние системы",
                "icon": "mdi:view-dashboard"
            }

        })

        cr = OrderedDict({
            "type": "custom:button-card",
            "layout": "icon_name_state",
            "state": [
                {
                    "value": "ПОЖАР 2",
                    "color": "red",
                    "icon": "mdi:fire"
                },
                {
                    "value": "ПОЖАР 1",
                    "color": "yellow",
                    "icon": "mdi:fire-extinguisher"
                },
                {
                    "value": "НЕИСПРАВНОСТИ",
                    "color": "orange",
                    "icon": "mdi:alert"
                },
                {
                    "value": "НОРМА",
                    "color": "#96ff2e",
                    "icon": "mdi:check-outline"
                },
                {
                    "value": "СБРОС",
                    "color": "cyan",
                    "icon": "mdi:timer"
                },
                {
                    "value": "НЕТ СВЯЗИ",
                    "color": "orange",
                    "icon": "mdi:server-network-off"
                }
            ],
            "styles": {"card": [{"padding": "0%"}, {"font-size": "30px"}]},
            "show_icon": True,
            "show_name": False,
            "show_state": True,
            "color_type": "card",
            "entity": f'sensor.{rcd}_{hcd}_{sec}_view_state'
        })

        if en not in sensor_entities_list:
            sensor_entities_list.append(en)
        for k, v in cs.items():
            if k not in customize_list:
                customize_list[k] = v
        return cr

    view_card_template = OrderedDict(
        {
            "type": "vertical-stack",
            "cards": [
                get_view_state_entity_card_btn(rcd, hcd, sec),
                {"type": "horizontal-stack",
                 "cards": [Entity(rcd, hcd, sec, 0, "client", client_template).get_card(),
                           Entity(rcd, hcd, sec, 0, "com_port", com_port_template).get_card(),
                           Entity(rcd, hcd, sec, 0, "mou_con", mou_con_template).get_card(),
                           Entity(rcd, hcd, sec, 0, "mou_state", mou_state_template).get_card()]
                 },
                {"type": "conditional",
                 "conditions": [{"entity": f"sensor.{rcd}_{hcd}_{sec}_floor_0_mou_con", "state": "ПОДКЛ"}],
                 "card": {"type": "horizontal-stack",
                          "cards": [Entity(rcd, hcd, sec, 0, "mou_mode", mou_mode_template).get_card(),
                                    Entity(rcd, hcd, sec, 0, "mou_fire", mou_fire_template).get_card(),
                                    Entity(rcd, hcd, sec, 0, "mou_error", mou_errors_template).get_card(),
                                    Entity(rcd, hcd, sec, 0, "mou_power", mou_power_template).get_card()]
                          }
                 }

            ]
        })

    fire_info_btn_card_template = OrderedDict({
        "type": 'custom:button-card',
        "name": "----- ПОЖАР ------",
        "styles": {"card": [{"font-weight": "bold"}, {"font-size": "40px"}, {"animation": "blink 1s ease infinite"}]},
        "color": "red",
        "color_type": "card"

    })

    fire_points_card_template = OrderedDict({
        "type": 'markdown',
        "content": '{% for s in states.sensor -%} {% if s.state == "ПОЖ 2" and s.name != "sensor.01_14_1_floor_0_mou_fire" %}        * Элемент {{s.entity_id}} , название {{s.name}} {% endif %}{%- endfor %}'
    })

    false_confirm_fire_btn_card_template = OrderedDict({
        "aspect_ratio": "2/1",
        "color": "green",
        "color_type": "card",
        "confirmation": {
            "text": "Вы уверены?"
        },
        "layout": "name_state",
        "name": "Ложь",
        "show_state": 1,
        "styles": {
            "card": [
                {
                    "font-weight": "bold"
                },
                {
                    "font-size": "25px"
                }
            ]
        },
        "tap_action": {
            "action": "call-service",
            "service": f"vers_asd_services.{rcd}_{hcd}_{sec}_execute_command",
            "service_data": {"command": "reset_fire", "data": {"confirm": "false"}}
        },
        "type": "custom:button-card"
    })

    true_confirm_fire_btn_card_template = OrderedDict({
        "aspect_ratio": "2/1",
        "color": "yellow",
        "color_type": "card",
        "confirmation": {
            "text": "Вы уверены?"
        },
        "layout": "name_state",
        "name": "Тест",
        "show_state": 1,
        "styles": {
            "card": [
                {
                    "font-weight": "bold"
                },
                {
                    "font-size": "25px"
                }
            ]
        },
        "tap_action": {
            "action": "call-service",
            "service": f"vers_asd_services.{rcd}_{hcd}_{sec}_execute_command",
            "service_data": {"command": "reset_fire", "data": {"confirm": "true"}}
        },
        "type": "custom:button-card"
    })

    test_confirm_fire_btn_card_template = OrderedDict({
        "aspect_ratio": "2/1",
        "color": "red",
        "color_type": "card",
        "confirmation": {
            "text": "Вы уверены?"
        },
        "layout": "name_state",
        "name": "Потвердить",
        "show_state": 1,
        "styles": {
            "card": [
                {
                    "font-weight": "bold"
                },
                {
                    "font-size": "20px"
                }
            ]
        },
        "tap_action": {
            "action": "call-service",
            "service": f"vers_asd_services.{rcd}_{hcd}_{sec}_execute_command",
            "service_data": {"command": "reset_fire", "data": {"confirm": "test"}}
        },
        "type": "custom:button-card"
    })

    fire_card_template = OrderedDict(
        {
            "type": "vertical-stack",
            "cards": [
                {"type": "conditional",
                 "conditions": [{"entity": f"sensor.{rcd}_{hcd}_{sec}_floor_0_mou_fire", "state": "ПОЖ 2"},
                                {"entity": f"sensor.{rcd}_{hcd}_{sec}_floor_0_mou_mode", "state": "АВТО"}],
                 "card": {"type": "vertical-stack",
                          "cards": [
                              fire_info_btn_card_template,
                              fire_points_card_template,
                              {"type": "horizontal-stack",
                               "cards": [
                                   false_confirm_fire_btn_card_template,
                                   test_confirm_fire_btn_card_template,
                                   true_confirm_fire_btn_card_template

                               ]}

                          ]
                          }
                 }

            ]
        })

    result = [
        view_card_template,
        fire_card_template
    ]

    return result


def sec_ent(rcd, hcd, sec):
    def get_arr_card(row_entities, args):

        stack_lv = OrderedDict()
        stack_lv['type'] = 'vertical-stack'
        stack_lv['cards'] = row_entities

        return stack_lv

    def get_row(entities, args):
        el = list(entities)

        lv = list()

        for i in el:
            lv.append(i.get_card())

        stack = OrderedDict()
        stack['type'] = 'horizontal-stack'
        stack['cards'] = lv

        return stack

    def get_floors_card(rcd, hcd, sec):
        def get_mte_entity(rcd, hcd, sec, flr):
            el = list()

            el.append(get_full_entity(rcd, hcd, sec, 50, 'device'))
            el.append(get_full_entity(rcd, hcd, sec, 50, 'air_gate_in'))
            #el.append(get_full_entity(rcd, hcd, sec, 50, 'air_gate_out'))
            el.append(get_full_entity(rcd, hcd, sec, 50, 'fan_in'))
            el.append(get_full_entity(rcd, hcd, sec, 50, 'fan_out'))
            el.append(get_full_entity(rcd, hcd, sec, 50, 'shleif_1'))

            return get_row(el, {})

        def get_floor_entity(rcd, hcd, sec, flr):
            el = list()

            el.append(get_full_entity(rcd, hcd, sec, flr, 'device'))
            el.append(get_full_entity(rcd, hcd, sec, flr, 'air_gate_in'))
            # el.append(get_full_entity(rcd, hcd, sec, flr, 'air_gate_out'))
            el.append(get_full_entity(rcd, hcd, sec, flr, 'exit_panel'))
            el.append(get_full_entity(rcd, hcd, sec, flr, 'fire_light'))
            el.append(get_full_entity(rcd, hcd, sec, flr, 'siren'))

            # for x in range(1, 9):
            el.append(get_full_entity(rcd, hcd, sec, flr, f'shleif_7'))

            return get_row(el, {})

        obj = list()

        obj.append(get_mte_entity(rcd, hcd, sec, 50))
        for i in range(15, 0, -1):
            obj.append(get_floor_entity(rcd, hcd, sec, i))

        arr = get_arr_card(obj, {})
        # print(ordered_dump(arr))
        return arr

    more_state_card_template = {
        "type": "vertical-stack",
        "cards": [
            {"type": "conditional",
             "conditions": [{"entity": f"sensor.{rcd}_{hcd}_{sec}_floor_0_mou_state", "state": "ОК"}],
             "card": get_floors_card(rcd, hcd, sec)
             },
            {"type": "conditional",
             "conditions": [{"entity": f"sensor.{rcd}_{hcd}_{sec}_floor_0_mou_state", "state_not": "ОК"}],
             "card": {"type": "markdown", "content": "# НЕ ДОСТУПНО В ТЕКУЩИЙ МОМЕНТ"}
             }

        ]
    }

    # print(ordered_dump(obj))

    return more_state_card_template


hass_path = "C:/Users/ipige/homeassistant"
street_dict = {
    '01': "Хвойная"
}


def get_lovelace_panel(rcd, hcd, sec):
    def save_file(path, data):
        file = open(f"{hass_path}/{path}", "w")
        file.write(data)
        file.close()

    dashboard_info = OrderedDict()

    f = str(f"{rcd}-{hcd}-{sec}")
    dashboard_info[f] = {
        "mode": "yaml",
        "filename": f"{rcd}_{hcd}_{sec}_lovelace_panel.yaml",
        "title": f"{street_dict[rcd]} {hcd}, Секция {sec}",
        "icon": "mdi:home",
        "show_in_sidebar": True,
        "require_admin": True
    }

    print(dashboard_info)
    save_file(f"objects/dashboards/{rcd}_{hcd}_{sec}_dashboard_info.yaml", ordered_dump(dashboard_info))

    lovelace_panel = {
        "title": "Система",
        "views": [
            {
                "title": "Обзор",
                "badges": [],
                "path": "view",
                "cards": view_card_ent(rcd, hcd, sec)
            },
            {
                "title": "Этажи",
                "path": "floors",
                "badges": [],
                "cards": [sec_ent(rcd, hcd, sec)]
            },
            {
                "title": "Действия",
                "path": "rpc_simple",
                "badges": [],
                "cards": []
            },
            {
                "title": "Настройки",
                "path": "rpc_more",
                "badges": [],
                "cards": [rpc_more_card_ent(rcd, hcd, sec)]
            },
            {
                "title": "Журнал",
                "path": "logbook",
                "badges": [],
                "cards": []
            },
            {
                "title": "Документы",
                "path": "docs",
                "badges": [],
                "cards": []
            }
        ]
    }

    save_file(f"{rcd}_{hcd}_{sec}_lovelace_panel.yaml", ordered_dump(lovelace_panel))

    save_file(f"objects/sensor/{rcd}-{hcd}-{sec}-sensor.yaml", ordered_dump(sensor_entities_list))
    save_file(f"objects/customize/{rcd}-{hcd}-{sec}-customize.yaml", ordered_dump(customize_list))
    save_file(f"objects/switch/{rcd}-{hcd}-{sec}-switch.yaml", ordered_dump(switch_entities_list))
    save_file(f"objects/input_select/{rcd}-{hcd}-{sec}-input_select.yaml", ordered_dump(input_select_entities_list))

    recorder_entities = [
        f"sensor.{rcd}_{hcd}_{sec}_floor_0_client",
        f"sensor.{rcd}_{hcd}_{sec}_floor_0_com_port",
        f"sensor.{rcd}_{hcd}_{sec}_floor_0_mou_con",
        f"sensor.{rcd}_{hcd}_{sec}_floor_0_mou_error",
        f"sensor.{rcd}_{hcd}_{sec}_floor_0_mou_fire",
        f"sensor.{rcd}_{hcd}_{sec}_floor_0_mou_mode",
        f"sensor.{rcd}_{hcd}_{sec}_floor_0_mou_state",
        f"sensor.{rcd}_{hcd}_{sec}_view_state",

    ]

    recorder_event_types = [
        f"{rcd}_{hcd}_{sec}_vers_asd_event",
        f"{rcd}_{hcd}_{sec}_vers_asd_command_response"
    ]

    save_file(f"objects/recorder_entities/{rcd}-{hcd}-{sec}-recorder_entities.yaml", ordered_dump(recorder_entities))
    save_file(f"objects/recorder_event_types/{rcd}-{hcd}-{sec}-recorder_event_types.yaml", ordered_dump(recorder_event_types))



get_lovelace_panel('01', '14', '1')
# get_lovelace_panel('01', '75', '6')
