import random
import os
import numpy as np
from scipy.stats import pearsonr
from multiprocessing import Pool


#correct_key = 0x15eb62e02fbc3981f9cfed3c30c7f70c99189bed20001f2ac2a9f68e62b8da62

def set_parmeter():
    known_words = 0
    word_bits = 8
    return [known_words,word_bits]

def cpa(alpha_key):
    T_Start = 0
    T_End = 5000
    T_Period = 1
    key_range = 0x100
    mask = 0xff

    known_words = set_parmeter()[0]
    word_bits = set_parmeter()[1]

    plain_cipher = os.path.join(os.getcwd(),'data/plain_cipher4.txt')
    files = os.listdir('data/wave4')
    dir_path = os.path.join(os.getcwd(),'data/wave4')
    out_dir = os.path.join(os.getcwd(),"out")

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

    plain = []
    with open(plain_cipher) as file:
        for raw in file:
            data = []
            plain_data = int(raw.split(',')[0],16)
            for i in range(known_words + 1):
                data.append((plain_data >> i*word_bits) & mask)
            plain.append(data)

    known_key = []
    for i in range(known_words):
        known_key.append((alpha_key >> i*word_bits) & mask)
    for i in range(len(known_key)):
        known_key_vector.append(np.array(known_key[0:(i+1)])[::-1])
    key_vector = np.append(known_key,0)[::-1]

    hw = []
    for i in range(len(plain)):
        value = 0
        for j in range(len(known_key)):
            plain_vector = np.array(plain[i][0:(j+1)])
            value = value + np.dot(plain_vector,known_key_vector[j]) >> (known_words+1-j)*word_bits
        keys = np.zeros(key_range)
        plain_vector = np.array(plain[i])
        for key in range(len(keys)):
            key_vector[0] = key
            value = int( value + np.dot(plain_vector,key_vector) ) & mask
            keys[key] = bin(value).count('1')
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
    known_words = set_parmeter()[0]
    word_bits = set_parmeter()[1]
    alpha_in_file = "alpha" + str(known_words*word_bits) + ".txt"

    out_dir = os.path.join(os.getcwd(),"out")
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
        alpha_file_path = os.path.join(out_dir,alpha_in_file)
        with open(alpha_file_path,"w") as f:
            f.write("0,0x0,0.0")

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
        key_dir = os.path.join(out_dir,hex(alpha_key))
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
