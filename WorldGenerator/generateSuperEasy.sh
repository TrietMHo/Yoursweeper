#!/bin/bash

rm -rf Problems
mkdir Problems

python WorldGenerator.py 1000 Easy_world_ 5 5 1

echo Finished generating worlds!
