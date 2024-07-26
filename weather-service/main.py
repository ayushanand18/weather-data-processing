"""
Main script file to run backend and database
"""

import argparse

def _run_tests():
    """ Run tests """
    print("--test: running tests")
    
    import unittest
    import tests.test_server
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(tests.test_server)
    
    runner = unittest.TextTestRunner()
    runner.run(suite)

def _run_dev_api_server(host, port):
    """ Run a dev instance of the FastAPI server """
    if not host:
        host = "0.0.0.0"
    
    if not port:
        port = 5000
    
    import uvicorn
    
    uvicorn.run('weather_service.main:app', host=host, port=port, reload=True)
    

def _run_db_migrate():
    """ Instantiate Postgres DB with schema, and empty tables """
    print("--migrate: running DB Migrate")

def _run_start_db():
    """ Start the DB instance on local machine """
    print("--db: starting DB")

def _show_help():
    """ Show Help Information """
    help_string = """usage: main.py [-h] [--tests] [--dev] [--migrate] [--db] [--host HOST] [--port PORT]

    options:
    -h, --help         show this help message and exit
    --tests            Run tests
    --dev DEV          Run dev FastAPI Server
    --migrate MIGRATE  Setup Postgres DB with database and tables. Make sure to update .env
    --db DB            Start the DB process. If you would manually start, please do not execute this
    --host HOST        Add host address to run the FastAPI Server
    --port PORT        Add port address to run the FastAPI Server
    """

    print(help_string)

def main():
    """
    Entry into the app, execute commands according to the arguments supplied.
    """
    parser = argparse.ArgumentParser(allow_abbrev=False)

    # Add arguments to be processed by the python cmd
    parser.add_argument('--tests', action='store_true', help='Run Unittests')
    parser.add_argument('--dev', action='store_true', help='Run dev FastAPI Server')
    parser.add_argument('--migrate', action='store_true', help='Setup Postgres DB with database and tables. Make sure to update .env')
    parser.add_argument('--db', action='store_true', help='Start the DB process. If you would manually start, please do not execute this')
    parser.add_argument('--host', dest='host', type=str, help='Add host address to run the FastAPI Server')
    parser.add_argument('--port', dest='port', type=int, help='Add port address to run the FastAPI Server')

    args = parser.parse_args()

    if args.tests:
        _run_tests()
    elif args.dev:
        _run_dev_api_server(args.host, args.port)
    elif args.migrate:
        _run_db_migrate()
    elif args.db:
        _run_start_db()
    else:
        _show_help()
        

if __name__ == "__main__":
    main()
