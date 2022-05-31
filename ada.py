import os
import sys
import logging
import requests

# Set environment variables to avoid storing credentials in your API script.
auth_email = os.environ['Ada_email']
auth_password = os.environ['Ada_password']

# Global script parameters
base_url = os.environ['Ada_base_url']  # https://ada.seiudsa.com/ in production, can be set with a string here
default_template_id = int()  # ID of template for matching, should be configured and retrieved in Ada front end
default_trigger_action = 'load'  # difference for preview, load to initiate
auth_cookies = None  # set by authenticate()


def authenticate():
    """
    Generate a session cookie using environment variables or return an existing session cookie.
    :return: RequestsCookieJar
    """
    global auth_cookies
    if not auth_cookies:
        payload = {'email': auth_email, 'password': auth_password}
        auth_response = requests.post(url=f'{base_url}api/v1/users/login',
                                      json=payload)
        try:
            assert auth_response.status_code == 200  # expect a 200 response code when authenticating
        except AssertionError:
            logging.exception(f'Authentication failed with unexpected status code {auth_response.status_code}: \
            {auth_response.text}')
            sys.exit(-1)

        auth_cookies = auth_response.cookies

    return auth_cookies


def upload_file(path_to_upload_file):
    """
    Load a file to Ada
    :param path_to_upload_file: path to the csv or xlsx file you wish to load
    :return: Response
    """
    with open(path_to_upload_file, 'rb') as f:
        upload_response = requests.post(url=f'{base_url}api/v2/upload/',
                                        files={"file": f},
                                        cookies=authenticate()
                                        )
    try:
        assert upload_response.status_code == 201  # expect a 201 response code when posting a file
    except AssertionError:
        logging.exception(f'Posting file for upload failed with unexpected status code {upload_response.status_code}: \
        {upload_response.text}')
        sys.exit(-1)

    logging.info(f'Upload id {upload_response.json()["id"]} posted {upload_response.json()["file_name"]} to \
    {upload_response.json()["file_url"]}')

    return upload_response


def trigger_match(load_file_response, 
                  template=default_template_id,
                  trigger_action=default_trigger_action):
    """
    Trigger a match on an uploaded file.
    :param load_file_response: Response object from upload_file()
    :param template: ID of an existing Ada template mapping the headers of the file submitted
    :param trigger_action: 'difference' to preview match or 'load' to insert new records
    :return: Response
    """
    payload = {
      "template": template,
      "trigger_action": trigger_action,
      "upload": load_file_response.json()['id']
    }
    trigger_response = requests.post(url=f'{base_url}api/v2/trigger/',
                                     json=payload,
                                     cookies=authenticate()
                                     )
    try:
        assert trigger_response.status_code == 201  # expect a 201 response code when triggering a match
    except AssertionError:
        logging.exception(f'Posting file for upload failed with unexpected status code {trigger_response.status_code}: \
        {trigger_response.text}.')
        sys.exit(-1)

    logging.info(f'Triggered match in {trigger_response.json()["trigger_action"]} mode.')

    # Report back a link to see the loaded file in the UI, based on the trigger_action selected.
    if trigger_response.json()["trigger_action"] == 'load':
        logging.info(f'Monitor progress at {base_url}upload/process/{trigger_response.json()["id"]}')
    elif trigger_response.json()["trigger_action"] == 'difference':
        logging.info(f'Monitor progress at {base_url}upload/preview/{trigger_response.json()["id"]}')
    else:
        logging.error('trigger_action may only take the value "load" or "difference"')

    return trigger_response


def main():
    logging.basicConfig(level="INFO")
    logging.info('Note: links to log output work only if you authenticate to Ada in the web browser first.')

    # Post the file, in this case from the working directory of the script
    load = upload_file(path_to_upload_file='TestFile.csv')  # Excel files (.xlsx format) are also accepted

    # Trigger processing of the uploaded file, overriding the default trigger_action
    outcome = trigger_match(load_file_response=load, trigger_action='difference')


if __name__ == '__main__':
    main()
