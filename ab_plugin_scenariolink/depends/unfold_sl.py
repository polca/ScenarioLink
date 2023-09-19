from unfold import Unfold

from unfold.data_cleaning import (
    check_exchanges_input,
    correct_fields_format,
)

from unfold.export import UnfoldExporter

from wurst.linking import (
    change_db_name,
    check_duplicate_codes,
    check_internal_linking,
    link_internal,
)
import pandas as pd
from typing import Union
from pathlib import Path


class Unfold_SL(Unfold):
    def __init__(self, path: Union[str, Path]):
        super(Unfold_SL, self).__init__(path)

    def write(self, superstructure: bool = False):
        """
        Write the databases.
        If superstructure is True, write the scenario difference file,
        along with a database.

        :param superstructure: bool, default False

        """

        if not superstructure:
            for scenario, database in self.databases_to_export.items():
                change_db_name(data=database, name=scenario)
                # check_exchanges_input(database, self.dependency_mapping)
                link_internal(database)
                check_internal_linking(database)
                check_duplicate_codes(database)
                correct_fields_format(database, scenario)
                print(f"Writing database for scenario {scenario}...")
                UnfoldExporter(scenario, database).write_database()

        else:
            try:
                self.scenario_df.to_excel(
                    f"{self.name or self.package.descriptor['name']}.xlsx", index=False
                )
            except ValueError:
                # from https://stackoverflow.com/questions/66356152/splitting-a-dataframe-into-multiple-sheets
                GROUP_LENGTH = 1000000  # set nr of rows to slice df
                with pd.ExcelWriter(
                    f"{self.package.descriptor['name']}.xlsx"
                ) as writer:
                    for i in range(0, len(self.scenario_df), GROUP_LENGTH):
                        self.scenario_df[i : i + GROUP_LENGTH].to_excel(
                            writer, sheet_name=f"Row {i}", index=False, header=True
                        )

            print(
                f"Scenario difference file exported to {self.package.descriptor['name']}.xlsx!"
            )
            print("")
            print("Writing superstructure database...")
            change_db_name(self.database, self.name or self.package.descriptor["name"])
            self.database = check_exchanges_input(
                self.database, self.dependency_mapping
            )
            link_internal(self.database)
            check_internal_linking(self.database)
            check_duplicate_codes(self.database)
            correct_fields_format(
                self.database, self.name or self.package.descriptor["name"]
            )
            UnfoldExporter(
                self.name or self.package.descriptor["name"], self.database
            ).write_database()
