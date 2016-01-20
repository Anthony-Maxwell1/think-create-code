
1. dump data from source database

    PYTHONPATH=.:$PYTHONPATH ./migrate_data/dump_data.py production-2T2015

1. insert data from json files, adjusting pk's

    PYTHONPATH=.:$PYTHONPATH ./migrate_data/load_data.py production-2T2015 development

    
