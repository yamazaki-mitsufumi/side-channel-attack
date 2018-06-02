def get_parameter(request):
    parameter = {}

    #experiment parameter
    parameter["candidate_key_length"] = 0
    parameter["poi_start"] = 0
    parameter["poi_end"] = 10
    parameter["key_range"] = 0x100
    parameter["estimation_key_length"] = 8
    parameter["alpha"] = 16

    #file parameter
    parameter["wave_dir_name"] = "wave"
    parameter["plain_text_file_name"] = "plain_cipher.txt"
    parameter["output_dir_name"] = "jauvart_cpa_out"
    parameter["result_file_name"] = "result.txt"

    #dependent on parameter
    candidate_key_length = parameter["candidate_key_length"]
    estimation_key_length = parameter["estimation_key_length"]
    result_key_length = candidate_key_length + estimation_key_length
    parameter["result_key_length"] = result_key_length

    modulo = 2**(result_key_length)
    parameter["modulo"] = modulo

    digit = candidate_key_length/4 if candidate_key_length != 0 else estimation_key_length/4
    candidate_key_format = '0' + str(int(digit)) + 'x'
    parameter["candidate_key_format"] = candidate_key_format

    digit = estimation_key_length/4
    estimation_key_format = '0' + str(int(digit)) + 'x'
    parameter["estimation_key_format"] = estimation_key_format

    digit = result_key_length/4
    result_key_format = '0' + str(int(digit)) + 'x'
    parameter["result_key_format"] = result_key_format

    candidate_file_name = str(candidate_key_length) + 'bit_candidate.txt'
    parameter["candidate_file_name"] = candidate_file_name

    final_result_file_name = str(result_key_length) + 'bit_result.txt'
    parameter["final_result_file_name"] = final_result_file_name

    output_candidate_file_name = str(result_key_length) + 'bit_candidate.txt'
    parameter["output_candidate_file_name"] = output_candidate_file_name

    return parameter[request]