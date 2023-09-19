from bw2data.database import DatabaseChooser

try:
    from bw2data.backends.peewee import SQLiteBackend, ActivityDataset, ExchangeDataset
except ImportError:
    from bw2data.backends import SQLiteBackend, ActivityDataset, ExchangeDataset

from wurst.brightway.extract_database import (
    extract_activity,
    add_input_info_for_indigenous_exchanges,
    add_input_info_for_external_exchanges,
    extract_exchange
)

def extract_brightway2_databases(database_names, add_properties=False, add_identifiers=False):
    """Extract a Brightway2 SQLiteBackend database to the Wurst internal format.

    ``database_names`` is a list of database names. You should already be in the correct project.

    Returns a list of dataset documents."""
    ERROR = "Must pass list of database names"
    if isinstance(database_names, str):
        database_names = [database_names]
    assert isinstance(database_names, (list, tuple, set)), ERROR

    databases = [DatabaseChooser(name) for name in database_names]
    ERROR = "Wrong type of database object (must be SQLiteBackend)"
    assert all(isinstance(obj, SQLiteBackend) for obj in databases), ERROR

    # Construct generators for both activities and exchanges
    # Need to be clever to minimize copying and memory use
    activity_qs = ActivityDataset.select().where(
        ActivityDataset.database << database_names
    )
    exchange_qs = ExchangeDataset.select().where(
        ExchangeDataset.output_database << database_names
    )

    # Retrieve all activity data
    print("Getting activity data")
    activities = [extract_activity(o, add_identifiers=add_identifiers) for o in tqdm(activity_qs)]
    # Add each exchange to the activity list of exchanges
    print("Adding exchange data to activities")
    add_exchanges_to_consumers(activities, exchange_qs, add_properties)
    # Add details on exchanges which come from our databases
    print("Filling out exchange data")
    add_input_info_for_indigenous_exchanges(activities, database_names, add_identifiers=add_identifiers)
    add_input_info_for_external_exchanges(activities, database_names, add_identifiers=add_identifiers)
    return activities

def add_exchanges_to_consumers(activities, exchange_qs, add_properties=False, add_identifiers=False):
    """Retrieve exchanges from database, and add to activities.

    Assumes that activities are single output, and that the exchange code is the same as the activity code. This assumption is valid for ecoinvent 3.3 cutoff imported into Brightway2."""
    lookup = {(o["database"], o["code"]): o for o in activities}

    with tqdm(total=exchange_qs.count()) as pbar:
        for i, exc in enumerate(exchange_qs):
            exc = extract_exchange(exc, add_properties=add_properties)
            output = tuple(exc.pop("output"))
            lookup[output]["exchanges"].append(exc)
            pbar.update(1)
    return activities

