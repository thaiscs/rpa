from sqlalchemy import text
from sqlalchemy.engine import Connection

def create_updated_at_trigger(conn: Connection):
    # 1. Trigger function
    conn.execute(text("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """))

    # 2. Attach trigger to every table that has updated_at
    conn.execute(text("""
        DO $$
        DECLARE
            t RECORD;
            trigger_name text;
        BEGIN
            FOR t IN
                SELECT table_name
                FROM information_schema.columns
                WHERE column_name = 'updated_at'
                  AND table_schema = 'public'
            LOOP
                trigger_name := 'set_updated_at_' || t.table_name;
                
                IF NOT EXISTS (
                      SELECT 1
                      FROM pg_trigger
                      WHERE tgname = trigger_name
                ) THEN
                    EXECUTE format(
                        'CREATE TRIGGER %I
                         BEFORE UPDATE ON %I
                         FOR EACH ROW 
                         EXECUTE FUNCTION update_updated_at_column();',
                        trigger_name, t.table_name
                );
                END IF;
            END LOOP;
        END$$;
    """))