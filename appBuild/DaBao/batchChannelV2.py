#!/usr/local/bin/python3
# coding:utf-8

# Show channel
# Usage: python batchChannelV2.py show xx.apk

# Single channel
# Usage: python batchChannelV2.py xx.apk channel_name

# Batch channels
# Usage: python batchChannelV2.py xx.apk channel_name1,channel_name2,channel_name3

# Batch channels by seq
# Usage: python batchChannelV2.py xx.apk channel_name 1 10

# Batch config in a file
# Usage: python batchChannelV2.py xx.apk -f test.conf

import sys
import os


def process_one_conf(working_dir):
    # show channel
    if len(sys.argv) == 3:
        if sys.argv[1] == 'show':
            apk_file_name = sys.argv[2]
            os.system('java -jar walle-cli-all.jar show ' + apk_file_name)
            exit(0)

    # get arguments from command line
    apk_file_name = sys.argv[1]
    channel_name = sys.argv[2]

    start_channel_seq = None
    end_channel_seq = None

    has_seq = len(sys.argv) >= 5
    if has_seq:
        start_channel_seq = int(sys.argv[3])
        end_channel_seq = int(sys.argv[4])

    # get single channel name or batch channel names if with start and end seq arguments
    channel_names = []
    if not has_seq:
        channel_names.extend(channel_name.split(','))
    else:
        max_seq_len = len(str(end_channel_seq))
        for i in range(start_channel_seq, end_channel_seq + 1):
            format_str = '{:0>' + str(max_seq_len) + 'd}'
            seq_postfix = format_str.format(i)
            # seq_postfix = str(i)
            channel_names.append(channel_name + seq_postfix)

    # build channel apk and rename
    for single_channel_name in channel_names:
        channel_names_batch = [single_channel_name]
        # all processed by batch_mode
        channel_names_str = ','.join(channel_names_batch)
        output_path = working_dir
        os.chdir(working_dir)
        cmd = 'java -jar walle-cli-all.jar batch -c ' + channel_names_str + ' ' + apk_file_name
        # print('cmd is:\n' + cmd)
        os.system(cmd)

        # rename apk files
        apk_name = apk_file_name[:-4]

        os.chdir(output_path)  # switch to output dir
        for c_name in channel_names_batch:
            generated_apk_file_name = apk_name + '_' + c_name
            name_segments = generated_apk_file_name.split('-')
            name_segments[1] = c_name
            name_segments[-1] = name_segments[-1].split('_')[0]
            final_apk_file_name = '-'.join(name_segments)
            # os.rename(generated_apk_file_name + '.apk', final_apk_file_name + '.apk')
            os.system('move ' + generated_apk_file_name + '.apk ' + final_apk_file_name + '.apk')


if __name__ == '__main__':
    conf_file = ''
    working_dir = os.getcwd()
    if len(sys.argv) >= 3 and sys.argv[2] == '-f':
        conf_file = sys.argv[3]
        with open(conf_file) as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('#'):
                    continue
                line_args = line.split()
                tmp_args = sys.argv[:2]
                tmp_args.extend(line_args)
                sys.argv = tmp_args
                print('process_one_conf args: ' + ' '.join(sys.argv))
                process_one_conf(working_dir)
    else:
        process_one_conf(working_dir)
