"""
Dynamic proxy classes for transparent API forwarding with usage tracking
"""

import inspect
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Union

from .context import get_effective_customer_id
from .tracker import UsageTracker

logger = logging.getLogger(__name__)


class TrackedProxy:
    """
    Base proxy class that forwards all method calls to the underlying client
    while selectively adding usage tracking to specific methods.
    """

    def __init__(
        self,
        client: Any,
        tracker: UsageTracker,
        track_methods: Dict[str, Callable] = None,
    ):
        """
        Initialize the proxy.

        Args:
            client: The underlying client (e.g., OpenAI client)
            tracker: Usage tracker instance
            track_methods: Dict mapping method names to tracking functions
        """
        # Store these with underscore prefixes to avoid conflicts
        object.__setattr__(self, "_client", client)
        object.__setattr__(self, "_tracker", tracker)
        object.__setattr__(self, "_track_methods", track_methods or {})
        object.__setattr__(self, "_tracked_attributes", {})

    def __getattr__(self, name: str) -> Any:
        """
        Dynamically forward attribute access to the underlying client.
        If the attribute is a method that should be tracked, wrap it.
        """
        # Check if we've already wrapped this attribute
        if name in self._tracked_attributes:
            return self._tracked_attributes[name]

        # Get the attribute from the underlying client
        try:
            attr = getattr(self._client, name)
        except AttributeError:
            # Don't cache non-existent attributes
            raise AttributeError(
                f"'{type(self._client).__name__}' object has no attribute '{name}'"
            )

        # If it's a callable and we have a tracker for it, wrap it
        if callable(attr) and name in self._track_methods:
            wrapped_attr = self._wrap_method(attr, name)
            self._tracked_attributes[name] = wrapped_attr
            return wrapped_attr

        # If it's another object that might need proxying, check if we should wrap it
        elif hasattr(attr, "__dict__") and not isinstance(
            attr, (str, int, float, bool, type(None))
        ):
            # This might be a sub-client (like client.chat.completions)
            # Check if any of our track methods start with this attribute name
            sub_track_methods = {
                k[len(name) + 1 :]: v
                for k, v in self._track_methods.items()
                if k.startswith(f"{name}.")
            }

            if sub_track_methods:
                wrapped_attr = TrackedProxy(attr, self._tracker, sub_track_methods)
                self._tracked_attributes[name] = wrapped_attr
                return wrapped_attr

        # For everything else, just return the original attribute
        self._tracked_attributes[name] = attr
        return attr

    def __setattr__(self, name: str, value: Any) -> None:
        """Forward attribute setting to the underlying client"""
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            setattr(self._client, name, value)

    def __dir__(self):
        """Return attributes from both proxy and underlying client"""
        proxy_attrs = [
            attr for attr in object.__dir__(self) if not attr.startswith("_")
        ]
        client_attrs = dir(self._client)
        return sorted(set(proxy_attrs + client_attrs))

    def _wrap_method(self, method: Callable, method_name: str) -> Callable:
        """Wrap a method to add usage tracking"""
        tracker_func = self._track_methods[method_name]

        def wrapped(*args, **kwargs):
            # Extract customer_id, track_usage, and metadata from kwargs if present
            customer_id = kwargs.pop("customer_id", None)
            track_usage = kwargs.pop("track_usage", True)
            custom_metadata = kwargs.pop("metadata", None)

            # Generate request ID for tracking
            request_id = str(uuid.uuid4())

            # Start timing
            start_time = time.time()
            end_time = None
            error_occurred = False
            error_type = None
            error_code = None
            error_message = None
            retry_count = 0

            # Detect if this is a streaming request
            streaming = kwargs.get("stream", False)
            time_to_first_token_ms = None

            # Call the original method
            try:
                result = method(*args, **kwargs)
                end_time = time.time()

                # Track usage if enabled
                if track_usage:
                    try:
                        tracker_func(
                            result=result,
                            customer_id=customer_id,
                            tracker=self._tracker,
                            method_name=method_name,
                            args=args,
                            kwargs=kwargs,
                            custom_metadata=custom_metadata,
                            # Enhanced tracking data
                            request_start_time=start_time,
                            request_end_time=end_time,
                            error_occurred=error_occurred,
                            error_type=error_type,
                            error_code=error_code,
                            error_message=error_message,
                            request_id=request_id,
                            streaming=streaming,
                            retry_count=retry_count,
                            time_to_first_token_ms=time_to_first_token_ms,
                        )
                    except Exception as e:
                        logger.warning(f"Failed to track usage for {method_name}: {e}")

                return result

            except Exception as e:
                end_time = time.time()
                error_occurred = True

                # Categorize error types
                error_message = str(e)
                if hasattr(e, "status_code"):
                    error_code = str(e.status_code)
                    if e.status_code == 429:
                        error_type = "rate_limit"
                    elif e.status_code == 401:
                        error_type = "authentication"
                    elif e.status_code == 403:
                        error_type = "authorization"
                    elif e.status_code >= 500:
                        error_type = "server_error"
                    elif e.status_code >= 400:
                        error_type = "invalid_request"
                elif "timeout" in error_message.lower():
                    error_type = "timeout"
                elif "connection" in error_message.lower():
                    error_type = "connection_error"
                else:
                    error_type = "unknown_error"

                # Track the error if usage tracking is enabled
                if track_usage:
                    try:
                        tracker_func(
                            result=None,
                            customer_id=customer_id,
                            tracker=self._tracker,
                            method_name=method_name,
                            args=args,
                            kwargs=kwargs,
                            custom_metadata=custom_metadata,
                            # Enhanced tracking data
                            request_start_time=start_time,
                            request_end_time=end_time,
                            error_occurred=error_occurred,
                            error_type=error_type,
                            error_code=error_code,
                            error_message=error_message,
                            request_id=request_id,
                            streaming=streaming,
                            retry_count=retry_count,
                            time_to_first_token_ms=time_to_first_token_ms,
                        )
                    except Exception as track_error:
                        logger.warning(
                            f"Failed to track error for {method_name}: {track_error}"
                        )

                # Log the error but re-raise it unchanged
                logger.debug(f"Method {method_name} failed: {e}")
                raise

        # Preserve the original function signature and metadata
        wrapped.__name__ = getattr(method, "__name__", method_name)
        wrapped.__doc__ = getattr(method, "__doc__", None)

        try:
            wrapped.__signature__ = inspect.signature(method)
        except (ValueError, TypeError):
            pass

        return wrapped

    def __repr__(self):
        """Return a helpful representation"""
        return f"TrackedProxy({repr(self._client)})"


def track_chat_completion(
    result,
    customer_id,
    tracker,
    method_name,
    args,
    kwargs,
    custom_metadata=None,
    # Enhanced tracking parameters
    request_start_time=None,
    request_end_time=None,
    error_occurred=None,
    error_type=None,
    error_code=None,
    error_message=None,
    request_id=None,
    streaming=None,
    retry_count=None,
    time_to_first_token_ms=None,
):
    """Track chat completion usage"""
    try:
        effective_customer_id = get_effective_customer_id(customer_id)

        if not effective_customer_id:
            logger.warning(
                "No customer_id provided for tracking. Set customer_id parameter or use set_customer_context()"
            )
            return

        if hasattr(result, "usage") and result.usage:
            # Combine system metadata with custom metadata
            metadata = {
                "response_id": getattr(result, "id", None),
                "created": getattr(result, "created", None),
                "finish_reason": (
                    getattr(result.choices[0], "finish_reason", None)
                    if result.choices
                    else None
                ),
            }

            # Add custom metadata if provided
            if custom_metadata:
                metadata.update(custom_metadata)

            # Use the new tracker method signature with enhanced analytics
            tracker.track_usage_background(
                customer_id=effective_customer_id,
                model=getattr(result, "model", kwargs.get("model", "unknown")),
                input_tokens=result.usage.prompt_tokens if result else 0,
                output_tokens=result.usage.completion_tokens if result else 0,
                provider="openai",
                metadata=metadata,
                request_start_time=request_start_time,
                request_end_time=request_end_time,
                error_occurred=error_occurred,
                error_type=error_type,
                error_code=error_code,
                error_message=error_message,
                request_id=request_id,
                streaming=streaming,
                retry_count=retry_count,
                time_to_first_token_ms=time_to_first_token_ms,
            )

    except Exception as e:
        logger.warning(f"Failed to extract usage data from chat completion: {e}")


def track_completion(
    result,
    customer_id,
    tracker,
    method_name,
    args,
    kwargs,
    custom_metadata=None,
    # Enhanced tracking parameters
    request_start_time=None,
    request_end_time=None,
    error_occurred=None,
    error_type=None,
    error_code=None,
    error_message=None,
    request_id=None,
    streaming=None,
    retry_count=None,
    time_to_first_token_ms=None,
):
    """Track legacy completion usage"""
    try:
        effective_customer_id = get_effective_customer_id(customer_id)

        if not effective_customer_id:
            logger.warning(
                "No customer_id provided for tracking. Set customer_id parameter or use set_customer_context()"
            )
            return

        if hasattr(result, "usage") and result.usage:
            # Combine system metadata with custom metadata
            metadata = {
                "response_id": getattr(result, "id", None),
                "created": getattr(result, "created", None),
            }

            # Add custom metadata if provided
            if custom_metadata:
                metadata.update(custom_metadata)

            # Use the new tracker method signature with enhanced analytics
            tracker.track_usage_background(
                customer_id=effective_customer_id,
                model=getattr(result, "model", kwargs.get("model", "unknown")),
                input_tokens=result.usage.prompt_tokens if result else 0,
                output_tokens=result.usage.completion_tokens if result else 0,
                provider="openai",
                metadata=metadata,
                request_start_time=request_start_time,
                request_end_time=request_end_time,
                error_occurred=error_occurred,
                error_type=error_type,
                error_code=error_code,
                error_message=error_message,
                request_id=request_id,
                streaming=streaming,
                retry_count=retry_count,
                time_to_first_token_ms=time_to_first_token_ms,
            )

    except Exception as e:
        logger.warning(f"Failed to extract usage data from completion: {e}")


# OpenAI tracking configuration
OPENAI_TRACK_METHODS = {
    "chat.completions.create": track_chat_completion,
    "completions.create": track_completion,
}
