# Data Store Server
This project implements a Python based multi-client data storage server with transaction support. The server allows clients to interact with a data store that supports basic operations like PUT, GET, DELETE, and also transaction management operations like BEGIN, COMMIT, and ROLLBACK.

#### Transaction methodology 
I manage transaction records through a dictionary. For each user, an entry is created in this dictionary, utilizing the thread's unique ID as the key and maintaining a stack as the corresponding value. Within this stack, each element is a list that captures the executed commands during a transaction. When a user initiates a transaction using the "BEGIN" command, a new stack entry is created for that thread's ID. As each command is processed within the transaction, I update the data and add the command to the transaction stack. In case of a command failure, I revert all prior commands within the stack and terminate the ongoing transaction. This action effectively restores the data to the state at the start of the most recent user transaction. On successful execution of all commands, when the user issues a "COMMIT" command, I remove the current transaction from the stack. This guarantees that all modifications to the data become irreversible.

An alternative strategy to implement rollback and commit functionality in transactions involves utilizing a local data store. With this approach, for each transaction, a separate local data store is maintained. During the transaction, any changes are applied to this local store. If any command within the transaction fails, the local data store is discarded. Conversely, upon hitting the "COMMIT" command, the global store is updated with the contents of the local data store. I opted against employing this method primarily to conserve memory usage.

### Assumptions
<ul>
    <li> Syntactical errors within the command are not regarded as failures and will not trigger a check to determine if a transaction can be committed. </li>
    <li> The commands are case insensitive. </li>
    <li> The data is shared collectively among all users, granting each user the capability to make modifications to the data store. </li>
</ul>


### Prerequisites
Python 3.x, the project uses packages from the python standard library

### How to Use
Modify the HOST and PORT constants in the server.py script to set the server's listening address and port. By default the server runs on localhost port 8891.
Run the script in your terminal: ``` python script_name.py```.

Clients can interact with the server either using the client.py or using any TCP client, such as telnet.


### DataStore Class
The DataStore class provides utility functions for interacting with the data store. It supports the following methods:

<ul>
    <li>put(key, value, thread_id): Assigns the provided value to the corresponding key within the data store. If a transaction is active, the change is recorded for potential rollback.</li>
    <li>get(key): Retrieves the value associated with the provided key.</li>
    <li>delete(key, thread_id): Removes the entry associated with the provided key. If a transaction is active, the change is recorded for potential rollback.</li>
    <li>begin(thread_id): Initiates a new transaction for a specific thread.</li>
    <li>commit(thread_id): Finalizes an ongoing transaction for a specified thread.</li>
    <li>rollback(thread_id): Reverts changes made during an ongoing transaction for a specific thread.</li>
    <li>check_if_transaction_exists(thread_id): Checks if transactions exist for a given thread.</li>
</ul>

### Server Class
The Server class manages incoming client connections and processes their commands. It utilizes the DataStore class for data storage and transaction support. It supports the following methods:

<ul>
    <li>process_command(command, thread_id): Parses and processes client commands.</li>
    <li>handle_request(client_connection): Listens for incoming data from a client connection.</li>
    <li>start(host, port): Initializes and starts the server by binding to a host and port, then listening for incoming client connections.</li>
</ul>

###### Supported Commands
<ul>
    <li>GET <key>: Retrieves the value associated with the given key.</li>
    <li>PUT <key> <value>: Assigns the provided value to the corresponding key.</li>
    <li>DELETE <key>: Removes the entry associated with the provided key.</li>
    <li>BEGIN: Initiates a new transaction.</li>
    <li>COMMIT: Finalizes an ongoing transaction.</li>
    <li>ROLLBACK: Reverts changes made during an ongoing transaction.</li>
</ul>

##### How to connect to server using telnet

To interact with the server using telnet:
<ul>
<li>Open a terminal.</li>
<li>Connect to the server: telnet 127.0.0.1 8891</li>
<li>Send commands and observe server responses.</li>
</ul>