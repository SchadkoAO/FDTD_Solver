import numpy as np
import matplotlib.pyplot as plt
import argparse
import traceback
import tarfile
import os
import re
import time


def read_tarinfo(fname):
    tar = tarfile.open(fname)
    return list(tar.getmembers()), tar


def read(file, tar_info):
    f = file.extractfile(tar_info)
    if f is None:
        return None, True
    content = f.read()
    return content, False


def should_parse_file(tar_file, t_start, t_end):
    regex = re.compile(r"i_(\w+)_(\d+)\.txt")
    try:
        m = regex.search(tar_file.name)
        file_type = m.group(1)
        t = int(m.group(2))
        return t_start <= t <= t_end and file_type == 'small'
    except BaseException:
        return False


def output_spot(name, content, dir_name, th):
    splited = content.decode("utf-8").split("\n")
    # Get area size
    first_x = float('inf')
    first_y = float('inf')
    last_x = 0
    last_y = 0
    for line in splited:
        line_splited = line.split(" ")
        if len(line_splited) != 3:
            print(line_splited)
            continue
        y = int(line_splited[1])
        x = int(line_splited[0])
        if last_x < x:
            last_x = x
        if first_x > x:
            first_x = x
        if last_y < y:
            last_y = y
        if first_y > y:
            first_y = y
    size_x = last_x - first_x
    size_y = last_y - first_y
    data = np.zeros((size_y + 1, size_x + 1))
    print("File {name} obtain size_x={size_x} size_y={size_y}".format(
        name=name,
        size_x=size_x,
        size_y=size_y
    ))
    # Read to NP array
    for line in splited:
        line_splited = line.split(" ")
        if len(line_splited) != 3:
            print(line_splited)
            continue
        y = int(line_splited[1])
        x = int(line_splited[0])
        val = float(line_splited[2])
        data[y - first_y, x - first_x] = val
    # Iterate over each slice
    spot_x = 0
    spot_y = 0
    spot_size = 1000
    spots = []
    for column_idx in range(data.shape[1]):
        column = data[:, column_idx]
        nonzero = np.count_nonzero(column)
        if nonzero == 0:
            continue
        spot_size = len(column)
        max_pos = np.argmax(column)
        total_energy = np.sum(column)
        for radius in range(10, round(len(column)/2 - 1)):
            spot = column[max_pos - radius : max_pos + radius]
            energy_inside_spot = np.sum(spot)
            if energy_inside_spot/total_energy > th:
                spot_size = 2 * radius
                break
        spots.append(spot_size)
    min_spot_idx = np.argmin(spots)
    min_spot_column = data[:, min_spot_idx]
    plt.gcf().clear()
    plt.plot(range(size_y+1), min_spot_column)
    plt.text(0, 2, "X={x} Spot={spot}".format(
        x=min_spot_idx,
        spot=spots[min_spot_idx]
    ), fontsize=12)
    plt.savefig(name.replace(".png", "_x={x}_spot={spot}.png".format(
        x=first_x + min_spot_idx, 
        spot=spots[min_spot_idx]
    )))


def main(tar_name, t_start, t_end, output_name, th):
    tar_info, file = read_tarinfo(tar_name)
    dir_name = "spots_{}".format(tar_name.replace(".tar.gz", ""))
    print(tar_info)

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    for tf in tar_info:
        try:
            if not should_parse_file(tf, t_start, t_end):
                print("Skipping: {}".format(tf.name))
                continue
            print("Processing {}".format(tf.name))
            content, isErr = read(file, tf)
            if isErr:
                print("Error during file processing: {}".format(tf.name))
                continue
            output_spot("spots_" + tf.name.replace(".txt", ".png"), content, dir_name, th)
        except BaseException:
            traceback.print_exc()
            continue

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_name", help="Path to file in which image will be saved")
    parser.add_argument("--th", help="Threshold for spot finding algorithm")
    parser.add_argument("--tar_file", help="Path to archive")
    parser.add_argument("--t_start", help="Time from to start read files")
    parser.add_argument("--t_end", help="Time until dumps should ba analized")
    args = parser.parse_args()

    out_name = str(args.out_name)
    tar_file = str(args.tar_file)
    t_start = int(args.t_start)
    t_end = int(args.t_end)
    th = float(args.th)

    print("Start processing spots: tar_file={tar_file}\n out_name={out_name}\n t_start={t_start}\n t_end={t_end}\n".format(
        tar_file=tar_file,
        out_name=out_name,
        t_start=t_start,
        t_end=t_end,
    ))

    main(
        tar_name=tar_file,
        output_name=out_name,
        t_start=t_start,
        t_end=t_end,
        th=th
    )
