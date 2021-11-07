import waps
import math
import random
import argparse
import sys
from gmpy2 import mpq
from fractions import Fraction

def assignment_to_weight(assignment, weightfunction):
    weight = 1.0
    for i in assignment:
        if i > 0:
            weight *= weightfunction[abs(i)]
        else:
            weight *= 1.0 - weightfunction[abs(i)]
    return weight


def weight_file_to_dict(weightfunctions):
    #if there is only one weight function we annotate both circuits with it
    if len(weightfunctions) == 1:
        weightfunctions.append(weightfunctions[0])
    w1= waps.fetchWeights(weightfunctions[0])
    w2= waps.fetchWeights(weightfunctions[1])
    return w1, w2


def generate_samples_and_counts(circuits, w1, w2, N=0):

    nnf_1, nnf_2 = [], []
    sampling_set = list(w1)
    if len(circuits) == 1:
        if circuits[0][-4:] == ".cnf":
            nnf_1 = waps.sampler(cnfFile=circuits[0])
            nnf_2 = waps.sampler(cnfFile=circuits[0])
            nnf_1.compile()
            nnf_2.compile()
        elif circuits[0][-4:] == ".nnf":
            nnf_1 = waps.sampler(dDNNFfile=circuits[0], samplingSet= sampling_set)
            nnf_2 = waps.sampler(dDNNFfile=circuits[0], samplingSet= sampling_set)
        else:
            print("Input circuit file is in incorrect format.")
            sys.exit(1)

    else: # the case where there are two circuits
        if circuits[0][-4:] == ".cnf":
            nnf_1 = waps.sampler(cnfFile=circuits[0])
            nnf_1.compile()
        elif circuits[0][-4:] == ".nnf":
            nnf_1 = waps.sampler(dDNNFfile=circuits[0], samplingSet= sampling_set)
        else:
            print("Input circuit file is in incorrect format.")
            sys.exit(1)

        if circuits[1][-4:] == ".cnf":
            nnf_2 = waps.sampler(cnfFile=circuits[1])
            nnf_2.compile()
        elif circuits[1][-4:] == ".nnf":
            nnf_2 = waps.sampler(dDNNFfile=circuits[1], samplingSet= sampling_set)
        else:
            print("Input circuit file is in incorrect format.")
            sys.exit(1)

    nnf_1.parse()
    nnf_2.parse()
    
    wCT1 = nnf_1.annotate(weights= w1)
    wCT2 = nnf_2.annotate(weights= w2)
    
    if N > 0:
        samples = nnf_1.sample(totalSamples=N, sampling_set=sampling_set)
        solList = list(samples)
        solList = [i.strip().split() for i in solList]
        solList = [[int(x) for x in i] for i in solList]

        assert(len(solList) == N)
        return solList, wCT1, wCT2

    else:
        return wCT1, wCT2

def number_of_samples(epsilon, eta, delta):
    gamma = (eta - epsilon)/2
    return int(math.ceil(math.log(2/delta)/(2*gamma**2)))

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--outputfile", type=str, default="samples_full.txt", help="output file for samples", dest='outputfile')
    parser.add_argument("--tolerant", type=int, default=1, help="1= Tolerant 0=exact", dest='tolerant')
    parser.add_argument("--epsilon", type=float, default=0.01, help="closeness parameter", dest='epsilon')
    parser.add_argument("--eta", type=float, default=0.2, help="farness parameter", dest="eta")
    parser.add_argument("--delta", type=float, default=0.01, help="error parameter", dest="delta")
    parser.add_argument("--seed", type=int, default=42, help="random seed", dest="seed")
    parser.add_argument("--circuit", nargs='+', type=str, default="", help='input cnf file(s)')
    parser.add_argument("--weightfunction", nargs='+', type=str, default="", help='input weightfunction file(s)')

    args = parser.parse_args()
    seed = args.seed
    eta,epsilon,delta = args.eta, args.epsilon, args.delta
    
    if len(args.circuit) == len(args.weightfunction) == 1:
        print("Only one file and one weightfunction given as input.")
        sys.exit(1)

    if len(args.circuit) > 2 or len(args.weightfunction) > 2:
        print("More than 2 files and/or weightfunctions given as input.")
        sys.exit(1)

    wt1, wt2 = weight_file_to_dict(args.weightfunction)

    if set(wt1.keys()) != set(wt2.keys()):
        print("Support is not same")
        print("Reject")

    elif args.tolerant == 1:
        N = number_of_samples(epsilon, eta, delta)
        print("Number of samples required to test tolerant closeness = ", N)
        gamma = (eta-epsilon)/2
        sample_list, wCT1, wCT2 = generate_samples_and_counts(args.circuit, wt1, wt2, N)
        print("Weighted Count of circuit 1 and 2", float(wCT1), float(wCT2))
        estimate = 0.0
        for i in sample_list:
            s1, s2 = assignment_to_weight(i, wt1), assignment_to_weight(i, wt2)
        #    print(s1, s2)
            r = (s2*wCT1)/(s1*wCT2)
            if r<1:
                estimate += 1.0 - r

        threshold = N*(epsilon+gamma)

        print("Thresold: ", threshold/N)
        print("Estimate: ", estimate/N)

        if estimate <= threshold:
            print("Accept")
        else:
            print("Reject")

    else:
        num_var_1 = 0
        num_var_2 = 0
        with open(args.circuit[0]) as f1:
            num_var_1 = int(f1.readline().strip().split()[3])
        with open(args.circuit[1]) as f2:
            num_var_2 = int(f2.readline().strip().split()[3])

        if num_var_1!=num_var_2:
            print("Not defined over same set of variables")
            print("Reject")
            sys.exit(0)

        #sampling_list = list(wt1)
        sampling_list = [i for i in range(1,num_var_1+1,1)]

        m = math.ceil(len(sampling_list)/delta)
        new_wt1, new_wt2 ={}, {}

        for i in wt1:
            S = mpq(random.randint(1,m))
            old_val_1 = mpq(wt1[i])
            old_val_2 = mpq(wt2[i])
            one = mpq(1)

            new_wt1[i]  = old_val_1*S
            new_wt1[-i] = (one-old_val_1)*(one-S)
            new_wt2[i]  = old_val_2*S
            new_wt2[-i] = (one-old_val_2)*(one-S)

        for i in sampling_list:
            if i not in wt1:
                S = mpq(random.randint(1,m))
                new_wt1[i]  = old_val_1*S
                new_wt1[-i] = (one-old_val_1)*(one-S)
                new_wt2[i]  = old_val_2*S
                new_wt2[-i] = (one-old_val_2)*(one-S)


        wCT1, wCT2 = generate_samples_and_counts(args.circuit, wt1, wt2)
        new_wCT1, new_wCT2 = generate_samples_and_counts(args.circuit, new_wt1, new_wt2)
        print(float(new_wCT1 - new_wCT2))

        if new_wCT1/wCT1 == new_wCT2/wCT2:
            print("Accept")
        else:
            print("Reject")

if __name__== "__main__":
    main()
