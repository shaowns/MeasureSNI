# MeasureSNI
To run:
```shell
python process_url_sni_info.py -f "name_of_url_file" -s no_of_ranks_to_skip
```
# To import the sql file into MySQL
Download the compressed sql from [here](https://goo.gl/nOXXwA). The file is stored in google drive due to Github's large file handling limitations.

To import the file into your database, do the following:

`$ gunzip < measureSNI.sql.gz | mysql -u [username] -p measureSNI`

Make sure mysql server is running on port 3306 (default). You will be asked for the password of the user you used. Database `measureSNI` must exist.

# To export the sql from MySQL
After you make your changes, to generate this same file again.

`$ mysqldump -u [username] -p --triggers=true --routines=true measureSNI|gzip > measureSNI.sql.gz`

Make note of the `--triggers` and `--routines` swithces. Without these the triggers and stored procedures may not be exported correctly. You will be asked for the password of the user you used.
