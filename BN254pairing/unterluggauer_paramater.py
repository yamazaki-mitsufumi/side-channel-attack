def get_parameter(request):
    parameter = {}
    #experiment_parameter
    parameter["target_word"] = 0
    parameter["poi_start"] = 1480
    parameter["poi_end"] = 1530
    parameter["word_length"] = 16
    parameter["modulo"] = 0x10000
    parameter["k"] = 16

    #file_parameter
    parameter["wave_dir_name"] = 'wave'
    parameter["plain_text_file_name"] = 'plain_cipher.txt'
    parameter["result_file_name"] = 'result.txt'
    parameter["output_dir_name"] = 'unterluggauer_cpa_out'
    parameter["word_format"] = '02x'

    #format_paramater
    target_word = parameter["target_word"]
    word_length = parameter["word_length"]
    digit_length = word_length/4

    word_format = '0' + str(int(digit_length))+ 'x'
    parameter["word_format"] = word_format

    output_candidate_key_length = digit_length*(target_word+1)
    output_candidate_key_format = '0' + str(int(output_candidate_key_length)) + 'x'
    parameter["output_candidate_key_format"] = output_candidate_key_format

    output_dir_length = digit_length*target_word if target_word != 0 else digit_length
    output_dir_format = '0' + str(int(output_dir_length)) + 'x'
    parameter["output_dir_format"] = output_dir_format

    final_result_length = digit_length*(target_word+1)
    final_result_format = '0' + str(int(final_result_length)) + 'x'
    parameter["final_result_format"] = final_result_format

    input_candidate_file_name = 'candidate_on_aiming_'+str(target_word)+'word.txt'
    parameter["input_candidate_file_name"] = input_candidate_file_name

    output_candidate_file_name = 'candidate_on_aiming_'+str(target_word+1)+'word.txt'
    parameter["output_candidate_file_name"] = output_candidate_file_name

    final_result_file_name = 'result_of_aiming_' + str(target_word) + '.txt'
    parameter["final_result_file_name"] = final_result_file_name

    return parameter[request]