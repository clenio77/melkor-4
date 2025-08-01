-- Script de inicialização do PostgreSQL para Melkor 3.0
-- Cria database, usuário e configurações iniciais

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Configurações de performance para desenvolvimento
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Criar schema para auditoria (futuro)
CREATE SCHEMA IF NOT EXISTS audit;

-- Comentários informativos
COMMENT ON DATABASE melkor_dev IS 'Database de desenvolvimento do Melkor 3.0 - Sistema de análise jurídica com IA';

-- Configurar timezone
SET timezone = 'America/Sao_Paulo';

-- Criar função para timestamps automáticos
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Mensagem de sucesso
DO $$
BEGIN
    RAISE NOTICE 'Database Melkor 3.0 inicializado com sucesso!';
    RAISE NOTICE 'Timezone configurado para: %', current_setting('timezone');
    RAISE NOTICE 'Extensões instaladas: uuid-ossp, pg_trgm';
END $$;
