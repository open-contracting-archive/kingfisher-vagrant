import time
import json
import requests

def get_url_request(url, headers=None, stream=False, tries=1, errors=None):
    '''
    Handle transient network errors, and URLs with
    intermittent timeouts.
    '''
    if not errors:
        errors = []

    error_msg = None

    if tries > 10:
        return (None, errors)
    try:
        r = requests.get(url, headers=headers, stream=stream)
        r.raise_for_status()
    except requests.exceptions.Timeout:
        error_msg = 'Request timeout'
    except requests.ConnectionError:
        error_msg = 'Connection error (attempt %s)'
    except requests.exceptions.TooManyRedirects:
        error_msg = 'Too many redirects'
    except requests.exceptions.RequestException as e:
        error_msg = 'Request exception: %s' % e

    if not error_msg:
        return r, []

    # only add to errors list if it is different from last error.
    if not errors or (errors and errors[-1] != error_msg):
        errors.append(error_msg)

    time.sleep(5)
    return get_url_request(url, headers, tries + 1, errors)


def save_content(url, filepath, headers=None):
    request, errors = get_url_request(url, stream=True, headers=headers)

    if not request:
        return errors

    try:
        with open(filepath, 'wb') as f:
            for chunk in request.iter_content(1024 ^ 2):
                f.write(chunk)
        return []
    except Exception as e:
        return [str(e)]


    




#if is_json:
#    try:
#        data = r.json()
#        return data, []
#    except json.JSONDecodeError:
#        error_msg = 'Failed to decode json'
#else:
#    try:
#        content = r.content
#        return content, []
#    except Exception as e:
#        error_msg = 'Unable to decode content: %s' % e
