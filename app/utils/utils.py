import random
import time

def random_sleep(min_seconds: float = 2, max_seconds: float = 5) -> None:
    """
    Sleep for a random amount of time between min_seconds and max_seconds
    """
    time.sleep(random.uniform(min_seconds, max_seconds))

def normalize_skill(skill: str) -> str:
    """
    Normalize skill names to maintain consistency
    """
    normalizations = {
        'Control M': 'Control-M',
        'Control-M': 'Control-M',
        'ControlM': 'Control-M',
        'API Management': 'API',
        'API': 'API',
        'REST API': 'REST',
        'RESTful': 'REST',
        'SOAP API': 'SOAP',
        'Web Services': 'Web Services',
        'Webservices': 'Web Services',
        'SQL Server': 'Microsoft SQL Server',
        'MSSQL': 'Microsoft SQL Server',
        'Microsoft SQL': 'Microsoft SQL Server'
    }
    return normalizations.get(skill, skill)
