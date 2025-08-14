#! /usr/bin/env python3

"""
COMP3311
24T1
Assignment 2
pokemon Database

Written by: <Gul Jain> <z5430560>
Written on: <21/04/2024>

File Name: Q5

Description: Print a formatted (recursive) evolution chain for a given pokemon
"""

# importing libraries 
import sys
import psycopg2
import helpers

# command line error message
USAGE = f"Usage: {sys.argv[0]} <pokemon_name>"

#***********************************************************************************************************************************

# pre-evolution pokemon function 
def pre_evolution_func(db, pokemon_name):

    # creating a cursor 
    cursor = db.cursor() 



    # sql query to get the pre evolution pokemon along with the evolution id. 
    query = """ 
        SELECT 
            pokemon.Name as pkname, 
            evolutions.id as evo_id 
        FROM 
            evolutions
        JOIN 
            pokemon ON (evolutions.Pre_Evolution).Pokedex_Number = (pokemon.id).Pokedex_Number
        AND 
            (evolutions.Pre_Evolution).Variation_Number = (pokemon.id).Variation_Number
        WHERE 
            (evolutions.Post_Evolution).Pokedex_Number = (SELECT (pokemon.id).Pokedex_Number FROM pokemon where name = %s)
        AND 
            (evolutions.Post_Evolution).Variation_Number = (SELECT (pokemon.id).Variation_Number FROM pokemon where name = %s)
        ORDER BY 
            evolutions.id 
        """
    # executing the query.
    cursor.execute(query, (pokemon_name, pokemon_name))

    # fetching data from query into pre_evo. 
    pre_evo = cursor.fetchall()
    
    # initiallizing an empty dict to store the pre_evo pokemons with along with their requirements. 
    pre_evo_pokemon = {}

    # looping through sql data
    for name, evolution_id in pre_evo:

        # sql query to fetch requirements and inverted status. 
        query = """
            SELECT 
                requirements.assertion as req_ass,  
                evolution_requirements.inverted as evo_inverted
            FROM 
                evolution_requirements
            JOIN 
                requirements ON evolution_requirements.Requirement = requirements.id 
            WHERE 
                evolution_requirements.evolution = %s 
            ORDER BY 
                evolution_requirements.inverted, requirements.id
        """
        
        # ecexuting the query 
        cursor.execute(query, (evolution_id,))

        # fetching requirements
        requirements_pre_pokemon = cursor.fetchall()

        # checking if there is already an entry with the given pokemon name
        if name in pre_evo_pokemon:
            
            # Convert to list if not already
            if not isinstance(pre_evo_pokemon[name], list):
                pre_evo_pokemon[name] = [pre_evo_pokemon[name]] 

            # formatting requirements 
            formatted_requirements = [req[0] if not req[1] else f"NOT {req[0]}" for req in requirements_pre_pokemon]

            # appending to the key - value list. 
            pre_evo_pokemon[name].append(formatted_requirements)
        else:
            # formatting requirements 
            formatted_requirements =[[req[0] if not req[1] else f"NOT {req[0]}" for req in requirements_pre_pokemon]]
            pre_evo_pokemon[name] = formatted_requirements
    
    # if pre_evo_pokemon is empty. i.e no pre-evolutions found. 
    if pre_evo_pokemon == {}:
        print(f"'{pokemon_name}' doesn't have any pre-evolutions.\n")
        return 0 

    # variables to check if or was used. 
    is_pre_or = False

    # iterating over the dict
    for pkmon in pre_evo_pokemon:

        print(f"'{pokemon_name}' can evolve from '{pkmon}' when the following requirements are satisfied:")

        # if there is more than one ways to evolve from 
        if len(pre_evo_pokemon[pkmon]) > 1:
            is_pre_or = True
        
        # if or needs to be used 
        if is_pre_or == True: 
            
            # iterating over the values of pokemon
            for i in pre_evo_pokemon[pkmon]:

                # if there are more than one reqs, i.e we need to use and 
                if len(i) > 1:
                    # printing and 
                    printed = "\n\t\tAND\n\t\t\t".join(i)
                    
                    # printing reqs 
                    print(f"\t\t\t{printed}")

                    # printing or. 
                    if is_pre_or:
                        print("\tOR\t")
                        is_pre_or = False
                # if we do not need to use and 
                else:
                    # printing reqs
                    print(f"\t\t{i[0]}\n")

                    # printing or 
                    if is_pre_or:
                        print("\tOR\t")
                        is_pre_or = False 

        # if or does not need to be used. 
        else: 

            for i in pre_evo_pokemon[pkmon]:

                # checking if there are more than one reqs , i.e and needs 
                if (len(i) > 1):

                    # printing and 
                    printed = "\n\tAND\n\t\t".join(i)
                    
                    # printing reqs
                    print(f"\t\t{printed}")
                # if no and and no or 
                else: 
                    # printing reqs 
                    print(f"\t{i[0]}\n")

        # recursively calling the function again. 
        pre_evolution_func(db, pkmon)
    
    return 0 
#***********************************************************************************************************************************

def post_evolution_func(db, pokemon_name):

    # creating a cursor 
    cursor = db.cursor()

    #initializing variables to check if 'or' or 'and' was used. 
    is_post_or = False
    is_post_and = False

    # sql query to get the post evolution pokemon along with the evolution id. 
    query = """ 
        SELECT 
            pokemon.Name as pkmon_name,
            evolutions.id as evo_id 
        FROM 
            evolutions
        JOIN 
            pokemon ON (evolutions.Post_Evolution).Pokedex_Number = (pokemon.id).Pokedex_Number
        AND 
            (evolutions.Post_Evolution).Variation_Number = (pokemon.id).Variation_Number
        WHERE 
            (evolutions.Pre_Evolution).Pokedex_Number = (SELECT (pokemon.id).Pokedex_Number FROM pokemon where name = %s)
        AND 
            (evolutions.Pre_Evolution).Variation_Number = (SELECT (pokemon.id).Variation_Number FROM pokemon where name = %s)
        ORDER BY 
            evolutions.id 
    """
    # executing the query.
    cursor.execute(query, (pokemon_name, pokemon_name))
    
    # fetching data from query into post_evo. 
    post_evo = cursor.fetchall()
    
    # initiallizing an empty dict to store the post_evo pokemons with along with their requirements. 
    post_evo_pokemon = {}
    
    # looping through sql data
    for name, evolution_id in post_evo:
    
        # sql query to fetch requirements and inverted status. 
        query = """
            SELECT 
                requirements.assertion as req_ass,  
                evolution_requirements.inverted as evo_inverted
            FROM 
                evolution_requirements
            JOIN 
                requirements ON evolution_requirements.Requirement = requirements.id 
            WHERE 
                evolution_requirements.evolution = %s 
            ORDER BY 
                evolution_requirements.inverted, requirements.id
        """
             # ecexuting the query 
        cursor.execute(query, (evolution_id,))

        # fetching requirements
        requirements_post_pokemon = cursor.fetchall()

        # checking if there is already an entry with the given pokemon name
        if name in post_evo_pokemon:
            
            # Convert to list if not already
            if not isinstance(post_evo_pokemon[name], list):
                post_evo_pokemon[name] = [post_evo_pokemon[name]] 

            # formatting requirements 
            formatted_requirements = [req[0] if not req[1] else f"NOT {req[0]}" for req in requirements_post_pokemon]

            # appending to the key - value list. 
            post_evo_pokemon[name].append(formatted_requirements)
        else:
            # formatting requirements 
            formatted_requirements =[[req[0] if not req[1] else f"NOT {req[0]}" for req in requirements_post_pokemon]]
            post_evo_pokemon[name] = formatted_requirements
    
    # if post_evo_pokemon is empty. i.e no post-evolutions found.
    if post_evo_pokemon == {}:
        print(f"\n'{pokemon_name}' doesn't have any post-evolutions.\n")
        return 0 

    # variables to check if or was used. 
    is_post_or = False

    # iterating over the dict
    for pkmon in post_evo_pokemon:
        print(f"'{pokemon_name}' can evolve into '{pkmon}' when the following requirements are satisfied:")

        # if there is more than one ways to evolve into 
        if len(post_evo_pokemon[pkmon]) > 1:
            is_post_or = True

        # if or needs to be used 
        if is_post_or == True:

            # iterating over the values of pokemon
            for i in post_evo_pokemon[pkmon]:

                # if there are more than one reqs, i.e we need to use and 

                if len(i) > 1:
                    # printing and 
                    printed = "\n\t\tAND\n\t\t\t".join(i)
                    # printing reqs 
                    print(f"\t\t\t{printed}")

                    # printing or.
                    if is_post_or:
                        print("\tOR\t")
                        is_post_or = False
                # if we do not need to use and 
                else:
                    # printing reqs
                    print(f"\t\t{i[0]}\n")

                    # printing or 
                    if is_post_or:
                        print("\tOR\t")
                        is_post_or = False 

        # if or does not need to be used.
        else: 
            for i in post_evo_pokemon[pkmon]:
                # checking if there are more than one reqs , i.e and needs
                if (len(i) > 1):

                    # printing and
                    printed = "\n\tAND\n\t\t".join(i)
                    
                    # printing reqs 
                    print(f"\t\t{printed}")

                # if no and and no or used
                else: 
                    # printing reqs
                    print(f"\t{i[0]}")

        # recursively calling the function again
        post_evolution_func(db, pkmon)
    
    return 0 

#***********************************************************************************************************************************
def main(db):
    
    # checking if correct number of arguments are called. 
    if len(sys.argv) != 2:
        print(USAGE)
        return 1

    # fetching pokemon name from the command line 
    pokemon_name = sys.argv[1]

    # calling pre evoultion function 
    pre_evolution_func(db, pokemon_name)

    # calling post evolution function 
    post_evolution_func(db, pokemon_name)

#***********************************************************************************************************************************

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
