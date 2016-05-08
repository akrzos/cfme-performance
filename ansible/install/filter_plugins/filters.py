def to_grafana_refid(number):
    """Convert a number to a string starting at character a and incrementing.  This only accounts
    for a to zz, anything greater than zz is probably too much to graph anyway."""
    character1 = ''
    idx = -1
    while number > 25:
        idx = idx + 1
        number -= 26
    else:
        if idx != -1:
            character1 = chr(idx + 65)
    return character1 + chr(number + 65)


class FilterModule(object):
    def filters(self):
        return {'to_grafana_refid': to_grafana_refid, }
