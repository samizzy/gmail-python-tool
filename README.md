# Project for sending batch mails using gmail.
## Pre requisites
# Make yourself a app/project/client id
Visit [Google Developer Console](https://console.developers.google.com/flows/enableapi?apiid=gmail&pli=1) and click on create project, give any desired name. After creation, download the credential.json file and store it in this projects root directory.
# Install python 3 and dependencies
- You will need python 3 or above and pip
- hit install.sh to install required dependencies.

## Running the application
- You need 3 files to run this i know it seems a lot, a html_template file, a contacts file and common yaml file for all mails.
- The contacts file should contain list of people. Each line should only contain <name>tab<emailid>. Use '#' character at the front of a line to exclude it.
- The html template file is not purely html, there is logic for extracting subject and body of mail. Also any yaml key taken from the yaml file will be passed to the html, so you can use ${key} inside html to substitute values.
- You also need to supply a user email id from which the email is to be sent. On the very firt run, the program will redirect you to your google page and ask you to grant permission, after access it will send the mail.
- hit python mail.py with mentioned arguments or there is exec.sh file where this command is also present, use this if you feel too lazy to type every time.
