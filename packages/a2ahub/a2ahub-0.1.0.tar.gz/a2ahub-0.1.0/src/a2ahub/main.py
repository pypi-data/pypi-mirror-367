"""
Main module for a2ahub package
"""

def hello_world(name: str = "World") -> str:
    """
    Return a hello world greeting.
    
    Args:
        name (str): The name to greet. Defaults to "World".
        
    Returns:
        str: A greeting message.
    """
    return f"Hello, {name}! Welcome to a2ahub!"


def main():
    """
    Main entry point for the command line interface.
    """
    print(hello_world())
    print("This is a2ahub package - ready for your awesome features!")


if __name__ == "__main__":
    main()
