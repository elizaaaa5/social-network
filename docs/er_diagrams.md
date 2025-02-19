erDiagram
    USERS ||--o{ USERS_ROLE : has
    USERS {
        uuid id PK
        string username
        string email
        string password_hash
        timestamp created_at
        boolean is_active
    }
    
    ROLE {
        uuid id PK
        string name
        string description
    }
    
    USERS_ROLE {
        uuid users_id FK
        uuid role_id FK
        timestamp assigned_at
    }

    POST ||--o{ POST_LIKE : has
    USERS ||--o{ POST : creates

    POST {
        uuid id PK
        uuid users_id FK
        text content
        timestamp created_at
        timestamp updated_at
        int version
    }

    POST_LIKE {
        uuid post_id FK
        uuid users_id FK
        string reaction_type
        timestamp created_at
    }
    
        POST_VIEW {
        uuid id PK
        uuid post_id FK
        uuid user_id FK
        string ip_address
        timestamp viewed_at
        string users_agent
    }

    COMMENT ||--o{ COMMENT_LIKE : "has"
    COMMENT ||--o{ COMMENT_METADATA : "stores"
    USERS ||--o{ COMMENT : "creates"

    COMMENT {
        uuid id PK
        uuid post_id FK
        uuid users_id FK
        uuid parent_id
        text content
        timestamp created_at
        int version
    }

    COMMENT_LIKE {
        uuid id PK
        uuid comment_id FK
        uuid users_id FK
        string reaction_type
        timestamp created_at
    }

    COMMENT_METADATA {
        uuid comment_id PK
        timestamp last_edited
        uuid edited_by
        boolean is_pinned
        boolean is_flagged
        string moderation_status
        string additional_info
    }

    POST_STATISTIC ||--|| POST : "references"
    COMMENT_STATISTIC ||--|| COMMENT : "references"
    USERS_ACTIVITY ||--|| USERS : "references"

    POST_STATISTIC {
        uuid post_id PK
        int total_views
        int total_likes
        int total_comments
        timestamp first_activity
        timestamp last_activity
    }

    COMMENT_STATISTIC {
        uuid comment_id PK
        int total_replies
        int total_likes
        timestamp first_created
        timestamp last_updated
    }

    USERS_ACTIVITY {
        uuid users_id PK
        timestamp last_active
        int total_posts_created
        int total_comments_created
        int total_reactions_given
    }