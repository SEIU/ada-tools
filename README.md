# ada-tools
The Ada API supports a wide variety of programatic interactions with the Ada webapp, and this repo contains sample scripts and other illustrative code to assist in doing so.

Sample files included in the repo can be altered to execute with credentials and parameters particular to your use case by editing the defined parameters and main() function.  

Sample files can also be imported as a module by placing the example script in the working directory of the running script and importing the sample file by name. For instance, import the authenticate(), upload_file(), or trigger_match() functions from ada_load_match.py with the following line:

    import ada_load_match

Access the functions in your script by calling them like 

    ada.upload_file()

or import specifics functions as needed like

    from ada import upload_file

