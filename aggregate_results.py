import os
import sys

import matplotlib.pyplot as plt
import pandas as pd


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


def sort_db(file):
    _file = open(file, 'r')
    lines = _file.readlines()[1:]
    _file.close()
    # group by process name and sort by instance #
    lines.sort(key=lambda x: (x.split(',')[0], int(x.split(',')[2])))
    # filter out the lines that have <not in them
    lines = list(filter(lambda x: '<not' not in x, lines))
    _file = open(file, 'w')
    _file.write("Process name, PID, instance #, # instructions, # cycles, # i-cache misses\n")
    for line in lines:
        _file.write(line)
    _file.close()


def plot_baton_graph(file):
    try:
        df = pd.read_csv(file)

        df.columns = df.columns.str.strip()

        expected_columns = ['Process name', 'instance #', '# instructions', '# cycles', '# i-cache misses']
        for col in expected_columns:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found in the CSV file.")

        # Data processing
        df = df.sort_values(by=['Process name', 'instance #'])
        df = df.reset_index(drop=True)
        df['# instructions'] = pd.to_numeric(df['# instructions'], errors='coerce')
        df['# cycles'] = pd.to_numeric(df['# cycles'], errors='coerce')
        df['# i-cache misses'] = pd.to_numeric(df['# i-cache misses'], errors='coerce')

        df['IPC'] = df['# instructions'] / df['# cycles']
        df['MPKI'] = df['# i-cache misses'] / df['# instructions'] * 1000

        # Group by process name and calculate mean
        df = df.groupby(['Process name']).mean()
        df = df.reset_index()

        # Rounding off the calculated values
        df['IPC'] = df['IPC'].round(2)
        df['MPKI'] = df['MPKI'].round(2)

        # Plotting IPC
        ipc_df = df[['Process name', 'IPC']].set_index('Process name')
        plt.figure(figsize=(12, 6))
        ax_ipc = ipc_df.plot.bar(rot=90)  # Rotate the labels vertically
        ax_ipc.set_xlabel("Process Name")
        ax_ipc.set_ylabel("IPC Value")
        ax_ipc.set_title("IPC Baton Graph")
        plt.tight_layout()
        plt.savefig("ipc_baton_graph.png")

        # Plotting MPKI
        mpki_df = df[['Process name', 'MPKI']].set_index('Process name')
        plt.figure(figsize=(12, 6))
        ax_mpki = mpki_df.plot.bar(rot=90)
        ax_mpki.set_xlabel("Process Name")
        ax_mpki.set_ylabel("MPKI Value")
        ax_mpki.set_title("MPKI Baton Graph")
        plt.tight_layout()
        plt.savefig("mpki_baton_graph.png")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    aggregate()
    sort_db(sys.argv[2] + ".csv")
    plot_baton_graph(sys.argv[2] + ".csv")
