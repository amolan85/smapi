from flask import Flask, request
from flask_cors import CORS 
from flask_jwt_extended import (
    JWTManager,
    verify_jwt_in_request,
    get_jwt_identity,
    create_access_token
)
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.society_routes import society_bp
from datetime import timedelta

app = Flask(__name__)

CORS(app,
     expose_headers=["Authorization"],
     resources={
         r"/api/*": {
             "origins": ["http://localhost:8081"]
         }
     }
)

app.config["JWT_SECRET_KEY"] = "super-secret-key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(society_bp, url_prefix="/api/society")

@app.after_request
def attach_token(response):
    try:
        # Check if request contains valid JWT
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()

        if identity:
            # Create new token (auto refresh)
            new_token = create_access_token(identity=identity)
            response.headers["Authorization"] = f"Bearer {new_token}"

    except Exception:
        pass
 
if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000, debug=True)


 