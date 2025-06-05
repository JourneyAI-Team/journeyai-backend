import datetime as dt


def format_datetime_to_string(date_time: dt.datetime) -> str:
    """
    Convert a datetime object to a formatted string.

    Parameters
    ----------
    date_time : datetime
        The datetime object to be formatted.

    Returns
    -------
    str
        A string representation of the datetime in the format "Sunday June 3, 2025 at 8:00 PM".
    """
    return date_time.strftime("%A %B %d, %Y at %I:%M %p")
