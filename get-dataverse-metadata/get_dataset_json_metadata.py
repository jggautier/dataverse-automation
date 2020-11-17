# Python script for downloading the Dataverse JSON metadata files of given list of datasets PIDs
# and the repository's metadatablock JSON

import csv
from csv import DictReader
import json
import os
from pathlib import Path
import requests
import time
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

# Create GUI for getting user input
window = Tk()
window.title('Get dataset metadata')
window.geometry('650x500')  # width x height

# Create label for Dataverse repository URL
labelRepositoryURL = Label(window, text='Enter Dataverse repository URL:', anchor='w')
labelRepositoryURL.grid(sticky='w', column=0, row=0)

# Create Dataverse repository URL text box
repositoryURL = str()
entryRepositoryURL = Entry(window, width=50, textvariable=repositoryURL)
entryRepositoryURL.grid(sticky='w', column=0, row=1, pady=2)

# Create help text for server name field
labelDataverseUrlHelpText = Label(window, text='Example: https://demo.dataverse.org/', foreground='grey', anchor='w')
labelDataverseUrlHelpText.grid(sticky='w', column=0, row=2)

# Create empty row in grid to improve spacing between the two fields
window.grid_rowconfigure(3, minsize=25)

# Create label for API key field
labelApikey = Label(window, text='API key:', anchor='w')
labelApikey.grid(sticky='w', column=0, row=4)

# Create API key field
apikey = str()
entryApikey = Entry(window, width=50, textvariable=apikey)
entryApikey.grid(sticky='w', column=0, row=5, pady=2)

# Create help text for API key field
labelApikeyHelpText = Label(window, text='If no API is entered, only published datasets will be found', foreground='grey', anchor='w')
labelApikeyHelpText.grid(sticky='w', column=0, row=6)

# Create empty row in grid to improve spacing between the two fields
window.grid_rowconfigure(7, minsize=25)

# Create label for Browse directory button
labelBrowseForFile = Label(window, text='Choose CSV or TXT file contain list of dataset PIDs:', anchor='w')
labelBrowseForFile.grid(sticky='w', column=0, row=8, pady=2)

# Create Browse directory button
buttonBrowseForFile = ttk.Button(window, text='Browse', command=lambda: retrieve_file())
buttonBrowseForFile.grid(sticky='w', column=0, row=9)

# Create empty row in grid to improve spacing between the two fields
window.grid_rowconfigure(11, minsize=25)

# Create label for Browse directory button
labelBrowseDirectory = Label(window, text='Choose folder to put the metadata files and metadatablock files folders into:', anchor='w')
labelBrowseDirectory.grid(sticky='w', column=0, row=12, pady=2)

# Create Browse directory button
buttonBrowseDirectory = ttk.Button(window, text='Browse', command=lambda: retrieve_directory())
buttonBrowseDirectory.grid(sticky='w', column=0, row=13)

# Create start button
buttonSubmit = ttk.Button(window, text='Start', command=lambda: retrieve_input())
buttonSubmit.grid(sticky='w', column=0, row=15, pady=40)


# Function called when Browse button is pressed for choosing text file with dataset PIDs
def retrieve_file():
    global datasetPIDFile

    # Call the OS's file directory window and store selected object path as a global variable
    datasetPIDFile = filedialog.askopenfilename(filetypes=[('Text files', '*.txt'), ('CSV files', '*.csv')])

    # Show user which file she chose
    labelShowChosenFile = Label(window, text='You chose: ' + datasetPIDFile, anchor='w', foreground='green', wraplength=500, justify='left')
    labelShowChosenFile.grid(sticky='w', column=0, row=10)


# Function called when Browse button is pressed
def retrieve_directory():
    global metadataFileDirectory

    # Call the OS's file directory window and store selected object path as a global variable
    metadataFileDirectory = filedialog.askdirectory()

    # Show user which directory she chose
    labelShowChosenDirectory = Label(
        window,
        text='You chose: ' + metadataFileDirectory,
        anchor='w', foreground='green',
        wraplength=500, justify='left'
    )
    labelShowChosenDirectory.grid(sticky='w', column=0, row=14)


# Function called when Start button is pressed
def retrieve_input():
    global repositoryURL
    global apikey

    # Store what's entered in dataverseUrl text box as a global variable
    repositoryURL = entryRepositoryURL.get()

    # Store what's entered in the API key text box as a global variable
    apikey = entryApikey.get()

    window.destroy()


# Keep window open until it's closed
mainloop()


def improved_get(_dict, path, default=None):
    for key in path.split('.'):
        try:
            _dict = _dict[key]
        except KeyError:
            return default
    return str(_dict)


# Save current time to append it to main folder name
currentTime = time.strftime('%Y.%m.%d_%H.%M.%S')

# Use the "Get Version" endpoint to get repository's Dataverse version (or set version as 'NA')
getInstallationVersionApiUrl = '%s/api/v1/info/version' % (repositoryURL)
response = requests.get(getInstallationVersionApiUrl)
getInstallationVersionApiData = response.json()
dataverseVersion = getInstallationVersionApiData['data']['version']
dataverseVersion = str(dataverseVersion.lstrip('v'))

# Create main directory name with current time
metadataFileDirectoryPath = str(Path(metadataFileDirectory)) + '/' + 'JSON_metadata_%s' % (currentTime)

# Create name for metadatablock files directory in main directory
# metadatablockFileDirectoryPath = str(Path(metadataFileDirectory)) + '/' + 'metadatablocks_v%s' % (dataverseVersion)

# Create dataset metadata and metadatablock directories
os.mkdir(metadataFileDirectoryPath)
# os.mkdir(metadatablockFileDirectoryPath)

# # Download metadatablock JSON files
# # Get list of the repository's metadatablock names
# metadatablocksApi = '%s/api/v1/metadatablocks' % (repositoryURL)
# metadatablocksApi = metadatablocksApi.replace('//api', '/api')

# response = requests.get(metadatablocksApi)
# data = response.json()

# metadatablockNames = []
# for i in data['data']:
#     name = i['name']
#     metadatablockNames.append(name)

# print('Downloading %s metadatablock JSON file(s) into metadatablocks folder:' % ((len(metadatablockNames))))

# for metadatablockName in metadatablockNames:
#     metadatablockApi = '%s/%s' % (metadatablocksApi, metadatablockName)
#     response = requests.get(metadatablockApi)

#     metadatablockFile = str(Path(metadatablockFileDirectoryPath)) + '/' '%s_v%s.json' % (metadatablockName, dataverseVersion)

#     with open(metadatablockFile, mode='w') as f:
#         f.write(json.dumps(response.json(), indent=4))

#     sys.stdout.write('.')
#     sys.stdout.flush()

# print('\nFinished downloading %s metadatablock JSON file(s)' % (len(metadatablockNames)))

# Download dataset JSON metadata
print('\nDownloading JSON metadata of all published dataset versions to dataset_metadata folder:')

# Initiate count for terminal progress indicator
count = 0

# Figure out if given file with datasetPIDFile is a txt file or csv file
# file_name = os.path.basename(datasetPIDFile)

datasetPIDs = []
if '.csv' in datasetPIDFile:
    with open(datasetPIDFile, mode='r', encoding='utf-8') as f:
        total = len(f.readlines()) - 1
    with open(datasetPIDFile, mode='r', encoding='utf-8') as f:
        csvDictReader = DictReader(f, delimiter=',')
        for row in csvDictReader:
            datasetPIDs.append(row['persistent_id'].rstrip())
elif '.txt' in datasetPIDFile:

# if '.txt' in datasetPIDFile:
    # Save number of items in the datasetPIDFile txt file in "total" variable
    total = len(open(datasetPIDFile).readlines())

    datasetPIDFile = open(datasetPIDFile)

    # For each dataset persistent identifier in the txt file, download the dataset's Dataverse JSON file into the metadata folder
    for datasetPID in datasetPIDFile:

        # Remove any trailing spaces from datasetPID
        datasetPIDs.append(datasetPID.rstrip())

for datasetPID in datasetPIDs:
    try:
        latestVersionUrl = '%s/api/datasets/:persistentId' % (repositoryURL)
        params = {'persistentId': datasetPID}
        if apikey:
            params['key'] = apikey
        response = requests.get(
            latestVersionUrl,
            params=params)
        latestVersionMetadata = response.json()
        if 'id' in latestVersionMetadata['data']:
        # if latestVersionMetadata['status'] == 'OK':
            persistentUrl = latestVersionMetadata['data']['persistentUrl']
            publisher = latestVersionMetadata['data']['publisher']

            allVersionUrl = '%s/api/datasets/:persistentId/versions' % (repositoryURL)
            params = {'persistentId': datasetPID}
            if apikey:
                params['key'] = apikey
            response = requests.get(
                allVersionUrl,
                params=params)
            allVersionsMetadata = response.json()
            if 'id' in allVersionsMetadata['data'][0]:
                for datasetVersion in allVersionsMetadata['data']:
                    datasetVersion = {
                        'status': latestVersionMetadata['status'],
                        'data': {
                            'persistentUrl': persistentUrl,
                            'publisher': publisher,
                            'datasetVersion': datasetVersion}}

                    # majorVersion = str(datasetVersion['data']['datasetVersion']['versionNumber'])
                    majorVersion = improved_get(datasetVersion, 'data.datasetVersion.versionNumber')
                    # minorVersion = str(datasetVersion['data']['datasetVersion']['versionMinorNumber'])
                    minorVersion = improved_get(datasetVersion, 'data.datasetVersion.versionMinorNumber')

                    if (majorVersion is not None) and (minorVersion is not None):
                        versionNumber = majorVersion + '.' + minorVersion
                        print('\t' + versionNumber)
                    # metadataFile = '%s.json' % (datasetPID.replace(':', '_').replace('/', '_'))
                        metadataFile = '%s_v%s.json' % (datasetPID.replace(':', '_').replace('/', '_'), versionNumber)
                    else:
                        metadataFile = '%s_vDRAFT.json' % (datasetPID.replace(':', '_').replace('/', '_'))

                    with open(os.path.join(metadataFileDirectoryPath, metadataFile), mode='w') as f:
                        f.write(json.dumps(datasetVersion, indent=4))

        # Increase count variable to track progress
        count += 1

        # Print progress
        print('%s of %s datasets' % (count, total), end='\r', flush=True)
        # print('%s' % (count), end='\r', flush=True)

    except Exception:
        print('Could not download JSON metadata of %s' % (datasetPID))
