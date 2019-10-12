import os
import click
import re
import shutil
from math import log, ceil
from solverStrategy import Strategies
from myDataClasses import Modes

class FilePair:
    def __init__(self, file1, file2):
        if "_sol" in file1:
            self.solutionFile, self.dataFile = file1, file2
        else:
            self.solutionFile, self.dataFile = file2, file1

@click.group()
def helpers():
    pass

def get_files_dict(path: str):
    data = dict()
    
    # r=root, d=directories, f = files
    for root, _, files in os.walk(path):
        for file in files:
            value = f'{root}/{file}'
            key = int(re.findall("[0-9]+", file)[0])

            if key in data.keys():
                data[key].append(value)
            else:
                data[key] = [value]
    return data

def getFiles(path: str):
    data = get_files_dict(path)
    
    result = list()
    for (key, pair) in data.items():
        value = FilePair(pair[0], pair[1])
        result.append((key, value))

    result.sort()
    result = [pair for (_, pair) in result]

    return result

inputModes = ["data", "solution"]

@helpers.command()
@click.option("--mode", type=click.Choice(inputModes), default=inputModes[0])
@click.argument("directory", required=True)
def get_test_files(mode, directory):
    filePairs = getFiles(path=directory)

    for pair in filePairs:
        if mode == "data":
            print(pair.dataFile)
        else:
            print(pair.solutionFile)

def to_csv(output_folder, input_folder, file_name: str):
    with open(f'{input_folder}/{file_name}', "r") as inF:
        with open(f'{output_folder}/{file_name.replace(".dat", ".csv")}', "w") as outF:
            line = inF.readline()
            while line:
                split = line.split("|")

                if len(split) < 2:
                    line = inF.readline()
                    continue

                data = split[0].strip().replace(" ", ";")
                bag = split[1].strip().replace(" ", "")

                outF.write(f'{data};{bag}\n')

                line = inF.readline()

@helpers.command()
@click.option("--dir_name", "--output_folder_name", type=str, default="result_csv")
@click.argument("input_dir", required=True)
@click.argument("output_dir", required=True)
def output_to_csv(dir_name, input_dir, output_dir):
    output_folder = f'{output_dir}/{dir_name}'

    if os.path.isdir(output_folder):
        shutil.rmtree(output_folder)
    os.mkdir(output_folder)

    for root, _, files in os.walk(input_dir):
        for file_name in files:
            to_csv(output_folder, root, file_name)
    print

def get_sums_dict(filepath, strategy, sums_dict, item_num):
    lines = list()
    with open(filepath, "r") as input_file:
        lines = input_file.readlines()
        currSum = 0
        for line in lines:
            currSum += int(line.split(" ")[1])

        if item_num not in sums_dict:
            sums_dict[item_num] = dict()

        if strategy not in sums_dict[item_num]:
            sums_dict[item_num][strategy] = currSum
        else:
            sums_dict[item_num][strategy] += currSum

    return lines

0, 1, 2,   3,  4,  5,  6,  7,  8,  9        
4, 7, 10, 13, 16, 19, 22, 25, 28, 31
def write_hist(output_folder, strategy, hist_dict, lines, startExp, endExp, step):
    if strategy not in hist_dict:
        hist_dict[strategy] = [0 for exp in range(startExp, endExp, step)]
    
    for line in lines:
        split = line.split(" ")
        if len(split) < 2:
            continue

        numOfConfigs = int(split[1])
        index = max(ceil(log(numOfConfigs + 1, 2)), startExp)
        index = min(index, endExp)
        index -= startExp
        index = ceil(index/step)
        hist_dict[strategy][index] += 1

def get_sums(sorted_files, output_folder):
    sums_dict = dict()
    for item_num in sorted(sorted_files):
        for filepath in sorted_files[item_num]:
            filename = filepath.split("/")[-1]
            strategy = filename.split("_inst_")[1].replace(".dat", "")
            get_sums_dict(filepath, strategy, sums_dict, item_num)
    
    with open(f'{output_folder}/sums.csv', "w") as sums_file:
        sums_file.write(f"N;Sum_{Strategies.BruteForce.name};Sum_{Strategies.BranchBound.name};Sum_{Strategies.UnsortedBranchBound.name}\n")
        for (item_num, sums_by_methods) in sums_dict.items():
            bf_sum = sums_by_methods.get(Strategies.BruteForce.name)
            bb_sum = sums_by_methods.get(Strategies.BranchBound.name) 
            ubb_sum = sums_by_methods.get(Strategies.UnsortedBranchBound.name)

            if bf_sum is None:
                bf_sum = 0
            if bb_sum is None:
                bb_sum = 0
            if ubb_sum is None:
                ubb_sum = 0

            sums_file.write(f'{item_num};{ceil(bf_sum)};{ceil(bb_sum)};{ceil(ubb_sum)}\n')

    print

def create_clean_folder(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)

@helpers.command()
@click.option("--dir_name", "--output_folder_name", type=str, default="results_aggregated")
@click.argument("input_dir", required=True)
@click.argument("output_dir", required=True)
def sums(dir_name, input_dir, output_dir):
    output_folder = f'{output_dir}/{dir_name}'

    create_clean_folder(output_folder)

    sorted_files = get_files_dict(input_dir)
    get_sums(sorted_files, output_folder)
            
    print

if __name__ == "__main__":
    helpers()   # pylint: disable=no-value-for-parameter