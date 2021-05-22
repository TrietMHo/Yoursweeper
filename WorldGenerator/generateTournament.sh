#!/bin/bash

rm -rf Problems
mkdir Problems
 
python WorldGenerator.py 1000 Beginner_world_ 8 8 10

python WorldGenerator.py 1000 Intermediate_world_ 16 16 40

python WorldGenerator.py 1000 Expert_world_ 16 30 99

echo Finished generating worlds!
