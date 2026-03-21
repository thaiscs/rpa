CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Tabela de Clientes
CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    razao_social TEXT NOT NULL,
    cnpj_cpf TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de Certificados
CREATE TABLE IF NOT EXISTS certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    client_id UUID NOT NULL
        REFERENCES clients(id)
        ON DELETE CASCADE,

    name TEXT NOT NULL,

    encrypted_cert JSONB NOT NULL,
    encrypted_key  JSONB NOT NULL,
    encrypted_cert_user TEXT,
    encrypted_cert_password TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);