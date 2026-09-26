"""Settings data helpers."""

import json

def deep_copy(data):

    return json.loads(
        json.dumps(
            data,
            ensure_ascii=False
        )
    )


def convert_settings(settings, button_count):

    converted_buttons = []


    source_buttons = settings.get(
        "buttons",
        []
    )


    for button in source_buttons:

        # ------------------------------------------------
        # 새로운 형식
        #
        # {
        #   "type": "key",
        #   "value": [...]
        # }
        # ------------------------------------------------

        if isinstance(
            button,
            dict
        ):

            button_type = button.get(
                "type",
                "key"
            )

            value = button.get(
                "value"
            )


            if button_type == "text":

                if not isinstance(
                    value,
                    str
                ):

                    value = ""


                converted_buttons.append({

                    "type": "text",

                    "value": value
                })


            else:

                if not isinstance(
                    value,
                    list
                ):

                    value = []


                converted_buttons.append({

                    "type": "key",

                    "value": value
                })


        # ------------------------------------------------
        # 예전 형식
        #
        # ["CONTROL", "C"]
        # ------------------------------------------------

        elif isinstance(
            button,
            list
        ):

            converted_buttons.append({

                "type": "key",

                "value": button
            })


        else:

            converted_buttons.append({

                "type": "key",

                "value": []
            })


    # ----------------------------------------------------
    # 버튼이 4개보다 적으면 빈 버튼 추가
    # ----------------------------------------------------

    while len(converted_buttons) < button_count:

        converted_buttons.append({

            "type": "key",

            "value": []
        })


    # ----------------------------------------------------
    # 버튼이 4개보다 많으면 앞의 4개만 사용
    # ----------------------------------------------------

    converted_buttons = converted_buttons[
        :button_count
    ]


    return {
        "buttons": converted_buttons
    }
