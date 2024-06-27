import os


def load_mock_response(file_name):
    file_path = os.path.join(os.path.dirname(__file__), 'mocks', file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
    return file_content
