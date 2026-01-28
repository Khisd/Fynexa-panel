if __name__ == "__main__":
    import os
    GITHUB_TOKEN = os.environ.get("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")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
