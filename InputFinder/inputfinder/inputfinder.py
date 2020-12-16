#!/usr/env/python3.8

"""
Description of inputfinder.py
Usage:

TODO:
- decision based fuzzing check for cov of each filetype
- mb multi thread
"""

import argparse
import os
import errno
import shutil
import subprocess
import time

#def sort_log():


def get_filetypes(list):
    all_filetypes = []
    unique_filetypes = []
    for files in list:
        index = files.rfind('.')
        all_filetypes.append(files[index:])
    for x in all_filetypes:
        if x not in unique_filetypes:
            unique_filetypes.append(x)
    return unique_filetypes


def fetch_x_of_one_filetype(list, filetype, number):
    new_list = ["dummy"]
    unique_filetypes = get_filetypes(list)
    found = 0
    for check in unique_filetypes:
        if check == filetype:
            found = 1
            break

    if found is 0:
        #exit(1)
        return 0

    for files in list:
        if filetype in files:
            found = 0
            for o in new_list:
                if filetype not in o:
                    continue
                if files is o:
                    continue
                if filetype in o:
                    found = found + 1
            if found < number:
                new_list.append(files)

    # remove dummy
    new_list.pop(0)
    return new_list


def fetch_x_of_each_filetype(list,number):
    new_list = ["dummy"]
    unique_filetypes = get_filetypes(list)

    for files in list:
        for x in unique_filetypes:
            if x in files:
                found = 0
                for o in new_list:
                    if x not in o:
                        continue
                    if files is o:
                        continue
                    if x in o:
                        found = found + 1
                if found < number:
                    new_list.append(files)

    # remove dummy
    new_list.pop(0)
    return new_list


def delete_log():
    log = "../log.txt"
    if os.path.exists(log):
        try:
            os.remove(log)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))


def write_log(cov, files):
    log = "../log.txt"
    try:
        with open(log, "a") as myfile:
            myfile.write("{}\t{}\n".format(cov, files))
    except FileNotFoundError as e:
        print(e)
    myfile.close()


def delete_fuzz_dir():
    if os.path.isdir("../fuzz"):
        try:
            shutil.rmtree("../fuzz")
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))


def create_fuzz_dir():
    try:
        os.makedirs("../fuzz")
        os.makedirs("../fuzz/in")
        os.makedirs("../fuzz/out")
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def provide_input(input):
    for f in input:
        try:
            shutil.copy(f, "../fuzz/in")
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))


def get_coverage(fuzzer_stats):
    mylines = []
    try:
        with open(fuzzer_stats, "r") as myfile:
            for myline in myfile:
                mylines.append(myline)
        coverage = mylines[6][20:]
    except FileNotFoundError as e:
        print(e)
        return "0"
    myfile.close()
    return coverage


def crawl_directories(directory):
    file_list = []
    for currentpath, folders, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(currentpath, file))
    return file_list


def check_for_multifile(string):
    if "??" in string:
        return 1
    else:
        return 0


def invoke_afl(string):
    p = subprocess.Popen(string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in p.stdout:
        print(line.decode())
        if "Fuzzing test case" in line.decode():
            #time.sleep(1)
            p.terminate()
        if "PROGRAM ABORT" in line.decode():
            print("Error in AFL")
            exit(1)

def main():
    print("""                                                                          
###########                                                                            
# Finder is part of https://github.com/...                                                                                                         
# Developed and maintained by @Kybranzf
#
# Invoke commands as root before fuzzing:
#   
#   echo core >/proc/sys/kernel/core_pattern
#   cd /sys/devices/system/cpu
#   echo performance | tee cpu*/cpufreq/scaling_governor
#
###########                                                                            
""")

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default='afl-fuzz -i ../fuzz/in/ -o ../fuzz/out/ /home/cybrg/master/fuzzing_work/libjpeg-turbo_/libjpeg-turbo/djpeg ??', help='input the command as you '
                                                                                          'would call afl from cmd\n '
                                                                                          'afl-fuzz -i in/ -o out/ '
                                                                                          'djpeg @@')
    parser.add_argument('-d', '--directory', default='../testcases_edges', help='directory where all files are')

    args = parser.parse_args()
    inputstring = args.input
    directory = args.directory
    list_of_files = []
    coverage = []

    afl_out_directory = "../fuzz/out/"
    afl_in_directory = "../fuzz/in/"
    afl_stats = afl_out_directory + "fuzzer_stats"
    fuzzer_stats = "../fuzz/out/fuzzer_stats"
    delete_log()

    # check for file wildcard ??
    is_multifile = check_for_multifile(inputstring)
    if is_multifile and directory:
        inputstring = inputstring.replace("??", "@@")
        list_of_files = crawl_directories(directory)
        count = len(list_of_files)

        list_1 = fetch_x_of_each_filetype(list_of_files, 1)
        list_10 = fetch_x_of_each_filetype(list_of_files, 10)
        list_50 = fetch_x_of_each_filetype(list_of_files, 50)
        #png = fetch_x_of_one_filetype(list_of_files, '.png', 10)

        #print("Filetypes found: {}".format(list_1))

        print('RAW AFL input: "{}"'.format(inputstring))
        print('Input files provided: "{}"'.format(count))

        # get coverage for each filetype
        unique_filetypes = get_filetypes(list_of_files)
        for filetypes in unique_filetypes:
            input = fetch_x_of_one_filetype(list_of_files, filetypes, 100)

            delete_fuzz_dir()
            create_fuzz_dir()

            provide_input(input)

            invoke_afl(inputstring)
            coverage.append(get_coverage(fuzzer_stats))
            print(input)
            print(coverage)
            #try:
            #    coverage.append(get_coverage("../fuzz/out/fuzzer_stats"))
            #    #print("Coverage: {} from file {}".format(get_coverage("../fuzz/out/fuzzer_stats")[:1], current_file))
            #except Exception as e:
            #   print(e)
            write_log(get_coverage(fuzzer_stats).replace('\r', '').replace('\n', ''), filetypes)
            #sort_log()
        exit(123)

if __name__ == '__main__':
    main()


