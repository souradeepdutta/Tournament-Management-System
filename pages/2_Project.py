import streamlit as st

st.set_page_config(
    page_title="Project",
    page_icon="♟️"
)

import pandas as pd
import mysql.connector
import chess.pgn
import os

# Define TrieNode class for trie implementation
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_game = False
        self.game_id = None

# Insert moves into the trie
def insert_move(root, moves, game_id):
    node = root
    node.is_end_of_game = False
    node.game_id = game_id
    if moves[0] not in node.children:
        node.children[moves[0]] = TrieNode()
    node = node.children[moves[0]]
    node.is_end_of_game = False
    node.game_id = game_id
    if (len(moves) > 1):
        insert_move(node, moves[1:], game_id)
        

def build_trie_from_pgn_directory(trie_root):
    for filename in os.listdir('.'):
        if filename.endswith('.pgn'):
            with open(filename) as file:
                game = chess.pgn.read_game(file)
                moves = [str(move) for move in game.mainline_moves()]
                insert_move(trie_root, moves, filename)

# Search for games by first few moves in the trie
def search_games(root, moves):
    node = root
    if moves[0] not in node.children:
        return None
    if (len(moves) <= 1):
        return node.game_id
    return search_games(node.children[moves[0]], moves[1:])

# Connect to your MySQL database
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ru198dan",
        database="chess"
    )


#Function to convert cursor to dataframe
def read_dataframe(cursor, query: str) -> pd.DataFrame:
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=columns)

    return df


# Function to query player tournament history
def query_player_tournament_history(cursor):
    player_id = st.text_input("Enter player ID: ")
    if player_id == "":
        st.warning(f"Please enter a value.")
    else:
        query = ("SELECT tournament.tournament_id, tournament.start_date, tournament.end_date, tournament.format "
                       "FROM tournament "
                       "INNER JOIN player_plays_in_tournament ON tournament.tournament_id = player_plays_in_tournament.tournament_id "
                       "WHERE player_plays_in_tournament.player_id = {}".format(player_id))
        cursor.execute(query)
        tournament_history = cursor.fetchall()
        st.write("Player Tournament History:")
        df = read_dataframe(cursor,query)
    
        if not tournament_history:
            st.write("Player has no tournament history.")
        else:
            st.dataframe(df, width=700)

# Function to seach palyer by name
def query_player_by_name(cursor):
    player_name = st.text_input("Enter player name: ")
    if player_name == "":
        st.warning(f"Please enter a value.")
    else:
       
        query = f"SELECT player_id FROM player WHERE Name LIKE '%{player_name}%'"
        cursor.execute(query)
        player_id = cursor.fetchall();
        df = read_dataframe(cursor,query)
        if not player_id:
            st.write("\nThere is no such player.")
        else:
            # for index, player in enumerate(player_id, start=1):
            #     st.write(f"{index}: {player}")
            st.dataframe(df, width=700)

# Function to query player performance in a specific tournament with points and standings
def query_player_performance(cursor):
    player_id = st.text_input("Enter player ID: ")
    tournament_id = st.text_input("Enter tournament ID: ")
    if player_id == "" or tournament_id =="":
        st.warning(f"Please enter a value.")
    else:
        query = ("SELECT player_plays_in_tournament.player_id, player_plays_in_tournament.tournament_id, "
                       "player_plays_in_tournament.points, "
                       "tournament.start_date, tournament.end_date, tournament.format "
                       "FROM player_plays_in_tournament "
                       "INNER JOIN tournament ON player_plays_in_tournament.tournament_id = tournament.tournament_id "
                       "WHERE player_plays_in_tournament.player_id = {} AND player_plays_in_tournament.tournament_id = {}".format(player_id, tournament_id))

        cursor.execute(query)
        performance = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(performance, columns=columns)
        if performance:
            # Fetch all players' points in the tournament and sort them
            cursor.execute("SELECT player_id, points FROM player_plays_in_tournament WHERE tournament_id = %s ORDER BY points DESC", (tournament_id,))
            tournament_standings = cursor.fetchall()

            # Calculate player's standing based on points
            player_standings = [player[0] for player in tournament_standings]
            player_position = player_standings.index(int(player_id)) + 1 if int(player_id) in player_standings else None

            # Print player performance and standing
            # st.write("Player Performance:")
            # st.write(f"Player ID: {performance[0]}") 
            # st.write(f"Tournament ID: {performance[1]}")
            # st.write(f"Points: {performance[2]}")
            # st.write(f"Start Date: {performance[3]}")
            # st.write(f"End Date: {performance[4]}")
            # st.write(f"Format: {performance[5]}")
            st.dataframe(df, width=700)
            if player_position:
                st.write(f"Player Standing in Tournament: {player_position} out of {len(tournament_standings)}")
            else:
                st.write("Player did not participate in the specified tournament.")
        else:
            st.write("Player did not participate in the specified tournament.")

# Function to query player general information with readable output
def query_player_info(cursor):
    player_id = st.text_input("Enter player ID: ")
    if player_id == "":
        st.warning(f"Please enter a value.")
    else:
        query = f"SELECT player_id, birth_date, name, country, elo FROM player WHERE player_id = {player_id}"
        cursor.execute(query)
        player_info = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(player_info, columns=columns)
        if player_info:
            # st.write("Player Information:")
            # st.write(f"Player ID: {player_info[0]}")
            # st.write(f"Name: {player_info[2]}")
            # st.write(f"Birth Date: {player_info[1]}")
            # st.write(f"Country: {player_info[3]}")
            # st.write(f"ELO Rating: {player_info[4]}")
            st.dataframe(df, width=700)
        else:
            st.write("Player not found.")

# Function to query player opening statistics with readable output
def query_player_opening_stats(cursor):
    player_id = st.text_input("Enter player ID: ")
    if player_id == "":
        st.warning(f"Please enter a value.")
    else:
        query = ("SELECT game.ECO, COUNT(*) AS play_count "
                       "FROM player_plays_game "
                       "INNER JOIN game ON player_plays_game.game_id = game.game_id "
                       "WHERE player_plays_game.player_id = {} "
                       "GROUP BY game.ECO".format(player_id))
        cursor.execute(query)
        opening_stats = cursor.fetchall()
        df = read_dataframe(cursor,query)
        if opening_stats:
            st.write("Player Opening Statistics:")
            # for stat in opening_stats:
            #     # st.write(f"ECO Code: {stat[0]}")
            #     # st.write(f"Play Count: {stat[1]}")
            #     # st.write()
            st.dataframe(df, width=700)
        else:
            st.write("No opening statistics found for the player.")

# Function to query recent tournaments with readable output
def query_recent_tournaments(cursor):
    query = "SELECT * FROM tournament ORDER BY start_date DESC LIMIT 10"
    cursor.execute(query)
    recent_tournaments = cursor.fetchall()
    df = read_dataframe(cursor,query)
    if recent_tournaments:
        st.write("Recent Tournaments:")
        # for tournament in recent_tournaments:
        #     # st.write(f"Tournament ID: {tournament[0]}")
        #     # st.write(f"Start Date: {tournament[1]}")
        #     # st.write(f"End Date: {tournament[2]}")
        #     # st.write(f"Format: {tournament[3]}")
        #     # st.write()
        st.dataframe(df, width=700)
    else:
        st.write("No recent tournaments found.")

# Function to query recent tournaments in a specific country with venue details
def query_recent_tournaments_in_country(cursor):
    country = st.text_input("Enter country name: ")
    if country == "":
        st.warning(f"Please enter a value.")
    else:
        query = ("SELECT tournament.tournament_id, tournament.start_date, tournament.end_date, tournament.format, "
                       "tournament_venue.country, tournament_venue.address "
                       "FROM tournament "
                       "INNER JOIN tournament_venue ON tournament.tournament_id = tournament_venue.tournament_id "
                       "WHERE tournament_venue.country = '{}' "
                       "ORDER BY tournament.start_date DESC LIMIT 10".format(country))
        cursor.execute(query)
        recent_tournaments = cursor.fetchall()
        df = read_dataframe(cursor,query)
        if recent_tournaments:
        #     st.write(f"Recent Tournaments in {country}:")
        #     for tournament in recent_tournaments:
        #         st.write(f"Tournament ID: {tournament[0]}")
        #         st.write(f"Start Date: {tournament[1]}")
        #         st.write(f"End Date: {tournament[2]}")
        #         st.write(f"Format: {tournament[3]}")
        #         st.write(f"Country: {tournament[4]}")
        #         st.write(f"Address: {tournament[5]}")
        #         st.write()
            st.dataframe(df, width=700)
        else:
            st.write(f"No recent tournaments found in {country}.")

# Function to check a player's title
def check_player_title(cursor):
    player_id = st.text_input("Enter player ID: ")
    if player_id == "":
        st.warning(f"Please enter a value.")
    else:
        query = "SELECT title_name FROM player_has_title WHERE player_id = '{}'".format(player_id)
        cursor.execute(query)
        titles = cursor.fetchall()
        df = read_dataframe(cursor,query)
        if titles:
            st.write("Player Titles:")
            # for title in titles:
            #     st.write(title[0])
            st.dataframe(df, width=700)
        else:
            st.write("Player does not have any titles.")

# Function to get a list of player's games with optional filters including rating range
def query_player_games(cursor):
    player_id = st.text_input("Enter player ID: ")
    min_rating_filter = st.text_input("Enter minimum rating (optional, press Enter to skip): ")
    max_rating_filter = st.text_input("Enter maximum rating (optional, press Enter to skip): ")
    result_filter = st.text_input("Enter result filter (optional, press Enter to skip): ")
    if player_id == "":
        st.warning(f"Please enter a value.")
    else:
        query = "SELECT game.game_id, game.tournament_id, game.table_number, game.round, game.Time, game.result, game.ECO " \
                "FROM player_plays_game " \
                "INNER JOIN game ON player_plays_game.game_id = game.game_id " \
                "WHERE player_plays_game.player_id = {}".format(player_id)
        params = [player_id]


        if result_filter:
            query += " AND game.result LIKE '%{}%'".format(result_filter)

        cursor.execute(query)
        player_games = cursor.fetchall()

        df = read_dataframe(cursor,query)

        if player_games:
            st.write("Player Games:")
            # for game in player_games:
            #     st.write(f"Game ID: {game[0]}")
            #     st.write(f"Tournament ID: {game[1]}")
            #     st.write(f"Table Number: {game[2]}")
            #     st.write(f"Round: {game[3]}")
            #     st.write(f"Time: {game[4]}")
            #     st.write(f"Result: {game[5]}")
            #     st.write(f"ECO Code: {game[6]}")
            #     st.write()
            st.dataframe(df, width=700)
        else:
            st.write("No games found for the player with the specified filters.")

# Function to query a game by its ID
def query_game_by_id(cursor, game_id):
    query = ("SELECT * FROM game WHERE game_id = {}".format(game_id))
    cursor.execute(query)
    game_data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(game_data, columns=columns)
    if game_data:
        st.write("Game Information:")
        # st.write(f"Game ID: {game_data[0]}")
        # st.write(f"Tournament ID: {game_data[1]}")
        # st.write(f"Table Number: {game_data[2]}")
        # st.write(f"Round: {game_data[3]}")
        # st.write(f"Time: {game_data[4]}")
        # st.write(f"Result: {game_data[5]}")
        # st.write(f"ECO Code: {game_data[6]}")
        st.dataframe(df, width=700)
    else:
        st.write("Game not found.")

# Main function
def main():
    db = connect_to_database()
    cursor = db.cursor()
    trie_root = TrieNode()
    pgn_files = ["sample-game.pgn"]  # List of PGN file paths
    build_trie_from_pgn_directory(trie_root)

    st.title("Chess Database")
    st.write("Welcome to the Chess Database!")

    choice = st.selectbox("Select an option:", ["Query Player Tournament History", "Query Player Performance in Specific Tournament", 
                                                 "Query Player General Information", "Query Player Opening Statistics", 
                                                 "Query Recent Tournaments", "Get Player by Name", "Query Recent Tournaments in Specific Country", 
                                                 "Check Player Title", "Get List of Player's Games", "Find Games by First Few Moves", 
                                                 "Query Game by ID", "Exit"])

    if choice == "Query Player Tournament History":
        query_player_tournament_history(cursor)
    elif choice == "Query Player Performance in Specific Tournament":
        query_player_performance(cursor)
    elif choice == "Query Player General Information":
        query_player_info(cursor)
    elif choice == "Query Player Opening Statistics":
        query_player_opening_stats(cursor)
    elif choice == "Query Recent Tournaments":
        query_recent_tournaments(cursor)
    elif choice == "Query Recent Tournaments in Specific Country":
        query_recent_tournaments_in_country(cursor)
    elif choice == "Check Player Title":
        check_player_title(cursor)
    elif choice == "Get List of Player's Games":
        query_player_games(cursor)
    elif choice == "Get Player by Name":
        query_player_by_name(cursor);
    elif choice == "Find Games by First Few Moves":
        moves_input = st.text_input("Enter the first few moves: ")
        if moves_input == "":
            st.warning(f"Please enter a value.")
        else:
            game_id = search_games(trie_root, moves_input.split())
            if game_id is not None:
                st.write(game_id[:-4])
                query_game_by_id(cursor, game_id[:-4])
            else:
                st.write("No game found with the specified moves.")
    elif choice == "Query Game by ID":
        game_id = st.text_input("Enter game ID: ")
        if game_id == "":
            st.warning(f"Please enter a value.")
        else:
            query_game_by_id(cursor, game_id)
    else:
        st.markdown("### Goodbye!")

    cursor.close()
    db.close()

if __name__ == "__main__":
    main()