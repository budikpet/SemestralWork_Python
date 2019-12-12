from typing import Dict, List
from algorithm_tester.tester_dataclasses import Parser

class KnapsackParser(Parser):

    def get_name(self) -> str:
        return "KnapsackParser"

    def get_output_file_name(self, click_args: Dict[str, object]) -> str:
        input_file_name: str = self.input_file.name.split("/")[-1]

        return input_file_name.replace(".dat", f'_{click_args["algorithm_name"]}_sol.dat')

    def get_next_instance(self) -> Dict[str, object]:
        instance: str = self.input_file.readline()

        if instance is None or instance == "":
            return None

        solution: Dict[str, object] = None
        values: List[str] = instance.split(" ")
        id, count, capacity = int(values.pop(0)), int(values.pop(0)), int(values.pop(0))
        it = iter(values)
        things = [(pos, int(weight), int(cost)) for pos, (weight, cost) in enumerate(list(zip(it, it)))]

        parsed_data = {
            "id": id,
            "item_count": count,
            "capacity": capacity,
            "things": things
        }

        return parsed_data

    def write_result_to_file(self, output_file, data: Dict[str, object]):
        columns: List[str] = data["algorithm"].get_columns()

        if data["check_time"] == False and "elapsed_time" in columns:
            columns.remove("elapsed_time")
        elif data["check_time"] == True and "elapsed_time" in columns and "elapsed_configs" in columns:
            columns.remove("elapsed_configs")


        if data.get("things") is not None:
            data["things"] = "".join(map(str, data["things"]))
        
        output_data = [data.get(column) for column in columns]
        
        output: str = f'{" ".join(map(str, output_data))}'
        output_file.write(f'{output}\n')