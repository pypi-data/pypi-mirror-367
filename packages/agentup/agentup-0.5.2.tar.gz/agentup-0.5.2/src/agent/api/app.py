import os
from contextlib import asynccontextmanager

import httpx
import structlog
import uvicorn
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from fastapi import FastAPI

from agent.config.a2a import JSONRPCError
from agent.config.constants import DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT
from agent.core.executor import GenericAgentExecutor as AgentExecutorImpl
from agent.push.notifier import EnhancedPushNotifier
from agent.services import AgentBootstrapper, ConfigurationManager

from .routes import create_agent_card, jsonrpc_error_handler, router, set_request_handler_instance

# Configure logging
structlog.contextvars.clear_contextvars()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize services using bootstrapper
    # This is where we set up the agent's services and capabilities
    logger.debug("Starting application lifespan with services")
    bootstrapper = AgentBootstrapper()

    try:
        # Single line initialization!
        await bootstrapper.initialize_services(app)

        # Setup request handler with services
        _setup_request_handler(app)

        yield

    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise
    finally:
        # Cleanup services
        await bootstrapper.shutdown_services()


def _setup_request_handler(app: FastAPI) -> None:
    # Get services from app state
    services = app.state.services

    # Create request handler with appropriate push notifier
    client = httpx.AsyncClient()

    # Use push service if available
    push_service = services.get("pushnotificationservice")
    if push_service and push_service.push_notifier:
        push_notifier = push_service.push_notifier
        logger.debug("Using service-provided push notifier")
    else:
        push_notifier = EnhancedPushNotifier(client=client)
        logger.debug("Using default push notifier")

    # Use the agent_card from app.state (already created in create_app())
    agent_card = app.state.agent_card

    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=AgentExecutorImpl(agent=agent_card),
        task_store=InMemoryTaskStore(),
        push_config_store=push_notifier,
        push_sender=push_notifier,
    )

    # Set global request handler
    set_request_handler_instance(request_handler)


def create_app() -> FastAPI:
    agent_card = create_agent_card()

    # Create FastAPI app
    app = FastAPI(
        title=agent_card.name,
        description=agent_card.description,
        version=agent_card.version,
        lifespan=lifespan,
    )

    # Store agent_card in app.state for reuse
    app.state.agent_card = agent_card

    # Configure middleware
    _configure_middleware(app)

    # Add routes and exception handlers
    app.include_router(router)
    app.add_exception_handler(JSONRPCError, jsonrpc_error_handler)

    return app


def _configure_middleware(app: FastAPI) -> None:
    config = ConfigurationManager()

    # Network rate limiting middleware (applied to FastAPI Middleware)
    rate_limit_config = config.get("rate_limiting", {})
    if rate_limit_config.get("enabled", True):
        from agent.api.rate_limiting import NetworkRateLimitMiddleware

        endpoint_limits = rate_limit_config.get(
            "endpoint_limits",
            {
                "/": {"rpm": 100, "burst": 120},
                "/mcp": {"rpm": 50, "burst": 60},
                "/health": {"rpm": 200, "burst": 240},
            },
        )
        app.add_middleware(NetworkRateLimitMiddleware, endpoint_limits=endpoint_limits)
        logger.debug("Network rate limiting middleware enabled")

    # Logging middleware
    logging_config = config.get("logging", {})
    if logging_config.get("correlation_id", True):
        try:
            from asgi_correlation_id import CorrelationIdMiddleware

            from agent.config.logging import LoggingConfig, create_structlog_middleware_with_config

            # Add correlation ID middleware
            app.add_middleware(CorrelationIdMiddleware)

            # Add structured logging middleware
            try:
                logging_cfg = LoggingConfig(**logging_config)
            except Exception:
                logging_cfg = LoggingConfig()

            StructLogMiddleware = create_structlog_middleware_with_config(logging_cfg)
            app.add_middleware(StructLogMiddleware)

            logger.debug("Structured logging middleware enabled")

        except ImportError:
            # Fallback to basic request logging
            if logging_config.get("request_logging", True):
                from .request_logging import add_correlation_id_to_logs

                add_correlation_id_to_logs(app)
                logger.debug("Basic request logging enabled")

    elif logging_config.get("request_logging", True):
        from .request_logging import add_correlation_id_to_logs

        add_correlation_id_to_logs(app)
        logger.debug("Basic request logging enabled")


# Create the app instance
app = create_app()


def main():
    host = os.getenv("SERVER_HOST", DEFAULT_SERVER_HOST)
    port = int(os.getenv("SERVER_PORT", DEFAULT_SERVER_PORT))

    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
