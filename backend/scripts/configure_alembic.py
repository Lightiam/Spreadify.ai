import configparser

def update_alembic_config():
    config = configparser.ConfigParser()
    config.read('alembic.ini')
    config['alembic']['sqlalchemy.url'] = 'sqlite:///./test.db'
    with open('alembic.ini', 'w') as f:
        config.write(f)

if __name__ == "__main__":
    update_alembic_config()
