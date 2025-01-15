from more_itertools import divide

from config.settings import PARTITIONS

def distribute_contact_list_to_partitions(contacts_list: list) -> list[list]:
    return [list(part) for part in divide(len(PARTITIONS), contacts_list)]

