#! /usr/bin/env python3


"""
COMP3311
24T1
Assignment 2
Pokemon Database

Written by: <Gul Jain> <z5430560>
Written on: <21/04/2024>

File Name: Q1.py

Description: List the number of pokemon and the number of locations in each game
"""

import sys
import psycopg2
import helpers

# Constants
USAGE = f"Usage: {sys.argv[0]}"

def main(db):

    #creating a cursor. 
    cursor = db.cursor()

    # sql query to fetch the game's region, game name and number of pokemons and locations in the game. 
    query = """
        SELECT games.region AS Region,
            games.name AS Game,
                COUNT( DISTINCT pokedex.national_id) as Pokemon,
            COUNT(DISTINCT locations.id) AS locations
        FROM games
        JOIN locations ON locations.appears_in = games.id
        JOIN pokedex ON pokedex.game = games.id 
        GROUP BY games.name, games.region
        ORDER BY games.region, games.name
    """

    # printing header 
    print("Region Game              #Pokemon #Locations")

    # executing the query. 
    cursor.execute(query)

    # fetching results into rows. 
    rows = cursor.fetchall()
    
    # iterarting over rows. 
    for row in rows:
        # fetching values 
        regionName, gameName, numPokemon, numLocation = row

        #printinng
        print(f"{regionName:<6} {gameName:<17} {numPokemon:<8} {numLocation}")

    # closing the cursor. 
    cursor.close()

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






