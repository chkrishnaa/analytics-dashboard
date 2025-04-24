from run import app

# Serverless entry point for Vercel
def handler(request, **kwargs):
    return app(request.environ, request.start_response)

# This allows the file to be run directly for local development
if __name__ == "__main__":
    app.run() 