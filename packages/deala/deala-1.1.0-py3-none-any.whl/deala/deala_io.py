import pandas as pd
import numpy as np
from scipy.stats import linregress
import os
from os import walk
import json
import brightway2 as bw
from tqdm import tqdm
import math
from deala import *
import uuid
from premise import *
from constructive_geometries import *
import bw2analyzer as bwa
import plotly.express as px
import plotly.graph_objects as go


class deala_io:
    def __init__(self):
        self.bw2 = bw
        self.pd = pd
        self.os = os
        self.json = json
        self.tqdm = tqdm
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Creation of a new database in the Python project
    def create_DB(self, name):
        if name in bw.databases:
            print(name + ' ' + 'is already included')
        else:
            db = bw.Database(name)
            db.register()
            return bw.Database(name)
    
    def deala_setup(self, overwrite=False):
        """
        Imports the 'marketsphere' database and DEALA impact assessment categories database.

        - If 'marketsphere' is already imported and overwrite is False, it prints a message and returns.
        - If 'marketsphere' is already imported and overwrite is True, it deletes the existing database and imports the new one.
        - Loads data from 'marketsphere.json' and allocates it to the 'marketsphere' database.
        - Imports DEALA impact assessment methods from 'DEALA.json'.
        - Sets the unit for the methods to "USD2023".
        """
        if "marketsphere" in bw.databases:
            if overwrite:
                del bw.databases["marketsphere"]
                print("The existing marketsphere database has been deleted.")
            else:
                print("The marketsphere database is already imported.")
                return

        # Define the 'marketsphere' database
        mdb = bw.Database('marketsphere')

        # Load data from 'marketsphere.json'
        # Construct the file path
        base_path = os.path.dirname(os.path.abspath(__file__))
        fp = os.path.join(base_path, "files", "characterization_models", "marketsphere.json")
        with open(fp) as f:
            data = json.load(f)

        # Allocate data and store it in the 'marketsphere' database
        mdb_data = {
            (dataset["database"], dataset["code"]): {
                "categories": (dataset["compartment"], dataset["subcompartment"]),
                "name": dataset["name"],
                "database": dataset["database"],
                "exchanges": [],
                "unit": dataset["unit"],
                "type": "biosphere"
            }
            for dataset in data
        }

        mdb.write(mdb_data)

         # Import DEALA Impact Assessment methods
        fp = os.path.join(base_path, "files", "characterization_models","DEALA.json")
        with open(fp) as f:
            data = json.load(f)

        methods = list(set(dataset['category'] + " " + dataset['method'] for dataset in data))

        for method in tqdm(methods):
            cfs=[]
            for datasets in data:
                if datasets["category"] in method and datasets["method"] in method:
                    m=bw.Method((datasets["method"],datasets["category"],datasets["indicator"]))
                    if m.name not in bw.methods: m.register()
                    bw.methods[m.name]['unit']="USD2023"
                    bw.methods.flush()
                    cf = ((datasets["database"], datasets["code"]),datasets["CF"])
                    cfs.append(cf)
            m.write(cfs)

        print('The marketsphere database and DEALA impact assessment methods are successfully imported.')

    # Defintion to create new activities in the database (DEALA acitivities)
    def new_DEALA_activity(self, database_name, name, reference_product, unit, category, location, comment, code1):
        """
        Create a new deala activity in a specified Brightway2 database.

        This function generates a new deala activity with the provided attributes and saves it to the specified database.
        It also creates a production exchange for the activity, ensuring it is properly linked within the database.

        Args:
            database_name (str): The name of the Brightway2 database where the activity will be created.
            name (str): The name of the activity.
            reference_product (str): The reference product associated with the activity.
            unit (str): The unit of measurement for the activity.
            category (list): A list of categories describing the activity.
            location (str): The geographical location of the activity.
            comment (str): A comment or description for the activity.
            code1 (str): A unique hexadecimal code to identify the activity.

        Returns:
            bw.Activity: The newly created activity object.

        Note:
            - The function assumes that the Brightway2 library (`bw`) is properly initialized and the database exists.
            - The `code1` parameter must be unique within the database to avoid conflicts.
        """
        data = {
            "name": name, "reference product": reference_product, "unit": unit, "categories": category, "location": location,
            "type": "process", "comment": comment
        }
        new_act = bw.Database(database_name).new_activity(
            code=code1, #gives each activity a hexa code
            **data
            )
        new_act.save()
        production_exchange = new_act.new_exchange(
            input=new_act, amount=1, type="production"
        )
        production_exchange.save()
        return new_act
    
    # Defintion to create new activities in the database (main acitivities)
    def new_activity(self, database_name, name, reference_product, unit, category, location):
        """
        Create a new activity in the specified Brightway2 database.

        This function generates a new activity with the provided attributes and saves it to the specified database.
        It also creates and saves a production exchange for the activity.

        Args:
            database_name (str): The name of the Brightway2 database where the activity will be created.
            name (str): The name of the activity.
            reference_product (str): The reference product associated with the activity.
            unit (str): The unit of measurement for the activity.
            category (str): The category or categories associated with the activity.
            location (str): The geographical location of the activity.

        Returns:
            bw.Activity: The newly created activity object.

        Notes:
            - Each activity is assigned a unique hexadecimal code using `uuid.uuid4().hex`.
            - A production exchange with an amount of 1 is automatically created and linked to the activity.
        """
        data = {
            "name": name, "reference product": reference_product, "unit": unit, "categories": category, "location": location,
            "type": "process"
        }
        new_act = bw.Database(database_name).new_activity(
            code=uuid.uuid4().hex, #gives each activity a hexa code
            **data
            )
        new_act.save()
        production_exchange = new_act.new_exchange(
            input=new_act, amount=1, type="production"
        )
        production_exchange.save()
        return new_act



    def compute_growth_rate(self, years, values, method="geo"):
        """
        Compute annual growth rate r from historical deflator data.
        
        Parameters:
        - years: list of int (years)
        - values: list of float (deflator values corresponding to years)
        - method: 'geo' for geometric mean, 'reg' for regression
        
        Returns:
        - r: annual growth rate (decimal, e.g., 0.03 for 3%)
        """
        if len(years) < 2:
            raise ValueError("Need at least two data points to compute growth rate.")

        if method == "geo":
            growth_rates = []
            for i in range(1, len(values)):
                yr_diff = years[i] - years[i-1]
                rate = (values[i] / values[i-1]) ** (1 / yr_diff) - 1
                growth_rates.append(rate)
            r = np.mean(growth_rates)
        elif method == "reg":
            # Linear regression on log(values) ~ years
            log_vals = np.log(values)
            slope, intercept, _, _, _ = linregress(years, log_vals)
            r = np.exp(slope) - 1
        else:
            raise ValueError("Method must be 'geo' or 'reg'")
        return r

    def normalize_and_extend_deflators(self, json_data, base_year=2023, extend_to_year=2030, method="geo"):
        """
        Normalize deflator series to base_year and extend to extend_to_year using growth rate from method.
        
        Parameters:
        - json_data: list of dicts, each with years as keys and deflator values
        - base_year: int, year to normalize deflators to (default 2023)
        - extend_to_year: int, last year to extrapolate deflator values to
        - method: "geo" or "reg" for growth rate calculation
        
        Returns:
        - extended_normalized_data: list of dicts with normalized and extended deflators
        """
        extended_data = []

        for entry in json_data:
            # Separate metadata and year data
            meta_keys = {k: v for k, v in entry.items() if not k.isdigit()}
            year_values = {}
            for k, v in entry.items():
                if k.isdigit() and v is not None:
                    try:
                        val = float(v)
                        if not np.isnan(val):
                            year_values[int(k)] = val
                    except:
                        pass
            
            # Check base_year presence
            base_val = year_values.get(base_year)
            if base_val is None or base_val == 0:
                print(f"Warning: Base year {base_year} missing or zero for country {entry.get('ISO-3166-1 ALPHA-2', 'Unknown')}. Skipping normalization and extension.")
                extended_data.append(entry)
                continue

            # Normalize existing years by base_val
            normalized_year_values = {year: val / base_val for year, val in year_values.items()}

            # Prepare data for growth calculation (only years <= base_year)
            # Or you might want all available years before base_year; adapt as needed
            historical_years = sorted([y for y in normalized_year_values if y <= base_year])
            historical_values = [normalized_year_values[y] for y in historical_years]

            # If not enough data to compute growth rate, skip extrapolation
            if len(historical_years) < 2:
                # Just keep normalized years, no extension
                extended_year_values = normalized_year_values.copy()
            else:
                # Compute growth rate r
                r = self.compute_growth_rate(historical_years, historical_values, method=method)

                # Extend series to extend_to_year
                extended_year_values = normalized_year_values.copy()
                last_known_year = max(normalized_year_values.keys())
                
                for year in range(last_known_year + 1, extend_to_year + 1):
                    years_ahead = year - base_year
                    # Extrapolate using (1 + r)^years_ahead, base_year normalized to 1
                    extended_year_values[year] = (1 + r) ** years_ahead
            
            # Convert keys back to str for consistency
            extended_year_values_str = {str(k): v for k, v in extended_year_values.items()}
            extended_entry = {**meta_keys, **extended_year_values_str}
            extended_data.append(extended_entry)

        return extended_data


    # --- Example usage ---

    # Suppose you have your JSON data loaded in variable `json_data`

    # extended_normalized = normalize_and_extend_deflators(
    #     json_data,
    #     base_year=2023,
    #     extend_to_year=2030,
    #     method="geo"  # or "reg"
    # )

    # print(extended_normalized)

    


    def import_DEALA_activities(self, base_year, dict_scenarios, repository_main_path, method_calc_r="geo", price_calculation="nominal"):
        """
        Imports DEALA activities from data files, calculates adjusted costs based on scenarios, 
        and creates or updates activities in the Brightway2 database.

        This function processes data files containing DEALA activities, calculates adjusted costs 
        for each scenario using GDP deflator and elasticity data, and creates or updates activities 
        in the respective Brightway2 databases. It also handles multi-year activities and ensures 
        proper linking with the 'marketsphere' database.

        Args:
            base_year (int): The base year for normalization of costs.
            dict_scenarios (dict): Dictionary mapping scenario names to their corresponding years.
            repository_main_path (str): Path to the main repository containing required files.
            method_calc_r (str): Method to calculate growth rate, either "geo" for geometric mean or "reg" for regression.
            price_calculation (str): Method for price calculation, either "nominal" for nominal prices or "real" for real prices.

        Returns:
            None
        """

        #load all gdp data for the defined scenarios
        fp = os.path.join(repository_main_path, "files", "GDP")

        lst_file_names = next(os.walk(fp), (None, None, []))[2]  # [] if no file

        lst_filepath=[os.path.join(dirpath,f) for (dirpath, dirnames, filenames) in os.walk(fp) for f in filenames]

        dict_gdp={}
        for file in lst_filepath:
            filename = os.path.basename(file)
            for key in dict_scenarios.keys():
                if os.path.splitext(filename)[0] in key:
                    df=pd.read_excel(file)
                    dict_gdp[key]=df

        list_databases = []

        # store all files in list including data to create DEALA activities
        fp = os.path.join(repository_main_path, "files", "DEALA_activities")

        lst_file_names = next(walk(fp), (None, None, []))[2]  # [] if no file

        if '.DS_Store' in lst_file_names:
            lst_file_names.remove('.DS_Store')

        
        # load the deflator and elasticity data

        # Define the file paths using os.path.join
        deflator_path = os.path.join(repository_main_path,"Files", "GDP", "gdp_deflator.json")
        elasticity_path = os.path.join(repository_main_path,"Files", "GDP", "elasticity.json")

        # Load the deflator and elasticity data
        data_deflator = json.load(open(deflator_path))
        data_elasticity = json.load(open(elasticity_path))

        # Normalize and extend the deflator and elasticity data
        for scenario in dict_scenarios:
            last_year = dict_scenarios[scenario]
        extended_normalized = self.normalize_and_extend_deflators(
            data_deflator,
            base_year=base_year,
            extend_to_year=last_year,
            method=method_calc_r  # "geo" or "reg"
        )

        # Step 1: Retrieve a list of existing databases
        for database in bw.databases:
            list_databases.append(database)

        # Step 2: Delete databases containing both 'ecoinvent' and target
        for database in list_databases:
            if 'DEALA' in database:
                del bw.databases[database]

        # Get a set of countries from the data_deflator list
        countries = {entry['ISO-3166-1 ALPHA-2'] for entry in data_deflator}

        # Loop over each scenario
        for scenario in dict_scenarios:
            # Register a new database for the given scenario
            db = bw.Database('DEALA_activities_' + scenario)
            db.register()
            
            # Loop over each file in the list of file names
            for file in tqdm(lst_file_names):
                # Load the data from the current file
                data = json.load(open(fp + "/" + file))
                
                # Loop over each dataset in the loaded data
                for dataset in tqdm(data):
                    for elasticity in data_elasticity:
                        if (
                            dataset['Sector'] == elasticity['Sector']
                            and dataset['Type'] == elasticity['Type']
                            and dataset['ISO-3166-1 ALPHA-2'] == elasticity['ISO-3166-1 ALPHA-2']
                        ):
                            elasticity_value = elasticity['Elasticity (long run)']
                    # check if real or nominal price calculation is used
                    if price_calculation in ["real", "nominal"]:
                        # Apply real price adjustments
                        base_price_nominal = dataset['Costs per unit [USD/unit]']
                        if dataset['ISO-3166-1 ALPHA-2'] in countries:
                            location = dataset['ISO-3166-1 ALPHA-2']
                        else:
                            location = "GLO"
                        for deflator in extended_normalized:
                            if str(dict_scenarios[scenario]) in deflator and location == deflator['ISO-3166-1 ALPHA-2']:
                                deflator_factor = deflator[str(base_year)] / deflator[str(dataset['Base Year'])]
                                base_price_real = base_price_nominal * deflator_factor
                                #project prices
                                projected_price_real = base_price_real * (dict_gdp[scenario].set_index('ISO Code').at[dataset['REMIND Region'], int(dict_scenarios[scenario])] / dict_gdp[scenario].set_index('ISO Code').at[dataset['REMIND Region'], int(dataset['Base Year'])]) ** elasticity_value

                                if price_calculation == "real":
                                    # If the price calculation is set to "real", keep the amount as is
                                    amount = projected_price_real
                                elif price_calculation == "nominal":
                                    # If the price calculation is set to "nominal", consider inflation
                                    inflation_factor= deflator[str(dict_scenarios[scenario])] / deflator[str(base_year)]
                                    amount = projected_price_real * inflation_factor
                    elif price_calculation not in ["real", "nominal"]:
                                            # Handle unexpected price calculation types
                                            raise ValueError(f"Unexpected price calculation type: {price_calculation}")

                    # Update the dataset with the calculated amount for the scenario
                    dataset.update({scenario: amount})
                    
                    # If the dataset includes years, create respective activities for each year
                    if dataset['Years'] > 0:
                        list_years = []
                        for i in range(1, dataset['Years'] + 1):
                            list_years.append(str(i) + " years")
                        
                        # Loop over the "marketsphere" database to create or update activities
                        for act in bw.Database('marketsphere'):
                            if act['categories'][0] == dataset['Identifier'] and act['categories'][1] in list_years:
                                act_new = self.new_DEALA_activity(db.name, dataset['Identifier'] + ' - ' + dataset['Type'] + ' - ' + act['categories'][1], dataset['Type'], dataset['Unit'], dataset['Identifier'], dataset['ISO-3166-1 ALPHA-2'], dataset['Description'], dataset['Code'] + act['categories'][1])
                                # Add act as marketsphere flow
                                act_new.new_exchange(input=act.key, amount=dataset[scenario], type='biosphere').save()
                    else:
                        # If no years are considered, create or update a single activity
                        for act in bw.Database('marketsphere'):
                            if act['categories'][0] == dataset['Identifier']:
                                act_new = self.new_DEALA_activity(db.name, dataset['Identifier'] + ' - ' + dataset['Type'], dataset['Type'], dataset['Unit'], dataset['Identifier'], dataset['ISO-3166-1 ALPHA-2'], dataset['Description'], dataset['Code'])
                                # Add act as marketsphere flow
                                act_new.new_exchange(input=act.key, amount=dataset[scenario], type='biosphere').save()

            # Create DEALA activities in the respective databases for the defined scenarios
    def create_default_DEALA_activities(self, name_DB, dict_scenarios):
        """
        Creates DEALA activities in separate databases based on defined scenarios.

        Args:
            name_DB (str): The base name for the databases.
            dict_scenarios (dict): A dictionary containing scenario names as keys.
            dict_activities (dict): A dictionary containing activity names as keys and associated information.

        Returns:
            None
        """
        # definition of remaining deala activities to represent remaining impact categories as dict. The value represents the years to be considered. The value is 0 if no values have to be considered
        dict_activities={
            'administration':['administration', 0],
            'insurance':['insurance', 0],
            'depreciation (linear) - machinery and equipment':['machinery and equipment', 50],
            'maintenance and repair':['maintenance and repair', 0],
            'interest (internal)':['interest', 0],
            'interest (external)':['interest', 0],
            'taxes':['taxes', 0],
            'research and development':['research and development', 0],
            'warranty':['warranty', 0],
            'subsidies (linear)':['subsidies', 50],
            'capital expenditures':['capital expenditures', 0],
            'capital-dependent subsidies':['subsidies', 0]

            }

        # For each scenario, a separate database is created
        for scenario in dict_scenarios:
            self.create_DB(name_DB + scenario)
            DB = bw.Database(name_DB + scenario)
            for activity in tqdm(dict_activities):
                if dict_activities[activity][1] > 0:
                    list_years = []
                    for i in range(0, dict_activities[activity][1] + 1, 1):
                        list_years.append(str(i) + " years")
                    for act in bw.Database('marketsphere'):
                        if act['categories'][0] in activity and act['categories'][1] in list_years:
                            act_new = self.new_activity(DB.name, activity + ' - ' + act['categories'][1], act['name'], 'USD', dict_activities[activity][0], 'GLO')
                            act_new.new_exchange(input=act.key, amount=1, type='biosphere').save()
                else:
                    for act in bw.Database('marketsphere'):
                        if act['categories'][0] in activity:
                            act_new = self.new_activity(DB.name, activity + ' - ' + act['categories'][1], act['name'], 'USD', dict_activities[activity][0], 'GLO')
                            act_new.new_exchange(input=act.key, amount=1, type='biosphere').save()

    def create_premise_databases(dict_scenarios, key_premise, source_type, filepath_ecoinvent, source_version, overwrite=False):
        """
        Creates premise databases based on given scenarios and other parameters.

        Args:
            dict_scenarios (dict): A dictionary containing scenario keys and corresponding years.
            key_premise (str): The decryption key for the premise database.
            source_type (str): Type of the source data (e.g., 'ecoinvent', 'custom', etc.).
            filepath_ecoinvent (str): File path to the ecoinvent data.
            source_version (str): Version of the source data.
            overwrite (bool): If True, overwrite existing databases. Default is False.

        Returns:
            None: The function does not return any value directly but creates premise databases.
        """
        list_scenarios = []

        # Split the keys and store the resulting strings as variables
        for key, values in dict_scenarios.items():
            db_name = f"{key}_{values}"
            if db_name in bw.databases:
                if overwrite:
                    del bw.databases[db_name]
                    print(f"Existing database '{db_name}' deleted due to overwrite=True.")
                    parts = key.split('_')
                    if len(parts) == 3:
                        model, pathway, year = parts
                        list_scenarios.append({"model": model, "pathway": pathway, "year": values})
                else:
                    print(f"Database '{db_name}' already exists. Skipping creation.")
                    continue
            else:
                parts = key.split('_')
                if len(parts) == 3:
                    model, pathway, year = parts
                    list_scenarios.append({"model": model, "pathway": pathway, "year": values})

        if not list_scenarios:
            print("No new scenarios to create databases for.")
            return

        clear_cache()

        # Initialize a NewDatabase object
        ndb = NewDatabase(
            scenarios=list_scenarios,
            source_type=source_type,
            source_file_path=filepath_ecoinvent,
            source_version=source_version,
            key=key_premise,
            # use_multiprocessing=True,  # Set to False if multiprocessing causes issues
            # keep_uncertainty_data=False,  # Set to True if you want to keep ecoinvent's uncertainty data
            # use_absolute_efficiency=True  # Set to True if you want to use IAM's absolute efficiency for power plants
        )

        ndb.update()
        ndb.write_db_to_brightway(f"{'ecoinvent'}_{source_version}-{'cutoff'}_{model}_{pathway}_{year}")



    def create_target_databases(self, filepath: str, target: str):
        """
        Creates and populates target databases based on the specified Excel file.

        Args:
            filepath (str): Path to the Excel file containing data of target (e.g. transport or energy).
            target (str): name of target (e.g. transport or energy)

        Returns:
            dict: A dictionary mapping activity tuples (name, location, database) to their keys.
        """
        list_databases = []
        dict_activities = {}

        # Step 1: Retrieve a list of existing databases
        for database in bw.databases:
            list_databases.append(database)

        # Step 2: Delete databases containing both 'ecoinvent' and target
        for database in list_databases:
            if 'ecoinvent' in database and target in database:
                del bw.databases[database]

        # Step 3: Import data from the specified Excel file
        for database in list_databases:
            index_ecoinvent = database.find('ecoinvent')
            if 'ecoinvent' in database and index_ecoinvent == 0:
                imp = bw.ExcelImporter(filepath)
                imp.apply_strategies()
                imp.match_database(database, fields=('name', 'unit', 'location'))
                imp.match_database(fields=('name', 'unit', 'location'))
                imp.match_database('biosphere3', fields=('name', 'unit', 'categories'))
                imp.write_database()

                # Step 4: Rename the newly created target database
                bw.Database(target).rename(target + '_' + database)

                # Step 5: Populate the dictionary with activity keys
                for act in bw.Database(target + '_' + database):
                    dict_activities[(act['name'], act['location'], act['database'])] = act.key

        return dict_activities
    
    def identify_dependent_activities(name_database):
        """
        Identifies dependent activities in target databases to DEALA database and creates a dictionary of matches.

        This function performs the following steps:
        1. Retrieves lists of target and DEALA databases.
        2. Creates a dictionary mapping target databases to corresponding DEALA databases.
        3. Iterates through target databases and identifies dependent activities.
        4. Populates a dictionary of matches for each activity.

        Args:
            target_db (str): Name of target database (e.g. 'Energy' or 'Transport').

        Returns:
            dict: A dictionary mapping input keys to lists of dependent activities.
            dict: A dictionary containing the matches of the databases.
            list: A list containing the DEALA databases stored in the project.
            list: A list containing the Target databases stored in the project.
        """
        lst_DB_DEALA = []
        lst_DB = []

        # Step 1: Retrieve lists of target and DEALA databases
        for database in bw.databases:
            if name_database in database and 'ecoinvent' in database:
                lst_DB.append(database)
            elif 'DEALA' in database:
                lst_DB_DEALA.append(database)

        # Step 2: Create a dictionary mapping target databases to DEALA databases
        # dict_databases = {key: value for key, value in zip(lst_DB, lst_DB_DEALA)}
        dict_databases={}
        for string in lst_DB:
            last_part=string.rsplit('_', 1)[-1]
            for match in lst_DB_DEALA:
                if last_part in match:
                    dict_databases[string]=match


        # Step 3: Identify dependent activities in target databases
        dict_matches = {}
        for database in tqdm(lst_DB):
            for activity in bw.Database(database):
                list_countries = []
                for exchange in activity.technosphere():
                    if 'ecoinvent' in exchange.input['database']:
                        key = exchange.input
                        dict_matches[key] = [exchange.input]
                        act = exchange.input
                        list_inputs = [act]
                        list_countries.append(act['location'])
                        for exchange in act.technosphere():
                            if (
                                exchange.input['location'] != act['location']
                                and exchange.input['reference product'] == act['reference product']
                                and exchange.input['location'] not in list_countries
                            ):
                                list_inputs.append(exchange.input)
                                list_countries.append(exchange.input['location'])
                                dict_matches[key].append(exchange.input)
                        while list_inputs:
                            list_check = []
                            for exchange in list_inputs[0].technosphere():
                                if exchange.input['location'] not in list_check:
                                    list_check.append(exchange.input['location'])
                                else:
                                    list_countries.append(exchange.input['location'])
                            for exchange in list_inputs[0].technosphere():
                                if (
                                    exchange.input['location'] != act['location']
                                    and exchange.input['reference product'] == act['reference product']
                                    and exchange.input['location'] not in list_countries
                                ):
                                    list_inputs.append(exchange.input)
                                    list_countries.append(exchange.input['location'])
                                    dict_matches[key].append(exchange.input)
                            list_inputs.pop(0)

        return dict_databases, dict_matches, lst_DB_DEALA, lst_DB


    def copy_and_add_DEALA_activity(dict_databases, dict_target, dict_activities):
        """
        Copies activities of target database and adds DEALA activity to specified databases.

        Args:
            dict_databases (dict): A dictionary mapping database names to their values.
            dict_target (dict): A dictionary containing information related to target database.
            dict_activities (dict): A dictionary containing activity information.

        Returns:
            None
        """

        for key, value in tqdm(dict_databases.items(), desc='Copy target activities and add DEALA activity to database'):
            for act_DEALA in bw.Database(value):
                if act_DEALA['name'] in dict_target.keys():
                    # Get activity from energy database
                    act=bw.get_activity(dict_activities[(dict_target[act_DEALA['name']], 'GLO', bw.Database(key).name)])
                    # Copy activity with name from DEALA activity and respective country
                    act_copy=act.copy(name=act_DEALA['name'], location=act_DEALA['location'])
                    act_copy.new_exchange(input=act_DEALA.key, amount = 1, type='technosphere').save()

        # Example usage:
        # copy_and_add_DEALA_activity(my_dict_databases, my_dict_energy)

    def find_location(self, Loc, df):
        """
        Finds the appropriate location for a given activity based on geographical matching.

        Args:
            Loc (str): The location to match.
            df (pandas.DataFrame): A DataFrame containing relevant data.

        Returns:
            str: The matched location.
            
        Raises:
            ValueError: If the location is not found or if both GLO and ROW are unavailable.
        """
        geomatcher = Geomatcher()  # Initialize the Geomatcher
        locations = geomatcher.within(Loc, biggest_first=False)  # Get matching locations
        
        for location in locations:
            if "ecoinvent" in location:
                location = location[1]  # Extract the actual location name from ecoinvent
            if location in df.columns and not df[location].isnull().values.any():
                return location  # Return the location if it exists in the DataFrame
            elif location == "GLO" and location in df.columns and df[location].isnull().values.any():
                if "RoW" in df.columns and not df["RoW"].isnull().values.any():
                    location = "RoW"  # Use RoW if available
                    return location
                elif "RER" in df.columns and not df["RER"].isnull().values.any():
                    location = "RER"  # Use RER if available
                    return location
                else:
                    raise ValueError(f"{location} of activity not found, GLO and ROW also not available")
            elif location == "GLO" and location not in df.columns:
                if "RoW" in df.columns and not df["RoW"].isnull().values.any():
                    location = "RoW"  # Use RoW if available
                return location

    def calculate_price_based_on_margin(self, db, deala_db, list_names, percentage_margin=0.2, overwrite=True):
        """
        Calculates the price of end products based on a margin and adds them to the DEALA database.
        Args:
            db (str): The name of the database containing the end products.
            deala_db (str): The name of the DEALA database where the prices will be added.
            list_names (list): A list of names of end products to calculate prices for.
            percentage_margin (float): The percentage margin to apply to the cost. Default is 0.2 (20%).
            overwrite (bool): If True, existing activities in the DEALA database will be overwritten. Default is True.

        """
        db_marketsphere = bw.Database('marketsphere')
        exchange = db_marketsphere.search('end product', limit=1)


        methods = [m for m in bw.methods if 'DEALA-Cost (BEIC 1)' in str(m) and 'cost' in str(m)]
        activities = [act for act in db if act['reference product'] in list_names]
        prod_sys=[]
        for act in activities:
            prod_sys.append({act:1}) #Definition for 1 kg to represent the right amount in the end
        bw.calculation_setups['multiLCA'] = {'inv': prod_sys, 'ia': methods}
        myMultiLCA = bw.MultiLCA('multiLCA')
        scores = myMultiLCA.results

        dict_RD={}
        total_cost={}

        for index, element in enumerate(prod_sys):
            for key in element.items():
                dict_RD[f"{key[0]['name']}_{key[0]['location']}"] = scores[index][0]

        for act in activities:
            amount=dict_RD[f"{act['name']}_{act['location']}"]
            for exc in act.technosphere():
                if f"{exc.input['name']}_{exc.input['location']}" in dict_RD:
                    amount=amount-dict_RD[f"{exc.input['name']}_{exc.input['location']}"]*exc.amount
            total_cost[(act['name'], act['location'])] = amount

        for act in activities:
            # calculate the price based on the margin
            price = total_cost[(act['name'], act['location'])] * (1 + percentage_margin)
            # add DEALA activity representing the price of the pan to DEALA database
            if overwrite:
                # delete the existing activity if overwrite is True
                for existing_act in deala_db.search('end products - ' + db.name + act['location'], limit=1):
                    existing_act.delete()
            # create a new activity in the DEALA database with the price
            act_new = self.new_activity(deala_db.name, 'end products - ' + db.name, db.name, 'item', 'end products', location=act['location'])
            #add the exchange with the price
            act_new.new_exchange(input=exchange[0].key, amount=price, type='biosphere').save()

            # add act_new to act
            act.new_exchange(input=act_new.key, amount=1, type='technosphere').save()


    def update_exchanges(self, dict_matches, lst_DB1, lst_DB2):
        """
        Updates technosphere exchanges in the given databases based on geographical matching.

        Args:
            dict_matches (dict): A dictionary containing matched locations for input exchanges.
                                 The keys are tuples of (name, reference product, location) and the values are lists of tuples
                                 with the same information for matched activities.
            lst_DB1 (list): A list of target-related database names where the exchanges will be updated.
            lst_DB2 (list): A list of ecoinvent database names to search for matching activities.

        Returns:
            None
        """
        
        for db1, db2 in zip(lst_DB1, lst_DB2):  
            for act in tqdm(bw.Database(db1)):
                for exc in act.technosphere():
                    if (exc.input['name'], exc.input['reference product'], exc.input['location']) in dict_matches:
                        list_locations = []
                        list_names = []
                        for entry in dict_matches[(exc.input['name'], exc.input['reference product'], exc.input['location'])]:
                            list_names.append((entry[0], entry[1]))
                            list_locations.append(entry[2])
                        df = pd.DataFrame([list_names], columns=list_locations)
                        location = self.find_location(act['location'], df)
                        results = bw.Database(db2).search(df[location][0][0] + " " + location, limit=1000)
                        for result in results:
                            if (
                                result['name'] == df[location].values[0][0]
                                and result['reference product'] == df[location].values[0][1]
                                and result['location'] == location
                            ):
                                exc.delete()
                                act.new_exchange(input=result, amount=exc.amount, type='technosphere').save()

    # Example usage:
    # update_exchanges(dict_matches, lst_DB_Energy)


    def identify_matches(database_name):
        """
        Identify dependent activities in the specified ecoinvent database.

        Parameters:
        database_name (str): The name of the ecoinvent database to search.

        Returns:
        dict: A dictionary where the keys are tuples containing the name, reference product, and location of the input,
            and the values are lists of tuples with the same information for dependent activities.
        """
        dict_matches = {}

        # Iterate over each activity in the specified database
        for activity in tqdm(bw.Database(database_name)):
            list_countries = []

            # Iterate over each technosphere exchange of the activity
            for exchange in activity.technosphere():
                if 'ecoinvent' in exchange.input['database']:
                    key = (exchange.input['name'], exchange.input['reference product'], exchange.input['location'])
                    dict_matches[key] = [(exchange.input['name'], exchange.input['reference product'], exchange.input['location'])]
                    act = exchange.input
                    list_inputs = [act]
                    list_countries.append(act['location'])

                    # Iterate over each technosphere exchange of the current activity
                    for exchange in act.technosphere():
                        if (
                            exchange.input['location'] != act['location']
                            and exchange.input['reference product'] == act['reference product']
                            and exchange.input['location'] not in list_countries
                        ):
                            list_inputs.append(exchange.input)
                            list_countries.append(exchange.input['location'])
                            dict_matches[key].append((exchange.input['name'], exchange.input['reference product'], exchange.input['location']))

                    # Process the list of inputs
                    while list_inputs:
                        list_check = []

                        # Iterate over each technosphere exchange of the first input in the list
                        for exchange in list_inputs[0].technosphere():
                            if exchange.input['location'] not in list_check:
                                list_check.append(exchange.input['location'])
                            else:
                                list_countries.append(exchange.input['location'])

                        for exchange in list_inputs[0].technosphere():
                            if (
                                exchange.input['location'] != act['location']
                                and exchange.input['reference product'] == act['reference product']
                                and exchange.input['location'] not in list_countries
                            ):
                                list_inputs.append(exchange.input)
                                list_countries.append(exchange.input['location'])
                                dict_matches[key].append((exchange.input['name'], exchange.input['reference product'], exchange.input['location']))

                        list_inputs.pop(0)

        return dict_matches

    # Example usage
    # database_name = "Energy_ecoinvent 3.9.1-cutoff_ecoSpold02"
    # dependent_activities = identify_dependent_activities(database_name)
    # print(dependent_activities)


    def regionalize_process(self, database_name, dict_countries):
        """
        Regionalizes processes and their exchanges in a specified database.
        This function creates regionalized copies of processes in the foreground system 
        based on the provided dictionary of countries. It then updates the exchanges 
        of the copied activities to match the location-specific processes.
        Args:
            database_name (str): The name of the database containing the processes to be regionalized.
            dict_countries (dict): A dictionary where keys are country identifiers and values are country names.
        Returns:
            None: The function modifies the database in place by creating regionalized copies 
            of processes and updating their exchanges.
        Notes:
            - The function assumes that the database contains processes with a 'location' attribute.
            - Exchanges are updated to match the location-specific processes based on their name, 
              reference product, and location.
            - The function uses the Brightway2 framework for database and activity manipulation.
        """
        
        # create regionalized copies of processes in the foreground system
        activities = [act for act in bw.Database(database_name)]
        for country in dict_countries.values():
            for act in activities:
                act.copy(name=act['name'], location=country)

        # regionalize exchanges of copied activities
        activities = [act for act in bw.Database(database_name)]
        for act in tqdm(activities, "change activity location"):
            exchanges = [exc for exc in act.technosphere()]
            for exc in exchanges:
                list_possibilities = []
                for alt in bw.Database(exc.input['database']):  
                    if exc.input['name'] == alt['name'] and exc.input['reference product'] == alt['reference product']:
                        list_possibilities.append(alt)
                geomatcher = Geomatcher()  # Initialize the Geomatcher
                locations = geomatcher.within(act['location'], biggest_first=False)
                matched_item = None  # To store the result

                for location in locations:
                    # Extract location from ecoinvent tuple if needed
                    if isinstance(location, tuple) and "ecoinvent" in location:
                        location = location[1]

                    # Check if this location is part of any item['location']
                    for item in list_possibilities:
                        if location in item['location']:
                            matched_item = item
                            break
                    if matched_item:
                        break  # Exit the outer loop if a match is found

                    # Special case: location is "GLO" but not present in list_possibilities
                    if location == "GLO" and not any("GLO" in item['location'] for item in list_possibilities):
                        if any("RoW" in item['location'] for item in list_possibilities):
                            matched_item = next(item for item in list_possibilities if "RoW" in item['location'])
                            break
                        elif any("RER" in item['location'] for item in list_possibilities):
                            matched_item = next(item for item in list_possibilities if "RER" in item['location'])
                            break

                # If no match is found at all
                if not matched_item:
                    print(f"No matching item found for {act}")



                act.new_exchange(
                    input=matched_item.key, amount=exc.amount, type="technosphere"
                ).save()
                exc.delete()
                act.save()


    def add_social_exchanges(self, lst_DB, df_social, fp, dict_project, target):
        """
        Adds social exchange data to specified databases.

        This method reads a JSON file containing cost data, filters the social exchanges
        DataFrame for the specified target activity, and iterates through the provided databases.
        For each activity in the databases, it identifies technosphere exchanges related to 'DEALA',
        retrieves the corresponding biosphere exchange amount, finds the location in the filtered
        DataFrame, and creates a new technosphere exchange using the project dictionary.

        Parameters:
            lst_DB (list): List of database names to process.
            df_social (pd.DataFrame): DataFrame containing social exchange information.
            fp (str): File path to the JSON file with cost data.
            dict_project (dict): Dictionary mapping project data for exchange creation.
            target (str): Target activity name to filter social exchanges.

        Returns:
            None

        Notes:
            - Uses tqdm for progress visualization.
            - Modifies the databases by adding new technosphere exchanges.
        """
        # Read json file including data for electricity cost
        with open(fp) as f:
            data = json.load(f)

        # Definition of df_result (row showing the social exchanges for electricity)
        mask = (df_social["Activity"] == target)
        df_result = df_social[mask]

        for database in lst_DB:
            for act in tqdm(bw.Database(database)):
                for exchange in act.technosphere():
                    if "DEALA" in exchange.input['database']:
                        for bio in exchange.input.biosphere():
                            amount = bio.amount
                        loc = self.find_location(act['location'], df_result)
                        act.new_exchange(
                            input=dict_project[(df_result[loc].values[0], df_result[loc].values[0], loc, 'shdb')],
                            amount=amount,
                            type='technosphere'
                        ).save()


    def calculate_investments_buildings_machine(self, db_act, machinery_keyword, building_keyword):
        """
        # Calculate the total investments for machinery and buildings

        Parameters:
            db_act (bw.Database): The foreground database containing activities.
            machinery_keyword (str): Keyword to identify machinery-related investments.
            building_keyword (str): Keyword to identify building-related investments.

        Returns:
            tuple: Two dictionaries containing investments for machinery and buildings as well as the sum of both.
                Format: (dict_machine, dict_buildings, total_investments)
        """
        # Dictionary for investment of machinery and equipment
        dict_machine = {}
        # Dictionary for investment of buildings
        dict_buildings = {}

        # Calculate investments for machinery
        for act in db_act:
            for exc in act.technosphere():
                if machinery_keyword in exc.input['name']:
                    dict_machine[(act['name'], act['location'])] = exc['amount']

        # Calculate investments for buildings
        for act in db_act:
            for exc in act.technosphere():
                if building_keyword in exc.input['name']:
                    for bio in exc.input.biosphere():
                        dict_buildings[(act['name'], act['location'])] = exc['amount'] * bio['amount']

        # Calculate the total investments for machinery and buildings
        total_investments = {}

        for key in dict_machine.keys():
            total_investments[key] = dict_machine[key]

        for key in dict_buildings.keys():
            if key in total_investments:
                total_investments[key] += dict_buildings[key]
            else:
                total_investments[key] = dict_buildings[key]

        return dict_machine, dict_buildings, total_investments
    
    def dependent_DEALA_activity_percentage_rate(self, db_act, db_deala, dict_investment, percentage_rate, keyword=None, amount=1, location=None):
        """
        Adds dependent DEALA activities with a percentage rate to the specified database.

        Parameters:
            db_act (bw.Database): The foreground database containing activities.
            db_deala (bw.Database): The DEALA database containing percentage rate activities.
            dict_investment (dict): A dictionary mapping activity names and locations to investment amounts.
            percentage_rate (str): Keyword to identify percentage rate activities in the DEALA database.
            amount (float, optional): Multiplier for the investment amount. Defaults to 1.
            location (str, optional): Location to filter activities. If None, location is ignored.

        Returns:
            None: The function modifies the database in place by adding new exchanges.
        """
        for exc in db_deala:
            if percentage_rate in exc['name'] and (keyword is None or keyword in exc['reference product']):
                # Add new exchange to activity
                for key in dict_investment.keys():
                    for act in db_act:
                        if key[0] in act['name'] and key[1] == act['location'] and (location is None or act['location'] == location):
                            act.new_exchange(input=exc.key, amount=dict_investment[key] * amount, type='technosphere').save()


    def calculate_personnel_cost_processes(self, db_act):
        """
        Calculate the personnel costs associated with processes in a given database.

        This function iterates through the activities in the provided database and calculates
        the personnel costs for each activity based on the technosphere exchanges and their
        corresponding biosphere flows.


            dict: A dictionary containing personnel costs for each activity, with keys as tuples
              of activity name and location, and values as the calculated personnel cost.
        """
        # Dictionary for personnel cost of processes
        dict_personnel = {}


        #calculate personnel cost of each activity of database
        for act in db_act:
            for exc in act.technosphere():
                if "personnel" in exc.input['name']:
                    for bio in exc.input.biosphere():
                        personnel_cost=exc.amount*bio.amount
                    dict_personnel[(act['name'], act['location'])] = personnel_cost

        return dict_personnel
    

    def calculate_total_cost_processes(self, db_act):
        """
        Calculate the total cost of processes in a given database.

        This function computes the total cost of each activity in the provided database, including all associated costs
        and subtracting the costs of dependent activities. It uses Brightway2's MultiLCA functionality to perform the 
        calculations based on predefined impact assessment methods.

        Args:
            db_act (bw.Database): The foreground database containing activities.

        Returns:
            dict: A dictionary containing the total cost for each activity, with keys as tuples of activity name and location,
                  and values as the calculated total cost.
        """
 
        #Definition of all methods to calculate the cost before taxes
        methods = [m for m in bw.methods if 'DEALA-Cost (BEIC 1)' in str(m) and 'cost' in str(m)]

        #calculate the total cost of acitvities
        prod_sys=[]
        for act in db_act:
            prod_sys.append({act:1}) #Definition for 1 kg to represent the right amount in the end
        bw.calculation_setups['multiLCA'] = {'inv': prod_sys, 'ia': methods}
        myMultiLCA = bw.MultiLCA('multiLCA')
        scores = myMultiLCA.results

        dict_RD={}
        total_cost={}

        for index, element in enumerate(prod_sys):
            for key in element.items():
                dict_RD[f"{key[0]['name']}_{key[0]['location']}"] = scores[index][0]

        for act in db_act:
            amount=dict_RD[f"{act['name']}_{act['location']}"]
            for exc in act.technosphere():
                if f"{exc.input['name']}_{exc.input['location']}" in dict_RD:
                    amount=amount-dict_RD[f"{exc.input['name']}_{exc.input['location']}"]*exc.amount
            total_cost[(act['name'], act['location'])] = amount

        return total_cost
    
    def calculate_total_cost_processes_wo_co_products(self, db_act):
            """
            Calculate the total cost of processes in a given database.

            This function computes the total cost of each activity in the provided database, including all associated costs
            and subtracting the costs of dependent activities. It uses Brightway2's MultiLCA functionality to perform the 
            calculations based on predefined impact assessment methods.

            Args:
                db_act (bw.Database): The foreground database containing activities.

            Returns:
                dict: A dictionary containing the total cost for each activity, with keys as tuples of activity name and location,
                    and values as the calculated total cost.
            """
    
            #Definition of all methods to calculate the cost before taxes
            methods = [m for m in bw.methods if 'DEALA-Cost (BEIC 3)' in str(m) and 'cost' in str(m) and 'co-product' not in str(m)]

            #calculate the total cost of acitvities
            prod_sys=[]
            for act in db_act:
                prod_sys.append({act:1}) #Definition for 1 kg to represent the right amount in the end
            bw.calculation_setups['multiLCA'] = {'inv': prod_sys, 'ia': methods}
            myMultiLCA = bw.MultiLCA('multiLCA')
            scores = myMultiLCA.results

            dict_RD={}
            total_cost={}

            for index, element in enumerate(prod_sys):
                for key in element.items():
                    dict_RD[f"{key[0]['name']}_{key[0]['location']}"] = sum(scores[index])

            for act in db_act:
                amount=dict_RD[f"{act['name']}_{act['location']}"]
                for exc in act.technosphere():
                    if f"{exc.input['name']}_{exc.input['location']}" in dict_RD:
                        amount=amount-dict_RD[f"{exc.input['name']}_{exc.input['location']}"]*exc.amount
                total_cost[(act['name'], act['location'])] = amount

            return total_cost



    def calculate_profit_processes(self, db_act, final_product):
        """
        Calculate the profit associated with processes in a given database before taxes.

        This function iterates through the activities in the provided database and calculates
        the profit for each activity that matches the specified final product. The profit is 
        computed using Brightway2's MultiLCA functionality based on predefined impact assessment 
        methods for DEALA profit.

        Args:
            db_act (bw.Database): The foreground database containing activities.
            final_product (str): The name of the final product to filter activities.

        Returns:
            float: The total profit sum for the specified final product before taxes.
        """

        #Definition of all methods to calculate the cost before taxes
        methods = [m for m in bw.methods if 'DEALA-Profit (BEIC 1)' in str(m) and 'profit' in str(m)]

        total_profit={}

        #calculate the profit of acitvities before taxes
        for act in db_act:
            profit_sum = 0
            if final_product in act['name']:
                prod_sys=[]
                prod_sys.append({act:1}) #Definition for 1 kg to represent the right amount in the end
                profit_sum = 0
                bw.calculation_setups['multiLCA'] = {'inv': prod_sys, 'ia': methods}
                myMultiLCA = bw.MultiLCA('multiLCA')
                profits = myMultiLCA.results
                for profit in profits[0]:
                    profit_sum = profit_sum + profit

                total_profit[(act['name'], act['location'])] = profit_sum

        return total_profit

    def calculate_impacts_per_activity(self, process_system, methods_list, file_paths, method_mapping):
        """
        Calculate environmental and economic impacts for each activity in the foreground system.

        Parameters:
        - process_system (list): List of reference flows representing the production system.
        - methods_list (list): List of impact assessment methods to be applied.
        - file_paths (dict): Dictionary mapping reference flows to file paths for saving results.
        - method_mapping (dict): Dictionary mapping method tuples to readable method names.

        Returns:
        - results (list): List of calculated results for each reference flow.
        """
        from openpyxl import load_workbook
        from tqdm import tqdm

        results = []
        for reference_flow in process_system:
            impact_results = {}
            lca_instance = bw.LCA(reference_flow)
            lca_instance.lci()

            # Determine file path for the reference flow
            try:
                file_path = file_paths[reference_flow['database']]
            except KeyError:
                file_path = file_paths[str(reference_flow)]

            # Iterate over all methods and calculate impacts
            for method in tqdm(methods_list):
                lca_instance.switch_method(method)
                impact_data = bwa.traverse_tagged_databases(reference_flow, method, label='name')
                impact_values = impact_data[0].values()
                impact_labels = list(impact_data[0].keys())

                # Filter out zero values
                filtered_labels = [label for label, value in zip(impact_labels, impact_values) if value != 0]
                filtered_values = [value for value in impact_values if value != 0]

                # Create a DataFrame for the results
                impact_df = pd.DataFrame({'Process': filtered_labels, 'Value': filtered_values})
                impact_results[method_mapping[method][0]] = impact_df

            # Save results to an Excel file
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for sheet_name, df in impact_results.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            results.append(impact_results)

        return results
    
    def generate_stacked_bar_chart_process_view(self, file_name, file_path, dict_method, methods, custom_colors=None, title_diagram=None):
        """
        Generate an interactive stacked bar chart for a given file and method dictionary.

        Parameters:
        - file_name (str): The name of the file (e.g., 'batch').
        - file_path (str): The path to the directory containing the file.
        - dict_method (dict): A dictionary mapping method tuples to readable method names.
        - methods (list): A list of methods to be visualized.
        - custom_colors (list): List of custom colors for the bars. If None, default Plotly colors are used.

        Returns:
        - None: Displays the interactive stacked bar chart.
        """

        # Default Plotly colors if no custom colors are provided
        if custom_colors is None:
            custom_colors = px.colors.qualitative.Plotly

        # Initialize an empty dictionary to store dataframes
        dict_df = {}

        # Iterate through files in the specified directory
        for file in os.listdir(file_path):
            if file_name in file:  # Check if the file name matches the input
                parts = file.split('_')
                if len(parts) >= 2:
                    last_part = parts[-1].replace('.xlsx', '')  # Extract country code
                    country_code = last_part
                # Read each sheet in the Excel file and store it in the dictionary
                for sheet in pd.ExcelFile(os.path.join(file_path, file)).sheet_names:
                    dict_df[(country_code, sheet)] = pd.read_excel(
                        os.path.join(file_path, file), sheet_name=sheet
                    )

        # Iterate through methods in the dictionary
        for method in methods:
            # Filter dataframes based on the method
            if method not in dict_method:
                print(f"Method {method} not found in dict_method.")
                continue
            filtered = {k: v for k, v in dict_df.items() if k[1] == dict_method[method][0]}
            if filtered == {}:
                print(f"No data found for method {method}.")
                continue
            for (country, _), df in filtered.items():
                df["Countries"] = country  # Add a column for country
            # Combine all filtered dataframes
            df_combined = pd.concat(filtered.values(), keys=filtered.keys(), ignore_index=True)

            # Calculate totals for each country
            totals = df_combined.groupby("Countries")["Value"].sum().to_dict()

            # Create an interactive stacked bar chart
            fig = px.bar(
                df_combined,
                x="Value",
                y="Countries",
                color="Process",
                orientation="h",
                color_discrete_sequence=custom_colors,  # Use user-defined colors
                labels={"Value": dict_method[method][1]},
                title=f"Impact Category: {method[1]} - {title_diagram}"
            )

            # Add diamonds to represent total values
            for country, total in totals.items():
                fig.add_scatter(
                    x=[total],
                    y=[country],
                    mode="markers",
                    marker=dict(symbol="diamond", size=10, color="black"),
                    name="Total",
                    showlegend=False
                )

            # Update layout and display the chart
            fig.update_layout(barmode='relative')
            fig.show()

    def create_horizontal_bar_plot_DEALA(self, df, title="Horizontal Bar Plot", custom_colors=None):
        """
        Creates a horizontal bar plot for the given DataFrame, visualizing the impact categories 
        across different BEIC levels. The plot is interactive and uses Plotly for visualization.

        Parameters:
        - df (pd.DataFrame): Input DataFrame containing the data to be visualized.
        - title (str): Title of the plot. Default is "Horizontal Bar Plot".
        - custom_colors (list): List of custom colors for the bars. If None, default Plotly colors are used.

        Returns:
        - None: Displays the plot in the notebook.
        """


        # Default Plotly colors if no custom colors are provided
        if custom_colors is None:
            custom_colors = px.colors.qualitative.Plotly

        # Define BEIC levels
        beic_levels = ['BEIC 3', 'BEIC 2', 'BEIC 1']

        for index in df.index:
            df_index = df.loc[index]
            country = index.split("item,")[1].split(",")[0].strip()
            scenario = index.split("item,")[1].strip()

            # Extract and sort impact categories
            categories = df_index.index
            sorted_categories = sorted(categories, key=lambda x: (x.split(' - ')[0], x.split(' - ')[-1]))
            impact_categories = list({cat.split(' - ')[-1] for cat in sorted_categories})
            impact_categories.sort()

            # Map impact categories to BEIC levels
            data_per_category = {impact: [0, 0, 0] for impact in impact_categories}

            for category in sorted_categories:
                impact_name = category.split(' - ')[-1]
                beic_name = next(b for b in beic_levels if b in category)
                beic_index = beic_levels.index(beic_name)
                value = df_index[category]
                data_per_category[impact_name][beic_index] = value

            # Create bar traces for each impact category
            traces = []
            for i, impact in enumerate(impact_categories):
                values = data_per_category[impact]
                traces.append(go.Bar(
                    y=beic_levels,
                    x=values,
                    name=impact,
                    orientation='h',
                    marker_color=custom_colors[i % len(custom_colors)],
                    customdata=np.array(beic_levels).reshape(-1, 1),
                    hovertemplate='%{customdata[0]}<br>Kategorie: ' + impact + '<br>Wert: %{x:.2f}<extra></extra>',
                ))

            # Calculate total value for the title (only BEIC 1)
            total_value = sum(data_per_category[impact][2] for impact in impact_categories)
            total_str = f"{total_value:,.2f}" if total_value <= 10 else f"{total_value:,.0f}"
            total_str = total_str.replace(',', 'X').replace('.', ',').replace('X', '.')

            # Create the plot
            fig = go.Figure(data=traces)

            fig.update_layout(
                barmode='relative',
                title=f'{title} = {total_str} USD ({scenario})',
                xaxis_title='USD',
                yaxis=dict(
                    categoryorder='array',
                    categoryarray=beic_levels,
                    title=None
                ),
                legend=dict(title='Impact Categories'),
            )

            # Display the plot
            fig.show()





        

                        


