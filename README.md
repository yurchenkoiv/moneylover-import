# moneylower-import

- Used for import transactions from csv file to money lover account. 
- Working only with extracted JWT token
- Python 3.9+ required

##Usage
### Clone repository and cd to cloned folder:
````commandline
git clone && cd 
````
### Install requirements with:
````commandline
pip install -r requirements.txt
````

### Edit config
  * Set JWT token
    * Login to web app
    * Open developer tools
    * Find authorization header
    * Copy JWT token 
  * Create (edit) csv config
    * Set csv file info
    * Update mapping (If you don't know your categories ids, 
      run the import for the first time. Table with categories will be
      displayed in the console)
### Run
````commandline
python data_loader.py csv_config_path
````
* For example:
````commandline
python data_loader.py csv_config_1.yaml
````

* If loading is done on the regular basis 
  from different csvs, 
  could be created more than one csv config
  and then just specifiing this config in the 
  args, like: 
  ``````commandline
  python data_loader.py csv_config_1.yaml
  python data_loader.py csv_config_2.yaml
  python data_loader.py csv_config_3.yaml
  ``````