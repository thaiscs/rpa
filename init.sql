CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Cria enum para tipo de pessoa
CREATE TYPE person_type_enum AS ENUM ('individual', 'company', 'mei', 'other');

-- ============================
-- Clients table
-- ============================
CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legal_name TEXT NOT NULL,
    tax_id TEXT NOT NULL UNIQUE,        -- CNPJ or CPF
    person_type person_type_enum NOT NULL DEFAULT 'company',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
-- ============================
-- Certificates table
-- ============================
CREATE TABLE IF NOT EXISTS certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    client_id UUID NOT NULL
        REFERENCES clients(id)
        ON DELETE CASCADE,

    name TEXT NOT NULL,

    -- Full PFX file encrypted (raw uploaded file)
    encrypted_pfx JSONB NOT NULL,
    -- Password used to unlock the PFX
    encrypted_pfx_password JSONB NOT NULL,
    -- Extracted certificate (.cer or PEM)
    encrypted_cert JSONB NOT NULL,
    -- Extracted private key (.key or PEM)
    encrypted_key JSONB NOT NULL,
    -- Metadata extracted automatically
    issuer TEXT,
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ,

    expired BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

-- ============================
-- Trigger function
-- ============================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Automatically attach trigger to every table with updated_at
DO $$
DECLARE
    t RECORD;
BEGIN
    FOR t IN
        SELECT table_schema, table_name
        FROM information_schema.columns
        WHERE column_name = 'updated_at'
          AND table_schema = 'public'
    LOOP
        EXECUTE format(
            'CREATE TRIGGER set_updated_at_%I
             BEFORE UPDATE ON %I.%I
             FOR EACH ROW
             EXECUTE FUNCTION update_updated_at_column();',
            t.table_name, t.table_schema, t.table_name
        );
    END LOOP;
END;
$$;