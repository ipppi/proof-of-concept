# IPPPI Proof-of-Concept

InterPlanetary Python Package Index is an attempt to build a resilient
and reproducible package index for the Python programming language,
where packages are regulated by human beings (as well as automated checks)
against malicious intentions and dependency conflicts.

This repository contains the proof-of-concept for the analysis and design
available at [ipppi.github.io].

## Prerequisites

* PostgreSQL with authentication `postgres`:`postgres`
* IPFS >= 0.7
* tox >= 3.3

## Installation and Usage

    git clone https://github.com/ipppi/proof-of-concept ipppi
    cd ipppi
    tox

[ipppi.github.io]: https://ipppi.github.io
