-- ============================================
-- Risko.ai Database Schema
-- Complete schema with enums and tables
-- ============================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create ENUM types
DO $$ BEGIN
    CREATE TYPE subscriptiontier AS ENUM ('free', 'creator', 'pro', 'agency');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE searchmode AS ENUM ('keywords', 'username');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE socialplatform AS ENUM ('tiktok', 'instagram', 'youtube', 'twitter', 'snapchat');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Table: profile_data

CREATE TABLE profile_data (
	id SERIAL NOT NULL, 
	username VARCHAR(100) NOT NULL, 
	channel_data JSONB NOT NULL, 
	recent_videos_data JSONB NOT NULL, 
	total_videos INTEGER, 
	avg_views FLOAT, 
	engagement_rate FLOAT, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
)

;

-- Table: users

CREATE TABLE users (
	id SERIAL NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	hashed_password VARCHAR(255), 
	full_name VARCHAR(255), 
	subscription_tier subscriptiontier NOT NULL, 
	credits INTEGER NOT NULL, 
	credits_reset_at TIMESTAMP WITHOUT TIME ZONE, 
	is_active BOOLEAN NOT NULL, 
	is_verified BOOLEAN NOT NULL, 
	is_admin BOOLEAN NOT NULL, 
	oauth_provider VARCHAR(50), 
	oauth_id VARCHAR(255), 
	avatar_url VARCHAR(500), 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	last_login_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;

-- Table: chat_messages

CREATE TABLE chat_messages (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	session_id VARCHAR(100) NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	content TEXT NOT NULL, 
	model VARCHAR(50), 
	mode VARCHAR(50), 
	tokens_used INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)

;

-- Table: competitors

CREATE TABLE competitors (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	username VARCHAR(100) NOT NULL, 
	display_name VARCHAR(255), 
	avatar_url VARCHAR(500), 
	bio TEXT, 
	followers_count INTEGER, 
	following_count INTEGER, 
	total_likes INTEGER, 
	total_videos INTEGER, 
	avg_views FLOAT, 
	engagement_rate FLOAT, 
	posting_frequency FLOAT, 
	recent_videos JSONB NOT NULL, 
	top_hashtags JSONB NOT NULL, 
	content_categories JSONB NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	notes TEXT, 
	tags JSONB NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	last_analyzed_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT uix_competitor_user_username UNIQUE (user_id, username), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)

;

-- Table: trends

CREATE TABLE trends (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	platform_id VARCHAR(100), 
	url VARCHAR(500), 
	description TEXT, 
	cover_url VARCHAR(500), 
	vertical VARCHAR(100), 
	music_id VARCHAR(100), 
	music_title VARCHAR(255), 
	author_username VARCHAR(100), 
	author_followers INTEGER, 
	stats JSONB NOT NULL, 
	initial_stats JSONB NOT NULL, 
	uts_score FLOAT, 
	cluster_id INTEGER, 
	similarity_score FLOAT, 
	reach_score FLOAT, 
	uplift_score FLOAT, 
	ai_summary TEXT, 
	embedding VECTOR(512), 
	search_query VARCHAR(255), 
	search_mode searchmode, 
	is_deep_scan BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	last_scanned_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT uix_trend_user_platform UNIQUE (user_id, platform_id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)

;

-- Table: user_accounts

CREATE TABLE user_accounts (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	platform socialplatform NOT NULL, 
	username VARCHAR(100) NOT NULL, 
	display_name VARCHAR(255), 
	avatar_url VARCHAR(500), 
	profile_url VARCHAR(500), 
	bio TEXT, 
	followers_count INTEGER, 
	following_count INTEGER, 
	total_posts INTEGER, 
	total_likes INTEGER, 
	total_views INTEGER, 
	avg_views FLOAT, 
	avg_likes FLOAT, 
	engagement_rate FLOAT, 
	posting_frequency FLOAT, 
	growth_history JSONB NOT NULL, 
	recent_posts JSONB NOT NULL, 
	top_posts JSONB NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	is_verified BOOLEAN NOT NULL, 
	is_primary BOOLEAN NOT NULL, 
	platform_user_id VARCHAR(255), 
	oauth_access_token TEXT, 
	oauth_refresh_token TEXT, 
	oauth_token_expires_at TIMESTAMP WITHOUT TIME ZONE, 
	oauth_scope VARCHAR(500), 
	oauth_connected_at TIMESTAMP WITHOUT TIME ZONE, 
	notes TEXT, 
	tags JSONB NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	last_synced_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT uix_user_platform_username UNIQUE (user_id, platform, username), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)

;

-- Table: user_searches

CREATE TABLE user_searches (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	query VARCHAR(255) NOT NULL, 
	mode searchmode NOT NULL, 
	is_deep BOOLEAN NOT NULL, 
	filters JSONB NOT NULL, 
	results_count INTEGER NOT NULL, 
	execution_time_ms INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)

;

-- Table: user_settings

CREATE TABLE user_settings (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	dark_mode BOOLEAN NOT NULL, 
	language VARCHAR(10) NOT NULL, 
	region VARCHAR(10) NOT NULL, 
	timezone VARCHAR(50) NOT NULL, 
	auto_generate_scripts BOOLEAN NOT NULL, 
	default_search_mode searchmode NOT NULL, 
	notifications_email BOOLEAN NOT NULL, 
	notifications_trends BOOLEAN NOT NULL, 
	notifications_competitors BOOLEAN NOT NULL, 
	notifications_new_videos BOOLEAN NOT NULL, 
	notifications_weekly_report BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)

;

-- Table: user_favorites

CREATE TABLE user_favorites (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	trend_id INTEGER NOT NULL, 
	notes TEXT, 
	tags JSONB NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uix_favorite_user_trend UNIQUE (user_id, trend_id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(trend_id) REFERENCES trends (id) ON DELETE CASCADE
)

;

-- Table: user_scripts

CREATE TABLE user_scripts (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	hook TEXT NOT NULL, 
	body JSONB NOT NULL, 
	call_to_action TEXT, 
	source_trend_id INTEGER, 
	tone VARCHAR(50) NOT NULL, 
	niche VARCHAR(100), 
	duration_seconds INTEGER NOT NULL, 
	language VARCHAR(10) NOT NULL, 
	model_used VARCHAR(50) NOT NULL, 
	viral_elements JSONB NOT NULL, 
	tips JSONB NOT NULL, 
	tags JSONB NOT NULL, 
	is_favorite BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(source_trend_id) REFERENCES trends (id) ON DELETE SET NULL
)

;
