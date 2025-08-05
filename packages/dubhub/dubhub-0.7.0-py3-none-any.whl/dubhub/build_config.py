# Build-time configuration for dubhub CLI
# This file is generated/modified during the build process

# Tailscale integration enabled/disabled at build time
TAILSCALE_ENABLED = False

# Custom host prompting enabled/disabled at build time
CUSTOM_HOST_ENABLED = False

def is_tailscale_enabled():
    """Check if Tailscale integration is enabled in this build."""
    return TAILSCALE_ENABLED

def is_custom_host_enabled():
    """Check if custom host prompting is enabled in this build."""
    return CUSTOM_HOST_ENABLED
