import json
from pathlib import Path
from typing import Any, Dict, Optional, Type, List, Callable, cast
from pydantic import create_model

from econagents import AgentRole
from econagents.core.events import Message
from econagents.core.manager.phase import PhaseManager
from econagents.core.state.game import GameState
from econagents.core.game_runner import GameRunner
from econagents.config_parser.base import BaseConfigParser, TYPE_MAPPING
from econagents.llm.observability import get_observability_provider
from econagents_ibex_tudelft.core.state.market import MarketState


def handle_market_event_impl(self: GameState, event_type: str, data: dict[str, Any]) -> None:
    """Handles market-related events by delegating to the MarketState instance."""
    try:
        getattr(self.public_information, self.meta._market_state_variable_name).process_event(  # type: ignore
            event_type=event_type, data=data
        )
    except Exception as e:
        raise ValueError(f"Error processing market event: {e}") from e


def handle_asset_movement_event_impl(self: GameState, event_type: str, data: dict[str, Any]) -> None:
    """Handles asset-movement events by delegating to the MarketState instance."""
    try:
        winning_condition = self.public_information.winning_condition  # type: ignore
        self.private_information.wallet[winning_condition]["balance"] = data["balance"]  # type: ignore
        self.private_information.wallet[winning_condition]["shares"] = data["shares"]  # type: ignore
    except Exception as e:
        raise ValueError(f"Error processing asset-movement event: {e}") from e


def get_custom_handlers_impl(self: GameState) -> Dict[str, Callable[[Message], None]]:
    """Returns custom handlers for market events."""
    market_events = ["add-order", "update-order", "delete-order", "contract-fulfilled"]
    asset_movement_event_handlers: Dict[str, Callable[[Message], None]] = {
        "asset-movement": self._handle_asset_movement_event  # type: ignore
    }
    market_event_handlers: Dict[str, Callable[[Message], None]] = {
        event: self._handle_market_event  # type: ignore
        for event in market_events
    }
    return {**asset_movement_event_handlers, **market_event_handlers}


class IbexTudelftConfigParser(BaseConfigParser):
    """
    IBEX-TUDelft configuration parser that extends the BaseConfigParser
    and adds role assignment functionality and MarketState support.
    """

    def __init__(self, config_path: Path):
        """
        Initialize the IBEX-TUDelft config parser.

        Args:
            config_path: Path to the YAML configuration file
        """
        super().__init__(config_path)
        self._role_classes: Dict[int, Type[AgentRole]] = {}
        # Extend type mapping with MarketState
        self.type_mapping = {**TYPE_MAPPING, "MarketState": MarketState}

    def register_role_class(self, role_id: int, role_class: Type[AgentRole]) -> None:
        """
        Register a role class for a specific role ID.

        Args:
            role_id: The role ID
            role_class: The agent role class
        """
        self._role_classes[role_id] = role_class

    def create_manager(
        self, game_id: int, state: GameState, agent_role: Optional[AgentRole], auth_kwargs: Dict[str, Any]
    ) -> PhaseManager:
        """
        Create a manager instance with custom event handlers for assign-name and assign-role events.
        The manager won't have a role initially, but will be assigned one during the game.

        Args:
            game_id: The game ID
            state: The game state instance
            agent_role: The agent role instance (may be None)
            auth_kwargs: Authentication mechanism keyword arguments

        Returns:
            A PhaseManager instance with custom event handlers
        """
        # Get the manager with the name assignment handler
        manager = super().create_manager(
            game_id=game_id,
            state=state,
            agent_role=None,
            auth_kwargs=auth_kwargs,
        )

        # Register custom event handler for assign-name event
        async def handle_name_assignment(message: Message) -> None:
            """Handle the name assignment event."""
            # Include the agent ID from auth_kwargs in the ready message
            agent_id = auth_kwargs.get("agent_id")
            ready_msg = {"gameId": game_id, "type": "player-is-ready", "agentId": agent_id}
            await manager.send_message(json.dumps(ready_msg))

        # Register custom event handler for assign-role event
        async def handle_role_assignment(message: Message) -> None:
            """Handle the role assignment event."""
            role_id = int(message.data.get("role", 0))
            manager.logger.info(f"Role assigned: {role_id}")

            # Initialize the agent based on the assigned role
            self._initialize_agent(manager, role_id)

        manager.register_event_handler("assign-role", handle_role_assignment)
        manager.register_event_handler("assign-name", handle_name_assignment)

        return manager

    def _detect_market_state_in_config(self) -> tuple[bool, Optional[tuple[str, str]]]:
        """
        Detects if MarketState is used in the state configuration.

        Returns:
            A tuple: (has_market_state_field, market_state_details).
            market_state_details is (field_name_on_section, section_attribute_name_on_gamestate)
            or None if not found.
        """
        state_conf = self.config.state
        # Check public_information first, then private, then meta
        for field_conf in state_conf.public_information:
            if field_conf.type == "MarketState":
                return True, (field_conf.name, "public_information")
        for field_conf in state_conf.private_information:
            if field_conf.type == "MarketState":
                return True, (field_conf.name, "private_information")
        for field_conf in state_conf.meta_information:
            if field_conf.type == "MarketState":
                return True, (field_conf.name, "meta")
        return False, None

    def _create_enhanced_state_class(self, base_class: Type[GameState]) -> Type[GameState]:
        """
        Creates an enhanced GameState class by subclassing base_class and injecting market event handlers.
        """
        enhanced_class_name = f"Enhanced{base_class.__name__}"
        enhanced_class = create_model(
            enhanced_class_name,
            __base__=base_class,
        )
        setattr(enhanced_class, "_handle_market_event", handle_market_event_impl)
        setattr(enhanced_class, "_handle_asset_movement_event", handle_asset_movement_event_impl)
        setattr(enhanced_class, "get_custom_handlers", get_custom_handlers_impl)
        return cast(Type[GameState], enhanced_class)

    def _check_additional_required_fields(self, base_dynamic_state_class: Type[GameState]) -> None:
        public_fields = base_dynamic_state_class().public_information.model_json_schema()["properties"]  # type: ignore
        private_fields = base_dynamic_state_class().private_information.model_json_schema()["properties"]  # type: ignore

        if (
            "winning_condition" not in public_fields.keys()  # type: ignore
            or "wallet" not in private_fields.keys()  # type: ignore
        ):
            raise ValueError("Winning condition or wallet is not present in the config")

    def create_state_class(self) -> Type[GameState]:
        """
        Create a GameState class with MarketState support.
        This method creates a custom state class that can handle MarketState fields.
        """
        from typing import Any, Optional
        from pydantic import Field as PydanticField
        from econagents.core.state.fields import EventField

        # Helper function to resolve field types including MarketState
        def resolve_field_type(field_type_str: str) -> Any:
            """Resolve type string to Python type, including custom types."""
            # First check our extended type mapping
            if field_type_str in self.type_mapping:
                return self.type_mapping[field_type_str]
            # Then check the base TYPE_MAPPING
            elif field_type_str in TYPE_MAPPING:
                return TYPE_MAPPING[field_type_str]
            else:
                try:
                    # Try to evaluate complex types
                    resolved_type = eval(field_type_str, {"list": list, "dict": dict, "Any": Any})
                    return resolved_type
                except (NameError, SyntaxError):
                    raise ValueError(f"Unsupported field type: {field_type_str}")

        def get_default_factory(factory_name: str) -> Any:
            """Get default factory function."""
            if factory_name == "list":
                return list
            elif factory_name == "dict":
                return dict
            elif factory_name == "MarketState":
                return MarketState
            else:
                raise ValueError(f"Unsupported default_factory: {factory_name}")

        def create_fields_dict(field_configs: List) -> Dict[str, Any]:
            """Create a dictionary of field definitions for create_model."""
            fields = {}
            for field in field_configs:
                base_type = resolve_field_type(field.type)
                field_type = Optional[base_type] if field.optional else base_type

                event_field_args = {
                    "event_key": field.event_key,
                    "exclude_from_mapping": field.exclude_from_mapping,
                    "events": field.events,
                    "exclude_events": field.exclude_events,
                }
                # Handle default vs default_factory
                if field.default_factory:
                    event_field_args["default_factory"] = get_default_factory(field.default_factory)
                else:
                    event_field_args["default"] = field.default

                # EventField needs to be the default value passed to create_model
                field_definition = EventField(**event_field_args)  # type: ignore
                fields[field.name] = (field_type, field_definition)
            return fields

        # Import necessary classes
        from econagents.core.state.game import MetaInformation, PrivateInformation, PublicInformation

        # Create dynamic classes using create_model
        meta_fields = create_fields_dict(self.config.state.meta_information)
        DynamicMeta = create_model(
            "DynamicMeta",
            __base__=MetaInformation,
            **meta_fields,
        )

        private_fields = create_fields_dict(self.config.state.private_information)
        DynamicPrivate = create_model(
            "DynamicPrivate",
            __base__=PrivateInformation,
            **private_fields,
        )

        public_fields = create_fields_dict(self.config.state.public_information)
        DynamicPublic = create_model(
            "DynamicPublic",
            __base__=PublicInformation,
            **public_fields,
        )

        # Create the final GameState subclass
        base_state_class = create_model(
            "DynamicGameState",
            __base__=GameState,
            meta=(DynamicMeta, PydanticField(default_factory=DynamicMeta)),
            private_information=(
                DynamicPrivate,
                PydanticField(default_factory=DynamicPrivate),
            ),
            public_information=(
                DynamicPublic,
                PydanticField(default_factory=DynamicPublic),
            ),
        )

        # Check if MarketState is used and enhance if needed
        has_market_state, market_state_details = self._detect_market_state_in_config()
        if has_market_state and market_state_details:
            self._check_additional_required_fields(base_state_class)
            return self._create_enhanced_state_class(cast(Type[GameState], base_state_class))
        return cast(Type[GameState], base_state_class)

    async def run_experiment(self, login_payloads: List[Dict[str, Any]], game_id: int) -> None:
        """
        Run the experiment from this configuration, potentially enhancing the GameState
        class with market event handlers if MarketState is specified in the config.
        """
        # Step 1: Get the state class with MarketState support
        final_state_class = self.create_state_class()

        # Step 2: Detect if MarketState is used for metadata
        has_market_state_field, market_state_details = self._detect_market_state_in_config()

        if not self.config.agent_roles:
            raise ValueError("Configuration has no 'agent_roles'.")

        # Create managers for each agent
        agents_for_runner = []
        for payload in login_payloads:
            current_agent_manager = self.create_manager(
                game_id=game_id,
                state=final_state_class(),
                agent_role=None,
                auth_kwargs=payload,
            )
            current_agent_manager.state.meta.game_id = game_id
            if market_state_details:
                setattr(current_agent_manager.state.meta, "_market_state_variable_name", market_state_details[0])
            agents_for_runner.append(current_agent_manager)

        # Create runner config
        runner_config_instance = self.config.runner.create_runner_config()
        runner_config_instance.state_class = final_state_class
        runner_config_instance.game_id = game_id

        if any(hasattr(role, "prompts") and role.prompts for role in self.config.agent_roles):
            prompts_dir = self.config._compile_inline_prompts()
            runner_config_instance.prompts_dir = prompts_dir

        runner = GameRunner(config=runner_config_instance, agents=agents_for_runner)
        await runner.run_game()

        if self.config._temp_prompts_dir and self.config._temp_prompts_dir.exists():
            import shutil

            shutil.rmtree(self.config._temp_prompts_dir)

    def _initialize_agent(self, manager: PhaseManager, role_id: int) -> None:
        """
        Initialize the agent instance based on the assigned role.

        Args:
            manager: The phase manager instance
            role_id: The role ID
        """
        agent_roles = self.config.agent_roles
        agent_role = next((role for role in agent_roles if role.role_id == role_id), None)
        if agent_role:
            manager.agent_role = agent_role.create_agent_role()
            manager.agent_role.logger = manager.logger  # type: ignore
            if self.config.runner.observability_provider:
                manager.agent_role.llm.observability = get_observability_provider(
                    self.config.runner.observability_provider
                )
        else:
            manager.logger.error("Invalid role assigned; cannot initialize agent.")
            raise ValueError("Invalid role for agent initialization.")


async def run_experiment_from_yaml(yaml_path: Path, login_payloads: List[Dict[str, Any]], game_id: int) -> None:
    """Run an experiment from a YAML configuration file."""
    parser = IbexTudelftConfigParser(yaml_path)
    await parser.run_experiment(login_payloads, game_id)
