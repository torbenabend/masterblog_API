"""
Simple Flask-based REST API for managing blog posts.

This module provides endpoints to create, read, update, delete, and search
posts stored in an in-memory list. It also supports optional sorting and
basic validation of input data.

Features:
- Retrieve all posts (with optional sorting)
- Add new posts
- Update existing posts
- Delete posts
- Search posts by title and/or content

Note:
    Data is stored in-memory and will be reset when the application restarts.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def get_new_id() -> int:
    """
    Generate a new unique ID for a post.

    Returns:
        int: A new ID that is one greater than the current maximum post ID.

    Raises:
        ValueError: If POSTS is empty and max() fails.
    """
    return 1 + max(
        (post["id"] for post in POSTS)
    )


def validate_post_data(post_data: dict[str, str]) -> bool:
    """
    Validate incoming post data.

    Ensures that the required fields 'title' and 'content' are present.

    Args:
        post_data (dict[str, str]): The post data to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    if "title" not in post_data or "content" not in post_data:
        return False
    return True


def find_post_by_id(post_id: int):
    """
    Find a post by its ID.

    Args:
        post_id (int): The ID of the post to find.

    Returns:
        dict | None: The matching post if found, otherwise None.
    """
    return next(
        (post for post in POSTS if post["id"] == post_id), None
    )


@app.route("/api/posts", methods=["GET"])
def get_posts():
    """
    Retrieve all posts, optionally sorted.

    Query Parameters:
        sort (str, optional): Field to sort by ('title' or 'content').
        direction (str, optional): Sort direction ('asc' or 'desc').

    Returns:
        Response: JSON list of posts or an error message if parameters are invalid.
    """
    sort_by = request.args.get("sort")
    sort_direction = request.args.get("direction")
    if sort_by is not None or sort_direction is not None:
        if (sort_by in ["title", "content"] and
                sort_direction in ["asc", "desc"]):
            reverse = sort_direction == "desc"
            sorted_posts = sorted(
                POSTS, key=lambda post: post[sort_by].lower(), reverse=reverse
            )
            return jsonify(sorted_posts)
        else:
            return (jsonify({"error": "Invalid parameter values for sorting"}),
                    400)
    return jsonify(POSTS)


@app.route("/api/posts", methods=["POST"])
def add_post():
    """
    Create a new post.

    Expects JSON input containing 'title' and 'content'.

    Returns:
        Response: The created post with assigned ID and HTTP status 201,
        or an error message with status 400 if validation fails.
    """
    new_post = request.get_json()
    if not validate_post_data(new_post):
        return jsonify(
            {"error": "Invalid post data: 'title' or 'content' missing"}
        ), 400
    new_post["id"] = get_new_id()
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """
    Delete a post by its ID.

    Args:
        post_id (int): The ID of the post to delete.

    Returns:
        Response: Success message if deleted, or error message if not found.
    """
    post_to_delete = find_post_by_id(post_id)
    if post_to_delete is None:
        return jsonify(
            {"error": f"Post with id {post_id} was not found."}
        ), 404
    POSTS.remove(post_to_delete)
    return jsonify(
        {"message": f"Post with id {post_id} has been deleted successfully."}
    )


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    """
    Update an existing post.

    Allows partial updates of post fields via JSON input.

    Args:
        post_id (int): The ID of the post to update.

    Returns:
        Response: The updated post, or an error message if not found.
    """
    post_to_update = find_post_by_id(post_id)
    if post_to_update is None:
        return jsonify(
            {"error": f"Post with id {post_id} was not found."}
        ), 404
    new_post_data = request.get_json()
    if new_post_data:
        for key, value in new_post_data.items():
            post_to_update[key] = value
    return jsonify(post_to_update)


@app.route("/api/posts/search")
def search_posts():
    """
    Search posts by title and/or content.

    Query Parameters:
        title (str, optional): Substring to search for in post titles.
        content (str, optional): Substring to search for in post content.

    Returns:
        Response: JSON list of matching posts.
    """
    title_to_search = request.args.get("title")
    content_to_search = request.args.get("content")
    if title_to_search is not None:
        search_results_title = [
            post for post in POSTS
            if title_to_search.lower() in post["title"].lower()
        ]
        if content_to_search is None:
            return jsonify(search_results_title)

    if content_to_search is not None:
        search_results_content = [
            post for post in POSTS
            if content_to_search.lower() in post["content"].lower()
        ]
        if title_to_search is None:
            return jsonify(search_results_content)

    search_results = [
        post for post in search_results_title if post in search_results_content
    ]

    return jsonify(search_results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
