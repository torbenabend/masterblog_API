from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def get_new_id() -> int:
    return 1 + max(
        (post["id"] for post in POSTS)
    )


def validate_post_data(post_data: dict[str, str]) -> bool:
    if "title" not in post_data or "content" not in post_data:
        return False
    return True


@app.route("/api/posts", methods=["GET"])
def get_posts():
    return jsonify(POSTS)


@app.route("/api/posts", methods=["POST"])
def add_post():
    new_post = request.get_json()
    if not validate_post_data(new_post):
        return jsonify(
            {"error": "Invalid post data: 'title' or 'content' missing"}
        ), 400
    new_post["id"] = get_new_id()
    POSTS.append(new_post)
    return jsonify(new_post), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)