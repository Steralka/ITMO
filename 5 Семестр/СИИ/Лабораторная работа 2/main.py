from pyswip import Prolog

def normalize_name(raw_name: str) -> str:
    clean = raw_name.replace("?", "").strip()
    if any("а" <= ch <= "я" or "А" <= ch <= "Я" for ch in clean):
        return f"'{clean}'"
    return clean.lower()


def run_query(prolog, query, var="X"):
    results = list(prolog.query(query))
    return [r[var] for r in results]


def print_results(label: str, person: str, results: list, empty_msg: str):
    if results:
        print(f"{label} {person}: {results}")
    else:
        print(empty_msg)


def main():
    prolog = Prolog()
    prolog.consult("family_facts.pl")
    prolog.consult("rules.pl")

    print("Система поддержки принятия решений (генеалогия)\n")
    print("Примеры запросов:")
    print(" - кто жив в 2020?")
    print(" - возраст Юлия в 2015")
    print(" - кто дети Кирилл?")
    print(" - кто родители Юлия?")
    print(" - кто предки Карина?")
    print(" - кто супруг Юлия в 2020?")
    print(" - кто вдовы в 2010?")
    print(" - кто братья Юлия?")
    print(" - кто кузены Карина?")
    print("Для выхода: exit\n")

    while True:
        user_input = input("Введи запрос: ").strip().lower()
        if user_input in ["exit", "выход"]:
            break

        try:
            if user_input.startswith("кто жив в"):
                year = int(user_input.split()[-1])
                result = run_query(prolog, f"alive_at(X, {year})")
                print_results("Живы в", year, result, f"Никто не жив в {year}.")

            elif user_input.startswith("кто умер в"):
                year = int(user_input.split()[-1])
                result = run_query(prolog, f"dead_at(X, {year})")
                print_results("Умерли к", year, result, f"Нет данных об умерших к {year}.")

            elif user_input.startswith("возраст"):
                parts = user_input.split()
                person = normalize_name(parts[1])
                year = int(parts[-1])
                result = list(prolog.query(f"age_at({person}, {year}, A)"))
                if result:
                    print(f"Возраст {person} в {year}: {result[0]['A']} лет")
                else:
                    print(f"Нет данных о возрасте {person} в {year}.")

            
            elif "дети" in user_input:
                person = normalize_name(user_input.split()[-1])
                result = run_query(prolog, f"child(X, {person})")
                print_results("Дети", person, result, f"У {person} нет детей.")

           
            elif "родители" in user_input:
                person = normalize_name(user_input.split()[-1])
                result = run_query(prolog, f"parent(X, {person})")
                print_results("Родители", person, result, f"Нет данных о родителях {person}.")

            
            elif "предки" in user_input:
                person = normalize_name(user_input.split()[-1])
                result = run_query(prolog, f"ancestor(X, {person})")
                print_results("Предки", person, result, f"Нет данных о предках {person}.")

            
            elif "потомки" in user_input:
                person = normalize_name(user_input.split()[-1])
                result = run_query(prolog, f"descendant(X, {person})")
                print_results("Потомки", person, result, f"Нет данных о потомках {person}.")

            
            elif "супруг" in user_input or "супруга" in user_input:
                parts = user_input.split()
                person = normalize_name(parts[2])
                year = int(parts[-1])
                result = run_query(prolog, f"spouse_at({person}, X, {year})")
                print_results("Супруг(а)", person, result, f"{person} не состоит в браке в {year}.")

            
            elif "вдовы" in user_input or "вдовцы" in user_input:
                year = int(user_input.split()[-1])
                result = run_query(prolog, f"widowed_at(X, _, {year})")
                if result:
                    print(f"Вдовы/вдовцы в {year}: {result}")
                else:
                    print(f"Нет вдов/вдовцов в {year}.")

            
            elif "братья" in user_input or "сёстры" in user_input:
                person = normalize_name(user_input.split()[-1])
                result = run_query(prolog, f"sibling(X, {person})")
                print_results("Братья/сёстры", person, result, f"Нет данных о братьях/сёстрах {person}.")

            
            elif "кузены" in user_input:
                person = normalize_name(user_input.split()[-1])
                result = run_query(prolog, f"cousin(X, {person})")
                print_results("Кузены", person, result, f"Нет данных о кузенах {person}.")

            else:
                print("Запрос не распознан. Попробуй другой.")

        except Exception as e:
            print("Ошибка при обработке запроса:", e)


if __name__ == "__main__":
    main()
