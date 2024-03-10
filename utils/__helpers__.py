import pickle, json
import os

def open_file(file_path, data=None):
    file_extention = file_path.split(".")[-1]
    match file_extention:
        case "json":
            module = json
            write_mode = "w"
            read_mode = "r"
        case "pickle":
            module = pickle
            write_mode = "wb"
            read_mode = "rb"

    if data:
        with open(file_path, write_mode) as file:
            if file_extention == "json":
                module.dump(data, file, indent=2)
            else:
                module.dump(data, file)
            return

    with open(file_path, read_mode) as file:
        return module.load(file)


def get_files(path: str, praser=int):
    files = os.listdir(path)

    return [praser(file[: file.index(".")]) for file in files]

def formate_time(seconds: int):
    time = [(str(int(seconds / 3600)), "h"), (str(int((seconds % 3600) / 60)), "min")]
    time = filter(lambda x: x[0] != "0" , time)
    time = map(lambda x: x[0] + x[1], time)
    return " ".join(time)

def formate_name(name: str):
    name = name.strip().capitalize()
    return name

def data_to_table(week: str):
  users_data = []

  for id in get_files("data/users"):
      user_data: dict = open_file(f"data/users/{id}.json")
      users_data.append(
          {
              "name": user_data["name"],
              "rank": user_data["activity"][week]["rank"],
              "amount": user_data["activity"][week]["amount"],
          }
      )

  users_data.sort(key=lambda x: x["rank"])

  txt = (
     f"{' '*3}  |  {'Coder':^20}  |  {'total':^9}  "
     f"\n{'-'*3}--|--{'-'*20}--|--{'-'*9}--"
     )

  for user_data in users_data:
      txt += f"\n{user_data["rank"]:>3}  |  {formate_name(user_data["name"]):<20}  |  {formate_time(user_data["amount"]):^9}"

  return txt
