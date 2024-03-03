import sqlite3
from typing import Any

import pytest

from engine import Engine


class SqliteWrapper:
    """
    I am not interested in implementing Transaction control
    (manual commit after each insert)
    So this wrapper commits on each executes, useful for testing,
    but this is not proper use of `sqlite3`
    """

    def __init__(self) -> None:
        self.con = sqlite3.connect(":memory:")
        self.cur = self.con.cursor()

    def execute(self, text: str) -> Any:
        res = self.cur.execute(text)
        self.con.commit()
        return res.fetchall()


class SameOutput:
    def __init__(self) -> None:
        self.sw = SqliteWrapper()
        self.e = Engine()

    def same(self, cmd: str) -> None:
        assert self.sw.execute(cmd) == self.e.execute(cmd)


def test1() -> None:
    sm = SameOutput()
    sm.same("CREATE TABLE user(firstname TEXT, secondname TEXT)")
    sm.same("INSERT INTO user VALUES ('alisher', 'zhuban'), ('john', 'doe')")
    sm.same("SELECT * FROM user")
    sm.same("SELECT firstname, secondname FROM user")
    sm.same("SELECT *, firstname, * FROM user")


def test2() -> None:
    sm = SameOutput()
    sm.same("CREATE TABLE user(name TEXT, age INTEGER)")
    sm.same("INSERT INTO user VALUES ('alisher', 22), ('john', 21)")
    sm.same("SELECT name FROM user WHERE age = 22")
    sm.same("SELECT name FROM user WHERE age BETWEEN 18 AND 21")
    sm.same("SELECT name FROM user WHERE age NOT BETWEEN 18 AND 21")


def test_nums() -> None:
    sm = SameOutput()
    sm.same("CREATE TABLE nums(x INTEGER)")
    sm.same("INSERT INTO nums VALUES (1), (2), (3), (4), (5)")
    sm.same("SELECT x FROM nums WHERE x == 1 OR x == 2")
    sm.same("SELECT x FROM nums WHERE NOT x == 3 AND NOT x == 2")
    sm.same("SELECT x FROM nums WHERE x != 1 AND x <> 2")
    sm.same("SELECT x FROM nums WHERE x <= 2 OR x >= 4")
    sm.same("SELECT x FROM nums WHERE x < 3")
    sm.same("SELECT x FROM nums WHERE x > 3")
    sm.same("SELECT x FROM nums WHERE x IN (5, 6, 7)")
    sm.same("SELECT x FROM nums WHERE x NOT IN (0, 1)")


def test_strings() -> None:
    sm = SameOutput()
    sm.same("CREATE TABLE s(t TEXT)")
    sm.same(
        "INSERT INTO s VALUES ('ali'), ('alisher'), ('Alisher'), ('john'), ('aset')"
    )
    sm.same("SELECT * FROM s WHERE t == 'ali'")
    sm.same("SELECT * FROM s WHERE t LIKE 'ali%'")
    sm.same("SELECT * FROM s WHERE t IN ('ali', 'aset')")


def test_duplicates() -> None:
    sm = SameOutput()
    sm.same("CREATE TABLE nums(x INTEGER)")
    sm.same("INSERT INTO nums VALUES (1), (1), (1)")
    sm.same("SELECT x FROM nums WHERE x == 1")
    sm.same("SELECT ALL x FROM nums WHERE x == 1")
    sm.same("SELECT DISTINCT x FROM nums WHERE x == 1")


def test_order() -> None:
    sm = SameOutput()
    sm.same("CREATE TABLE nums(x INTEGER)")
    sm.same("INSERT INTO nums VALUES (5), (3), (4), (1), (2)")
    sm.same("SELECT x FROM nums ORDER BY x")


# sqlbolt.com like tests
CREATE_MOVIES = """
    CREATE TABLE Movies (id INT, title TEXT, director TEXT, year INT, length_minutes INT);
"""

INSERT_MOVIES = """
    INSERT INTO Movies VALUES 
        (1, 'Toy Story', 'John Lasseter', 1995, 81),
        (2, 'A Bugs Life', 'John Lasseter', 1998, 95),
        (3, 'Toy Story 2', 'John Lasseter', 1999, 93),
        (4, 'Monsters, Inc.', 'Pete Docter', 2001, 92),
        (5, 'Finding Nemo', 'Andrew Stanton', 2003, 107),
        (6, 'The Incredibles', 'Brad Bird', 2004, 116),
        (7, 'Cars', 'John Lasseter', 2006, 117),
        (8, 'Ratatouille', 'Brad Bird', 2007, 115),
        (9, 'WALL-E', 'Andrew Stanton', 2008, 104),
        (10, 'Up', 'Pete Docter', 2009, 101),
        (11, 'Toy Story 3', 'Lee Unkrich', 2010, 103),
        (12, 'Cars 2', 'John Lasseter', 2011, 120),
        (13, 'Brave', 'Brenda Chapman', 2012, 102),
        (14, 'Monsters University', 'Dan Scanlon', 2013, 110);
"""

CREATE_NORTH = """
CREATE TABLE North_american_cities (city, country, population, latitude, longitude);
"""

INSERT_NORTH = """
    INSERT INTO North_american_cities VALUES
        ('Guadalajara', 'Mexico', 1500800, 20.659699, -103.349609),
        ('Toronto', 'Canada', 2795060, 43.653226, -79.383184),
        ('Houston', 'United States', 2195914, 29.760427, -95.369803),
        ('New York', 'United States', 8405837, 40.712784, -74.005941),
        ('Philadelphia', 'United States', 1553165, 39.952584, -75.165222),
        ('Havana', 'Cuba', 2106146, 23.05407, -82.345189),
        ('Mexico City', 'Mexico', 8555500, 19.432608, -99.133208),
        ('Phoenix', 'United States', 1513367, 33.448377, -112.074037),
        ('Los Angeles', 'United States', 3884307, 34.052234, -118.243685),
        ('Ecatepec de Morelos', 'Mexico', 1742000, 19.601841, -99.050674),
        ('Montreal', 'Canada', 1717767, 45.501689, -73.567256),
        ('Chicago', 'United States', 2718782, 41.878114, -87.629798);
"""

CREATE_BOX_OFFICE = """
    CREATE TABLE Boxoffice (movie_id, rating, domestic_sales, international_sales);
"""

INSERT_BOX_OFFICE = """
    INSERT INTO Boxoffice VALUES
        (5,  8.2,	380843261,	555900000),
        (14, 7.4,	268492764,	475066843),
        (8,  8, 	206445654,	417277164),
        (12, 6.4,	191452396,	368400000),
        (3,  7.9,	245852179,	239163000),
        (6,  8, 	261441092,	370001000),
        (9,  8.5,	223808164,	297503696),
        (11, 8.4,	415004880,	648167031),
        (1,  8.3,	191796233,	170162503),
        (7,  7.2,	244082982,	217900167),
        (10, 8.3,	293004164,	438338580),
        (4,  8.1,	289916256,	272900000),
        (2,  7.2,	162798565,	200600000),
        (13, 7.2,	237283207,	301700000);
"""

CREATE_BUILDINGS = """
    CREATE TABLE Buildings (building_name, capacity);
"""

INSERT_BUILDINGS = """
    INSERT INTO Buildings VALUES
        ('1e', 24),
        ('1w', 32),
        ('2e', 16),
        ('2w', 20);
"""

CREATE_EMPLOYEES = """
    CREATE TABLE Employees (role TEXT, name TEXT, building TEXT, years_employed INT);
"""

INSERT_EMPLOYEES = """
    INSERT INTO Employees VALUES
        ('Engineer',	'Becky A.',	    '1e',	4),
        ('Engineer',	'Dan B.',	    '1e',	2),
        ('Engineer',	'Sharon F.',	'1e',	6),
        ('Engineer',	'Dan M.',	    '1e',	4),
        ('Engineer',	'Malcom S.',	'1e',	1),
        ('Artist',	    'Tylar S.',	    '2w',	2),
        ('Artist',	    'Sherman D.',   '2w',	8),
        ('Artist',	    'Jakob J.',	    '2w',	6),
        ('Artist',	    'Lillia A.',	'2w',	7),
        ('Artist',	    'Brandon J.',   '2w',	7),
        ('Manager',	    'Scott K.',	    '1e',	9),
        ('Manager', 	'Shirlee M.',   '1e',	3),
        ('Manager',	    'Daria O.',	    '2w',	6),
        ('Engineer',	'Yancy I.',     NULL,   0),
        ('Artist',  	'Oliver P.',    NULL,   0);
"""


def test_lesson1() -> None:
    sm = SameOutput()
    sm.same(CREATE_MOVIES)
    sm.same(INSERT_MOVIES)
    sm.same("SELECT title FROM movies;")
    sm.same("SELECT director FROM movies;")
    sm.same("SELECT title, director FROM movies;")
    sm.same("SELECT title, year FROM movies;")
    sm.same("SELECT * FROM movies;")


def test_lesson2() -> None:
    sm = SameOutput()
    sm.same(CREATE_MOVIES)
    sm.same(INSERT_MOVIES)
    sm.same("""
        SELECT id, title FROM movies 
        WHERE id = 6;
    """)
    sm.same("""
        SELECT title, year FROM movies
        WHERE year BETWEEN 2000 AND 2010;
    """)
    sm.same("""
        SELECT title, year FROM movies
        WHERE year < 2000 OR year > 2010;
    """)
    sm.same("""
        SELECT title, year FROM movies
        WHERE year <= 2003; 
    """)


def test_lesson3() -> None:
    sm = SameOutput()
    sm.same(CREATE_MOVIES)
    sm.same(INSERT_MOVIES)
    sm.same("""
        SELECT title, director FROM movies 
        WHERE title LIKE 'Toy Story%';
    """)
    sm.same("""
        SELECT title, director FROM movies 
        WHERE director = 'John Lasseter';
    """)
    sm.same("""
        SELECT title, director FROM movies 
        WHERE director != 'John Lasseter';
    """)
    sm.same("""
        SELECT * FROM movies 
        WHERE title LIKE 'WALL-_';
    """)


@pytest.mark.xfail
def test_lesson4() -> None:
    sm = SameOutput()
    sm.same(CREATE_MOVIES)
    sm.same(INSERT_MOVIES)
    sm.same("""
        SELECT DISTINCT director FROM movies
        ORDER BY director ASC;
    """)
    sm.same("""
        SELECT title, year FROM movies
        ORDER BY year DESC
        LIMIT 4;
    """)
    sm.same("""
        SELECT title FROM movies
        ORDER BY title ASC
        LIMIT 5;
    """)
    sm.same("""
        SELECT title FROM movies
        ORDER BY title ASC
        LIMIT 5 OFFSET 5;
    """)


@pytest.mark.xfail
def test_lesson5() -> None:
    sm = SameOutput()
    sm.same(CREATE_NORTH)
    sm.same(INSERT_NORTH)
    sm.same("""
        SELECT city, population FROM north_american_cities
        WHERE country = 'Canada';
    """)
    sm.same("""
        SELECT city, latitude FROM north_american_cities
        WHERE country = 'United States'
        ORDER BY latitude DESC;
    """)
    sm.same("""
        SELECT city, longitude FROM north_american_cities
        WHERE longitude < -87.629798
        ORDER BY longitude ASC;
    """)
    sm.same("""
        SELECT city, population FROM north_american_cities
        WHERE country LIKE 'Mexico'
        ORDER BY population DESC
        LIMIT 2;
    """)
    sm.same("""
        SELECT city, population FROM north_american_cities
        WHERE country LIKE 'United States'
        ORDER BY population DESC
        LIMIT 2 OFFSET 2;
    """)


@pytest.mark.xfail
def test_lesson6() -> None:
    sm = SameOutput()
    sm.same(CREATE_MOVIES)
    sm.same(INSERT_MOVIES)
    sm.same(CREATE_BOX_OFFICE)
    sm.same(INSERT_BOX_OFFICE)
    sm.same("""
        SELECT title, domestic_sales, international_sales 
        FROM movies
        JOIN boxoffice
            ON movies.id = boxoffice.movie_id;
    """)
    sm.same("""
        SELECT title, domestic_sales, international_sales
        FROM movies
        JOIN boxoffice
            ON movies.id = boxoffice.movie_id
        WHERE international_sales > domestic_sales;
    """)
    sm.same("""
        SELECT title, rating
        FROM movies
        JOIN boxoffice
            ON movies.id = boxoffice.movie_id
        ORDER BY rating DESC;
    """)


@pytest.mark.xfail
def test_lesson7() -> None:
    sm = SameOutput()
    sm.same(CREATE_BUILDINGS)
    sm.same(INSERT_BUILDINGS)
    sm.same(CREATE_EMPLOYEES)
    sm.same(INSERT_EMPLOYEES)
    sm.same("SELECT DISTINCT building FROM employees;")
    sm.same("SELECT * FROM buildings;")
    sm.same("""
        SELECT DISTINCT building_name, role 
        FROM buildings 
        LEFT JOIN employees
            ON building_name = building;
    """)


@pytest.mark.xfail
def test_lesson8() -> None:
    sm = SameOutput()
    sm.same(CREATE_BUILDINGS)
    sm.same(INSERT_BUILDINGS)
    sm.same(CREATE_EMPLOYEES)
    sm.same(INSERT_EMPLOYEES)
    sm.same("""
        SELECT name, role FROM employees
        WHERE building IS NULL;
    """)
    sm.same("""
        SELECT DISTINCT building_name
        FROM buildings 
        LEFT JOIN employees
            ON building_name = building
        WHERE role IS NULL;
    """)


@pytest.mark.xfail
def test_lesson9() -> None:
    sm = SameOutput()
    sm.same(CREATE_MOVIES)
    sm.same(INSERT_MOVIES)
    sm.same(CREATE_BOX_OFFICE)
    sm.same(INSERT_BOX_OFFICE)
    sm.same("""
        SELECT title, (domestic_sales + international_sales) / 1000000 AS gross_sales_millions
        FROM movies
        JOIN boxoffice
            ON movies.id = boxoffice.movie_id;
    """)
    sm.same("""
        SELECT title, rating * 10 AS rating_percent
        FROM movies
        JOIN boxoffice
            ON movies.id = boxoffice.movie_id;
    """)
    sm.same("""
        SELECT title, year
        FROM movies
        WHERE year % 2 = 0;
    """)


@pytest.mark.xfail
def test_lesson10() -> None:
    sm = SameOutput()
    sm.same(CREATE_EMPLOYEES)
    sm.same(INSERT_EMPLOYEES)
    sm.same("SELECT MAX(years_employed) as Max_years_employed FROM employees;")
    sm.same("""
        SELECT role, AVG(years_employed) as Average_years_employed
        FROM employees
        GROUP BY role;
    """)
    sm.same("""
        SELECT building, SUM(years_employed) as Total_years_employed
        FROM employees
        GROUP BY building;
    """)


@pytest.mark.xfail
def test_lesson11() -> None:
    sm = SameOutput()
    sm.same(CREATE_EMPLOYEES)
    sm.same(INSERT_EMPLOYEES)
    sm.same("""
        SELECT role, COUNT(*) as Number_of_artists
        FROM employees
        WHERE role = 'Artist';
    """)
    sm.same("""
    SELECT role, COUNT(*)
        FROM employees
        GROUP BY role;
    """)
    sm.same("""
        SELECT role, SUM(years_employed)
        FROM employees
        GROUP BY role
        HAVING role = 'Engineer';
    """)


@pytest.mark.xfail
def test_lesson12() -> None:
    sm = SameOutput()
    sm.same(CREATE_MOVIES)
    sm.same(INSERT_MOVIES)
    sm.same(CREATE_BOX_OFFICE)
    sm.same(INSERT_BOX_OFFICE)
    sm.same("""
        SELECT director, COUNT(id) as Num_movies_directed
        FROM movies
        GROUP BY director;
    """)
    sm.same("""
        SELECT director, SUM(domestic_sales + international_sales) as Cumulative_sales_from_all_movies
        FROM movies
        INNER JOIN boxoffice
            ON movies.id = boxoffice.movie_id
        GROUP BY director;
    """)


@pytest.mark.xfail
def test_lesson13() -> None:
    sm = SameOutput()
    sm.same(CREATE_MOVIES)
    sm.same(INSERT_MOVIES)
    sm.same(CREATE_BOX_OFFICE)
    sm.same(INSERT_BOX_OFFICE)
    sm.same("INSERT INTO movies VALUES (4, 'Toy Story 4', 'El Directore', 2015, 90);")
    sm.same("SELECT * FROM movies;")
    sm.same("INSERT INTO boxoffice VALUES (4, 8.7, 340000000, 270000000);")
    sm.same("SELECT * FROM boxoffice;")


@pytest.mark.xfail
def test_lesson14() -> None:
    sm = SameOutput()
    sm.same(CREATE_MOVIES)
    sm.same(INSERT_MOVIES)
    sm.same("""
        UPDATE movies
        SET director = 'John Lasseter'
        WHERE id = 2;
    """)
    sm.same("SELECT * FROM movies WHERE director = 'John Lasseter';")
    sm.same("""
        UPDATE movies
        SET year = 1999
        WHERE id = 3;
    """)
    sm.same("SELECT * FROM movies WHERE id = 3;")
    sm.same("""
        UPDATE movies
        SET title = 'Toy Story 3', director = 'Lee Unkrich'
        WHERE id = 11;
    """)


@pytest.mark.xfail
def test_lesson15() -> None:
    sm = SameOutput()
    sm.same(CREATE_MOVIES)
    sm.same(INSERT_MOVIES)
    sm.same("DELETE FROM movies where year < 2005;")
    sm.same("SELECT * FROM movies;")
    sm.same("DELETE FROM movies where director = 'Andrew Stanton'")


@pytest.mark.xfail
def test_lesson16() -> None:
    sm = SameOutput()
    sm.same("""
        CREATE TABLE Database (
            Name TEXT,
            Version FLOAT,
            Download_count INTEGER
    );""")
    sm.same("SELECT * FROM Database;")


@pytest.mark.xfail
def test_lesson17() -> None:
    sm = SameOutput()
    sm.same(CREATE_MOVIES)
    sm.same(INSERT_MOVIES)
    sm.same("""
        ALTER TABLE Movies
        ADD COLUMN Aspect_ratio FLOAT DEFAULT 2.39;
    """)
    sm.same("SELECT * FROM movies;")
    sm.same("""
        ALTER TABLE Movies
        ADD COLUMN Language TEXT DEFAULT 'English';
    """)
    sm.same("SELECT * FROM movies;")


@pytest.mark.xfail
def test_lesson18() -> None:
    sm = SameOutput()
    sm.same(CREATE_MOVIES)
    sm.same(INSERT_MOVIES)
    sm.same(CREATE_BOX_OFFICE)
    sm.same(INSERT_BOX_OFFICE)
    sm.same("DROP TABLE Movies;")
    sm.same("DROP TABLE BoxOffice;")
