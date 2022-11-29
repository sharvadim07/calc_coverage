import logging
import argparse

parser = argparse.ArgumentParser(description='Calculation of reads coverage by samtools depth file program')
parser.add_argument('-d','--depth', type=str,                   
                    help='Input depth file', required=True)
parser.add_argument('-n','--npos', type=int,                    
                    help='Number of positions (window size) to calc average coverage. NOT WORKED YET!', required=False)
parser.add_argument('-p','--prefix', type=str,                  
                    help='Out files prefix', required=True)

args = parser.parse_args()

def read_depth_file(depth_file_name):
    with open(depth_file_name, 'r') as depth_file:
        cur_chrom = ''
        prev_pos = -1
        depths_list = []
        for line in depth_file:
            depth_line = line.split('\t')
            cur_pos = int(depth_line[1])
            cur_cov = int(depth_line[2])
            if cur_chrom != depth_line[0]:
                cur_chrom = depth_line[0]                
            else:
                for i in range(cur_pos - (prev_pos + 1)):
                    depths_list.append((cur_chrom, prev_pos + (i+1), 0))            
            depths_list.append((cur_chrom, cur_pos, cur_cov))
            prev_pos = cur_pos
    return depths_list

from operator import itemgetter

def avg_per_chrom(depths_list):
    avg_depth_per_chrom = []
    cur_chrom = ''
    sum_depth_per_cur_chrom = 0
    chrom_pos_counter = 1
    for depth_line in depths_list:
        cur_cov = int(depth_line[2])
        if cur_chrom != depth_line[0]:
            if cur_chrom != '':
                avg_depth_per_chrom.append((cur_chrom, chrom_pos_counter, round(sum_depth_per_cur_chrom/chrom_pos_counter, 2)))
            sum_depth_per_cur_chrom = cur_cov
            chrom_pos_counter = 1
            cur_chrom = depth_line[0]                
        else:
            chrom_pos_counter += 1
            sum_depth_per_cur_chrom += cur_cov
    return sorted(avg_depth_per_chrom, key=itemgetter(2), reverse=True)

with open(args.prefix + "_avg_cov_per_chrom.txt", 'w') as out_file:
    for avg_depth_per_chrom in avg_per_chrom(read_depth_file(args.depth)):
        out_file.write('\t'.join(map(str,avg_depth_per_chrom)) + '\n')