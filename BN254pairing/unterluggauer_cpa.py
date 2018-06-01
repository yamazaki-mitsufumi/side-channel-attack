import numpy as np
import os
from scipy.stats import pearsonr
from multiprocessing import Pool


#correct_key = 0x15eb62e02fbc3981f9cfed3c30c7f70c99189bed20001f2ac2a9f68e62b8da62

def get_parameter(request):
    parameter = {}
    #experiment_parameter
    parameter["poi_start"] = 0
    parameter["poi_end"] = 5000
    parameter["target_word"] = 0
    parameter["word_length"] = 8
    parameter["modulo"] = 0x100
    parameter["k"] = 16

    #format_parameter
    parameter["wave_dir_name"] = 'wave'
    parameter["plain_text_file_name"] = 'plain_cipher.txt'
    parameter["result_file_name"] = 'result.txt'
    parameter["output_dir_name"] = 'unterluggauer_cpa_out'
    parameter["word_format"] = '02x'

    #dependent on target_word and word_length
    target_word = parameter["target_word"]

    output_candidate_key_length = (word_length/4)*(target_word+1)
    output_candidate_key_format = '0' + str(output_candidate_key_length) + 'x'
    parameter["output_candidate_key_format"] = output_candidate_key_format

    output_dir_length = (word_length/4)*target_word if target_word != 0 else 2
    output_dir_format = '0' + str(output_dir_length) + 'x'
    parameter["output_dir_format"] = output_dir_format

    final_result_length = (word_length/4)*(target_word+1)
    final_result_format = '0' + str(final_result_length) + 'x'
    parameter["final_result_format"] = final_result_format

    input_candidate_file_name = 'candidate_on_aiming_'+str(target_word)+'word.txt'
    parameter["input_candidate_file_name"] = input_candidate_file_name

    output_candidate_file_name = 'candidate_on_aiming_'+str(target_word+1)+'word.txt'
    parameter["output_candidate_file_name"] = output_candidate_file_name

    final_result_file_name = 'result_of_aiming_' + str(target_word) + '.txt'
    parameter["final_result_file_name"] = final_result_file_name

    return parameter[request]

def get_waves(wave_dir):
    waves = []
    wave_file_list = os.listdir(wave_dir)
    for file_name in wave_file_list:
        wave = []
        file_path = os.path.join(wave_dir, file_name)
        with open(file_path) as file:
            str_wave = file.read().split()
            wave = list(map(int,str_wave))
        waves.append(wave)
    return waves

def get_plain_paragraph(plain_text_file):
    plain_paragraph = []
    with open(plain_text_file) as file:
        for row in file:
            plain_text = int(row.split(',')[1],16)	#wavefile,plaintext,cihpertext
            plain_paragraph.append(plain_text)
    return plain_paragraph

def vector_transformed_by(data):
    word_length = get_parameter("word_length")
    modulo = get_parameter("modulo")
    target_word = get_parameter("target_word")
    vector = []
    for i in range(target_word + 1):	#i = 0,1,...,target_word
        element = int(data) % modulo
        vector.append(element)
        data >> word_length
    return vector

def calculate_unterluggauer_hamming_weight(plain_matrix,key_vector):
    word_length = get_parameter("word_length")
    modulo = get_parameter("modulo")
    l = get_parameter("target_word")
    hamming_weight_matrix = []
    for plain_vector in plain_matrix:
        key_hamming_weight_vector = []
        value = 0
        for m in range(l):
            value = value + (np.dot(plain_vector[:m+1],key_vector[l-m:]) >> ((l-m)*word_length))
        for key in range(2**word_length):
            key_vector[0] = key
            c = int(value + np.dot(plain_vector,key_vector)) % modulo
            hw = bin(c).count('1')
            key_hamming_weight_vector.append(hw)
        hamming_weight_matrix.append(key_hamming_weight_vector)
    return hamming_weight_matrix

def change_0_to_randint_with(matrix):
    max_random = get_parameter("word_length")
    for i in range(len(matrix)):
        if matrix[i].std() == 0:
            matrix[i] = np.random.randint(0,max_random,len(matrix[i]))
    return matrix

def calculate_correlation(left_matrix,right_matrix):
    matrix = []
    for l in left_matrix:
        row = []
        for r in right_matrix:
            correlation, p = pearsonr(l,r)
            row.append(correlation)
        matrix.append(row)
    return matrix

def output_correlation(candidate_key, correlation_matrix):
    output_dir_name = get_parameter("output_dir_name")
    output_dir_format = get_parameter("output_dir_format")
    word_format = get_parameter("word_format")
    output_dir = os.path.join(os.getcwd(), output_dir_name)
    key_dir = os.path.join(output_dir, format(candidate_key, output_dir_format))
    if not os.path.isdir(key_dir):
        os.mkdir(key_dir)

    for key,correlation in enumerate(correlation_matrix):
        output_file = os.path.join(key_dir, format(key, word_format))
        with open(output_file, 'w') as file:
            str_correlation = list(map(str, correlation))
            file.write('\n'.join(str_correlation))

def output_max_correlation(candidate_key, subscripted_max_correlation_vector):
    output_dir_name = get_parameter("output_dir_name")
    output_dir_format = get_parameter("output_dir_format")
    word_format = get_parameter("word_format")
    output_dir = os.path.join(os.getcwd(),output_dir_name)
    key_dir = os.path.join(output_dir,format(candidate_key,output_dir_format))
    if not os.path.isdir(key_dir):
        os.mkdir(key_dir)

    result_file_name = get_parameter("result_file_name")
    output_file = os.path.join(key_dir,result_file_name)
    with open(output_file, 'w') as file:
        for key_max in subscripted_max_correlation_vector:
            key = format(key_max[0], word_format)
            max_correlation = str(key_max[1])
            file.write(key+','+max_correlation+'\n')

def cpa(candidate_key):
    poi_start = get_parameter("poi_start")
    poi_end = get_parameter("poi_end")

    wave_dir_name = get_parameter("wave_dir_name")
    wave_dir = os.path.join(os.getcwd(),wave_dir_name)
    slow_wave_matrix = get_waves(wave_dir)
    wave_matrix = np.array(slow_wave_matrix)[:,poi_start:poi_end].T

    plain_text_file_name = get_parameter("plain_text_file_name")
    plain_text_file = os.path.join(os.getcwd(),plain_text_file_name)
    plain_paragraph = get_plain_paragraph(plain_text_file)
    slow_plain_matrix = list(map(vector_transformed_by, plain_paragraph))
    plain_matrix = np.array(slow_plain_matrix)

    slow_key_vector = vector_transformed_by(candidate_key)[::-1]
    key_vector = np.array(slow_key_vector)

    slow_hamming_weight_matrix = calculate_unterluggauer_hamming_weight(plain_matrix,key_vector)
    unsafe_hamming_weight_matrix = np.array(slow_hamming_weight_matrix).T	#this have possibility of 0 div
    hamming_weight_matrix = change_0_to_randint_with(unsafe_hamming_weight_matrix)

    correlation_matrix = calculate_correlation(hamming_weight_matrix,wave_matrix)
    max_correlation_vector = list(map(lambda key_correlation_wave: np.amax(np.absolute(key_correlation_wave)), correlation_matrix))
    subscripted_max_correlation_vector = [(key, max_correlation) for key,max_correlation in enumerate(max_correlation_vector)]
    subscripted_max_correlation_vector.sort(key= lambda key_correlation: key_correlation[1],reverse=True)

    output_correlation(candidate_key, correlation_matrix)
    output_max_correlation(candidate_key, subscripted_max_correlation_vector)

def get_candidate_key_list(file_path):
    candidate_key_list = []
    with open(candidate_file) as file:
        for row in file:
            candidate_key = int(row.split(",")[0],16)
            candidate_key_list.append(candidate_key)
    return candidate_key_list

def get_result(candidate_key_list):
    output_dir_name = get_parameter("output_dir_name")
    output_dir_format = get_parameter("output_dir_format")
    result_file_name = get_parameter("result_file_name")
    target_word = get_parameter("target_word")
    word_length = get_parameter("word_length")
    output_dir = os.path.join(os.getcwd(),output_dir_name)

    result = []
    for candidate_key in candidate_key_list:
        key_dir = os.path.join(output_dir,format(candidate_key,output_dir_format))
        result_file = os.path.join(key_dir,result_file_name)
        with open(result_file) as file:
            for row in file:
                correlation = float(row.split(',')[1])
                key = int(row.split(',')[0],16)
                all_key = (key << target_word*word_length) | candidate_key
                result.append((all_key,correlation))
    return result

def output_final_result(result):
    output_dir_name = get_parameter("output_dir_name")
    output_dir = os.path.join(os.getcwd(),output_dir_name)
    final_result_file_name = get_parameter("final_result_file_name")
    final_result_file = os.path.join(output_dir, final_result_file_name)
    result.sort(key=lambda key_correlation: key_correlation[1],reverse=True)

    with open(result_file,'w') as file:
        for key_max in result:
            final_result_format = get_parameter("final_result_format")
            key = format(key_max[0], final_result_format)
            max_correlation = str(key_max[1])
            file.write(key+','+max_correlation+'\n')


def output_candidate_key_list(result):
    output_dir_name = get_parameter("output_dir_name")
    output_dir = os.path.join(os.getcwd(),output_dir_name)
    output_candidate_file_name = get_parameter("output_candidate_file_name")
    output_candidate_file = os.path.join(output_dir,output_candidate_file_name)
    result.sort(key=lambda key_correlation: key_correlation[1],reverse=True)
    k = get_parameter("k")
    candidate_list = result[:k]

    with open(output_candidate_file,'w') as file:
        for key_max in candidate_list:
            output_candidate_key_format = get_parameter("output_candidate_key_format")
            key = format(key_max[0], output_candidate_key_format)
            max_correlation = str(key_max[1])
            file.write(key+','+max_correlation+'\n')

if __name__ == '__main__':
    #out directory initialization
    output_dir_name = get_parameter("output_dir_name")
    output_dir = os.path.join(os.getcwd(),output_dir_name)
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
        input_candidate_file_name = get_parameter("input_candidate_file_name")
        candidate_file = os.path.join(output_dir,input_candidate_file_name)
        with open(candidate_file,"w") as file:
            file.write("00,0.0")

    input_candidate_file_name = get_parameter("input_candidate_file_name")
    candidate_file = os.path.join(output_dir,input_candidate_file_name)
    candidate_key_list = get_candidate_key_list(candidate_file)

    #pool = Pool(8)
    #pool.map(cpa, candidate_key_list)
    #pool.close()
    cpa(candidate_key_list[0])

    result = get_result(candidate_key_list)
    output_final_result(result)
    output_candidate_key_list(result)
