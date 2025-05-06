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
