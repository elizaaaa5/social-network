import grpc
import uuid
from concurrent import futures
import os
import sys
from datetime import datetime
import logging

# Add the directory to sys.path to import the generated code
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the generated gRPC code
from app.proto import post_service_pb2, post_service_pb2_grpc
from app.database import PostRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostServiceServicer(post_service_pb2_grpc.PostServiceServicer):
    def __init__(self):
        self.post_repository = PostRepository()
    
    def CreatePost(self, request, context):
        logger.info(f"Creating post for user {request.user_id}")
        post = self.post_repository.create_post(
            user_id=request.user_id,
            title=request.title,
            content=request.content
        )
        
        return post_service_pb2.Post(
            id=str(post.id),
            user_id=post.user_id,
            title=post.title,
            content=post.content,
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat()
        )
    
    def GetPost(self, request, context):
        logger.info(f"Getting post {request.post_id}")
        post = self.post_repository.get_post(request.post_id)
        
        if post is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Post with ID {request.post_id} not found")
            return post_service_pb2.Post()
        
        return post_service_pb2.Post(
            id=str(post.id),
            user_id=post.user_id,
            title=post.title,
            content=post.content,
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat()
        )
    
    def ListPosts(self, request, context):
        logger.info(f"Listing posts for user {request.user_id}")
        posts, total = self.post_repository.list_posts(
            user_id=request.user_id,
            page=request.page,
            page_size=request.page_size
        )
        
        response = post_service_pb2.ListPostsResponse(total=total)
        
        for post in posts:
            post_pb = post_service_pb2.Post(
                id=str(post.id),
                user_id=post.user_id,
                title=post.title,
                content=post.content,
                created_at=post.created_at.isoformat(),
                updated_at=post.updated_at.isoformat()
            )
            response.posts.append(post_pb)
        
        return response
    
    def UpdatePost(self, request, context):
        logger.info(f"Updating post {request.post_id}")
        post = self.post_repository.update_post(
            post_id=request.post_id,
            title=request.title,
            content=request.content
        )
        
        if post is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Post with ID {request.post_id} not found")
            return post_service_pb2.Post()
        
        return post_service_pb2.Post(
            id=str(post.id),
            user_id=post.user_id,
            title=post.title,
            content=post.content,
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat()
        )
    
    def DeletePost(self, request, context):
        logger.info(f"Deleting post {request.post_id} for user {request.user_id}")
        success = self.post_repository.delete_post(
            post_id=request.post_id,
            user_id=request.user_id
        )
        
        if not success:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Post with ID {request.post_id} not found or not authorized")
        
        return post_service_pb2.DeletePostResponse(success=success)

def serve():
    port = os.getenv("POST_SERVICE_PORT", "50051")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    post_service_pb2_grpc.add_PostServiceServicer_to_server(
        PostServiceServicer(), server
    )
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info(f"Post service running on port {port}")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
