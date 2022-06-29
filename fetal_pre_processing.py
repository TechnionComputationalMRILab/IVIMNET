# -*- coding: utf-8 -*-

import os
import numpy as np
import matplotlib.pyplot as plt
from utiles import read_data_sitk
from directories import *

if __name__ == "__main__":
    
    cases = os.path.join(DATA_DIRECTORY, "cases")
    segs = os.path.join(DATA_DIRECTORY, "segs")

    all_cases = True # if False take only minor motion cases

    bvalues = np.array([0,50,100,200,400,600])
    b_len = len(bvalues)

    # minor motion cases idx
    case_idx = np.array([647, 693, 697, 710, 756, 794, 798, 800, 801, 807,817,819, 828, 844, 856, 860,  877, 887])

    if (all_cases):
        num_cases = 39
    else:
        num_cases = len(case_idx)
    all_signals = []
    signals_mean = []

    for idx, filename in enumerate(os.listdir(cases)):
        if (not all_cases):
            if int(filename[4:7]) not in case_idx:
                continue
        case_path = (os.path.join(cases, filename))
        case = read_data_sitk(case_path)

        segmentation_path = os.path.join(segs, filename.replace("case", "seg"))
        seg = read_data_sitk(segmentation_path)

        slice_select = np.argwhere(seg!=0)
        slice_number = slice_select[0][0]
        mean_signal = np.zeros(b_len)
        for b_val_idx in range (b_len):
            sig = case[slice_number,:,:, b_val_idx]
            sig = sig[seg[slice_number,:,:]!=0]
            sig = sig.mean()
            mean_signal[b_val_idx] = sig
        signals_mean.append(mean_signal)

        plot = 0
        if(plot):
            plt.plot()
            plt.plot(np.arange(0,610,10), np.log(sig/sig[0]))
            plt.title("Ivim Model for case " + (filename.replace('case', '')).replace('.nii',''))
            plt.xlabel("b values")
            plt.ylabel("log(S/S0)")
            plt.legend()

        x_idx, y_idx = slice_select[:,1], slice_select[:,2]
        sx, sy, sb = case[slice_number,x_idx[0]:x_idx[-1]+1,y_idx[0] : y_idx[-1]+1,:].shape #len(set(x_idx)), len(set(y_idx)), b_len
        clinic_signal = case[slice_number,x_idx[0]:x_idx[-1]+1,y_idx[0] : y_idx[-1]+1,:]

        out_signal = clinic_signal.reshape(-1, sb) # list of pixels according to the image columns

        clinic_image = clinic_signal
        clinic_signal = out_signal
        all_signals.append(clinic_signal)

    signals_mean, all_signals_arr = np.stack(signals_mean, axis=0), np.vstack(all_signals)
    signals_mean = signals_mean[::-1,:]
    signals_mean_csv = np.asarray(signals_mean)

    np.savetxt(os.path.join(DATA_DIRECTORY, 'fetal', f'fetal_mean_signals_{num_cases}.csv'), signals_mean_csv, delimiter=",")
    np.savetxt(os.path.join(DATA_DIRECTORY, 'fetal', f'fetal_all_signals_{num_cases}.csv'), all_signals_arr, delimiter=",")
