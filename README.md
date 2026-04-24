# dls-datagateway-scripts
Collection of utility scripts for Diamond DataGateway users.

## queue_file_downloads
Submits DataGateway Download requests for a list of specific filepaths. A minimal example can be run with:
```bash
python3 queue_file_downloads.py input-file.txt --username=abc12345
```

Full help text and description of arguments is available with the `--help` command:
```bash
python3 queue_file_downloads.py input-file.txt --help
```
```
usage: queue_file_downloads [-h] [--url URL] [-a AUTHENTICATOR] -u USERNAME
                            [-p PASSWORD_FILE] [--download-name DOWNLOAD_NAME]
                            [--access-method {https,globus,dls}]
                            [--email-address EMAIL_ADDRESS]
                            [-m MONITOR_INTERVAL]
                            input_file

Submits DataGateway Download requests for a list of specific filepaths. The
list will be split into separate parts of up to 10,000 files for performance
reasons and held in a queue until system load is low enough to process the
request. Once submitted Downloads can be monitored by the script by using the
--monitor-interval argument. Downloads will also be visible in the DataGateway
UI as usual, and notifications sent to the provided --email-address.

positional arguments:
  input_file            File containing the full paths of all files to submit
                        for download, separated by newlines. The path should
                        match the 'location' field displayed in the
                        DataGateway UI.

options:
  -h, --help            show this help message and exit
  --url URL             The url address of the DataGateway instance to submit
                        requests to.
  -a AUTHENTICATOR, --authenticator AUTHENTICATOR
                        The authentication mechanism to use for DataGateway
                        login.
  -u USERNAME, --username USERNAME
                        The username used for DataGateway login.
  -p PASSWORD_FILE, --password-file PASSWORD_FILE
                        Location of file containing password for DataGateway
                        login. If not provided, the password will need to be
                        provided by prompt.
  --download-name DOWNLOAD_NAME
                        Custom file name/identifier for the download(s). If
                        not set will default to the current date and time.
                        '_part_N' will be appended to the each part Download
                        of up to 10,000 files.
  --access-method {https,globus,dls}
                        The choice of access method for the data. https:
                        download files via your browser. globus: download the
                        data to Globus Online. dls: restore to the DLS file
                        system. Data will be available in one of the following
                        directory structures:
                        /dls/staging/dls/$instrument/data/$year/$visit or
                        /dls/staging/dls/$village/data/$proposal/$visit. Users
                        will have 15 days to process and transfer their data.
                        After that period, data will be deleted from DLS
                        filesystem.
  --email-address EMAIL_ADDRESS
                        Optional address to email status messages to.
  -m MONITOR_INTERVAL, --monitor-interval MONITOR_INTERVAL
                        Monitor the submitted downloads to see if they are
                        complete with an interval of this many minutes. Non-
                        positive values will disable monitoring.
```

## search_files

Performs DataGateway searches for Datafiles matching the provided query.
```bash
python3 search_files.py input-file.txt 'visitId:"AB1234-1"' --username=abc12345
```

Full help text and description of arguments is available with the `--help` command:
```bash
python3 search_files.py --help
```
```
usage: search_files [-h] [--url URL] [-a AUTHENTICATOR] -u USERNAME
                    [-p PASSWORD_FILE] [-m MAX_RESULTS]
                    output_file query

Performs DataGateway searches for Datafiles matching the provided query. These paths will be written to file in
batches, and can then be inspected and filtered further if needed before submitting using queue_file_downloads.

positional arguments:
  output_file           File to append newline separated paths to.
                        This can then be provided as an input to queue_file_downloads.
  query                 Lucene syntax formatted search query. Full help text and examples can be found
                        in the DataGateway UI. Note that wildcards can significantly increase the time
                        taken to perform a search, and the more specific the search query is the more
                        efficient it will be. Some example searches are:
                            'visitId:AB1234'
                                Search for all Datafiles in all parts of proposal
                            'visitId:"AB1234-1"'
                                Search for all Datafiles in a (part) visit
                            'location.fileName:"config.txt"'
                                Search for Datafiles with a specific file name and extension (both required)
                            'location.fileName:config'
                                Search for Datafiles with a specific name but any extension
                            'location.fileName:txt'
                                Search for Datafiles with the extension 'txt', but no requirement on the name
                            'location:raw'
                                Search for Datafiles with the directory 'raw' somewhere in their path
                            'location:(raw processed)'
                                Search for Datafiles with either of two directories somewhere in their path
                            'location.exact:/dls/i0/data/2000'
                                Search for Datafiles in any subdirectory of the provided path (case sensitive)
                            'location.exact:/dls/i0/data/202?/*/raw/config.txt'
                                Search for a full path with wildcards (case sensitive)
                            '+location.exact:/dls/i0/data/202? +location:(raw processed) +location.fileName:txt'
                                Search for multiple criteria (all of which are required to match)

optional arguments:
  -h, --help            show this help message and exit
  --url URL             The url address of the DataGateway instance to submit requests to.
  -a AUTHENTICATOR, --authenticator AUTHENTICATOR
                        The authentication mechanism to use for DataGateway login.
  -u USERNAME, --username USERNAME
                        The username used for DataGateway login.
  -p PASSWORD_FILE, --password-file PASSWORD_FILE
                        Location of file containing password for DataGateway login. If not provided, the password will need to be provided by prompt.
  -m MAX_RESULTS, --max-results MAX_RESULTS
                        The maximum number of results to request in a single batch. If unset, the server default value will be used.
```

## get_size

Queries for the total volume of the requested entity(ies).
```bash
python3 get_size.py --username=abc12345 files input-file.txt
python3 get_size.py --username=abc12345 visit 'ab1234-1'
```

Full help text and description of arguments is available with the `--help` command:
```bash
python3 get_size.py --help
```
```
usage: get_size [-h] [--url URL] [-a AUTHENTICATOR] -u USERNAME
                [-p PASSWORD_FILE]
                {visit,files} ...

Queries DataGateway Download API for the volume of all Datafiles within a
visit or a list of specific filepaths.

positional arguments:
  {visit,files}         Target for query.

optional arguments:
  -h, --help            show this help message and exit
  --url URL             The url address of the DataGateway instance to submit
                        requests to.
  -a AUTHENTICATOR, --authenticator AUTHENTICATOR
                        The authentication mechanism to use for DataGateway
                        login.
  -u USERNAME, --username USERNAME
                        The username used for DataGateway login.
  -p PASSWORD_FILE, --password-file PASSWORD_FILE
                        Location of file containing password for DataGateway
                        login. If not provided, the password will need to be
                        provided by prompt.
```
```bash
python3 get_size.py files --help
```
```
usage: get_size files [-h] input_file

positional arguments:
  input_file  File containing the full paths of all files to query for size,
              separated by newlines. The path should match the 'location'
              field displayed in the DataGateway UI.

optional arguments:
  -h, --help  show this help message and exit
```
```bash
python3 get_size.py visit --help
```
```
usage: get_size visit [-h] visit_id

positional arguments:
  visit_id    Visit id in the form AB1234-1.

optional arguments:
  -h, --help  show this help message and exit
```
