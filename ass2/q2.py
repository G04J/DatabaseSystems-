#! /usr/bin/env python3
"""
COMP3311
24T1
Assignment 2
Pokemon Database

Written by: <Gul Jain> <z5430560>
Written on: <21/04/2024>

File Name: Q2

Description: List all locations where a specific pokemon can be found
"""

# HELPER FUNCTIONS 

#helper function to get the column length for each column
#************************************************************
def maxColLen(headers, results): 

    # initializing an array that stores length of headers of each column. 
    max_col_len = [len(header) for header in headers]
    
    # iterating over the results. 
    for row in results:

        # changing rows to type 'list'
        row = list(row)

        # joining the fifth element of the row if it is a list. 
        row[5] = ", ".join(row[5])
        
        # iterating over the row to fetch the maximum col length
        for i in range(len(row)):

            # changing the value of the max column if the length of the element 
            # is larger than the value of max_col_len[i]. 
            max_col_len[i] = max(max_col_len[i], len(str(row[i])))  
    
    return max_col_len
#************************************************************

#Importing libraries
import sys
import psycopg2
import helpers

#command line argument error message
USAGE = f"Usage: {sys.argv[0]} <pokemon_name>"

def main(db):

    # checking if correct agurments are passed. 
    if len(sys.argv) != 2:
        print(USAGE)
        return 1

    #noting pokemon name from command line 
    pokemon_name = sys.argv[1]

    #creating a cursor 
    cur = db.cursor()
#************************************************************
    
    #writing a sql query. 
    query = """
        SELECT 
            games.name, 
            locations.name, 

            -- changing rarity from integers to strings of 'common', 'uncommon', 
            -- 'rare' and 'Limited' based on their values. 
            CASE
                WHEN encounters.rarity < 1 THEN 'Limited' 
                WHEN encounters.rarity < 6 THEN 'Rare'
                WHEN encounters.rarity < 21 THEN 'Uncommon'
                ELSE 'Common'
                END AS rarity,

            (encounters.levels).min, 
            (encounters.levels).max, 
            STRING_AGG(
                CASE 
                    WHEN encounter_requirements.inverted THEN 'Not ' || requirements.assertion 
                    ELSE requirements.assertion 
                END, 
                ', ' ORDER BY requirements.assertion
            ) AS requirements
        FROM 
            encounters
            JOIN pokemon ON encounters.occurs_with = pokemon.id
            JOIN locations ON encounters.occurs_at = locations.id
            JOIN games ON locations.appears_in = games.id
            LEFT JOIN encounter_requirements ON encounters.id = encounter_requirements.encounter
            LEFT JOIN requirements ON encounter_requirements.requirement = requirements.id
        WHERE 
            pokemon.name = %s
        GROUP BY 
            games.region, 
            games.name, 
            locations.name,
            encounters.rarity,
            (encounters.levels).min, 
            (encounters.levels).max,
            encounters.id 
        ORDER BY 
            games.region, 
            games.name, 
            locations.name,
            rarity,
            (encounters.levels).min, 
            (encounters.levels).max,
            requirements
    """
    cur.execute(query, (pokemon_name,))
    results = cur.fetchall()
#************************************************************
    # initializing headers array. 
    headers = ["Game", "Location", "Rarity", "MinLevel", "MaxLevel", 
               "Requirements"]

    # calling function maxColLen to get the maximum col length
    max_col_len = maxColLen(headers, results)

    # creating the header with headers elements and max_col_len spacing. 
    header_row = ' '.join(map(lambda header, width: header.ljust(width), headers, max_col_len))

    # printing the header
    print(header_row)
#************************************************************

    # initialzing an empty array to store unique rows to ensure that we are not printing identical rows more than once. 
    UniqueRows = []

    # iterating over results. 
    for game, location, rarity, min_level, max_level, requirements in results:

        # noting down the requirements into a set from a string
        reqs = set(requirements.split(", "))
        # sorting the requirements after storing the reqs into a list as sets do not have indexes. 
        reqs = sorted(list(reqs))
        # joining the requirements into a set once again. 
        unique_requirements_str = ", ".join(reqs)

        # zipping together all the values with the max_col_len. 
        algined_entries = zip([game, location, rarity, min_level, max_level, unique_requirements_str],
                max_col_len)

        #initializing an empty array row. 
        row = []

        # iterating over algined_entires to give spacing. 
        for value, width in algined_entries:  
            row.append(str(value).ljust(width))
        
        # joining rows. 
        row = " ".join(row)

        # checking if the row is already present or not. 
        if (tuple(row) in UniqueRows):
            continue
        # adding the row to UniqueRows to keep check. 
        UniqueRows.append(tuple(row))
        
        #printing row 
        print(row)

#************************************************************
    cur.close()
    return 0

if __name__ == '__main__':
    exit_code = 0
    db = None
    try:
        db = psycopg2.connect(dbname="pkmon")
        exit_code = main(db)
    except psycopg2.Error as err:
        print("DB error: ", err)
        exit_code = 1
    except Exception as err:
        print("Internal Error: ", err)
        raise err
    finally:
        if db is not None:
            db.close()
    sys.exit(exit_code)
