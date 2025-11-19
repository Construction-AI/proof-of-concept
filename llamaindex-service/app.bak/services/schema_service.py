import app.core.schema_loader as sl

def load_schema():
    return sl.load_schema()

def flatten_fields():
    return sl.flatten_fields(load_schema())