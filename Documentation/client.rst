Client
======

Handshake concept
-----------------
Server:  Initiates turn with string "T"
Client:  Answers with string "Y"

After that the client can send up to 999 map requests and can start one bomb. 
After bombing the client must reinitiate the new turn as described above

The game is terminated from the server by sending the string "EOG".

Please ensure, that all steps of the handshake is correctly implemented in the client. If that is not the case, you will run in an unsynced behaviour 
and therefore a dead-loop

Helper Functions
----------------

.. automodule:: client
    :members:
