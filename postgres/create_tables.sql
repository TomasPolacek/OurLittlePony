-- Creation of bets table
CREATE TABLE IF NOT EXISTS bets (
  bet_id serial PRIMARY KEY,
  match_type varchar(250),
  team1  varchar(250),
  team2  varchar(250),
  odds_1 float,
  odds_2 float,
  odds_x float,
  odds_1x float,
  odds_2x float,
  odds_12 float,
  ts date
);  