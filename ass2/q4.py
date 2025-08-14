#! /usr/bin/env python3


"""
COMP3311
24T1
Assignment 2
Pokemon Database

Written by: <Gul Jain> <z5430560>
Written on: <21/04/2024>

File Name: Q4

Description: Print the best move a given pokemon can use against a given type in a given game for each level from 1 to 100
"""

# importing libraries. 
import sys
import psycopg2
import helpers


# command line incorrect agruments error message. 
USAGE = f"Usage: {sys.argv[0]} <Game> <Attacking Pokemon> <Defending Pokemon>"
#*******************************************************************
def main(db):

    # checking if correct arguemtns were passed. 
    if len(sys.argv) != 4:
        print(USAGE)
        return 1

    # fetching arguemnts
    game_name = sys.argv[1]
    attacking_pokemon_name = sys.argv[2]
    defending_pokemon_name = sys.argv[3]

    # creating the cursor. 
    cursor = db.cursor()
#*******************************************************************

    # query to fetch game id. 
    query = """
    SELECT 
        ID 
    FROM 
        Games 
    WHERE 
        name = %s
    """

    # executing the query.
    cursor.execute(query, (game_name,))

    # fetching game_id. 
    game_id = cursor.fetchone()
    
 #*******************************************************************
    # query to fetch first and seccond type of attacking pokemon. 
    query = """
        SELECT 
            First_Type, 
            Second_Type
        FROM 
            Pokemon WHERE Name = %s
    """
    cursor.execute(query, (attacking_pokemon_name,))
    attacking_pokemon = cursor.fetchone()

    # if attacking pokemon not found. 
    if (attacking_pokemon is None): 
        print(f'Pokemon "{attacking_pokemon_name}" does not exist')
        return 1
    # storing first and second type into respective variables. 
    attacking_pokemon_f_type = attacking_pokemon[0]
    attacking_pokemon_s_type = attacking_pokemon[1]
#*******************************************************************
    # query to fetch first and seccond type of defending pokemon. 
    query = """
        SELECT 
            First_Type, 
            Second_Type
        FROM 
            Pokemon WHERE Name = %s
    """
    
    cursor.execute(query, (defending_pokemon_name,))
    defending_pokemon = cursor.fetchone()

    # if defending pokemon not found. 
    if (defending_pokemon is None): 
        print(f'Pokemon "{defending_pokemon_name}" does not exist')
        return 1

   # storing first and second type into respective variables.
    defending_pokemon_f_type = defending_pokemon[0]
    defending_pokemon_s_type = defending_pokemon[1]
#*******************************************************************

    # query to fetch name of move, its effective power and the requriements for the move. 
    query = """
    SELECT
        moves.name,
        FLOOR(
            FLOOR(
                CASE
                    WHEN moves.Of_Type IN (%s, %s) THEN FLOOR (moves.Power * 1.5)
                    ELSE moves.Power
                END
            ) * COALESCE( NULLIF(type_eff1.multiplier, 1) / 100.0, 1)
              * COALESCE( NULLIF(type_eff2.multiplier, 1) / 100.0, 1)
        ) AS effective_power,
        STRING_AGG(requirements.Assertion, ' OR ' ORDER BY requirements.ID) 
    FROM
        moves
        JOIN 
            learnable_moves ON learnable_moves.Learns = moves.ID
        JOIN
            pokemon ON pokemon.ID = learnable_moves.Learnt_By
        JOIN 
            types ON moves.Of_Type = types.ID
        LEFT JOIN 
            type_effectiveness type_eff1 ON type_eff1.attacking = types.ID 
                AND type_eff1.Defending = %s

        LEFT JOIN 
            type_effectiveness type_eff2 ON type_eff2.attacking = types.ID 
                AND type_eff2.Defending = %s 
                AND type_eff2.Defending IS NOT NULL
        JOIN 
            requirements ON learnable_moves.Learnt_When = requirements.ID
    WHERE
        moves.Power IS NOT NULL
        AND 
            pokemon.name = %s
        AND 
            learnable_moves.Learnt_In = %s
        
    GROUP BY
        moves.name, 
        effective_power
    ORDER BY
        effective_power DESC,
        moves.name
    """
    # executing the query. 
    cursor.execute(query, (attacking_pokemon_f_type,
    attacking_pokemon_s_type, 
    defending_pokemon_f_type,
    defending_pokemon_s_type,
    attacking_pokemon_name, game_id))

    # fetching results. 
    moves = cursor.fetchall()
#*******************************************************************
    # if no moves found 
    if moves is None:
        print("No moves available or no type effectiveness data found.")
        return 0 
    
    # if moves found 
    print(f'If "{attacking_pokemon_name}" attacks "{defending_pokemon_name}" in "{game_name}" it\'s available moves are:')

    # iterating over moves
    for move in moves:

        # fetching values
        mv_name, effective_pwr, reqs = move

        # printing
        print(f'\t{mv_name}')

        print(f'\t\twould have a relative power of {effective_pwr}')

        print(f'\t\tand can be learnt from {reqs}')

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
