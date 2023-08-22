'''
 # @ Author: Ahmad Shayaan
 # @ Create Time: 2023-08-21 14:55:02
 # @ Modified by: Ahmad Shayaan
 # @ Modified time: 2023-08-22 14:31:44
 # @ Description:
 '''

import socket
import threading
import json

HOST = "127.0.0.1"
PORT = 8891

class DataStore():
    '''
    This class offers utility functions for interacting with the data store.
    Attributes:
        None
    Methods:
        put(key, value, thread_id)
            Assigns the provided value to the corresponding key within the data store.
        get(key):
            Retrieves the value associated with the provided key.
        delte(key, thread_id)
            Removes the entry associated with the provided key.
        begin(thread_id)
            Initiates a new transaction for a specific thread
        commit(thread_id)
            Finalizes an ongoing transaction for a specified thread
        rollback(thread_id)
            Reverts changes made during an ongoing transaction for a specific thread.
        check_if_transaction_exists(thread_id)
            Checks if transactions exits for given thread_id
    '''
    def __init__(self):
        self.data = {}
        self.transactions = {}
        self.lock = threading.Lock()
    
    def put(self, key:str, value, thread_id):
        '''
        The put method adds a key-value pair to the data store, allowing for potential 
        ollback during ongoing transactions
        
        Parameters:
            key: The identifier for the data entry in the store.
            value: The value associated with the provided key.
            thread_id: The unique identifier for the current thread accessing the data store.
        '''
        with self.lock:
            try:
                if thread_id in self.transactions.keys() and len(self.transactions[thread_id]) > 0:
                    self.transactions[thread_id][-1].append(("PUT",key, self.data.get(key,None))) #adding the key to delete in case of rollback
                    self.data[key] = value
                else:
                    self.data[key] = value
                return "SUCCESS"
            except Exception as e:
                return "ERROR"
    
    def get(self, key:str):
        '''
        The get method retrieves the value associated with a given key from the data store within.

        Parameters:
            key: The identifier for the data entry in the store.
        '''
        with self.lock:
            return self.data.get(key,None)
    
    def delete(self, key:str, thread_id):
        '''
        The delete method enables the removal of a data entry from the store while considering ongoing transactions.

        Parameter:
            key: The identifier for the data entry in the store.
            thread_id: The unique identifier for the current thread accessing the data store.
        '''
        with self.lock:
            if key in self.data.keys():
                if thread_id in self.transactions.keys() and len(self.transactions[thread_id]) > 0:
                    self.transactions[thread_id][-1].append(("DELETE",key,self.data[key])) #adding the key value pair in case of rollback
                    del self.data[key]
                else:
                    del self.data[key]
                return "SUCCESS"
            else:
                return "ERROR"
    
    def begin(self, thread_id): 
        '''
        Initiates a new transaction associated with the provided thread_i

        Parameter:
            thread_id: The unique identifier for the current thread accessing the data store.
        '''
        with self.lock:
            if thread_id not in self.transactions.keys():
                self.transactions[thread_id] = [[]]
            else:
                self.transactions[thread_id].append([])
            return {"status":"Ok", "mesg":"Began new transactions"}
    
    def commit(self, thread_id):
        '''
        Thie method is responsible for finalizing a transaction associated with a specific thread_id.

        Parameter:
            thread_id: The unique identifier for the current thread accessing the data store.
        '''
        with self.lock:
            if thread_id in self.transactions.keys() and len(self.transactions[thread_id]) > 0:
                self.transactions[thread_id].pop()
                return {"status":"Ok", "mesg":"Transaction committed"}
            else:
                return {"status":"Error", "mesg":"No transactions to commit"}

    def rollback(self, thread_id):
        '''
        This funciton enables the reversal of changes made during an ongoing transaction.

        Parameter:
            thread_id: The unique identifier for the current thread accessing the data store.
        '''
        with self.lock:
            if thread_id in self.transactions.keys() and len(self.transactions[thread_id]) > 0:
                rollback_transactions = self.transactions[thread_id].pop()
            else:
                return {"status":"Error", "mesg":"No transactions to rollback"}
            
            for transaction in reversed(rollback_transactions):
                if transaction[0].upper() == "PUT":
                    if transaction[2] is None:
                        del self.data[transaction[1]]
                    else:
                        self.data[transaction[1]] = transaction[2]
                
                if transaction[0].upper() == "DELETE":
                    self.data[transaction[1]] = transaction[2]
                
        return {"status":"Ok", "mesg":"Transaction roll backed"}
    
    def check_if_transaction_exists(self, thread_id):
        ''''
        This function check if trasactions exists for a given thread_id

        Parameter:
            thread_id: The unique identifier for the current thread accessing the data store.
        '''
        return True if thread_id in self.transactions.keys() else False

class Server():
    '''
    This class provides the infrastructure for a multi-client data storage server 
    that interacts with a DataStore.

    Attributes:
        None
    Methods:
        process_command(command, thread)
            Parses and processes client commands
        handle_request(client_connection)
            Listens for incoming data from a client connection
        start(hostm, port)
            Initializes and starts the server by binding to a host and port, 
            and then listening for incoming client connections.
    '''
    def __init__(self):
        self.data_store = DataStore()
    
    def process_command(self, command, thread_id):
        '''
        This function handles client commands by interpreting and executing them 
        within the context of the associated DataStore

        Parameters:
            command: A string containing the command from the client.
            thread_id: A unique identifier for the thread associated with the client request.
        '''
        command = command.split()
        if not command:
            return {"status": "Error", "mesg": "Invalid command"}

        method = command[0].upper() if type(command[0]) == str else command[0]
        if method == "BEGIN" and len(command) == 1:
            return self.data_store.begin(thread_id)
        
        if method == "COMMIT" and len(command) == 1:
            return self.data_store.commit(thread_id)
        
        if method == "ROLLBACK" and len(command) == 1:
            return self.data_store.rollback(thread_id)
        
        if method == "GET" and len(command) == 2:
            value = self.data_store.get(command[1])
            if value is None:
                return {"status": "Error", "mesg": "Key not found"}
            return {"status": "Ok", "result": value}

        if method == "PUT" and len(command) == 3:
            value = self.data_store.put(command[1], command[2], thread_id)
            if value == "ERROR":
                # If the command execution encounters an error, 
                # we perform a rollback of all entries within the current transaction.
                _ = self.data_store.rollback(thread_id)
                if self.data_store.check_if_transaction_exists(thread_id):
                    return {"status": "Error", "mesg": "Failed to set value, ending current transaction"}    
                return {"status": "Error", "mesg": "Failed to set value"}
            elif value == "SUCCESS":
                return {"status": "Ok"}
        
        if method == "DELETE" and len(command) == 2:
            value = self.data_store.delete(command[1], thread_id)
            if value == "ERROR":
                # If the command execution encounters an error, 
                # we perform a rollback of all entries within the current transaction.
                _ = self.data_store.rollback(thread_id)
                if self.data_store.check_if_transaction_exists(thread_id):
                   return {"status": "Error", "mesg": "Failed to set value, ending current transaction"}    
                return {"status": "Error", "mesg": "Key not found"}
            elif value == "SUCCESS":
                return {"status": "Ok"}

        else:
            return {"status": "Error", "mesg": "Invalid command"}
    
    def handle_request(self, client_connection):
        '''
        This function manages incoming client connections by continuously receiving 
        and processing data from the client. 

        Parameters:
            client_connection: The connection object for the connected client
        '''
        while True:
            data = client_connection.recv(1024).decode('utf-8')
            if data == "END":
                client_connection.send(json.dumps({"status": "OK", "mesg": "Closing connection"}).encode('utf-8'))
                break
            response = self.process_command(data, threading.current_thread().name)
            client_connection.send(json.dumps(response).encode('utf-8'))
            print(self.data_store.transactions)
        client_connection.close()
        

    def start(self, host, port):
        '''
        This initiates the server, allowing it to listen for incoming client connections on 
        a specified host and port. It operates as a continuous loop to facilitate multiple 
        client connections simultaneously. 

        Parameters:
            host: The host address for the server to listen on.
            port: The port number for the server to listen on.
        '''
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(5) #For now setting the number of clients to 5
        print(f"Server listining on port {port}")
        
        while True:
            client_connection, _ = server_socket.accept()
            client_thread = threading.Thread(target=self.handle_request, args=(client_connection,))
            client_thread.start()
        

if __name__ == '__main__':
    server = Server()
    server.start(HOST, PORT)