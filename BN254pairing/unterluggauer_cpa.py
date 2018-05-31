import random
import os
import numpy as np
from scipy.stats import pearsonr
from multiprocessing import Pool
import time


#correct_key = 0x15eb62e02fbc3981f9cfed3c30c7f70c99189bed20001f2ac2a9f68e62b8da62

def get_parameter(request):
    parameter = {}
    parameter["known_words"] = 0
    parameter["word_length"] = 8
    parameter["modulo"] = 0x100
    parameter["output_format"] = '02x'
    return parameter[request]

def get_waves(wave_dir):
    waves = []
    wave_file_list = os.listdir(wave_dir)
    print(len(wave_file_list))
    for file_name in wave_file_list:
        wave = []
        file_path = os.path.join(wave_dir, file_name)
        with open(file_path) as file:
            raw = file.read().split()
            wave = list(map(int,raw))
        waves.append(wave)
    print(len(waves))
    return waves

def get_plain_text(plain_text_file):
    plain_paragraph = []
    with open(plain_text_file) as file:
        for raw in file:
            plain_text = int(raw.split(',')[1],16)
            plain_paragraph.append(plain_text)
    return plain_paragraph

def vector_transformed_by(data):
    word_length = get_parameter("word_length")
    modulo = get_parameter("modulo")
    known_words = get_parameter("known_words")
    vector = []
    for i in range(known_words + 1):
        element = int(data) % modulo
        vector.append(element)
        data >> word_length
    return vector

def calculate_unterluggauer_hamming_weight(plain_matrix,key_vector):
    word_length = get_parameter("word_length")
    modulo = get_parameter("modulo")
    l = get_parameter("known_words")
    hamming_weight = []
    for plain_vector in plain_matrix:
        key_hamming_weight = []
        value = 0
        for m in range(l):
            i = m+1
            value = value + (np.dot(plain_vector[:i],key_vector[l-i:]) >> ((l-m)*word_length))
        for key in range(2**word_length):
            key_vector[0] = key
            c = int(value + np.dot(plain_vector,key_vector)) % modulo
            hw = bin(c).count('1')
            key_hamming_weight.append(hw)
        hamming_weight.append(key_hamming_weight)
    return hamming_weight

def change_0_to_randint_with(matrix):
    max_random = get_parameter("word_length")
    for i in range(len(matrix)):
        if matrix[i].std() == 0:
            matrix[i] = np.random.randint(0,max_random,len(matrix[i]))
    return matrix

def calculate_correlation(left_matrix,right_matrix):
    matrix = []
    for l in left_matrix:
        raw = []
        for r in right_matrix:
            correlation, p = pearsonr(l,r)
            raw.append(correlation)
        matrix.append(raw)
    return matrix

def cpa(known_key):
    T_Start = 0
    T_End = 10

    print("start")

    wave_dir = os.path.join(os.getcwd(),'wave')
    wave_list_data = get_waves(wave_dir)
    wave_matrix = np.array(wave_list_data)[:,T_Start:T_End].T
    print(len(wave_matrix))

    print("ok_w")

    plain_text_file = os.path.join(os.getcwd(),'plain_cipher.txt')
    plain_paragraph = get_plain_text(plain_text_file)
    plain_matrix_data = list(map(vector_transformed_by, plain_paragraph))
    plain_matrix = np.array(plain_matrix_data)

    print("ok_p")

    known_key_vector_data = vector_transformed_by(known_key)[::-1]
    key_vector = np.array(known_key_vector_data)

    print("ok_k")

    hamming_weight_matrix_data = calculate_unterluggauer_hamming_weight(plain_matrix,key_vector)
    unsafe_hamming_weight_matrix = np.array(hamming_weight_matrix_data).T	#this have possibility of 0 div
    hamming_weight_matrix = change_0_to_randint_with(unsafe_hamming_weight_matrix)

    print("ok_h")

    correlation_matrix = calculate_correlation(hamming_weight_matrix,wave_matrix)
    max_correlation_vector = list(map(lambda key_correlation_wave: np.amax(np.absolute(key_correlation_wave)), correlation_matrix))
    subscripted_max_correlation_vector = [(i, max_correlation) for i,max_correlation in enumerate(max_correlation_vector)]
    subscripted_max_correlation_vector.sort(key= lambda x: x[1],reverse=True)

    print("ok_c")

    out_dir = os.path.join(os.getcwd(),"unterluggauer_cpa_out")
    output_format = get_parameter("output_format")
    key_dir = os.path.join(out_dir,format(known_key,"02x"))
    if not os.path.isdir(key_dir):
        os.mkdir(key_dir)
    for key in range(len(correlation_matrix)):
        out = os.path.join(key_dir,format(key,"02x"))
        with open(out,'w') as file:
            for t in range(len(correlation_matrix[key])):
                file.write(str(correlation_matrix[key][t]) + '\n')
        out = os.path.join(key_dir,'meta.txt')
        with open(out, 'w') as file:
            for i in range(len(correlation_matrix)):
                file.write(str(i+1)+','+hex(subscripted_max_correlation_vector[i][0])+','+str(subscripted_max_correlation_vector[i][1]) + '\n')


if __name__ == '__main__':
    alpha_out = 16
    known_words = get_parameter("known_words")
    word_bits = get_parameter("word_length")
    alpha_in_file = "alpha" + str(known_words*word_bits) + ".txt"

    out_dir = os.path.join(os.getcwd(),"unterluggauer_cpa_out")
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
        alpha_file_path = os.path.join(out_dir,alpha_in_file)
        with open(alpha_file_path,"w") as f:
            f.write("1,0x0,0.0")

    alpha_keys = []
    p = os.path.join(out_dir,alpha_in_file)
    with open(p) as file:
        alpha_key = 0
        for raw in file.read().split():
            alpha_key = int(raw.split(",")[1],16)
            alpha_keys.append(alpha_key)

    start = time.time()
    #pool = Pool(8)
    #pool.map(cpa, alpha_keys)
    #pool.close()
    cpa(0)
    print(str(time.time() - start))

    alpha_top = []
    for alpha_key in alpha_keys:
        key_dir = os.path.join(out_dir,format(alpha_key,"02x"))
        meta_file = os.path.join(key_dir,"meta.txt")
        with open(meta_file) as file:
            for raw in file.read().split():
                key = (int(raw.split(',')[1],16) << (known_words*word_bits) ) | alpha_key
                r = float(raw.split(',')[2])
                alpha_top.append((key,r))
    alpha_top.sort(key=lambda x: x[1],reverse=True)


    alpha_out_file = "alpha" + str((known_words+1)*word_bits) + ".txt"
    p = os.path.join(out_dir, alpha_out_file)
    with open(p,"w") as file:
        for i in range(alpha_out):
            file.write(str(i+1)+','+hex(alpha_top[i][0])+','+str(alpha_top[i][1]) + '\n')
