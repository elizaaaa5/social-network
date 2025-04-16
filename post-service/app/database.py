from datetime import datetime
import uuid
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns
import os
from typing import List, Optional

# Get Cassandra configuration from environment variables
CASSANDRA_HOSTS = os.getenv("CASSANDRA_HOSTS", "cassandra-db").split(",")
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "post_service")
CASSANDRA_USER = os.getenv("CASSANDRA_USER", "cassandra")
CASSANDRA_PASSWORD = os.getenv("CASSANDRA_PASSWORD", "cassandra")

def connect_to_cassandra():
    auth_provider = PlainTextAuthProvider(
        username=CASSANDRA_USER, 
        password=CASSANDRA_PASSWORD
    )
    
    cluster = Cluster(
        CASSANDRA_HOSTS, 
        auth_provider=auth_provider
    )
    
    session = cluster.connect()
    
    # Create keyspace if it doesn't exist
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': '1'}}
    """)
    
    # Connect to keyspace
    connection.setup(
        CASSANDRA_HOSTS, 
        CASSANDRA_KEYSPACE, 
        auth_provider=auth_provider
    )
    
    return session

class Post(Model):
    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    user_id = columns.Text(index=True)
    title = columns.Text()
    content = columns.Text()
    created_at = columns.DateTime(default=datetime.utcnow)
    updated_at = columns.DateTime(default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class PostRepository:
    def __init__(self):
        self.session = connect_to_cassandra()
        sync_table(Post)
    
    def create_post(self, user_id: str, title: str, content: str) -> Post:
        post = Post.create(
            user_id=user_id,
            title=title,
            content=content
        )
        return post
    
    def get_post(self, post_id: str) -> Optional[Post]:
        try:
            return Post.get(id=uuid.UUID(post_id))
        except Post.DoesNotExist:
            return None
    
    def list_posts(self, user_id: str, page: int = 1, page_size: int = 10) -> tuple[List[Post], int]:
        query = Post.objects.filter(user_id=user_id)
        total = query.count() # Get total count first

        # Fetch enough items to cover up to the desired page
        # Note: This can be inefficient for large page numbers in Cassandra
        # A better approach might involve cursor-based pagination (paging state)
        # if performance becomes an issue.
        limit_needed = page * page_size
        fetched_posts = list(query.limit(limit_needed))

        # Calculate the slice start index
        start_index = (page - 1) * page_size

        # Get the posts for the requested page
        posts_for_page = fetched_posts[start_index:] 
        # We don't need end_index because limit already capped the total fetched items

        return posts_for_page, total
    
    def update_post(self, post_id: str, title: str, content: str) -> Optional[Post]:
        try:
            post = Post.get(id=uuid.UUID(post_id))
            post.title = title
            post.content = content
            post.updated_at = datetime.utcnow()
            post.save()
            return post
        except Post.DoesNotExist:
            return None
    
    def delete_post(self, post_id: str, user_id: str) -> bool:
        try:
            post = Post.get(id=uuid.UUID(post_id))
            if post.user_id != user_id:
                return False
            post.delete()
            return True
        except Post.DoesNotExist:
            return False
