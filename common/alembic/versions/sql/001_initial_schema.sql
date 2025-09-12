-- Create businesses table first
CREATE TABLE IF NOT EXISTS businesses (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create users table based on UserData schema
CREATE TABLE IF NOT EXISTS users (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    is_pending BOOLEAN,
    profile_picture_url TEXT,
    job_title VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create index on is_active for filtering
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Create junction table for many-to-many relationship between users and businesses
CREATE TABLE IF NOT EXISTS user_businesses (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_uuid UUID NOT NULL REFERENCES users(uuid) ON DELETE CASCADE,
    business_uuid UUID NOT NULL REFERENCES businesses(uuid) ON DELETE CASCADE,
    role VARCHAR(100),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_uuid, business_uuid)
);

-- Create indexes for the junction table
CREATE INDEX IF NOT EXISTS idx_user_businesses_user_uuid ON user_businesses(user_uuid);
CREATE INDEX IF NOT EXISTS idx_user_businesses_business_uuid ON user_businesses(business_uuid);
CREATE INDEX IF NOT EXISTS idx_user_businesses_is_primary ON user_businesses(is_primary);

INSERT INTO businesses (uuid, name, created_at, updated_at) VALUES
(
    '66cdd613-0be9-4f62-b819-e841d888744c',
    'TechCorp Solutions',
    '2024-01-01 09:00:00+00',
    '2024-01-01 09:00:00+00'
),
(
    'e0a7189e-4868-49c9-b20d-9a0508fc79f3',
    'Innovation Labs',
    '2024-01-02 10:00:00+00',
    '2024-01-02 10:00:00+00'
);

-- Insert mock data (5 users)
INSERT INTO users (uuid, first_name, last_name, email, is_active, is_pending, profile_picture_url, job_title, created_at, updated_at) VALUES
(
    '550e8400-e29b-41d4-a716-446655440001',
    'John',
    'Doe',
    'john.doe@example.com',
    true,
    false,
    'https://example.com/profiles/john_doe.jpg',
    'Software Engineer',
    '2024-01-15 10:30:00+00',
    '2024-01-15 10:30:00+00'
),
(
    '550e8400-e29b-41d4-a716-446655440002',
    'Jane',
    'Smith',
    'jane.smith@example.com',
    true,
    true,
    'https://example.com/profiles/jane_smith.jpg',
    'Product Manager',
    '2024-01-16 14:20:00+00',
    '2024-01-16 14:20:00+00'
),
(
    '550e8400-e29b-41d4-a716-446655440003',
    'Mike',
    'Johnson',
    'mike.johnson@example.com',
    false,
    false,
    NULL,
    'Data Scientist',
    '2024-01-17 09:15:00+00',
    '2024-01-20 16:45:00+00'
),
(
    '550e8400-e29b-41d4-a716-446655440004',
    'Sarah',
    'Wilson',
    'sarah.wilson@example.com',
    true,
    false,
    'https://example.com/profiles/sarah_wilson.jpg',
    'UX Designer',
    '2024-01-18 11:00:00+00',
    '2024-01-18 11:00:00+00'
),
(
    '550e8400-e29b-41d4-a716-446655440005',
    'David',
    'Brown',
    'david.brown@example.com',
    true,
    true,
    'https://example.com/profiles/david_brown.jpg',
    'DevOps Engineer',
    '2024-01-19 13:30:00+00',
    '2024-01-22 08:20:00+00'
);

-- Insert user-business relationships
-- 3 users linked to TechCorp Solutions, 2 users linked to Innovation Labs
-- John is in both businesses (with TechCorp as primary)
INSERT INTO user_businesses (uuid, user_uuid, business_uuid, role, is_primary, created_at, updated_at) VALUES
(
    'a0000000-0000-0000-0000-000000000001',
    '550e8400-e29b-41d4-a716-446655440001', -- John Doe
    '66cdd613-0be9-4f62-b819-e841d888744c', -- TechCorp Solutions
    'Software Engineer',
    true,
    '2024-01-15 10:30:00+00',
    '2024-01-15 10:30:00+00'
),
(
    'a0000000-0000-0000-0000-000000000002',
    '550e8400-e29b-41d4-a716-446655440001', -- John Doe
    'e0a7189e-4868-49c9-b20d-9a0508fc79f3', -- Innovation Labs
    'Senior Software Engineer',
    false,
    '2024-01-15 10:30:00+00',
    '2024-01-15 10:30:00+00'
),
(
    'a0000000-0000-0000-0000-000000000003',
    '550e8400-e29b-41d4-a716-446655440002', -- Jane Smith
    '66cdd613-0be9-4f62-b819-e841d888744c', -- TechCorp Solutions
    'Product Manager',
    true,
    '2024-01-16 14:20:00+00',
    '2024-01-16 14:20:00+00'
),
(
    'a0000000-0000-0000-0000-000000000004',
    '550e8400-e29b-41d4-a716-446655440003', -- Mike Johnson
    '66cdd613-0be9-4f62-b819-e841d888744c', -- TechCorp Solutions
    'Data Scientist',
    true,
    '2024-01-17 09:15:00+00',
    '2024-01-20 16:45:00+00'
),
(
    'a0000000-0000-0000-0000-000000000005',
    '550e8400-e29b-41d4-a716-446655440004', -- Sarah Wilson
    'e0a7189e-4868-49c9-b20d-9a0508fc79f3', -- Innovation Labs
    'UX Designer',
    true,
    '2024-01-18 11:00:00+00',
    '2024-01-18 11:00:00+00'
),
(
    'a0000000-0000-0000-0000-000000000006',
    '550e8400-e29b-41d4-a716-446655440005', -- David Brown
    'e0a7189e-4868-49c9-b20d-9a0508fc79f3', -- Innovation Labs
    'DevOps Engineer',
    true,
    '2024-01-19 13:30:00+00',
    '2024-01-22 08:20:00+00'
);

-- Create a trigger to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_businesses_updated_at 
    BEFORE UPDATE ON businesses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_businesses_updated_at 
    BEFORE UPDATE ON user_businesses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
