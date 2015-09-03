#!/bin/bash
python manage.py loaddata /conrec/fixtures/conrec.json
python manage.py runserver 8989
