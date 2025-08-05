"""
Enhanced Automation Middleware for MCP Server

Automatically extracts memories, creates tasks, and triggers sequential thinking
on all incoming user messages.

Requires: memory_manager.MemoryManager, sequential_thinking.SequentialThinkingEngine
"""

from fastmcp.server.middleware import Middleware, MiddlewareContext

class EnhancedAutomationMiddleware(Middleware):
    def __init__(self, memory_manager, thinking_engine):
        self.memory_manager = memory_manager
        self.thinking_engine = thinking_engine

    async def on_message(self, context: MiddlewareContext, call_next):
        # Only process user-originated tool calls and chat messages
        try:
            method = getattr(context, "method", "")
            message = getattr(context, "message", {})
            # Only process tool calls or chat-like messages
            if method in ("tools/call", "chat/send", "message/send"):
                # Extract content from message params
                params = getattr(message, "params", None) or getattr(message, "arguments", None) or {}
                # Try common keys for user content
                content = params.get("content") or params.get("text") or params.get("prompt") or ""
                if isinstance(content, str) and content.strip():
                    # Add to memory and auto-create tasks
                    try:
                        self.memory_manager.add_context_memory(content)
                    except Exception:
                        pass
                    try:
                        self.memory_manager.auto_create_task_from_context(content)
                    except Exception:
                        pass
                    # Optionally: trigger sequential thinking for complex prompts
                    if len(content) > 200 and "objective" in params:
                        try:
                            self.thinking_engine.create_thinking_chain(params.get("objective", content[:100]))
                        except Exception:
                            pass
        except Exception:
            pass

        # Continue normal processing
        return await call_next(context)
