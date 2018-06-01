import os, sys
from multiprocessing import Pool, cpu_count

pardir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pardir)
from unterluggauer_paramater import get_parameter
from unterluggauer_cpa import get_candidate_key_list, cpa, get_result, output_final_result, output_candidate_key_list

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

    pool = Pool(cpu_count())
    pool.map(cpa, candidate_key_list)
    pool.close()

    result = get_result(candidate_key_list)
    output_final_result(result)
    output_candidate_key_list(result)