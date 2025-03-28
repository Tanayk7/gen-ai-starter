import re 

def matches_pattern(pattern, target):
    # replace '{num}' with a regular expression that matches a number
    pattern_regex = re.sub(r'\{num\}', r'\\d+', pattern)
    # remove all spaces and parentheses from the pattern and make it case-insensitive
    pattern_regex = re.sub(r'[()\s]', '', pattern_regex)
    pattern_regex = pattern_regex.lower()
    # remove all spaces and parentheses from the target and make it case-insensitive
    target_regex = re.sub(r'[()\s]', '', target)
    target_regex = target_regex.lower()
    # check if the pattern regex matches anywhere in the target string
    return re.search(pattern_regex, target_regex) is not None

def remove_special_chars(s):
    # Remove non-alphanumeric characters and preserve spaces between words
    return re.sub(r'[^a-zA-Z0-9\s]', '', s)

def has_valid_phone_number(text):
    regex = re.compile(r"\(?\d+\)?[-.\s]?\d+[-.\s]?\d+")
    match = regex.search(text)
    if match:
        return True
    return False 

def has_valid_email(line):
    """
    Check if the given line contains a valid email address.
    """
    # Regular expression pattern to match email addresses
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    # Check if the line contains a match to the email pattern
    match = re.search(email_pattern, line)
    # If a match is found, return True. Otherwise, return False.
    return bool(match)
