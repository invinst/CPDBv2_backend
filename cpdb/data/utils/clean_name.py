import re


POPULAR_IRISH_O_NAMES = [
    'oboyle', 'obrien', 'ocallaghan', 'ocarroll', 'oconnell', 'oconnor', 'odonnell',
    'odonovan', 'oneill', 'oreilly', 'oshaughnessy', 'oshea'
]
POPULAR_IRISH_O_NAMES_REGEX = '|'.join(POPULAR_IRISH_O_NAMES)


def remove_wrong_spacing(name):
    # John Hollowell  Jr. -> John Hollowell Jr.
    return re.sub(r'\s+', ' ', name)


def capitalise_generation_suffix(name):
    # Mark Loop Iv -> Mark Loop IV
    def upper_suffix(match):
        return match.group(1).upper()

    return re.sub(r'\b(X?(IX|IV|V?I{0,3}))$', upper_suffix, name, flags=re.IGNORECASE)


def correct_irish_name(name):
    # Eric O suoji -> Eric O'Suoji
    # Eric Obrien -> Erc O'Brien
    def fix_irish_name(match):
        return f"O'{match.group('word').capitalize()}"

    def fix_irish_name_2(match):
        name = match.group(0)
        rest_part = name[1:]
        return f"O'{rest_part.capitalize()}"

    if re.search(POPULAR_IRISH_O_NAMES_REGEX, name, re.IGNORECASE):
        return re.sub(POPULAR_IRISH_O_NAMES_REGEX, fix_irish_name_2, name, flags=re.IGNORECASE)
    else:
        return re.sub(r'\bO( |\')(?P<word>\w+)', fix_irish_name, name, flags=re.IGNORECASE)


def correct_suffix_jr_sr(name):
    # Clarence Pendleton jr -> Clarence Pendleton Jr.
    def fix_suffix(match):
        return f'{match.group(1).capitalize()}.'

    return re.sub(r'\b(jr|sr)\.?$', fix_suffix, name, flags=re.IGNORECASE)


def correct_suffix_dot(name):
    # Neil Shelton El. -> Neil Shelton El
    def fix_suffix(match):
        if re.match(r'(?:jr|sr)', match.group(1), re.IGNORECASE):
            return f'{match.group(1).capitalize()}.'
        return match.group(1).capitalize()

    return re.sub(r'\b(\w{2,})\.', fix_suffix, name, flags=re.IGNORECASE)


def correct_initial(name):
    # C Pepol -> C. Pepol
    def fix_initial(match):
        if match.group('initial').endswith('.'):
            return match.group('initial')
        else:
            return f"{match.group('initial')}."

    return re.sub(r'(?<!\')\b(?P<initial>\w\.?)(?=\s|$)', fix_initial, name)


def fix_typo_o(name):
    # Kimberly C0nnolly -> Kimberly Connolly
    return re.sub('0', 'o', name)


def correct_title(name):
    # Julio Yushu'A -> Julio Yushu'a
    def fix_incorrect_capitalization(match):
        return match.group(0).lower()
    return re.sub(r'\'\w\b', fix_incorrect_capitalization, name)


def expand_or_correct_abbreviated_name(name):
    # Wm Donnelly -> William Donnelly
    abbr_list = [('wm', 'william'), ('cl', 'C.L.')]
    for abbr, replace in abbr_list:
        name = re.sub(r'\b%s\.?\b' % abbr, replace, name, flags=re.IGNORECASE)
    return name


def clean_name(name):
    new_name = name.strip(' ')
    new_name = fix_typo_o(new_name)
    new_name = expand_or_correct_abbreviated_name(new_name)
    new_name = new_name.title()
    new_name = correct_title(new_name)
    new_name = remove_wrong_spacing(new_name)
    new_name = capitalise_generation_suffix(new_name)
    new_name = correct_irish_name(new_name)
    new_name = correct_suffix_dot(new_name)
    new_name = correct_suffix_jr_sr(new_name)
    new_name = correct_initial(new_name)

    return new_name
