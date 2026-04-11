from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

async def create_updated_at_trigger(engine: AsyncEngine):
    async with engine.begin() as conn:
        # 1. Trigger function
        await conn.execute(text("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """))

        # 2. Attach trigger to tables that have updated_at
        await conn.execute(text("""
        DO $$
        DECLARE
            t RECORD;
        BEGIN
            FOR t IN
                SELECT table_name
                FROM information_schema.columns
                WHERE column_name = 'updated_at'
                  AND table_schema = 'public'
            LOOP
                EXECUTE format(
                    'CREATE TRIGGER IF NOT EXISTS set_updated_at_%I
                     BEFORE UPDATE ON %I
                     FOR EACH ROW
                     EXECUTE FUNCTION update_updated_at_column();',
                    t.table_name, t.table_name
                );
            END LOOP;
        END$$;
        """))