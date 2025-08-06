# Changelog

## [0.0.82] - 2025-08-05

### Added
- [Roadmap doc](https://github.com/elroy-bot/elroy/blob/main/docs/roadmap.md)
- Web API with endpoints for memory augmentation and querying
- User ID support for vector storage, enabling multi-user memory isolation
- Root API route for health checks and service status

### Improved
- Enhanced CLI header display with better formatting
- Updater now supports uv tool installation with fallback to pip for more reliable package management
- Memory augmentation operations now available through API endpoints

### Infrastructure
- Added web API infrastructure with FastAPI integration
- Database migrations for user ID support in vector storage tables

## [0.0.81] - 2025-07-10

### Added
- Status table for document ingestion in directories, with improved real-time feedback

### Improved
- Major performance improvements for simple exchanges by adding a decision step for whether memory check is needed
- Irrelevant memories are now ejected asynchronously, reducing context noise and improving recall
- Document ingestion logic updated: newly ingested docs are no longer added to status, and status is shown for directory ingests
- Turned off assistant greeting by default for a less intrusive startup experience
- Do not consider messages starting with `/ask` as slash commands
- Memory filtering on startup is now removed for faster initialization

### Fixed
- Bugfixes for memory ejection and context refresh logic
- More robust handling of document ingestion and status reporting
- Various minor bugfixes in async task scheduling and memory operations

### Infrastructure
- Delayed import of `scipy` and `DBSCAN` to speed up startup and avoid unnecessary dependencies
- Cleaned up and standardized error messages
- Updated and expanded test coverage for memory and document ingestion features

## [0.0.80] - 2025-06-14

### Improved
- Enhanced memory filtering with relevance processing to reduce noise
- Updated default log level

### Breaking change
- Removed Aider integration. The integration caused dependency issues

## [0.0.79] - 2025-04-20

### Added
- Add opt-in shell execution tool

### Improved
- More configurable tool and display options:
    - Option to exclude memory panel display
    - More granular dependencies

## [0.0.78] - 2025-04-10

### Added
- Simplified memory retrieval assistant tool: Assistant tool can now better retrieve source document information for memories
- Ensure a memory is created at least every `n` messages (configurable)
- Plaintext output option for messages

### Fixed
- Tool call argument validation
- API key requirement handling
- Message timestamp consistency
- Context message validation

### Improved
- Default user name changed from "UNKNOWN" to "User"
- PostgreSQL configuration flexibility

## [0.0.77] - 2025-03-16

### Added
- Support for Arize-Phoenix tracing!
- Directory-based document ingestion with recursive and pattern matching: try it with `elroy ingest`
- Reflective memory option: Increase reflection of memories
- Overhauled documentation

### Fixed
- Fix for context overflow in embeddings
- Context message ordering bug
- Assistant name consistency in memory operations

### Improved
- Shorter, more focused greeting messages
- More engaging persona and tone

## [0.0.76] - 2025-02-28

### Added
- Added ingest_doc API function
- Memory update functionality with timestamp tracking
- Example notebook for repository document ingestion

### Fixed
- Context message concurrent operations handling
- Missing timestamp in context messages
- Bug where /pop function ejected too many messages operation

### Improved
- Installation documentation updates for stable branch

## [0.0.75] - 2025-02-23

### Added
- Document ingestion support for markdown files!
- New tools for examining memory sources and origins

![file_ingestion_demo](images/file_ingestion_demo.gif)

### Improved
- Add --first flag to disable assistant greeting
- Enhanced memory retrieval with source tracking

## [0.0.74] - 2025-02-18

### Added
- Support for configuring OpenAI API base URL and API key
- Remember function restored to API

### Fixed
- More reliable handling of empty messages
- Better string conversion for text outputs

### Improved
- Enhanced inline tool handling with validation

## [0.0.73] - 2025-02-15

### Added
- Automatic model selection based on available API keys:
  - With ANTHROPIC_API_KEY: Uses Claude 3 Sonnet
  - With OPENAI_API_KEY: Uses GPT-4o and text-embedding-3-small
  - With GEMINI_API_KEY: Uses Gemini 2.0 Flash
- Display of selected models at startup for better transparency

### Fixed
- Improved handling of new user creation in API mode

## [0.0.72] - 2025-02-13

### Added
- /save command

### Improved
- Updated logic for selecting chat and embedding model API
- Support for Gemini models

## [0.0.71] - 2025-02-07

### Added
- New slash commands!
    - Accessing memories and goals:
        - /search_memories: Search against goals and memories
        - /print_active_goals
        - /print_complete_goals
        - /print_memories
    - Managing context messages:
        - /pop: Remove n messages from convo
        - /rewrite: Rewrite the last assistant response
- New API function: record_message, useful for backfilling (see [examples/backfill_chat_logs.py](examples/backfill_chat_logs.py))
- Discord bot script

### Fixed
- Clearer error handling for SQLite platform mismatch
- Slash commands can now be cancelled

## [0.0.70] - 2025-02-03

### Added
- Code syntax highlighting for code in Elroy responses
- New `remember_convo` command for conversation memory
- New CLI command: list-tools
- Installation script for easier setup

### Infrastructure
- Small updates on top of 0.0.69

## [0.0.69] - 2025-02-03

### Added
- Code syntax highlighting for code in Elroy responses
- New `remember_convo` command for conversation memory
- New CLI command: list-tools
- Installation script for easier setup

### Improved
- More graceful handling of invalid parameters with warnings
- Documentation updates and clarifications

## [0.0.68] - 2025-01-27

### Added
- MCP support! Use `elroy mcp print-config` for the server configuration

## [0.0.67] - 2025-01-26

### Added
- API expanded to include more memory and goal functions

## [0.0.66] - 2025-01-26

### Infrastructure
- Migrated from Poetry to UV for streamlined package management

## [0.0.65] - 2025-01-24

### Fixed
- Resolved threading issues in sqlite for improved stability
- Fixed tool calling schema injection for better reliability

### Improved
- Assistant name now displays correctly in title bar

## [0.0.64] - 2025-01-23

### Fixed
- Improved error recovery and differentiation in toolkit
- --inline-tools option for models that do not natively support tool calls.

### Improved
- Context refresh is now based on context token counts, rather than wall clock time

## [0.0.63] - 2025-01-22

### Fixed
- Improved release script reliability and deployment consistency

## [0.0.62] - 2025-01-21

### Added
- Support for custom user-defined tools
- Stream internal thought output
- Option to show sensitive values in print-config command

### Fixed
- Improved timezone handling in login messages
- More robust tool calling
- Fixed print-config functionality

## [0.0.61] - 2025-01-10

### Fixed
- Improved handling of system paths

## [0.0.60] - 2025-01-09

### Improved
- Added some debug info to print-config

## [0.0.59] - 2025-01-06

### Improved
- print-config now works without requiring database connection for basic operations like viewing settings

## [0.0.58] - 2025-01-05

### Improved
- Improve readability of /print_config and /print_context_messages commands
- Bugfixes to declutter conversation history

## [0.0.57] - 2025-01-04

### Added
- Memory consolidation overhaul: Consolidation is now based on how many memories have been created since the last consolidation operation, rather than time.
- Consolidated memoires now store source metadata
- Maximum limit on consecutive tool calls to prevent infinite loops

### Improved
- Commands are now regular CLI commands, rather than flags
- Autocomplete improvements
- Results from assistant function calls are now printed to the console

## [0.0.56] - 2024-12-30

### Improved
- Fixes for command autocomplete

## [0.0.55] - 2024-12-29

### Added
- Custom assistant name configuration via new command
- Default configuration file location for easier setup
- UV package manager installation instructions

### Improved
- Enhanced conversation context management and summarization
- Streamlined database setup documentation
- More comprehensive conversation summaries including tool interactions
- Enable or disable tools via explicit parameter rather than introspection of model settings (enabled by default)


### Documentation
- Expanded README with additional installation options
- Clearer database setup instructions

## [0.0.54] - 2024-12-26

### Added
- SQLite support! The defualt data store is now SQLite.

### Breaking changes
- The default data store is now SQLite, and the database env var has been renamed from ELROY_POSTGRES_URL to ELROY_DATABASE_URL (ELROY_POSTGRES_URL will still be recognized for backward compatibility)

## [0.0.53] - 2024-12-19

### Improved
- New `/help` command with improved command autocomplete functionality
- Cross-platform support for Elroy cache and home directories using platformdirs
- `ctrl-r` Conversation search now spans sessions

### Infrastructure
- DB schema migrations to prepare for sqlite support
- Added Discord community server

### Documentation
- Added Discord server link to README
- Update Docker setup documentation

## [0.0.52] - 2024-12-16

### Added
- Ability to create multiple "users" in a single deployment. Each user has isolated memories.
- Customizable personas: Specify your own default persona for all assistants via the `default_persona` config value, or use `--set-persona` to set a persona for one specific assistant.
- Model alias support for easier model selection: --o1, --gpt-4o, --sonnet, etc. See README for full list of aliases.
- Configurable assistant greeting: use `no-enable-assistant-greeting` to prevent the assistant from sending the first message.

### Improved
- Enhanced model fallback behavior: Primarily motivated by Anthropic - if a rate limit is used, Elroy will automatically attempt to switch to a fallback model (order of fallback behavior can be found via `elroy --list-models`)
- Better detection of tool support for OpenAI and Anthropic models: Chat functionality and memory consolidation are now supported for models that do not support tools.
- Streamlined CLI commands and tools organization

### Fixed
- Various minor bugfixes and stability improvements

## [0.0.51] - 2024-11-30

### Improved
- Fix multi-argument system commands. For user initiatied system commands with multiple arguments, the user will now be prompted to enter each argument.

## [0.0.50] - 2024-11-28

### Breaking changes
- CLI commands have been converted to flags, so:
    - `remember` is now `--remember`
    - `remember` with `-f` is not `--remember-file`
    - `list-models` is now `--list-models`
    - `chat` is now `--chat`. This remains the default command if no command is provided.
- Docker integration is updated
    - `--use-docker-postgres` flag is removed. You can start the docker database using the `scripts/docker_postgres.py` script.

### Improved
- Enhanced CLI configuration with streamlined flag organization
- Optimized default parameters for better out-of-box experience
- Improved Docker integration for more reliable container usage

### Fixed
- Resolved various test suite issues

## [0.0.49] - 2024-11-25

### Improved
- Replaced JSON LLM outputs with Markdown, added more fault tolerance in parsing responses with unexpected formatting.

## [0.0.48] - 2024-11-22

### Fixed
- Fixed type mismatch in context refresh wait timing

### Infrastructure
- Updated Discord release announcements to use announcements channel

## [0.0.47] - 2024-11-22

### Added
- Added configurable LLM response caching: `enable_caching`, defaulting to true.
- New system commands for troubleshooting:
    - `/tail_elroy_logs`: View log Elroy logs from within the chat UI
    - `/print_elroy_config`: View Elroy config from within the chat UI
    - `/create_bug_report`: Open a pre-filled bug report in the browser (available to the user only, not the assistant)

## [0.0.46] - 2024-11-20

### Added
- Added expanded configuration options for better customization

### Fixed
- Improved CHANGELOG.md handling with better path resolution and error management

## [0.0.45] - 2024-11-19

### Added
- Added automated Discord announcements for new releases

### Infrastructure
- Improved CI workflow to prevent duplicate runs on branch pushes

## [0.0.44] - 2024-11-19

### Improved
- Enhanced release process with streaming subprocess output and progress logging
- Updated documentation for clarity and completeness

### Legal
- Changed project license to Apache 2.0

## [0.0.43] - 2024-11-18

### Fixed
- Minor fixes

## [0.0.42] - 2024-11-17

### Added
- Updated README to document all startup options and system commands for better user guidance.
- Added more verbose error output for tool calls to improve debugging and error tracking.

### Fixed
- Improved autocomplete functionality by filtering goals and memories for more relevant options.
- Simplified demo recording script for easier demonstration creation.

### Improved
- Enhanced error handling for goal-related functions to better surface available goals.
- Added override parameters to name setting functions to discourage redundant calls.
- Provided additional context in login messages for a more informative user experience.

### Infrastructure
- Added a `wait-for-pypi` job to verify package availability before Docker publishing, ensuring smoother deployment processes.

## [0.0.41] - 2024-11-14

### Infrastructure
- Updates to package publishing

## [0.0.40] - 2024-11-14

### Added
- Initial release of Elroy, a CLI AI personal assistant with long-term memory and goal tracking capabilities.
- Features include long-term memory, goal tracking, and a memory panel for relevant memories during conversations.
- Supports installation via Docker, pip, or from source.
- Includes commands for system management, goal management, memory management, user preferences, and conversation handling.
