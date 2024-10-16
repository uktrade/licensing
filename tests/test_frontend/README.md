# End-to-End tests
We use playwright for end-to-end testing.
To run the end-to-end tests for licensing:\
`invoke frontendtests`

## Test structure
Tests are currently organised in folders corresponding to the views. Within each folder, each view/step of apply-for-a-licence will have its own testfile.

## Useful Commands
A useful command for writing end-to-end tests is:\
`pipenv run playwright codegen http://apply-for-a-licence:8000/`

If you run into issues running playwright, you may need to install the playwright dependencies:\
`playwright install`
