*** Settings ***
Documentation   Test the basic file handling of the Einsicht text-editor
Resource        resources/basic.resource
Default Tags    positive
Suite Teardown  Close the file

*** Test Cases ***

Open new empty file
    Create a new file
    Ensure autocomplete is closed
    Ensure search bar is closed
    Close the file