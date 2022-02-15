# SIGMOD20
Runner-up solution for SIGMOD 2020 Programming Contest

Luca Zecchini, Giovanni Simonini, Sonia Bergamaschi: Entity Resolution on Camera Records without Machine Learning. DI2KG @ VLDB 2020 (2nd International Workshop on Challenges and Experiences from Data Integration to Knowledge Graphs), CEUR Workshop Proceedings, vol. 2726, CEUR-WS.org (2020). http://ceur-ws.org/Vol-2726/paper3.pdf

---

This repository contains the solution conceived for SIGMOD 2020 Programming Contest [1], where I concluded as runner-up.
The task consisted in performing entity matching on camera records extracted from 24 e-commerce websites.

---

REQUIREMENTS
The code needs to import pandas, json, os, re and time packages.

INPUT
The code takes in input just the json files contained in dataset X (available on contest website).
The empty folder Dataset/2013_camera_specs/ must be filled with the source folders of this dataset (buy.net, cammarkt.com, www.alibaba.com and so on) containing the respective json files.

OUTPUT
The code generates the file matches_from_solved.csv, that is the csv C containing the matches and used for the submissions.

EXECUTION
Just execute code.py file.
Once satisfied imports, it will read all the specifications json files, assign them brand and model and create the output files.

---

[1] SIGMOD 2020 Programming Contest Website: https://www.inf.uniroma3.it/db/sigmod2020contest/
