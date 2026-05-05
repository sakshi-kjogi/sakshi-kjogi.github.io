-- Run this entire script in the Supabase dashboard → SQL Editor

CREATE TABLE IF NOT EXISTS users (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(255) NOT NULL,
    role          VARCHAR(50)  NOT NULL DEFAULT 'Customer'
                      CHECK (role IN ('Customer', 'RestaurantOwner', 'DeliveryPerson', 'Admin')),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
    user_id    UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    token      TEXT        NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Speed up token lookups
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens (token);
