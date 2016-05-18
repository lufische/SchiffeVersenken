# SchiffeVersenken

## About
Talking with colleagues at lunch seems to be the best source of silly ideas. Following the discussion about the simple game **Battleships** (**SchiffeVersenken** in german) and the optimal strategy for winning sure was fun - however, no real answer could be found by theoretical estimations.

It arise the plan to implement battleship bots, following different strategies, and selecting the best one in the end. To this end, we concluded, we need the round histograms of each bot. This, in turn, allows for the calculation of the winning probability for each duel.

## Idea
The bots can communicate with the server via a socket connection. The server can handle simple commands as
- bomb: Bomb selected field
- requestField: Sends which fields have already been bombed
- ...
The server itself creates random ship maps and terminates the game if all ships are destroyed. 

To emphasize: This project is definitly a quick-and-dirty-style scripting!

## Dependencies
Uses *python* for coding and *sphinx* for awesome looking documentations.

## The contest
Everybody can implement their bot in *client.py* as function *botRound* and test the capability with the script *looper.sh*.
Any good ideas? We are happy to see all kinds of bots! Just send a pull request.
