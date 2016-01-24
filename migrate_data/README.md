1. dump data from source database

    ./migrate_data/dump_data.py production-2T2015

1. insert data from json files, adjusting pk's

    source .virtualenv/bin/activate
    ./migrate_data/load_data.py production-2T2015 development
