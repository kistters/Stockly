def clean_signs(sign: str, data: dict, fields_to_clean: list):
    for key, value in data.items():
        if key in fields_to_clean:
            data[key] = value.replace(sign, '')
    return data
