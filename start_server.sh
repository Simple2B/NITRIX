#!/bin/bash
echo !!!!run db upgrade!!!!
poetry run flask db upgrade
echo !!!!start server!!!!
poetry run flask run -h 0.0.0.0
