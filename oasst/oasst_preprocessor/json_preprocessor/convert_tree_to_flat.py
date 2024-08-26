import json

keys_to_add = [
    'lang',
    'review_count',
    'review_result',
    'deleted',
    'rank',
    'synthetic',
    'model_name',
    'detoxify',
    'message_tree_id',
    'tree_state',
    'emojis',
    'lavels',
    'link',
    '변호사명',
    '작업자명',
    '작업일자',
    '사용여부',
]


def dfs_collect_fields(message, keys_to_add):
    """
    DFS를 사용하여 트리를 순회하면서 하위 노드에서 특정 필드를 수집하고 반환합니다.

    Args:
        message (dict): 현재 메시지
        keys_to_add (list): 수집할 필드의 키 목록

    Returns:
        dict: 하위 노드에서 수집된 필드와 값
    """
    fields_to_add = {}
    for key in keys_to_add:
        if key in message:
            if isinstance(message[key], list):
                # 리스트의 경우, 리스트를 복사하여 추가합니다.
                fields_to_add[key] = message[key].copy()
            else:
                fields_to_add[key] = message[key]

    if 'replies' in message:
        for reply in message['replies']:
            child_fields = dfs_collect_fields(reply, keys_to_add)
            for key, value in child_fields.items():
                # 필드가 이미 있으면 리스트를 합칩니다.
                if key in fields_to_add and isinstance(fields_to_add[key], list) and isinstance(value, list):
                    fields_to_add[key].extend(value)
                else:
                    fields_to_add[key] = value

    return fields_to_add


def dfs_update_message(message, keys_to_add):
    """
    DFS를 사용하여 트리를 순회하면서 하위 노드에서 수집된 필드를 상위 노드에 업데이트합니다.

    Args:
        message (dict): 현재 메시지
        keys_to_add (list): 수집할 필드의 키 목록
    """
    fields_to_add = dfs_collect_fields(message, keys_to_add)

    if fields_to_add:
        # 현재 메시지에 필드를 추가
        for key, value in fields_to_add.items():
            if key in message:
                # 기존 값이 리스트이면, 리스트를 합칩니다.
                if isinstance(message[key], list) and isinstance(value, list):
                    message[key].extend(value)
                else:
                    message[key] = value
            else:
                message[key] = value

    if 'replies' in message:
        for reply in message['replies']:
            dfs_update_message(reply, keys_to_add)


def seperate_replie_at_tree(input_file):
    """
    주어진 JSON 파일을 읽고, 하위 메시지의 중복 필드를 상위 메시지로 이동시키는 트리 구조로 변환한 후,
    결과를 새로운 JSON 파일로 저장합니다.

    Args:
        input_file (str): 입력 JSON 파일의 경로
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for message in data:
        dfs_update_message(message, keys_to_add)

    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def split_replies(input_file):
    """
    JSON 파일을 읽고, 각 메시지의 'replies' 필드의 값을 상위 메시지에서 분리하여
    새로운 파일에 저장합니다.

    Args:
        input_file (str): 입력 JSON 파일의 경로
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    def process_message(message):
        """
        메시지에서 'replies' 필드를 분리하여 새로운 리스트에 저장합니다.

        Args:
            message (dict): 현재 메시지

        Returns:
            dict: 업데이트된 메시지와 분리된 replies 리스트
        """
        replies = message.pop('replies', [])
        separated_replies = []
        for reply in replies:
            # 'replies' 필드를 가지는 각 하위 메시지를 'replies' 키 없이 업데이트
            separated_replies.append(reply)
            process_message(reply)  # 재귀적으로 하위 메시지를 처리

        return separated_replies

    result = []
    for message in data:
        replies = process_message(message)
        if replies:
            # 메시지에서 'replies'를 분리하고, 별도의 리스트에 저장
            for reply in replies:
                result.append(reply)

    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


def convert_tree_to_flat(input_file):
    """
    주어진 JSON 파일을 처리하여, 먼저 트리 구조를 평탄화하고,
    이후에 'replies' 필드를 분리하여 저장합니다.

    Args:
        input_file (str): 입력 JSON 파일의 경로
    """
    seperate_replie_at_tree(input_file)
    split_replies(input_file)