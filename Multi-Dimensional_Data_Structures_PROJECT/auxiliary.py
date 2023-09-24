from beautifultable import BeautifulTable


def letter_normalization(letter):
    return ord(letter.upper()) - 65


def display_results(results_list):
    table = BeautifulTable(maxwidth=150)
    table.column_headers = ["Surname", "Awards", "Education"]

    sorted_list = sorted(results_list, key=lambda x: x["surname"])

    for result in sorted_list:
        table.append_row([result["surname"], result["awards"], result["education"]])

    return table


def save_results(results_list):
    with open("results.txt", "w", encoding="utf-8") as output_file:
        output_file.write(display_results(results_list).get_string())
