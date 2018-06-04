from multiprocessing import cpu_count

def get_parameter(request):
    parameter = {}
    #experiment_parameter
    parameter["target_word"] = 1
    parameter["poi_start"] = 1480
    parameter["poi_end"] = 1530
    parameter["word_length"] = 16
    parameter["modulo"] = 0x10000
    parameter["k"] = 16
    parameter["candidate_key_length"] = parameter["target_word"]*parameter["word_length"]
    parameter["result_key_length"] = parameter["candidate_key_length"] + parameter["word_length"]
    parameter["parallel"] = False

    #file_parameter
    parameter["wave_dir_name"] = 'wave'
    parameter["plain_text_file_name"] = 'plain_cipher.txt'
    parameter["result_file_name"] = 'result.txt'
    parameter["output_dir_name"] = 'unterluggauer_cpa_out'
    parameter["final_result_file_name"] = str(parameter["result_key_length"]) + 'bit_result.txt'
    parameter["candidate_file_name"] = str(parameter["candidate_key_length"]) + 'bit_candidate.txt'
    parameter["output_candidate_file_name"] = str(parameter["result_key_length"]) + 'bit_candidate.txt'

    #format_paramater
    target_word = parameter["target_word"]
    word_length = parameter["word_length"]
    candidate_key_length = parameter["candidate_key_length"]
    digit_length = word_length/4

    word_format = '0' + str(int(digit_length)) + 'x'
    parameter["word_format"] = word_format

    estimation_key_format = '0' + str(int(digit_length)) + 'x'
    parameter["estimation_key_format"] = estimation_key_format

    candidate_key_digit = candidate_key_length/4 if candidate_key_length != 0 else word_length/4
    candidate_key_format = '0' + str(int(candidate_key_digit)) + 'x'
    parameter["candidate_key_format"] = candidate_key_format

    parameter["result_key_format"] = '0' + str(int(parameter["result_key_length"]/4))+ 'x'

    return parameter[request]