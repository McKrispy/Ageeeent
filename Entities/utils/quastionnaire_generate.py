import json

def load_json_in_cmd(json_object: dict):
    questions = json_object["questions"]
    for question in questions:
        print(f"question['question']\n")
        options = question["options"]
        for option in options:
            print(option)
        print("--------------------------------")



if __name__ == "__main__":
    with open("Data/DataFormat/questionnaire.json", "r") as f:
        json_object = json.load(f)
    load_json_in_cmd(json_object)