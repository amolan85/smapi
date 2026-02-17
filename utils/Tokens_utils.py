from flask_jwt_extended import create_access_token

def generate_token(user):
    return create_access_token(
        identity=str(user["id"]),
        additional_claims={"role": user["role"]}
    )
