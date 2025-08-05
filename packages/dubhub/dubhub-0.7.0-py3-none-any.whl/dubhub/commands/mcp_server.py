import logging
import httpx
import psycopg
from urllib.parse import urlparse, urlunparse
from mcp.server.fastmcp import FastMCP
from .. import utils
from ..version import VERSION
from .. import client as api_client
from ..build_config import is_tailscale_enabled

# Conditional Tailscale imports
if is_tailscale_enabled():
    from ..tailscale import create_tailscale_forwarder, stop_forwarder_by_clone_uuid
else:
    # Provide stub functions when Tailscale is disabled
    def create_tailscale_forwarder():
        return None
    
    def stop_forwarder_by_clone_uuid(clone_uuid):
        return {"success": False, "message": "Tailscale not enabled in this build"}

mcp = FastMCP("baseshift-clone-management")
logger = logging.getLogger(__name__)

# In-memory storage for started clones
started_clones = {}

# Global Tailscale forwarder instance
tailscale_forwarder = None

# Log Tailscale availability on module load
if not is_tailscale_enabled():
    pass  # Silently skip Tailscale integration


@mcp.tool()
async def start_clone(dub_uuid: str = None, org_token: str = None) -> str:
    """Starts a new database clone.

    This tool initiates the creation of a new clone from a production database. It communicates with the Baseshift server to provision the necessary resources. The started clone's details, including its UUID and connection string, are stored in memory for the duration of the server's runtime.

    Args:
        dub_uuid: The unique identifier for the Dub to be cloned. If not provided, it will be retrieved from the config file.
        org_token: The organization token for authentication. If not provided, it will be retrieved from the config file.

    Returns:
        A confirmation message with the clone's details upon successful creation, or an error message if it fails.
    """
    global tailscale_forwarder
    
    try:
        dub_uuid = utils.get_config_value(
            dub_uuid, "BASESHIFT_DUB_UUID", "dubUuid", required=True
        )
        org_token = utils.get_config_value(
            org_token, "BASESHIFT_ORG_TOKEN", "orgToken", required=True
        )
        server = utils.get_config_value(
            None, "DUBHUB_HOST", "host", default="https://app.dubhub.io"
        )

        logger.info(f"Attempting to start clone with dub_uuid: '{dub_uuid}'")

        response = await api_client.start_clone_api_async(dub_uuid, org_token, server)

        if response.status_code >= 400:
            error_body = ""
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text

            error_message = f"API request failed with status {response.status_code}. Server response: {error_body}"
            logger.error(error_message)
            return f"Error: {error_message}"

        result = response.json()
        logger.info(f"Full API response from start_clone: {result}")

        # Normalize the connection string key from 'conn_string' to 'connectionString'
        if "conn_string" in result and "connectionString" not in result:
            result["connectionString"] = result.pop("conn_string")

        clone_uuid = result.get("cloneUuid")
        conn_string = result.get("connectionString")

        if not clone_uuid:
            return f"Error: Clone UUID not found in response. {result}"

        if not conn_string:
            # Still add to started_clones so list_clones shows it, but without a conn string it will fail on run_sql
            started_clones[clone_uuid] = result
            logger.error(
                f"Clone {clone_uuid} started but no connectionString was returned."
            )
            return f"Error: Connection string not found in API response for clone {clone_uuid}. {result}"

        # Handle Tailscale forwarder integration if server provides auth key
        tailscale_auth_key = result.get("ts_auth_key")
        if tailscale_auth_key and is_tailscale_enabled():
            # Initialize forwarder if not already done
            if not tailscale_forwarder:
                try:
                    tailscale_forwarder = create_tailscale_forwarder()
                    logger.info("Tailscale forwarder initialized successfully for MCP server with server-provided auth key")
                except Exception as e:
                    logger.error(f"Failed to initialize Tailscale forwarder: {e}")
                    return f"Error: Failed to initialize Tailscale forwarder: {e}"
            
            try:
                # Parse connection string to extract host and port
                if "://" in conn_string:
                    parsed = urlparse(conn_string)
                    original_host = parsed.hostname
                    original_port = parsed.port or 5432
                else:
                    # DSN-style parsing
                    params = dict(item.split("=", 1) for item in conn_string.split())
                    original_host = params.get("host", "localhost")
                    original_port = int(params.get("port", 5432))

                # Generate remote hostname and client device name
                dub_name = result.get("dub_name", "unknown")
                clone_uuid_short = clone_uuid[:6]
                tailscale_hostname = f"dubhub-{dub_name}"  # Remote host to connect to
                client_hostname = f"{dub_name}-clone-client-{clone_uuid_short}"  # Local client device name
                
                logger.info(f"Starting Tailscale forwarder for {original_host}:{original_port} as {tailscale_hostname}")
                forwarder_response = tailscale_forwarder.start(
                    auth_key=tailscale_auth_key,
                    remote_host=tailscale_hostname,  # Use Tailscale hostname
                    remote_port=int(original_port),
                    clone_uuid=clone_uuid,
                    dub_name=dub_name,
                    dub_uuid=dub_uuid,
                    hostname=client_hostname,  # Client device name in tailnet
                    ephemeral=True,
                )
                
                if forwarder_response.get("success"):
                    local_port = forwarder_response.get("local_port")
                    logger.info(f"Tailscale forwarder started for MCP, local port: {local_port}")
                    
                    # Update connection string to use localhost with forwarded port
                    if "://" in conn_string:
                        parsed = urlparse(conn_string)
                        new_netloc = f"localhost:{local_port}"
                        if parsed.username:
                            user_info = parsed.username
                            if parsed.password:
                                user_info = f"{user_info}:{parsed.password}"
                            new_netloc = f"{user_info}@{new_netloc}"
                        new_url_parts = parsed._replace(netloc=new_netloc)
                        result["connectionString"] = urlunparse(new_url_parts)
                    else:
                        # DSN-style update
                        params = dict(item.split("=", 1) for item in conn_string.split())
                        params["host"] = "localhost"
                        params["port"] = str(local_port)
                        result["connectionString"] = " ".join(f"{k}={v}" for k, v in params.items())
                    
                    # Add Tailscale info to the result
                    result["tailscale_enabled"] = True
                    result["tailscale_local_port"] = local_port
                    result["tailscale_hostname"] = tailscale_hostname
                else:
                    error_msg = forwarder_response.get("error", "Unknown error")
                    logger.error(f"Failed to start Tailscale forwarder for MCP: {error_msg}")
                    return f"Error: Failed to start Tailscale forwarder: {error_msg}"
                    
            except Exception as e:
                logger.error(f"Exception starting Tailscale forwarder for MCP: {e}")
                return f"Error: Exception starting Tailscale forwarder: {e}"
        else:
            # Fallback to direct connection if no Tailscale auth key
            logger.info("No Tailscale auth key configured, using direct connection")

        started_clones[clone_uuid] = result
        logger.info(f"Clone started successfully: {clone_uuid}")
        return f"Clone started successfully: {result}"
    except Exception as e:
        logger.exception("Error starting clone")
        return f"Error: {e}"


@mcp.tool()
async def stop_clone(clone_uuid: str, org_token: str = None) -> str:
    """Stops a running database clone.

    This tool terminates a specified clone, releasing its resources. It communicates with the Baseshift server to perform the stop operation. If the clone was started during the current server session, it will be removed from the in-memory list of started clones.

    Args:
        clone_uuid: The unique identifier of the clone to be stopped.
        org_token: The organization token for authentication. If not provided, it will be retrieved from the config file.

    Returns:
        A confirmation message upon successful termination, or an error message if it fails.
    """
    try:
        org_token = utils.get_config_value(
            org_token, "BASESHIFT_ORG_TOKEN", "orgToken", required=True
        )
        server = utils.get_config_value(
            None, "DUBHUB_HOST", "host", default="https://app.dubhub.io"
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{server}/api/clone/stop",
                json={
                    "cloneUuid": clone_uuid,
                    "orgToken": org_token,
                    "VERSION": VERSION,
                },
            )
            response.raise_for_status()
            
            # Stop any associated Tailscale forwarder
            try:
                forwarder_result = stop_forwarder_by_clone_uuid(clone_uuid)
                if forwarder_result:
                    logger.info(f"Stopped Tailscale forwarder for clone {clone_uuid}")
            except Exception as forwarder_error:
                logger.warning(f"Error stopping Tailscale forwarder for clone {clone_uuid}: {forwarder_error}")
                # Don't fail the entire stop operation if forwarder cleanup fails
            
            if clone_uuid in started_clones:
                del started_clones[clone_uuid]
            return f"Clone stopped successfully: {response.json()}"
    except Exception as e:
        logger.exception("Error stopping clone")
        return f"Error: {e}"


@mcp.tool()
def list_clones() -> dict:
    """Lists all clones that have been started during the current server session.

    This tool returns a dictionary of clones that were started using the `start_clone` tool since the MCP server was last launched. The keys are the clone UUIDs, and the values are the details returned by the server upon creation.

    Returns:
        A dictionary containing the details of all in-memory clones.
    """
    return started_clones


@mcp.tool()
def run_sql(
    clone_uuid: str, sql_query: str, dbname: str = None, limit: int = 100
) -> str:
    """Runs a read-only SQL query against a specified started clone.

    This tool connects to the database of a running clone and executes a given SQL query. It is intended for read-only operations. The connection uses the connection string that was returned when the clone was started.

    Args:
        clone_uuid: The unique identifier of a clone that is currently in the 'started' state.
        sql_query: The SQL query string to be executed against the clone's database.
        dbname: The name of the database to connect to. If not provided, the default database from the clone's connection string will be used.
        limit: The maximum number of rows to fetch from the query result. Defaults to 100.

    Returns:
        A string containing the formatted query results, a message indicating no rows were returned, or an error message if the query fails or the clone is not found.
    """
    if clone_uuid not in started_clones:
        return "Error: Clone not found."

    clone_info = started_clones[clone_uuid]
    conn_string = clone_info.get("connectionString")

    if not conn_string:
        return "Error: Connection string not found for this clone."

    # If a dbname is provided, we need to modify the connection string
    if dbname:
        try:
            if "://" in conn_string:
                # Handle URI-style connection strings
                parsed = urlparse(conn_string)
                # The path component in a postgres URI is the database name, with a leading slash
                new_url_parts = parsed._replace(path=f"/{dbname}")
                conn_string = urlunparse(new_url_parts)
            else:
                # Handle DSN-style connection strings
                params = dict(item.split("=", 1) for item in conn_string.split())
                params["dbname"] = dbname
                conn_string = " ".join(f"{k}={v}" for k, v in params.items())
        except Exception as e:
            logger.error(
                f"Failed to modify connection string for dbname '{dbname}': {e}"
            )
            return f"Error: Failed to switch database to '{dbname}'."

    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query)
                rows = cur.fetchmany(limit)
                if not rows:
                    return "Query executed successfully, no rows returned."

                colnames = [desc[0] for desc in cur.description]
                result = [dict(zip(colnames, row)) for row in rows]
                return f"Query result:\n{result}"
    except Exception as e:
        logger.exception("Error running SQL query")
        return f"Error: {e}"


def start_mcp_server():
    """Initializes and runs the MCP server using FastMCP."""
    config = utils.load_config()
    if not config:
        logger.error(
            "Failed to load configuration. Make sure '.baseshift/config' exists and is valid."
        )
        return

    mcp.run(transport="stdio")
