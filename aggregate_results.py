import os
import sys


def aggregate():
    input_dir, output_file = sys.argv[1], sys.argv[2] + ".csv"
    output = open(output_file, 'w')
    output.write("Process name, PID, instance #, # instructions, # cycles, # i-cache misses\n")
    process_map = {}
    for filename in os.listdir(input_dir):
        process_name = filename.split('_')[0]
        pid = filename.split('_')[1]
        if process_name not in process_map:
            process_map[process_name] = 1
        else:
            process_map[process_name] += 1

        file = open(input_dir + '/' + filename, 'r')
        lines = file.readlines()
        if " Performance counter stats for process id '" + pid + "':\n" not in lines:
            print("Error: " + filename + " does not contain performance counter stats")
            continue
        useful_lines = lines[lines.index(" Performance counter stats for process id '" + pid + "':\n") + 2:]

        instructions = useful_lines[0].split()[0]
        cycles = useful_lines[1].split()[0]
        cache_misses = useful_lines[2].split()[0]

        output.write(process_name + ',' + pid + ',' + str(process_map[process_name]) + ',' + instructions + ','
                     + cycles + ',' + cache_misses + '\n')
        file.close()
    output.close()


if __name__ == '__main__':
    aggregate()
