import time
import requests

RETRY_TIME = 10


def get_url_request(url, headers=None, stream=False, tries=1, errors=None):
    '''
    Handle transient network errors, and URLs with
    intermittent timeouts.
    '''
    if not errors:
        errors = []

    error_msg = None

    if tries > 3:
        return (None, errors)
    try:
        r = requests.get(url, headers=headers, stream=stream)
        r.raise_for_status()
    except requests.exceptions.Timeout:
        error_msg = 'Request timeout'
    except requests.ConnectionError:
        error_msg = 'Connection error'
    except requests.exceptions.TooManyRedirects:
        error_msg = 'Too many redirects'
    except requests.exceptions.RequestException as e:
        error_msg = 'Request exception (Code %s): %s' % (r.status_code, e)

    if not error_msg:
        return r, []

    # only add to errors list if it is different from last error.
    if not errors or (errors and errors[-1] != error_msg):
        errors.append(error_msg)

    time.sleep(RETRY_TIME)
    return get_url_request(url, headers, stream, tries + 1, errors)


control_codes_to_filter_out = [
    b'\\u0000',
    b'\x02',
    b'\x04',
    b'\x05',
    b'\x07',
    b'\x0B',
    b'\x0E',
    b'\x11',
    b'\x12',
    b'\x13',
    b'\x14',
    b'\x15',
    b'\x17',
    b'\x19',
    b'\x1A',
]


def save_content(url, filepath, headers=None):
    request, errors = get_url_request(url, stream=True, headers=headers)

    if not request:
        return errors

    warnings = []
    try:
        with open(filepath, 'wb') as f:
            for chunk in request.iter_content(1024 ^ 2):
                for control_code_to_filter_out in control_codes_to_filter_out:
                    if control_code_to_filter_out in chunk:
                        chunk = chunk.replace(control_code_to_filter_out, b'')
                        warnings.append('We had to replace control codes: ' + str(control_code_to_filter_out))
                f.write(chunk)
        return SaveContentResponse(warnings=warnings)
    except Exception as e:
        return SaveContentResponse(errors=[str(e)], warnings=warnings)


class SaveContentResponse:
    def __init__(self, warnings=[], errors=[]):
        self.errors = errors
        self.warnings = warnings


# if is_json:
#    try:
#        data = r.json()
#        return data, []
#    except json.JSONDecodeError:
#        error_msg = 'Failed to decode json'
# else:
#    try:
#        content = r.content
#        return content, []
#    except Exception as e:
#        error_msg = 'Unable to decode content: %s' % e
