/*
    COMP3311 24T1 Assignment 1
    IMDB Views, SQL Functions, and PlpgSQL Functions
    Student Name: <Gul Jain>
    Student ID: <z5430560>
*/

-- Question 1 --

/**
    Write a SQL View, called Q1, that:
    Retrieves the 10 movies with the highest number of votes.
*/
CREATE OR REPLACE VIEW Q1(Title, Year, Votes) AS
    -- TODO: Write your SQL query here
    SELECT primary_title AS Title, release_year AS Year, votes AS Votes
    FROM movies
    WHERE votes IS NOT NULL
    -- To get the votes in the order of highest to lowest
    ORDER BY votes DESC
    -- To fetch the top 10 votes.
    LIMIT 10
;

-- Question 2 --

/**
    Write a SQL View, called Q2(Name, Title), that:
    Retrieves the names of people who have a year of death recorded in the database
    and are well known for their work in movies released between 2017 and 2019.
*/
CREATE OR REPLACE VIEW Q2(Name, Title) AS
    -- selecting name from table people, and primary_title from movies.
    SELECT people.name AS Name, movies.primary_title AS Title 
    FROM people 
        JOIN principals ON people.id = principals.person
        JOIN movies ON principals.movie = movies.id
        JOIN releases ON movies.id = releases.movie
    -- Ensuring that year of death has been recorded. 
    WHERE people.death_year IS NOT NULL
    -- Adding constraints. 
    AND movies.release_year BETWEEN 2017 AND 2019
    GROUP BY people.name, movies.primary_title
    ORDER BY people.name
;

-- -- -- Question 3 --

/**
    Write a SQL View, called Q3(Name, Average), that:
    Retrieves the genres with an average rating not less than 6.5 and with more than 60 released movies.
*/
CREATE OR REPLACE VIEW Q3(Name, Average) AS
    -- Selecting name from table genres and average of score from movies up to two decimal places. 
    SELECT genres.name AS Name, ROUND(AVG(movies.score), 2) AS Average
    FROM genres 
        JOIN movies_genres ON genres.id = movies_genres.genre
        JOIN movies ON movies_genres.movie = movies.id
    GROUP BY genres.id
    -- Adding constraints according to the question. 
    HAVING COUNT(movies.id) > 60 AND AVG(movies.score) >= 6.5
    ORDER BY Average DESC, Name   
;
-- -- -- Question 4 --

/**
    Write a SQL View, called Q4(Region, Average), that:
    Retrieves the regions with an average runtime greater than the average runtime of all movies.
*/

CREATE OR REPLACE VIEW Q4(Region, Average) AS
    -- TODO: Write your SQL query here
    -- Selecting the region from table releases and average of runtime up to 0 decimal places. 
    SELECT region AS Region, ROUND(AVG(runtime),0) AS Average
    FROM releases
        JOIN movies ON releases.movie = movies.id
    WHERE runtime IS NOT NULL
    GROUP BY region
    HAVING AVG(runtime) > (SELECT AVG(runtime) FROM movies) 
    ORDER BY ROUND(AVG(runtime), 0) DESC, Region 
;

-- -- -- Question 5 --

-- /**
--     Write a SQL Function, called Q5(Pattern TEXT) RETURNS TABLE (Movie TEXT, Length TEXT), that:
--     Retrieves the movies whose title matches the given regular expression,
--     and displays their runtime in hours and minutes.
-- */
CREATE OR REPLACE FUNCTION Q5(Pattern TEXT)
    RETURNS TABLE (Movie TEXT, Length TEXT)
    AS $$
    -- selecting primary_title from movie and concating runtime into hours and minutes.
    SELECT primary_title AS Movie, CONCAT(ROUND(runtime / 60), ' Hours ', runtime % 60, ' Minutes') AS Length
    FROM movies
    -- Verifying if the primary_title of the movie matches the pattern given using regular expressions. 
    WHERE primary_title ~ Pattern AND runtime IS NOT NULL
    ORDER BY primary_title;
    $$ LANGUAGE SQL
;

-- -- -- Question 6 --

-- /**
--     Write a SQL Function, called Q6(GenreName TEXT) RETURNS TABLE (Year Year, Movies INTEGER), that:
--     Retrieves the years with at least 10 movies released in a given genre.
-- */
CREATE OR REPLACE FUNCTION Q6(GenreName TEXT)
    RETURNS TABLE (Year Year, Movies INTEGER)
    AS $$
        SELECT movies.release_year AS Year, COUNT(genres.name) AS Movies
        FROM movies 
        JOIN movies_genres ON movies_genres.movie = movies.id
        JOIN genres ON genres.id = movies_genres.genre
        WHERE movies.release_year IS NOT NULL AND genres.name = GenreName
        GROUP BY movies.release_year
        HAVING COUNT(genres.name) > 10
        ORDER BY COUNT(genres.name) DESC, movies.release_year DESC;
    $$ LANGUAGE SQL
;

-- -- Question 7 --

/**
    Write a SQL Function, called Q7(MovieName TEXT) RETURNS TABLE (Actor TEXT), that:
    Retrieves the actors who have played multiple different roles within the given movie.
*/
CREATE OR REPLACE FUNCTION Q7(MovieName TEXT)
    RETURNS TABLE (Actor TEXT)
    AS $$
        -- TODO: Write your SQL query here
        SELECT people.name AS Actor
        FROM roles
            JOIN movies ON movies.id = roles.movie
            JOIN people ON people.id = roles.person
        WHERE movies.primary_title = MovieName
        GROUP BY movies.primary_title, people.name
        HAVING COUNT(roles.person) > 1
        ORDER BY people.name
    $$ LANGUAGE SQL
;

-- Question 8 --

/**
    Write a SQL Function, called Q8(MovieName TEXT) RETURNS TEXT, that:
    Retrieves the number of releases for a given movie.
    If the movie is not found, then an error message should be returned.
*/

CREATE OR REPLACE FUNCTION Q8(MovieName TEXT)
    RETURNS TEXT
    AS $$
    DECLARE
        release_num INTEGER;
        does_movie_exist INTEGER;
    BEGIN
        -- checking if the movie exists in the database or not.
        SELECT COUNT(*) INTO does_movie_exist 
        FROM movies 
        WHERE primary_title = MovieName;
        -- If movie found 
        IF does_movie_exist > 0 THEN

            -- counting number of releases.
            SELECT COUNT(*) INTO release_num
            FROM releases 
                JOIN movies ON movies.id = releases.movie
            WHERE movies.primary_title = MovieName;

            -- returning number of releases if number of releases more than 0 
            IF release_num > 0 THEN
                RETURN 'Release count: ' || release_num;
            ELSE
            -- If not releases found
                RETURN 'No releases found for "' || MovieName || '"';
            END IF;
        
        ELSE 
            -- message if movie was not a part of the database. 
            RETURN 'Movie "' || MovieName || '" not found';
        END IF;
    END;
$$ LANGUAGE PLpgSQL;


-- -- Question 9 --

/**
    Write a SQL Function, called Q9(MovieName TEXT) RETURNS SETOF TEXT, that:
    Retrieves the Cast and Crew of a given movie.
*/

CREATE OR REPLACE FUNCTION Q9(MovieName TEXT)
    RETURNS SETOF TEXT
    AS $$
    DECLARE 
    -- Declaring variables used. 
        crew_info RECORD;
        cast_info RECORD;
        person_name TEXT;
        movie_name TEXT;
        job_name TEXT;
    BEGIN
        -- Fetching crew information value by looping. 
        FOR crew_info IN 
            SELECT movies.primary_title AS movie_name, people.name AS person_name, professions.name AS job_name
            FROM credits 
            JOIN movies ON movies.id = credits.movie
            JOIN people ON people.id = credits.person
            JOIN professions ON professions.id = credits.profession
            WHERE movies.primary_title = MovieName
        -- Assigning values to variables. 
        LOOP
            movie_name := crew_info.movie_name;
            person_name := crew_info.person_name;
            job_name := crew_info.job_name;
        
            RETURN NEXT '"' || person_name || '" worked on "' || movie_name || '" as a ' || job_name;
        
        END LOOP;
        -- Doing the same process for cast information. 
        FOR cast_info IN 
            SELECT movies.primary_title AS movie_name, people.name AS person_name, roles.played AS job_name
            FROM roles 
            JOIN movies ON movies.id = roles.movie
            JOIN people ON people.id = roles.person
            JOIN professions ON professions.id = roles.profession
            WHERE movies.primary_title = MovieName
        
        LOOP
            person_name := cast_info.person_name;
            movie_name := cast_info.movie_name;
            job_name := cast_info.job_name;
           
            RETURN NEXT '"' || person_name || '" played "' || job_name || '" in "' || movie_name || '"';
        
        END LOOP;
        RETURN;
    END;
    $$ LANGUAGE PLpgSQL
;


-- -- Question 10 --

/**
    Write a PLpgSQL Function, called Q10(MovieRegion CHAR(4)) RETURNS TABLE (Year INTEGER, Best_Movie TEXT, Movie_Genre Text,Principals TEXT), that:
    Retrieves the list of must-watch movies for a given region, year by year.
*/

CREATE OR REPLACE FUNCTION Q10(MovieRegion CHAR(4))  
    RETURNS TABLE (Year INTEGER, Best_Movie TEXT, Movie_Genre TEXT, Principals TEXT)
    AS $$   
    DECLARE 
        curr_yr YEAR;
        max_score RATING;
        curr_yr_record RECORD;
    BEGIN
        -- For each distinct year in our database (from latest to oldest)
        FOR curr_yr IN 
            SELECT DISTINCT movies.release_year 
            FROM movies
            WHERE movies.release_year IS NOT NULL
            ORDER BY movies.release_year DESC
        LOOP 
            -- max_score = maximum movie score for the year. 
            SELECT 
                MAX(movies.score)
            INTO 
                max_score

            FROM movies
                JOIN releases ON movies.id = releases.movie
            WHERE 
                movies.release_year IS NOT NULL AND 
                releases.region IS NOT NULL AND 
                movies.release_year = curr_yr AND 
                releases.region = MovieRegion;

            -- Iterating through our database with a specific year, max_score and region
            FOR curr_yr_record IN 

                -- Agrregating genre as a string for Best_Movie using CTE (Common Table Expressions)
                WITH genres AS (
                    SELECT movie,
                    string_agg(genres.name, ', ' ORDER BY genres.name) AS Movie_Genre
                    FROM movies_genres join genres
                    ON movies_genres.genre = genres.id
                    GROUP BY movie
                ),
                -- Agrregating people as a string for Best_Movie using CTE (Common Table Expressions)
                people AS (
                    SELECT movie,
                    string_agg( people.name, ', ' ORDER BY people.name) AS Principals
                    FROM principals JOIN people
                    ON principals.person = people.id
                    GROUP BY movie
                )

                SELECT 
                    movies.primary_title as Best_Movie,
                    genres.Movie_Genre,
                    people.Principals
                FROM 
                    movies
                    JOIN releases ON movies.id = releases.movie
                    LEFT JOIN genres ON movies.id = genres.movie
                    LEFT JOIN people ON movies.id = people.movie
                WHERE 
                    movies.release_year = curr_yr AND 
                    movies.primary_title IS NOT NULL AND 
                    movies.score = max_score AND 
                    releases.region = MovieRegion
                GROUP BY 
                    movies.release_year, movies.primary_title, movies.score, genres.Movie_Genre, people.Principals
                ORDER BY 
                    movies.score DESC
            LOOP
                -- Assigning values.
                Year := curr_yr;
                Best_Movie := curr_yr_record.Best_Movie;
                Movie_Genre := curr_yr_record.Movie_Genre;
                Principals := curr_yr_record.Principals;
                RETURN NEXT;
            END LOOP;
        END LOOP;
        RETURN;
    END;
    $$ LANGUAGE PLpgSQL
;
