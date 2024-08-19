# backend.py
from sqlalchemy import create_engine, MetaData, Table, insert, update, delete, select, func

class DatabaseHandler:
    def __init__(self, db_path):
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        self.current_table = None

    def get_table_names(self):
        return self.metadata.tables.keys()

    def set_current_table(self, table_name):
        self.current_table = Table(table_name, self.metadata, autoload_with=self.engine)

    def get_columns(self):
        if self.current_table is not None:
            return self.current_table.columns.keys()
        return []

    def add_entry(self, **kwargs):
        if self.current_table is None:
            raise Exception("No table selected")
        ins = insert(self.current_table).values(**kwargs)
        with self.engine.connect() as conn:
            conn.execute(ins)
    
    def update_entry(self, where_clause, **kwargs):
        if self.current_table is None:
            raise Exception("No table selected")
        upd = update(self.current_table).where(where_clause).values(**kwargs)
        with self.engine.connect() as conn:
            conn.execute(upd)
    
    def delete_entry(self, where_clause):
        if self.current_table is None:
            raise Exception("No table selected")
        del_stmt = delete(self.current_table).where(where_clause)
        with self.engine.connect() as conn:
            conn.execute(del_stmt)
    
    def query_entries(self):
        if self.current_table is None:
            raise Exception("No table selected")
        sel = select([self.current_table])
        with self.engine.connect() as conn:
            result = conn.execute(sel)
            return result.fetchall()
        
    def get_max_value(self, column_name):
        """Returns the maximum value of the specified column."""
        if self.current_table is None:
            raise ValueError("No table selected.")
        max_value = self.session.query(func.max(getattr(self.current_table.c, column_name))).scalar()
        return max_value
