import copy
import time
from typing import Any, Optional
import uuid

from typing_extensions import override

from flotorch.sdk.session import FlotorchSession
from flotorch.sdk.utils.logging_utils import log_object_creation,log_error,log_warning,log_info
from google.adk.events.event import Event
from google.adk.sessions.base_session_service import BaseSessionService
from google.adk.sessions.base_session_service import GetSessionConfig
from google.adk.sessions.base_session_service import ListSessionsResponse
from google.adk.sessions.session import Session
from google.adk.sessions.state import State



class FlotorchADKSession(BaseSessionService):
    """A Flotorch-based implementation of the session service.

    Uses FlotorchSession from SDK for session management while maintaining
    ADK-compatible interface.
    """

    def __init__(self, api_key: str, base_url: str):
        """Initialize FlotorchADKSession.

        Args:
            api_key: The API key for Flotorch service.
            base_url: The base URL for Flotorch service.
        """
        
        # Flotorch session for session management
        self._flotorch_session = FlotorchSession(
            api_key=api_key,
            base_url=base_url,
        )
        
        # In-memory state management (for app_state and user_state)
        # These are kept in memory as they're not part of FlotorchSession
        self.user_state: dict[str, dict[str, dict[str, Any]]] = {}
        self.app_state: dict[str, dict[str, Any]] = {}
        
        # Log object creation
        log_object_creation("FlotorchADKSession", base_url=base_url)

    @override
    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        return self._create_session_impl(
            app_name=app_name,
            user_id=user_id,
            state=state,
            session_id=session_id,
        )

    def create_session_sync(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        # logger.warning('Deprecated. Please migrate to the async method.')
        return self._create_session_impl(
            app_name=app_name,
            user_id=user_id,
            state=state,
            session_id=session_id,
        )

    def _create_session_impl(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        session_id = (
            session_id.strip()
            if session_id and session_id.strip()
            else str(uuid.uuid4())
        )
        
        # Create session using FlotorchSession
        try:
            session_data = self._flotorch_session.create(
                app_name=app_name,
                user_id=user_id,
                uid=session_id,
                state=state or {},
            )
        except Exception as e:
            log_error("FlotorchADKSession._create_session_impl", e, session_id=session_id)
            raise
        
        # Create ADK Session object
        session = Session(
            app_name=app_name,
            user_id=user_id,
            id=session_id,
            state=session_data.get('state', {}),
            last_update_time=session_data.get('last_update_time', time.time()),
        )

        copied_session = copy.deepcopy(session)
        return self._merge_state(app_name, user_id, copied_session)

    @override
    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        return self._get_session_impl(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            config=config,
        )

    def get_session_sync(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        # logger.warning('Deprecated. Please migrate to the async method.')
        return self._get_session_impl(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            config=config,
        )

    def _get_session_impl(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        # Get session using FlotorchSession
        try:
            session_data = self._flotorch_session.get(
                uid=session_id,
                after_timestamp=config.after_timestamp if config else None,
                num_recent_events=config.num_recent_events if config else None,
            )
        except Exception as e:
            log_error("FlotorchADKSession._get_session_impl", e, session_id=session_id)
            return None
        
        if not session_data:
            return None

        # Create ADK Session object
        session = Session(
            app_name=app_name,
            user_id=user_id,
            id=session_id,
            state=session_data.get('state', {}),
            last_update_time=session_data.get('last_update_time', time.time()),
        )
        
        # Add events if available
        events_data = session_data.get('events', [])
        try:
            session.events = [
                self._convert_flotorch_event_to_adk(event_data)
                for event_data in events_data
            ]
        except Exception as e:
            log_error("FlotorchADKSession._get_session_impl", e, session_id=session_id, events_count=len(events_data))
            session.events = []  # Fallback to empty events list

        copied_session = copy.deepcopy(session)
        return self._merge_state(app_name, user_id, copied_session)

    def _merge_state(
        self, app_name: str, user_id: str, copied_session: Session
    ) -> Session:
        # Merge app state
        if app_name in self.app_state:
            for key in self.app_state[app_name].keys():
                copied_session.state[State.APP_PREFIX + key] = self.app_state[app_name][
                    key
                ]

        if (
            app_name not in self.user_state
            or user_id not in self.user_state[app_name]
        ):
            return copied_session

        # Merge session state with user state.
        for key in self.user_state[app_name][user_id].keys():
            copied_session.state[State.USER_PREFIX + key] = self.user_state[app_name][
                user_id
            ][key]
        return copied_session

    @override
    async def list_sessions(
        self, *, app_name: str, user_id: str
    ) -> ListSessionsResponse:
        return self._list_sessions_impl(app_name=app_name, user_id=user_id)

    def list_sessions_sync(
        self, *, app_name: str, user_id: str
    ) -> ListSessionsResponse:
        # logger.warning('Deprecated. Please migrate to the async method.')
        return self._list_sessions_impl(app_name=app_name, user_id=user_id)

    def _list_sessions_impl(
        self, *, app_name: str, user_id: str
    ) -> ListSessionsResponse:
        # List sessions using FlotorchSession
        try:
            sessions_data = self._flotorch_session.list(
                app_name=app_name,
                user_id=user_id,
            )
        except Exception as e:
            log_error("FlotorchADKSession._list_sessions_impl", e, app_name=app_name, user_id=user_id)
            return ListSessionsResponse(sessions=[])
        
        sessions_without_events = []
        for session_data in sessions_data:
            session = Session(
                app_name=app_name,
                user_id=user_id,
                id=session_data.get('uid', ''),
                state=session_data.get('state', {}),
                last_update_time=session_data.get('last_update_time', time.time()),
            )
            session.events = []  # Don't include events in list response
            copied_session = copy.deepcopy(session)
            copied_session = self._merge_state(app_name, user_id, copied_session)
            sessions_without_events.append(copied_session)
            
        return ListSessionsResponse(sessions=sessions_without_events)

    @override
    async def delete_session(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        self._delete_session_impl(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

    def delete_session_sync(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        # logger.warning('Deprecated. Please migrate to the async method.')
        self._delete_session_impl(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

    def _delete_session_impl(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        if (
            self._get_session_impl(
                app_name=app_name, user_id=user_id, session_id=session_id
            )
            is None
        ):
            return

        # Delete session using FlotorchSession
        try:
            self._flotorch_session.delete(session_id)
        except Exception as e:
            log_error("FlotorchADKSession._delete_session_impl", e, session_id=session_id)
            raise

    @override
    async def append_event(self, session: Session, event: Event) -> Event:
        # Update the in-memory session.
        await super().append_event(session=session, event=event)
        session.last_update_time = event.timestamp

        # Update the storage session
        app_name = session.app_name
        user_id = session.user_id
        session_id = session.id



        # Verify session exists
        try:
            session_data = self._flotorch_session.get(uid=session_id)
        except Exception as e:
            log_error("FlotorchADKSession.append_event", e, session_id=session_id)
            return event
            
        if not session_data:
            log_warning("FlotorchADKSession.append_event", f'session_id {session_id} not found in FlotorchSession')
            return event

        # Handle state delta updates
        if event.actions and event.actions.state_delta:
            for key in event.actions.state_delta:
                if key.startswith(State.APP_PREFIX):
                    self.app_state.setdefault(app_name, {})[
                        key.removeprefix(State.APP_PREFIX)
                    ] = event.actions.state_delta[key]

                if key.startswith(State.USER_PREFIX):
                    self.user_state.setdefault(app_name, {}).setdefault(user_id, {})[
                        key.removeprefix(State.USER_PREFIX)
                    ] = event.actions.state_delta[key]

        # Add event using FlotorchSession
        try:
            event_data = self._convert_adk_event_to_flotorch(event)
            self._flotorch_session.add_event(
                uid=session_id,
                invocation_id=event.invocation_id,
                author=event.author,
                content=event_data.get('content'),
                actions=event_data.get('actions'),
                **event_data.get('metadata', {})
            )
        except Exception as e:
            log_error("FlotorchADKSession.append_event", e, session_id=session_id, event_id=event.id)
            raise

        return event

    def _convert_flotorch_event_to_adk(self, event_data: dict[str, Any]) -> Event:
        """Convert Flotorch event data to ADK Event object."""
        from google.adk.events.event_actions import EventActions
        import datetime
        
        event_actions = EventActions()
        if event_data.get('actions'):
            event_actions = EventActions(
                state_delta=event_data['actions'].get('state_delta', {}),
                # Add other action fields as needed
            )

        # Handle timestamp conversion
        timestamp = event_data.get('timestamp', time.time())
        if isinstance(timestamp, str):
            try:
                # Parse ISO format timestamp
                dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timestamp = dt.timestamp()
            except (ValueError, AttributeError) as e:
                # Fallback to current time if parsing fails
                log_warning("FlotorchADKSession._convert_flotorch_event_to_adk", f"Failed to parse timestamp: {timestamp}", error=str(e))
                timestamp = time.time()

        event = Event(
            id=event_data.get('uid_event', ''),
            invocation_id=event_data.get('invocation_id', ''),
            author=event_data.get('author', ''),
            actions=event_actions,
            content=event_data.get('content'),
            timestamp=timestamp,
            error_code=event_data.get('error_code'),
            error_message=event_data.get('error_message'),
        )
        
        return event

    def _convert_adk_event_to_flotorch(self, event: Event) -> dict[str, Any]:
        """Convert ADK Event object to Flotorch event data."""
        # Convert Content object to dictionary format
        content_dict = None
        if event.content:
            content_dict = {
                'role': event.content.role,
                'parts': []
            }
            
            if event.content.parts:
                for part in event.content.parts:
                    part_dict = {}
                    
                    # Handle text parts
                    if hasattr(part, 'text') and part.text is not None:
                        part_dict['text'] = part.text
                    
                    # Handle inline_data parts
                    if hasattr(part, 'inline_data') and part.inline_data is not None:
                        part_dict['inline_data'] = {
                            'mime_type': part.inline_data.mime_type,
                            'data': part.inline_data.data if isinstance(part.inline_data.data, (str, bytes)) else str(part.inline_data.data)
                        }
                    
                    # Handle file_data parts
                    if hasattr(part, 'file_data') and part.file_data is not None:
                        part_dict['file_data'] = {
                            'mime_type': part.file_data.mime_type,
                            'file_uri': part.file_data.file_uri
                        }
                    
                    # Handle function_call parts
                    if hasattr(part, 'function_call') and part.function_call is not None:
                        part_dict['function_call'] = {
                            'name': part.function_call.name,
                            'args': part.function_call.args
                        }
                    
                    # Handle function_response parts
                    if hasattr(part, 'function_response') and part.function_response is not None:
                        part_dict['function_response'] = {
                            'name': part.function_response.name,
                            'response': part.function_response.response
                        }
                    
                    # Handle executable_code parts
                    if hasattr(part, 'executable_code') and part.executable_code is not None:
                        part_dict['executable_code'] = {
                            'code': part.executable_code.code,
                            'language': part.executable_code.language
                        }
                    
                    # Handle code_execution_result parts
                    if hasattr(part, 'code_execution_result') and part.code_execution_result is not None:
                        part_dict['code_execution_result'] = {
                            'outcome': part.code_execution_result.outcome,
                            'output': part.code_execution_result.output
                        }
                    
                    # Handle thought parts
                    if hasattr(part, 'thought') and part.thought is not None:
                        part_dict['thought'] = part.thought
                    
                    # Handle thought_signature parts
                    if hasattr(part, 'thought_signature') and part.thought_signature is not None:
                        # Convert bytes to base64 string if needed
                        if isinstance(part.thought_signature, bytes):
                            import base64
                            part_dict['thought_signature'] = base64.b64encode(part.thought_signature).decode('utf-8')
                        else:
                            part_dict['thought_signature'] = part.thought_signature
                    
                    # Handle video_metadata parts
                    if hasattr(part, 'video_metadata') and part.video_metadata is not None:
                        part_dict['video_metadata'] = {
                            'start_offset': part.video_metadata.start_offset,
                            'end_offset': part.video_metadata.end_offset
                        }
                    
                    if part_dict:  # Only add non-empty parts
                        content_dict['parts'].append(part_dict)
        
        event_data = {
            'content': content_dict,
            'actions': {},
            'metadata': {}
        }
        
        # Ensure all data is JSON serializable
        try:
            import json
            json.dumps(event_data)
        except (TypeError, ValueError) as e:
            # If serialization fails, create a minimal safe version
            log_warning("FlotorchADKSession._convert_adk_event_to_flotorch", f"JSON serialization failed: {str(e)}")
            event_data = {
                'content': {
                    'role': 'user' if content_dict else 'assistant',
                    'parts': [{'text': 'Message content could not be serialized'}]
                } if content_dict else None,
                'actions': {},
                'metadata': {}
            }
        
        if event.actions:
            event_data['actions'] = {
                'state_delta': event.actions.state_delta or {},
                # Add other action fields as needed
            }
        
        if event.partial is not None:
            event_data['metadata']['partial'] = event.partial
        if event.turn_complete is not None:
            event_data['metadata']['turn_complete'] = event.turn_complete
        if event.interrupted is not None:
            event_data['metadata']['interrupted'] = event.interrupted
        if event.branch:
            event_data['metadata']['branch'] = event.branch
        if event.custom_metadata:
            event_data['metadata']['custom_metadata'] = event.custom_metadata
        if event.long_running_tool_ids:
            event_data['metadata']['long_running_tool_ids_json'] = list(event.long_running_tool_ids)
        if event.grounding_metadata:
            event_data['metadata']['grounding_metadata'] = event.grounding_metadata
            
        return event_data
