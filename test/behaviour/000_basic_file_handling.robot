*** Settings ***
Documentation   Test the basic file handling of the Einsicht text-editor
Resource        resources/basic.resource
Default Tags    positive

*** Test Cases ***

Open new empty file
    Create a new file
    Ensure autocomplete is closed
    Ensure search bar is closed
    Close the file
    
Enter text into empty file
    Create a new file
    Ensure text does not contain    Lorem ipsum
    Write text                      Lorem ipsum dolor sit amet
    Ensure text contains            Lorem ipsum
    Close the file
    
Save text in a new file
    Create a new file
    Write text                      Lorem ipsum dolor sit amet
    Save file to                    /01-save-text-in-a-new-file.txt
    Close the file
    Ensure file exists              /01-save-text-in-a-new-file.txt
    Ensure file contains            /01-save-text-in-a-new-file.txt     Lorem ipsum