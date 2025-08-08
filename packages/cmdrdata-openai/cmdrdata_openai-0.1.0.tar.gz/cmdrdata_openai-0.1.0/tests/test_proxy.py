"""
Unit tests for TrackedProxy and method tracking
"""

import pytest
from unittest.mock import Mock, patch
import inspect

from cmdrdata_openai.proxy import (
    TrackedProxy,
    track_chat_completion,
    track_completion,
    OPENAI_TRACK_METHODS,
)
from cmdrdata_openai.tracker import UsageTracker


class TestTrackedProxy:
    """Test suite for TrackedProxy"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_tracker = Mock(spec=UsageTracker)
        self.track_methods = {"test_method": Mock(), "chat.completions.create": Mock()}

    def test_proxy_initialization(self):
        """Test TrackedProxy initialization"""
        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods=self.track_methods,
        )

        assert proxy._client is self.mock_client
        assert proxy._tracker is self.mock_tracker
        assert proxy._track_methods == self.track_methods
        assert proxy._tracked_attributes == {}

    def test_getattr_simple_attribute(self):
        """Test __getattr__ for simple attributes"""
        self.mock_client.simple_attr = "test_value"

        proxy = TrackedProxy(
            client=self.mock_client, tracker=self.mock_tracker, track_methods={}
        )

        assert proxy.simple_attr == "test_value"
        assert "simple_attr" in proxy._tracked_attributes

    def test_getattr_tracked_method(self):
        """Test __getattr__ for tracked methods"""
        mock_method = Mock(return_value="method_result")
        self.mock_client.test_method = mock_method

        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods={"test_method": Mock()},
        )

        # Get the wrapped method
        wrapped_method = proxy.test_method

        # Call the wrapped method
        result = wrapped_method()

        # Verify original method was called
        mock_method.assert_called_once()
        assert result == "method_result"

        # Verify method is cached
        assert "test_method" in proxy._tracked_attributes

    def test_getattr_nested_attributes(self):
        """Test __getattr__ for nested attributes"""
        # Set up nested structure
        self.mock_client.chat = Mock()
        self.mock_client.chat.completions = Mock()
        self.mock_client.chat.completions.create = Mock(return_value="chat_result")

        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods={"chat.completions.create": Mock()},
        )

        # Access nested attribute
        chat_proxy = proxy.chat

        # Should be a TrackedProxy itself
        assert isinstance(chat_proxy, TrackedProxy)
        assert chat_proxy._client is self.mock_client.chat

        # Access deeper
        completions_proxy = chat_proxy.completions
        assert isinstance(completions_proxy, TrackedProxy)

        # Call the tracked method
        result = completions_proxy.create()
        assert result == "chat_result"

    def test_getattr_nonexistent_attribute(self):
        """Test __getattr__ for non-existent attributes"""
        # Create a more restrictive mock that doesn't auto-create attributes
        restrictive_mock = Mock(spec=[])  # Empty spec means no allowed attributes

        proxy = TrackedProxy(
            client=restrictive_mock, tracker=self.mock_tracker, track_methods={}
        )

        with pytest.raises(
            AttributeError, match="'Mock' object has no attribute 'nonexistent'"
        ):
            _ = proxy.nonexistent

    def test_setattr_client_attribute(self):
        """Test __setattr__ for client attributes"""
        proxy = TrackedProxy(
            client=self.mock_client, tracker=self.mock_tracker, track_methods={}
        )

        proxy.new_attr = "new_value"

        # Should set on the underlying client
        assert self.mock_client.new_attr == "new_value"

    def test_setattr_private_attribute(self):
        """Test __setattr__ for private attributes"""

        # Use a simple object instead of Mock to avoid auto-creation of attributes
        class SimpleClient:
            pass

        simple_client = SimpleClient()

        proxy = TrackedProxy(
            client=simple_client, tracker=self.mock_tracker, track_methods={}
        )

        proxy._private_attr = "private_value"

        # Should set on the proxy itself
        assert proxy._private_attr == "private_value"
        assert not hasattr(simple_client, "_private_attr")

    def test_dir_method(self):
        """Test __dir__ method includes both proxy and client attributes"""
        self.mock_client.client_attr = "value"

        proxy = TrackedProxy(
            client=self.mock_client, tracker=self.mock_tracker, track_methods={}
        )

        proxy.proxy_attr = "proxy_value"

        dir_result = dir(proxy)

        # Should include client attributes
        assert "client_attr" in dir_result
        # Should include proxy attributes (but not private ones starting with _)
        assert "proxy_attr" in dir_result

    def test_wrap_method_basic(self):
        """Test _wrap_method basic functionality"""
        mock_method = Mock(return_value="result")
        mock_tracker_func = Mock()

        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods={"test_method": mock_tracker_func},
        )

        wrapped = proxy._wrap_method(mock_method, "test_method")

        # Call wrapped method
        result = wrapped("arg1", kwarg1="value1")

        # Verify original method was called
        mock_method.assert_called_once_with("arg1", kwarg1="value1")
        assert result == "result"

        # Verify tracker was called
        mock_tracker_func.assert_called_once()

    def test_wrap_method_with_tracking_parameters(self):
        """Test _wrap_method extracts tracking parameters"""
        mock_method = Mock(return_value="result")
        mock_tracker_func = Mock()

        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods={"test_method": mock_tracker_func},
        )

        wrapped = proxy._wrap_method(mock_method, "test_method")

        # Call with tracking parameters
        result = wrapped(
            "arg1", kwarg1="value1", customer_id="test-customer", track_usage=True
        )

        # Verify tracking parameters were removed from kwargs
        mock_method.assert_called_once_with("arg1", kwarg1="value1")

        # Verify tracker was called with correct parameters
        call_args = mock_tracker_func.call_args
        assert call_args[1]["customer_id"] == "test-customer"
        assert call_args[1]["tracker"] is self.mock_tracker
        assert call_args[1]["method_name"] == "test_method"

    def test_wrap_method_tracking_disabled(self):
        """Test _wrap_method when tracking is disabled"""
        mock_method = Mock(return_value="result")
        mock_tracker_func = Mock()

        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods={"test_method": mock_tracker_func},
        )

        wrapped = proxy._wrap_method(mock_method, "test_method")

        # Call with tracking disabled
        result = wrapped("arg1", track_usage=False)

        # Verify original method was called
        mock_method.assert_called_once_with("arg1")

        # Verify tracker was NOT called
        mock_tracker_func.assert_not_called()

    def test_wrap_method_preserves_signature(self):
        """Test _wrap_method preserves original method signature"""

        def original_method(arg1: str, arg2: int = 10) -> str:
            """Original method docstring"""
            return f"{arg1}_{arg2}"

        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods={"test_method": Mock()},
        )

        wrapped = proxy._wrap_method(original_method, "test_method")

        # Check that metadata is preserved
        assert wrapped.__name__ == "original_method"
        assert wrapped.__doc__ == "Original method docstring"

        # Check signature (if available)
        try:
            original_sig = inspect.signature(original_method)
            wrapped_sig = inspect.signature(wrapped)
            # Signatures should be the same
            assert str(original_sig) == str(wrapped_sig)
        except (ValueError, TypeError):
            # Signature inspection might fail in some environments
            pass

    def test_wrap_method_exception_handling(self):
        """Test _wrap_method handles exceptions properly"""

        def failing_method():
            raise ValueError("Method failed")

        mock_tracker_func = Mock()

        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods={"test_method": mock_tracker_func},
        )

        wrapped = proxy._wrap_method(failing_method, "test_method")

        # Call should raise the original exception
        with pytest.raises(ValueError, match="Method failed"):
            wrapped()

        # Tracker should be called with error information when method fails
        mock_tracker_func.assert_called_once()
        call_args = mock_tracker_func.call_args[1]
        assert call_args["error_occurred"] is True
        assert call_args["error_type"] == "unknown_error"
        assert call_args["error_message"] == "Method failed"

    def test_wrap_method_tracker_exception_handling(self):
        """Test _wrap_method handles tracker exceptions gracefully"""
        mock_method = Mock(return_value="result")
        mock_tracker_func = Mock(side_effect=Exception("Tracker failed"))

        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods={"test_method": mock_tracker_func},
        )

        wrapped = proxy._wrap_method(mock_method, "test_method")

        with patch("cmdrdata_openai.proxy.logger") as mock_logger:
            # Should not raise exception even if tracker fails
            result = wrapped()

            # Original method should still return its result
            assert result == "result"

            # Warning should be logged
            mock_logger.warning.assert_called_once()

    def test_repr_method(self):
        """Test __repr__ method"""
        proxy = TrackedProxy(
            client=self.mock_client, tracker=self.mock_tracker, track_methods={}
        )

        repr_str = repr(proxy)
        assert "TrackedProxy" in repr_str
        assert repr(self.mock_client) in repr_str


class TestTrackingFunctions:
    """Test suite for tracking functions"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_tracker = Mock()
        self.mock_result = Mock()
        self.mock_result.model = "gpt-4"
        self.mock_result.usage = Mock()
        self.mock_result.usage.prompt_tokens = 10
        self.mock_result.usage.completion_tokens = 15
        self.mock_result.id = "chatcmpl-test123"
        self.mock_result.created = 1234567890
        self.mock_result.choices = [Mock()]
        self.mock_result.choices[0].finish_reason = "stop"

    def test_track_chat_completion_success(self):
        """Test successful chat completion tracking"""
        with patch(
            "cmdrdata_openai.proxy.get_effective_customer_id"
        ) as mock_get_customer:
            mock_get_customer.return_value = "test-customer"

            track_chat_completion(
                result=self.mock_result,
                customer_id="test-customer",
                tracker=self.mock_tracker,
                method_name="chat.completions.create",
                args=(),
                kwargs={"model": "gpt-4"},
            )

            # Verify tracker was called
            self.mock_tracker.track_usage_background.assert_called_once()
            call_kwargs = self.mock_tracker.track_usage_background.call_args[1]

            assert call_kwargs["customer_id"] == "test-customer"
            assert call_kwargs["model"] == "gpt-4"
            assert call_kwargs["input_tokens"] == 10
            assert call_kwargs["output_tokens"] == 15
            assert call_kwargs["provider"] == "openai"
            assert call_kwargs["metadata"]["response_id"] == "chatcmpl-test123"
            assert call_kwargs["metadata"]["finish_reason"] == "stop"

    def test_track_chat_completion_no_customer_id(self):
        """Test chat completion tracking without customer ID"""
        with patch(
            "cmdrdata_openai.proxy.get_effective_customer_id"
        ) as mock_get_customer:
            with patch("cmdrdata_openai.proxy.logger") as mock_logger:
                mock_get_customer.return_value = None

                track_chat_completion(
                    result=self.mock_result,
                    customer_id=None,
                    tracker=self.mock_tracker,
                    method_name="chat.completions.create",
                    args=(),
                    kwargs={},
                )

                # Verify warning was logged
                mock_logger.warning.assert_called_once_with(
                    "No customer_id provided for tracking. Set customer_id parameter or use set_customer_context()"
                )

                # Verify tracker was NOT called
                self.mock_tracker.track_usage_background.assert_not_called()

    def test_track_chat_completion_no_usage_data(self):
        """Test chat completion tracking without usage data"""
        self.mock_result.usage = None

        with patch(
            "cmdrdata_openai.proxy.get_effective_customer_id"
        ) as mock_get_customer:
            mock_get_customer.return_value = "test-customer"

            track_chat_completion(
                result=self.mock_result,
                customer_id="test-customer",
                tracker=self.mock_tracker,
                method_name="chat.completions.create",
                args=(),
                kwargs={},
            )

            # Verify tracker was NOT called (no usage data)
            self.mock_tracker.track_usage_background.assert_not_called()

    def test_track_chat_completion_exception_handling(self):
        """Test chat completion tracking handles exceptions gracefully"""
        # Make the result object raise an exception
        self.mock_result.usage = Mock()
        self.mock_result.usage.prompt_tokens = 10
        # Remove completion_tokens to cause AttributeError
        del self.mock_result.usage.completion_tokens

        with patch(
            "cmdrdata_openai.proxy.get_effective_customer_id"
        ) as mock_get_customer:
            with patch("cmdrdata_openai.proxy.logger") as mock_logger:
                mock_get_customer.return_value = "test-customer"

                # Should not raise exception
                track_chat_completion(
                    result=self.mock_result,
                    customer_id="test-customer",
                    tracker=self.mock_tracker,
                    method_name="chat.completions.create",
                    args=(),
                    kwargs={},
                )

                # Warning should be logged
                mock_logger.warning.assert_called_once()

    def test_track_completion_success(self):
        """Test successful legacy completion tracking"""
        # Modify result for legacy completion format
        self.mock_result.model = "text-davinci-003"

        with patch(
            "cmdrdata_openai.proxy.get_effective_customer_id"
        ) as mock_get_customer:
            mock_get_customer.return_value = "test-customer"

            track_completion(
                result=self.mock_result,
                customer_id="test-customer",
                tracker=self.mock_tracker,
                method_name="completions.create",
                args=(),
                kwargs={"model": "text-davinci-003"},
            )

            # Verify tracker was called
            self.mock_tracker.track_usage_background.assert_called_once()
            call_kwargs = self.mock_tracker.track_usage_background.call_args[1]

            assert call_kwargs["customer_id"] == "test-customer"
            assert call_kwargs["model"] == "text-davinci-003"
            assert call_kwargs["input_tokens"] == 10
            assert call_kwargs["output_tokens"] == 15
            assert call_kwargs["provider"] == "openai"


class TestOpenAITrackMethods:
    """Test suite for OPENAI_TRACK_METHODS configuration"""

    def test_openai_track_methods_configuration(self):
        """Test OPENAI_TRACK_METHODS contains expected methods"""
        assert "chat.completions.create" in OPENAI_TRACK_METHODS
        assert "completions.create" in OPENAI_TRACK_METHODS

        # Verify the functions are callable
        assert callable(OPENAI_TRACK_METHODS["chat.completions.create"])
        assert callable(OPENAI_TRACK_METHODS["completions.create"])

        # Verify they point to the correct functions
        assert OPENAI_TRACK_METHODS["chat.completions.create"] == track_chat_completion
        assert OPENAI_TRACK_METHODS["completions.create"] == track_completion


if __name__ == "__main__":
    pytest.main([__file__])
