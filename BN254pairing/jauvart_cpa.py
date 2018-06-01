import random
import os
import numpy as np
from scipy.stats import pearsonr
from multiprocessing import Pool


#correct_key = 0x15eb62e02fbc3981f9cfed3c30c7f70c99189bed20001f2ac2a9f68e62b8da62

def set_parmeter():
    alpha_bits = 8
    mask = 0xffff
    return [alpha_bits,mask]

def cpa(alpha_key):
    T_Start = 0
    T_End = 5000
    T_Period = 1
    key_range = 0x100

    parmeter = set_parmeter()
    alpha_bits = parmeter[0]
    mask = parmeter[1]

    meta = os.listdir('wave_meta4')
    meta_path = os.path.join(os.getcwd(),'wave_meta4')
    files = os.listdir('wave')
    dir_path = os.path.join(os.getcwd(),'wave')
    out_dir = os.path.join(os.getcwd(),"jauvart_cpa_out")

    plain = []
    for file_name in meta:
        p = os.path.join(meta_path,file_name)
        data = 0
        with open(p) as file:
            data = int(file.read().split(",")[0],16) & mask
        plain.append(data)

    wave = []
    for file_name in files:
        data = []
        p = os.path.join(dir_path,file_name)
        with open(p) as file:
            all_data = file.read().split('\n')
            for i in range(T_Start,T_End,T_Period):
                data.append(int(all_data[i]))
        wave.append(data)
    wave = np.array(wave).T

    hw = []
    for i in range(len(plain)):
        keys = np.zeros(key_range)
        for key in range(len(keys)):
            all_key = (key << alpha_bits) | alpha_key
            keys[key] = bin((plain[i] * all_key) & mask).count('1')
        hw.append(keys)
    hw = np.array(hw).T

    for key in range(len(hw)):
        if hw[key].std() == 0:
            for i in range(len(hw[key])):
                hw[key][i] = random.randint(0, bin(mask).count('1'))

    corr = []
    corr_max = []
    for key in range(len(hw)):
        raw = []
        for t in range(len(wave)):
            r, p = pearsonr(hw[key], wave[t])
            raw.append(r)
        corr.append(raw)
        corr_max.append((key,np.amax(np.absolute(raw))))
    corr_max.sort(key=lambda x: x[1],reverse=True)

    key_dir = os.path.join(out_dir,hex(alpha_key))
    if not os.path.isdir(key_dir):
        os.mkdir(key_dir)
    for key in range(len(corr)):
        out = os.path.join(key_dir,hex(key))
        with open(out,'w') as file:
            for t in range(len(corr[key])):
                file.write(str(corr[key][t]) + '\n')
        out = os.path.join(key_dir,'meta.txt')
        with open(out, 'w') as file:
            for i in range(len(corr)):
                file.write(str(i+1)+','+hex(corr_max[i][0])+','+str(corr_max[i][1]) + '\n')


if __name__ == '__main__':
    alpha_out = 16
    alpha_bits = set_parmeter()[0]
    alpha_in_file = "alpha" + str(alpha_bits) + ".txt"

    out_dir = os.path.join(os.getcwd(),"jauvart_cpa_out")
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
    
    pool = Pool(8)
    pool.map(cpa, alpha_keys)
    pool.close()

    alpha_top = []
    for alpha_key in alpha_keys:
        key_dir = os.path.join(out_dir,hex(alpha_key))
        meta_file = os.path.join(key_dir,"meta.txt")
        with open(meta_file) as file:
            for raw in file.read().split():
                key = (int(raw.split(',')[1],16) << alpha_bits) | alpha_key
                r = float(raw.split(',')[2])
                alpha_top.append((key,r))
    alpha_top.sort(key=lambda x: x[1],reverse=True)


    alpha_out_file = "alpha" + str(alpha_bits + 8) + ".txt"
    p = os.path.join(out_dir, alpha_out_file)
    with open(p,"w") as file:
        for i in range(alpha_out):
            file.write(str(i+1)+','+hex(alpha_top[i][0])+','+str(alpha_top[i][1]) + '\n')