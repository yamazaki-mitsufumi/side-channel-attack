import random
import os
import numpy as np
from scipy.stats import pearsonr
from multiprocessing import Pool, cpu_count

from jauvart_parameter import get_parameter

#correct_key = 0x15eb62e02fbc3981f9cfed3c30c7f70c99189bed20001f2ac2a9f68e62b8da62

def get_plain_vector():
    plain_text_file_name = get_parameter("plain_text_file_name")
    plain_text_file = os.path.join(os.getcwd(), plain_text_file_name)
    raw_plain_vector = []
    with open(plain_text_file) as file:
        for row in file:
            plain_text = int(row.split(',')[1], 16)
            raw_plain_vector.append(plain_text)
    plain_vector = np.array(raw_plain_vector)
    return plain_vector

def get_wave_matrix():
    poi_start = get_parameter("poi_start")
    poi_end = get_parameter("poi_end")
    wave_dir_name = get_parameter("wave_dir_name")
    wave_dir = os.path.join(os.getcwd(), wave_dir_name)
    wave_file_list = os.listdir(wave_dir)
    raw_wave_matrix = []
    for file_name in wave_file_list:
        wave_file = os.path.join(wave_dir, file_name)
        with open(wave_file) as file:
            wave = list(map(int, file.read().split()))
            raw_wave_matrix.append(wave)
    wave_matrix = np.array(raw_wave_matrix)[:,poi_start:poi_end].T
    return wave_matrix

def change_0_to_randint_with(matrix):
    max_random = get_parameter("result_key_length")
    for i in range(len(matrix)):
        if matrix[i].std() == 0:
            matrix[i] = np.random.randint(0,max_random,len(matrix[i]))
    return matrix

def calculate_jauvart_hamming_weight_matrix(plain_vector, candidate_key):
    key_range = get_parameter("key_range")
    candidate_key_length = get_parameter("candidate_key_length")
    modulo = get_parameter("modulo")
    raw_hamming_weight_matrix = []
    for estimation_key in range(key_range):
        key = estimation_key*(2**candidate_key_length) + candidate_key
        key_hamming_wave = []
        for plain in plain_vector:
            middle_value = (plain*key) % modulo
            hamming_weight = bin(middle_value).count('1')
            key_hamming_wave.append(hamming_weight)
        raw_hamming_weight_matrix.append(key_hamming_wave)
    unsafe_hamming_weight_matrix = np.array(raw_hamming_weight_matrix)
    hamming_weight_matrix = change_0_to_randint_with(unsafe_hamming_weight_matrix)
    return hamming_weight_matrix

def calculate_correlation_matrix(left_matrix,right_matrix):
    matrix = []
    for l in left_matrix:
        row = []
        for r in right_matrix:
            correlation, p = pearsonr(l,r)
            row.append(correlation)
        matrix.append(row)
    return matrix

def calculate_max_correlation_list(correlation_matrix):
    raw_max_correlation_list = list(map(lambda key_correlation_wave: np.amax(np.absolute(key_correlation_wave)), correlation_matrix))
    max_correlation_list = [(key, max_correlation) for key,max_correlation in enumerate(raw_max_correlation_list)]
    max_correlation_list.sort(key= lambda key_correlation: key_correlation[1],reverse=True)
    return max_correlation_list

def output_correlation(candidate_key ,correlation_matrix):
    output_dir_name = get_parameter("output_dir_name")
    output_dir = os.path.join(os.getcwd(), output_dir_name)
    candidate_key_format = get_parameter("candidate_key_format")
    key_dir = os.path.join(output_dir, format(candidate_key, candidate_key_format))
    if not os.path.isdir(key_dir):
        os.mkdir(key_dir)

    estimation_key_format = get_parameter("estimation_key_format")
    for key,correlation in enumerate(correlation_matrix):
        output_file = os.path.join(key_dir, format(key, estimation_key_format))
        with open(output_file, 'w') as file:
            str_correlation = list(map(str, correlation))
            file.write('\n'.join(str_correlation))

def output_max_correlation(candidate_key, correlation_list):
    output_dir_name = get_parameter("output_dir_name")
    output_dir = os.path.join(os.getcwd(), output_dir_name)
    candidate_key_format = get_parameter("candidate_key_format")
    key_dir = os.path.join(output_dir, format(candidate_key, candidate_key_format))
    if not os.path.isdir(key_dir):
        os.mkdir(key_dir)

    result_file_name = get_parameter("result_file_name")
    result_file = os.path.join(key_dir, result_file_name)
    result_key_format = get_parameter("result_key_format")
    with open(result_file, 'w') as file:
        for key_max in correlation_list:
            key = format(key_max[0], result_key_format)
            max_correlation = str(key_max[1])
            file.write(key+','+max_correlation+'\n')

def cpa(candidate_key):
    plain_vector = get_plain_vector()
    wave_matrix = get_wave_matrix()
    hamming_weight_matrix = calculate_jauvart_hamming_weight_matrix(plain_vector, candidate_key)
    correlation_matrix = calculate_correlation_matrix(hamming_weight_matrix, wave_matrix)
    max_correlation_list = calculate_max_correlation_list(correlation_matrix)
    output_correlation(candidate_key, correlation_matrix)
    output_max_correlation(candidate_key, max_correlation_list)

def initialize():
    output_dir_name = get_parameter("output_dir_name")
    output_dir = os.path.join(os.getcwd(),output_dir_name)
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
        candidate_file_name = get_parameter("candidate_file_name")
        candidate_file = os.path.join(output_dir, candidate_file_name)
        with open(candidate_file,"w") as file:
            file.write("0,0.0")

def get_candidate_key_list():
    output_dir_name = get_parameter("output_dir_name")
    output_dir = os.path.join(os.getcwd(),output_dir_name)
    candidate_file_name = get_parameter("candidate_file_name")
    candidate_file = os.path.join(output_dir, candidate_file_name)
    candidate_key_list = []
    with open(candidate_file) as file:
        for row in file:
            candidate_key = int(row.split(",")[0],16)
            candidate_key_list.append(candidate_key)
    return candidate_key_list

def get_result(candidate_key_list):
    output_dir_name = get_parameter("output_dir_name")
    output_dir = os.path.join(os.getcwd(),output_dir_name)
    result = []
    for candidate_key in candidate_key_list:
        candidate_key_format = get_parameter("candidate_key_format")
        key_dir = os.path.join(output_dir,format(candidate_key, candidate_key_format))
        result_file_name = get_parameter("result_file_name")
        result_file = os.path.join(key_dir,result_file_name)
        with open(result_file) as file:
            for row in file:
                correlation = float(row.split(',')[1])
                key = int(row.split(',')[0],16)
                candidate_key_length = get_parameter("candidate_key_length")
                result_key = key*(2**candidate_key_length) + candidate_key
                result.append((result_key,correlation))
    result.sort(key=lambda key_correlation: key_correlation[1],reverse=True)
    return result

def output_final_result(result):
    output_dir_name = get_parameter("output_dir_name")
    output_dir = os.path.join(os.getcwd(),output_dir_name)
    final_result_file_name = get_parameter("final_result_file_name")
    final_result_file = os.path.join(output_dir, final_result_file_name)
    with open(final_result_file,'w') as file:
        for key_max in result:
            result_key_format = get_parameter("result_key_format")
            key = format(key_max[0], result_key_format)
            max_correlation = str(key_max[1])
            file.write(key+','+max_correlation+'\n')

def output_candidate_key_list(result):
    alpha = get_parameter("alpha")
    output_dir_name = get_parameter("output_dir_name")
    output_dir = os.path.join(os.getcwd(),output_dir_name)
    candidate_key_list = result[:alpha]
    output_candidate_file_name = get_parameter("output_candidate_file_name")
    output_candidate_file = os.path.join(output_dir, output_candidate_file_name)
    with open(output_candidate_file,'w') as file:
        for key_max in candidate_key_list:
            result_key_format = get_parameter("result_key_format")
            key = format(key_max[0], result_key_format)
            max_correlation = str(key_max[1])
            file.write(key+','+max_correlation+'\n')

if __name__ == '__main__':
    initialize()

    candidate_key_list = get_candidate_key_list()

    if(get_parameter("parallel")):
        pool = Pool(cpu_count())
        pool.map(cpa, candidate_key_list)
        pool.close()
    else:
        for candidate_key in candidate_key_list:
            cpa(candidate_key)

    result = get_result(candidate_key_list)
    output_final_result(result)
    output_candidate_key_list(result)
