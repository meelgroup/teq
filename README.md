# Teq, a closeness testing algorithm for probabilistic circuits.

Teq is an algorithm developed to test whether two PCs (in NNF) are close in total variation(TV) distance. It uses WAPS as the underlying sampler. This work is by Yash Pote and Kuldeep S. Meel, as published in [NeurIPS'21](https://meelgroup.github.io/files/publications/NeurIPS21_PCtest.pdf).

## Requirements to run the code

* Python 3+
 
To install the required libraries, run:

```
pip install -r requirements.txt
```

## Getting Started

To run the closeness test with the benchmarks used in the paper:
 
```
python teq.py --eta 0.9 --epsilon 0.86 --delta 0.01 --seed 42 --weightfunction tests/wts/3_a.wt tests/wts/3_b.wt --circuit tests/14a.cnf tests/14b.cnf
```

The above command will test whether the two PCs (14a.cnf,3_a.wt) and  (14b.cnf,3_b.wt) are closer than 0.86 or further than 0.9 in TV distance.
The TV distance between the two PCs as calculated using brute-force techniques is 0.852, hence the test is expected to output Accept.


For the command-

```
python teq.py --eta ETA --epsilon EPSILON --delta DELTA --seed SEED --weightfunction file1.wt file2.wt --circuit file1.nnf file2.nnf
```

ETA takes values in (0,1),
EPSILON takes values in (0,1),
DELTA takes values in (0,1), and
SEED takes integer values,


## How to Cite

If you use Teq, please cite the following paper : [NeurIPS'21](https://meelgroup.github.io/files/publications/NeurIPS21_PCtest.pdf). Here is the [BIB file](https://www.comp.nus.edu.sg/~meel/bib/PM21.bib)
