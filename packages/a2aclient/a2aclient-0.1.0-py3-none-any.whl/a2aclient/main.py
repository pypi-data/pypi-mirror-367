"""
Main module for a2aclient
"""

def hello_world(name: str = "World") -> str:
    """
    A simple hello world function.
    
    Args:
        name (str): The name to greet. Defaults to "World".
        
    Returns:
        str: A greeting message.
    """
    return f"Hello, {name}! Welcome to a2aclient!"


def main():
    """Main entry point for the application."""
    print(hello_world())


if __name__ == "__main__":
    main()
