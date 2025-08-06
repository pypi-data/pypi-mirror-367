"""Version and release information for raxodus."""

__version__ = "0.1.1"
__codename__ = "Mondain"
__tagline__ = "The dark wizard whose defeat marked the beginning of the Age of Darkness"

def get_avatar_url(style: str = "bottts") -> str:
    """Get the DiceBear avatar URL for the current release.

    Args:
        style: Avatar style (pixel-art, adventurer, bottts, etc.)

    Returns:
        URL to the avatar image
    """
    return f"https://api.dicebear.com/9.x/{style}/svg?seed={__codename__}"

def get_version_info() -> str:
    """Get full version information.

    Returns:
        Formatted version string with codename
    """
    return f"raxodus v{__version__} - '{__codename__}'"
