# SIGMOD20
Runner-up solution for SIGMOD 2020 Programming Contest

Luca Zecchini, Giovanni Simonini, Sonia Bergamaschi: "Entity Resolution on Camera Records without Machine Learning". DI2KG @ VLDB 2020 (2nd International Workshop on Challenges and Experiences from Data Integration to Knowledge Graphs), CEUR Workshop Proceedings, vol. 2726, CEUR-WS.org (2020). http://ceur-ws.org/Vol-2726/paper3.pdf

---

This repository contains the solution conceived for SIGMOD 2020 Programming Contest [1], where I concluded as runner-up.
The task consisted in performing entity matching on a dataset of camera records extracted from 24 e-commerce websites.
The dataset is part of Alaska benchmark (see the repository [2] and the related paper [3] for more details).

---

REQUIREMENTS

The code is written in Python and needs to import pandas, json, os, re and time packages.

INPUT

The code takes in input just the json files contained in the camera dataset (available as the dataset "X" on the contest website).
A folder "Dataset" must be created here and it should directly contain the main folder of the camera dataset (namely, "2013_camera_specs") with all its content (i.e., the folders corresponding to the sources, containing the respective json files).

OUTPUT

The code generates the file "matches_from_solved.csv", that is the csv file containing the matches and used for the submissions.

EXECUTION

Just execute "code.py" file.
Once satisfied imports, it will read all specification json files, assign them brand and model and create the output files.

---

[1] SIGMOD 2020 Programming Contest Website: https://www.inf.uniroma3.it/db/sigmod2020contest
[2] Alaska Benchmark GitHub Repository: https://github.com/merialdo/research.alaska
[3] Valter Crescenzi, Andrea De Angelis, Donatella Firmani, Maurizio Mazzei, Paolo Merialdo, Federico Piai, Divesh Srivastava: "Alaska: A Flexible Benchmark for Data Integration Tasks". CoRR abs/2101.11259 (2021). https://arxiv.org/abs/2101.11259
