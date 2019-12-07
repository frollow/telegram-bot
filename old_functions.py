def create_json():
    with open('parser_job.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        users_list = []
        path = Path('users_list.json')
        for row in reader:
            user = {
                'telegram_id': int(row['telegram_id']),
                'user_name': row['user_name'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'look_for_job': int(row['look_for_job']),
                'look_for_employer': int(row['look_for_employer']),
                'add_promo': int(row['add_promo']),
                'is_bot': row['is_bot'],
                'date_first_action': int(row['date_first_action']),
                'date_last_action': int(row['date_last_action']),
            }
            users_list.append(user)
        print(users_list)
        path.write_text(json.dumps(users_list,
                                   ensure_ascii=False,
                                   indent=4,
                                   separators=(',', ': ')),
                        encoding='utf-8'
                        )
create_json()
path = Path('users_list.json')
data = json.loads(path.read_text(encoding='utf-8'))

print(len(data))