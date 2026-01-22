# Open Harness API

~~~meta
version: 0.2.0
base_url: https://api.openharness.org/v1
auth: bearer
auth_header: Authorization
content_type: application/json
errors: standard
~~~

The Open Harness API provides a standardized interface for interacting with AI agent harnesses. This specification enables portability and interoperability across diverse harness implementations including Claude Code, Goose, LangChain Deep Agent, Letta, and others.

---

# Global Types

```typescript
// Common identifiers
type UUID = string;                    // format: uuid-v4
type ISO8601 = string;                 // format: ISO 8601 datetime
type HarnessId = string;               // format: kebab-case identifier
type AgentId = string;
type SkillId = string;
type SessionId = string;
type ExecutionId = string;

// Pagination
interface PaginationParams {
  limit?: number;                      // 1-100, default: 20
  offset?: number;                     // default: 0
}

interface PaginatedResponse<T> {
  data: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

// Harness types
type ExecutionType = "hosted" | "sdk" | "ide";
type HarnessStatus = "active" | "beta" | "coming_soon" | "maintenance" | "deprecated";

interface Harness {
  id: HarnessId;
  name: string;
  vendor: string;
  description: string;
  execution_type: ExecutionType;
  status: HarnessStatus;
  capabilities: CapabilityManifest;
  created_at: ISO8601;
  updated_at: ISO8601;
}

interface CapabilityManifest {
  agents: DomainCapability;
  skills: DomainCapability;
  mcp: DomainCapability;
  execution: DomainCapability;
  sessions: DomainCapability;
  memory: DomainCapability;
  subagents: DomainCapability;
  files: DomainCapability;
  hooks: DomainCapability;
  planning: DomainCapability;
  models: DomainCapability;
}

interface DomainCapability {
  supported: boolean;
  operations: string[];
  limitations?: string[];
}

// Agent types (OAF-compliant)
interface Agent {
  id: AgentId;
  // OAF identity fields
  name: string;
  vendorKey: string;                   // Organization/vendor identifier (kebab-case)
  agentKey: string;                    // Agent identifier (kebab-case)
  version: string;                     // Semantic version (e.g., "1.0.0")
  slug: string;                        // URL-friendly identifier
  // Metadata
  description: string;
  author?: string;
  license?: string;                    // SPDX license identifier
  tags: string[];
  // Composition
  skills: SkillReference[];
  mcp_servers: McpServerReference[];
  // Configuration
  config: AgentConfig;
  created_at: ISO8601;
  updated_at: ISO8601;
}

interface AgentConfig {
  model?: string | ModelConfig;        // Model alias ("sonnet") or full config
  temperature?: number;                // 0.0-1.0
  max_tokens?: number;
  system_prompt?: string;
  tools_access?: ToolsAccessControl;
}

interface ModelConfig {
  provider: string;                    // e.g., "anthropic", "openai"
  name: string;                        // e.g., "claude-sonnet-4-5"
  embedding?: string;                  // e.g., "voyage-2"
}

interface ToolsAccessControl {
  allow?: string[];                    // Allowed tool patterns
  deny?: string[];                     // Denied tool patterns
}

interface SkillReference {
  skill_id: SkillId;
  version?: string;
  required: boolean;
}

interface McpServerReference {
  server_id: string;
  tools?: string[];                    // Specific tools to enable
  required: boolean;
}

// Skill types
interface Skill {
  id: SkillId;
  name: string;
  description: string;
  version: string;
  vendor: string;
  category: SkillCategory;
  created_at: ISO8601;
  updated_at: ISO8601;
}

type SkillCategory = "user" | "plugin" | "builtin" | "organization";

interface SkillVersion {
  version: string;
  created_at: ISO8601;
  changelog?: string;
}

// MCP types
interface McpServer {
  id: string;
  name: string;
  transport: McpTransport;
  status: "connected" | "disconnected" | "error";
  tools: McpTool[];
  resources: McpResource[];
  prompts: McpPrompt[];
}

type McpTransport =
  | { type: "stdio"; command: string; args?: string[] }
  | { type: "http"; url: string }
  | { type: "sse"; url: string };

interface McpTool {
  name: string;
  description: string;
  input_schema: object;
}

interface McpResource {
  uri: string;
  name: string;
  mime_type?: string;
}

interface McpPrompt {
  name: string;
  description: string;
  arguments?: PromptArgument[];
}

interface PromptArgument {
  name: string;
  description: string;
  required: boolean;
}

// Execution types
type ExecutionStatus = "pending" | "running" | "completed" | "failed" | "cancelled";

interface Execution {
  id: ExecutionId;
  harness_id: HarnessId;
  status: ExecutionStatus;
  progress?: ExecutionProgress;
  started_at: ISO8601;
  completed_at?: ISO8601;
  artifacts_count: number;
}

interface ExecutionProgress {
  percentage: number;                  // 0-100
  current_step: string;
  steps_completed: number;
  steps_total: number;
}

interface ExecutionResult {
  execution_id: ExecutionId;
  status: ExecutionStatus;
  output: string;
  artifacts: ArtifactSummary[];
  tool_calls: ToolCallSummary[];
  usage: UsageStats;
}

interface ArtifactSummary {
  id: string;
  name: string;
  mime_type: string;
  size_bytes: number;
}

interface ToolCallSummary {
  id: string;
  name: string;
  success: boolean;
  duration_ms: number;
}

interface UsageStats {
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
}

// Session types
interface Session {
  id: SessionId;
  harness_id: HarnessId;
  name?: string;
  status: "active" | "paused" | "ended";
  message_count: number;
  created_at: ISO8601;
  updated_at: ISO8601;
}

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  tool_calls?: ToolCall[];
  created_at: ISO8601;
}

interface ToolCall {
  id: string;
  name: string;
  input: object;
  output?: object;
  status: "pending" | "running" | "completed" | "failed";
}

// Memory types
interface MemoryState {
  agent_id: AgentId;
  blocks: MemoryBlock[];
  archive_size: number;
}

interface MemoryBlock {
  label: string;
  value: string;
  read_only: boolean;
  updated_at: ISO8601;
}

// File types
interface FileInfo {
  path: string;
  name: string;
  type: "file" | "directory";
  size_bytes?: number;
  mime_type?: string;
  modified_at: ISO8601;
}

// Hook types
type HookEvent = "pre_tool" | "post_tool" | "stop" | "error" | "custom";

interface Hook {
  id: string;
  event: HookEvent;
  handler: HookHandler;
  enabled: boolean;
}

type HookHandler =
  | { type: "webhook"; url: string }
  | { type: "command"; command: string };

// Planning types
interface Plan {
  execution_id: ExecutionId;
  tasks: PlanTask[];
  updated_at: ISO8601;
}

interface PlanTask {
  id: string;
  content: string;
  status: "pending" | "in_progress" | "completed";
  order: number;
}

// Webhook types
interface Webhook {
  id: string;
  url: string;                         // format: uri, HTTPS required
  events: string[];
  secret: string;
  enabled: boolean;
  created_at: ISO8601;
}

// Streaming event types
type ExecutionEvent =
  | { type: "text"; content: string }
  | { type: "thinking"; content: string }
  | { type: "tool_call_start"; id: string; name: string; input: object }
  | { type: "tool_call_delta"; id: string; input_delta: object }
  | { type: "tool_call_end"; id: string }
  | { type: "tool_result"; id: string; success: boolean; output?: object }
  | { type: "artifact"; id: string; name: string; mime_type: string; size_bytes: number }
  | { type: "progress"; percentage: number; step: string; step_number: number; total_steps: number }
  | { type: "error"; code: string; message: string; recoverable: boolean }
  | { type: "done"; usage: UsageStats };

// WebSocket message types
type ClientMessage =
  | { type: "message"; id: string; content: string }
  | { type: "stdin"; id: string; data: string }
  | { type: "cancel"; execution_id: string };

type ServerMessage =
  | { type: "text"; id: string; content: string }
  | { type: "thinking"; id: string; content: string }
  | { type: "tool_call"; id: string; tool: string; input: object }
  | { type: "stdout"; id: string; data: string }
  | { type: "stderr"; id: string; data: string }
  | { type: "prompt"; id: string; prompt: string }
  | { type: "artifact"; id: string; name: string; mime_type: string }
  | { type: "error"; id: string; code: string; message: string }
  | { type: "done"; id: string; usage: UsageStats };

// Error types
interface ErrorResponse {
  error: {
    code: string;
    message: string;
    domain?: string;
    operation?: string;
    details?: Record<string, unknown>;
  };
}
```

---

# 1. Harness Registry

Manage harness registration, configuration, and health.

## Capability: List Harnesses

~~~meta
id: harnesses.list
transport: HTTP GET /harnesses
auth: required
~~~

### Intention
Retrieves all registered harnesses with their current status and capabilities. Use this to discover available harnesses and their supported features before executing operations.

### Input
```typescript
interface ListHarnessesRequest extends PaginationParams {
  status?: HarnessStatus;              // Filter by status
  execution_type?: ExecutionType;      // Filter by type
}
```

### Output
```typescript
interface ListHarnessesResponse extends PaginatedResponse<Harness> {}
```

---

## Capability: Get Harness

~~~meta
id: harnesses.get
transport: HTTP GET /harnesses/{harnessId}
auth: required
~~~

### Intention
Retrieves detailed information about a specific harness including its full capability manifest.

### Input
```typescript
interface GetHarnessRequest {
  harnessId: HarnessId;                // path parameter
}
```

### Output
```typescript
interface GetHarnessResponse {
  harness: Harness;
}
```

---

## Capability: Register Harness

~~~meta
id: harnesses.register
transport: HTTP POST /harnesses
auth: required
~~~

### Intention
Registers a new harness with the Open Harness system. Typically used by harness vendors or administrators to add support for a new agent harness.

### Input
```typescript
interface RegisterHarnessRequest {
  id: HarnessId;
  name: string;                        // 1-100 chars
  vendor: string;                      // 1-100 chars
  description: string;                 // 1-1000 chars
  execution_type: ExecutionType;
  config: HarnessConfig;
}

interface HarnessConfig {
  base_url?: string;                   // For hosted harnesses
  binary_path?: string;                // For SDK/IDE harnesses
  skills_path?: string;                // Where skills are installed
}
```

### Output
```typescript
interface RegisterHarnessResponse {
  harness: Harness;
}
```

---

## Capability: Update Harness

~~~meta
id: harnesses.update
transport: HTTP PATCH /harnesses/{harnessId}
auth: required
~~~

### Intention
Updates configuration for an existing harness.

### Input
```typescript
interface UpdateHarnessRequest {
  harnessId: HarnessId;                // path parameter
  name?: string;
  description?: string;
  config?: Partial<HarnessConfig>;
  status?: HarnessStatus;
}
```

### Output
```typescript
interface UpdateHarnessResponse {
  harness: Harness;
}
```

---

## Capability: Unregister Harness

~~~meta
id: harnesses.unregister
transport: HTTP DELETE /harnesses/{harnessId}
auth: required
~~~

### Intention
Removes a harness from the registry. This does not uninstall the harness itself, only removes it from Open Harness management.

### Logic Constraints
- Cannot unregister a harness with active sessions or running executions
- Credentials associated with this harness will be deleted

### Input
```typescript
interface UnregisterHarnessRequest {
  harnessId: HarnessId;                // path parameter
}
```

### Output
Returns 204 No Content on success.

---

## Capability: Get Capabilities

~~~meta
id: harnesses.capabilities
transport: HTTP GET /harnesses/{harnessId}/capabilities
auth: required
~~~

### Intention
Retrieves the full capability manifest for a harness. Use this to determine which operations are supported before attempting them.

### Input
```typescript
interface GetCapabilitiesRequest {
  harnessId: HarnessId;                // path parameter
}
```

### Output
```typescript
interface GetCapabilitiesResponse {
  harness_id: HarnessId;
  harness_name: string;
  version: string;
  capabilities: CapabilityManifest;
}
```

---

## Capability: Health Check

~~~meta
id: harnesses.health
transport: HTTP GET /harnesses/{harnessId}/health
auth: optional
~~~

### Intention
Checks connectivity and health of a harness. Returns status information useful for monitoring and debugging.

### Input
```typescript
interface HealthCheckRequest {
  harnessId: HarnessId;                // path parameter
}
```

### Output
```typescript
interface HealthCheckResponse {
  status: "healthy" | "degraded" | "unhealthy";
  latency_ms: number;
  version?: string;
  checks: HealthCheck[];
}

interface HealthCheck {
  name: string;
  status: "pass" | "fail";
  message?: string;
}
```

---

## Capability: Validate Credentials

~~~meta
id: harnesses.validateCredentials
transport: HTTP POST /harnesses/{harnessId}/validate-credentials
auth: required
~~~

### Intention
Validates API credentials for a harness and optionally stores them for future use.

### Input
```typescript
interface ValidateCredentialsRequest {
  harnessId: HarnessId;                // path parameter
  api_key: string;
  base_url?: string;                   // Override default API URL
  store?: boolean;                     // default: false
}
```

### Output
```typescript
interface ValidateCredentialsResponse {
  valid: boolean;
  stored: boolean;
  error?: string;
}
```

---

# 2. Agents

Full agent lifecycle management.

## Capability: List Agents

~~~meta
id: agents.list
transport: HTTP GET /harnesses/{harnessId}/agents
auth: required
~~~

### Intention
Lists all agents deployed on a specific harness.

### Input
```typescript
interface ListAgentsRequest extends PaginationParams {
  harnessId: HarnessId;                // path parameter
}
```

### Output
```typescript
interface ListAgentsResponse extends PaginatedResponse<Agent> {}
```

---

## Capability: Create Agent

~~~meta
id: agents.create
transport: HTTP POST /harnesses/{harnessId}/agents
content_type: multipart/form-data
auth: required
~~~

### Intention
Creates and deploys a new agent on the harness. The agent bundle includes the AGENTS.md manifest and any supporting files.

### Logic Constraints
- Agent name in AGENTS.md frontmatter must be unique on this harness
- Maximum bundle size: 50MB
- Files array preserves directory structure via filename paths
- AGENTS.md is required at the root of the bundle

### Input
```typescript
interface CreateAgentRequest {
  harnessId: HarnessId;                // path parameter
  metadata: {
    name: string;
    description: string;
  };
  files: File[];                       // AGENTS.md + supporting files
}
```

### Output
```typescript
interface CreateAgentResponse {
  agent: Agent;
}
```

---

## Capability: Get Agent

~~~meta
id: agents.get
transport: HTTP GET /harnesses/{harnessId}/agents/{agentId}
auth: required
~~~

### Intention
Retrieves the current state and configuration of an agent.

### Input
```typescript
interface GetAgentRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter
}
```

### Output
```typescript
interface GetAgentResponse {
  agent: Agent;
}
```

---

## Capability: Update Agent

~~~meta
id: agents.update
transport: HTTP PATCH /harnesses/{harnessId}/agents/{agentId}
auth: required
~~~

### Intention
Updates agent configuration without redeploying the full bundle.

### Input
```typescript
interface UpdateAgentRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter
  name?: string;
  description?: string;
  config?: Partial<AgentConfig>;
}
```

### Output
```typescript
interface UpdateAgentResponse {
  agent: Agent;
}
```

---

## Capability: Delete Agent

~~~meta
id: agents.delete
transport: HTTP DELETE /harnesses/{harnessId}/agents/{agentId}
auth: required
~~~

### Intention
Removes an agent from the harness.

### Logic Constraints
- Cannot delete an agent with active sessions
- Associated memory blocks will be deleted

### Input
```typescript
interface DeleteAgentRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter
}
```

### Output
Returns 204 No Content on success.

---

## Capability: Clone Agent

~~~meta
id: agents.clone
transport: HTTP POST /harnesses/{harnessId}/agents/{agentId}/clone
auth: required
~~~

### Intention
Creates a copy of an existing agent with a new name.

### Input
```typescript
interface CloneAgentRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter
  new_name: string;                    // 1-100 chars
  include_memory?: boolean;            // default: false
}
```

### Output
```typescript
interface CloneAgentResponse {
  agent: Agent;
}
```

---

## Capability: Export Agent

~~~meta
id: agents.export
transport: HTTP GET /harnesses/{harnessId}/agents/{agentId}/export
auth: required
~~~

### Intention
Downloads the complete agent as an OAF package (.oaf file), following the Open Agent Format specification.

### Logic Constraints
- Content-Disposition header contains `{agentKey}.oaf` as filename
- Package is a standard ZIP archive with `.oaf` extension
- Root contains AGENTS.md manifest with full OAF frontmatter
- Directory structure follows OAF specification:
  - `AGENTS.md` - Agent manifest (required)
  - `skills/` - Local skills following AgentSkills.io spec
  - `mcp-configs/` - MCP server configurations (ActiveMCP.json + config.yaml per server)
  - `versions/` - Historical versions (if include_versions=true)
  - `examples/` - Usage examples
  - `tests/` - Test scenarios
  - `docs/` - Additional documentation
  - `assets/` - Media files

### Input
```typescript
interface ExportAgentRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter
  include_memory?: boolean;            // default: false, include memory snapshot
  include_versions?: boolean;          // default: false, include version history
  contents_mode?: "bundled" | "referenced";  // default: "bundled"
}
```

### Output
Returns raw bytes with `Content-Type: application/zip` and `.oaf` extension.

The package contains a `PACKAGE.yaml` manifest when multiple agents are bundled:
```yaml
# PACKAGE.yaml
name: "package-name"
version: "1.0.0"
contents_mode: "bundled"  # or "referenced"
agents:
  - path: "agent-name/"
    name: "agent-name"
    version: "1.0.0"
```

---

## Capability: Import Agent

~~~meta
id: agents.import
transport: HTTP POST /harnesses/{harnessId}/agents/import
content_type: multipart/form-data
auth: required
~~~

### Intention
Imports an agent from an OAF package (.oaf file) following the Open Agent Format specification.

### Logic Constraints
- Agent identity (vendorKey/agentKey) must be unique on this harness
- Bundle must contain valid AGENTS.md at root with required OAF frontmatter:
  - `name`, `vendorKey`, `agentKey`, `version`, `slug` (required)
  - `description`, `author`, `license`, `tags` (required metadata)
- Maximum bundle size: 50MB
- If contents_mode is "referenced", skills are fetched from well-known URLs
- SPDX license identifier must be valid if provided

### Input
```typescript
interface ImportAgentRequest {
  harnessId: HarnessId;                // path parameter
  bundle: File;                        // .oaf ZIP file
  rename_to?: string;                  // Override agent name
  merge_strategy?: "fail" | "overwrite" | "skip";  // default: "fail"
}
```

### Output
```typescript
interface ImportAgentResponse {
  agent: Agent;
  warnings: string[];                  // Non-fatal import warnings
}
```

---

# 3. Skills

Skill registration, installation, discovery, and versioning.

## Capability: List Skills

~~~meta
id: skills.list
transport: HTTP GET /harnesses/{harnessId}/skills
auth: required
~~~

### Intention
Lists all skills installed or registered on the harness.

### Input
```typescript
interface ListSkillsRequest extends PaginationParams {
  harnessId: HarnessId;                // path parameter
  category?: SkillCategory;            // Filter by category
}
```

### Output
```typescript
interface ListSkillsResponse extends PaginatedResponse<Skill> {}
```

---

## Capability: Register Skill

~~~meta
id: skills.register
transport: HTTP POST /harnesses/{harnessId}/skills
content_type: multipart/form-data
auth: required
~~~

### Intention
Registers or installs a skill on the harness. Skills consist of a SKILL.md manifest plus optional supporting files.

### Logic Constraints
- Skill name in SKILL.md frontmatter must match root directory name
- Maximum bundle size: 10MB
- SKILL.md is required at the root
- Binary assets should be in an `assets/` subdirectory
- Accepted file types: .md, .py, .js, .ts, .json, .yaml, .jinja, .txt

### Input
```typescript
interface RegisterSkillRequest {
  harnessId: HarnessId;                // path parameter
  metadata: {
    display_title: string;             // 1-100 chars
    category?: SkillCategory;
  };
  files: File[];                       // SKILL.md + supporting files
}
```

### Output
```typescript
interface RegisterSkillResponse {
  skill: Skill;
}
```

---

## Capability: Get Skill

~~~meta
id: skills.get
transport: HTTP GET /harnesses/{harnessId}/skills/{skillId}
auth: required
~~~

### Intention
Retrieves details about a specific skill.

### Input
```typescript
interface GetSkillRequest {
  harnessId: HarnessId;                // path parameter
  skillId: SkillId;                    // path parameter
}
```

### Output
```typescript
interface GetSkillResponse {
  skill: Skill;
}
```

---

## Capability: Update Skill

~~~meta
id: skills.update
transport: HTTP PATCH /harnesses/{harnessId}/skills/{skillId}
auth: required
~~~

### Intention
Updates skill metadata without uploading a new version.

### Input
```typescript
interface UpdateSkillRequest {
  harnessId: HarnessId;                // path parameter
  skillId: SkillId;                    // path parameter
  display_title?: string;
  category?: SkillCategory;
}
```

### Output
```typescript
interface UpdateSkillResponse {
  skill: Skill;
}
```

---

## Capability: Uninstall Skill

~~~meta
id: skills.uninstall
transport: HTTP DELETE /harnesses/{harnessId}/skills/{skillId}
auth: required
~~~

### Intention
Uninstalls or unregisters a skill from the harness.

### Logic Constraints
- Cannot uninstall a skill that is referenced by active agents

### Input
```typescript
interface UninstallSkillRequest {
  harnessId: HarnessId;                // path parameter
  skillId: SkillId;                    // path parameter
}
```

### Output
Returns 204 No Content on success.

---

## Capability: List Skill Versions

~~~meta
id: skills.listVersions
transport: HTTP GET /harnesses/{harnessId}/skills/{skillId}/versions
auth: required
~~~

### Intention
Lists all available versions of a skill.

### Input
```typescript
interface ListSkillVersionsRequest {
  harnessId: HarnessId;                // path parameter
  skillId: SkillId;                    // path parameter
}
```

### Output
```typescript
interface ListSkillVersionsResponse {
  skill_id: SkillId;
  current_version: string;
  versions: SkillVersion[];
}
```

---

## Capability: Rollback Skill

~~~meta
id: skills.rollback
transport: HTTP POST /harnesses/{harnessId}/skills/{skillId}/rollback
auth: required
~~~

### Intention
Reverts a skill to a previous version.

### Input
```typescript
interface RollbackSkillRequest {
  harnessId: HarnessId;                // path parameter
  skillId: SkillId;                    // path parameter
  version: string;                     // Target version
}
```

### Output
```typescript
interface RollbackSkillResponse {
  skill: Skill;
  previous_version: string;
}
```

---

## Capability: Discover Skills

~~~meta
id: skills.discover
transport: HTTP POST /harnesses/{harnessId}/skills/discover
auth: required
~~~

### Intention
Discovers skills available on the harness that are not yet registered. Useful for finding built-in or auto-detected skills.

### Input
```typescript
interface DiscoverSkillsRequest {
  harnessId: HarnessId;                // path parameter
  search_paths?: string[];             // Additional paths to search
}
```

### Output
```typescript
interface DiscoverSkillsResponse {
  discovered: DiscoveredSkill[];
}

interface DiscoveredSkill {
  name: string;
  path: string;
  category: SkillCategory;
  already_registered: boolean;
}
```

---

## Capability: Validate Skill

~~~meta
id: skills.validate
transport: HTTP POST /harnesses/{harnessId}/skills/validate
content_type: multipart/form-data
auth: required
~~~

### Intention
Validates a skill bundle without installing it. Returns any errors or warnings.

### Input
```typescript
interface ValidateSkillRequest {
  harnessId: HarnessId;                // path parameter
  files: File[];                       // SKILL.md + supporting files
}
```

### Output
```typescript
interface ValidateSkillResponse {
  valid: boolean;
  errors: ValidationIssue[];
  warnings: ValidationIssue[];
}

interface ValidationIssue {
  file: string;
  line?: number;
  message: string;
  code: string;
}
```

---

## Capability: Download Skill

~~~meta
id: skills.download
transport: HTTP GET /harnesses/{harnessId}/skills/{skillId}/download
auth: required
~~~

### Intention
Downloads the complete skill bundle as a ZIP file.

### Logic Constraints
- Content-Disposition header contains skill name as filename
- ZIP preserves directory structure

### Input
```typescript
interface DownloadSkillRequest {
  harnessId: HarnessId;                // path parameter
  skillId: SkillId;                    // path parameter
  version?: string;                    // Specific version, default: latest
}
```

### Output
Returns raw ZIP bytes with `Content-Type: application/zip`.

---

## Capability: Upgrade Skill

~~~meta
id: skills.upgrade
transport: HTTP POST /harnesses/{harnessId}/skills/{skillId}/upgrade
content_type: multipart/form-data
auth: required
~~~

### Intention
Upgrades an existing skill to a new version.

### Logic Constraints
- New version must be greater than current version
- Skill name in SKILL.md must match existing skill

### Input
```typescript
interface UpgradeSkillRequest {
  harnessId: HarnessId;                // path parameter
  skillId: SkillId;                    // path parameter
  files: File[];                       // New SKILL.md + supporting files
  changelog?: string;                  // 1-1000 chars
}
```

### Output
```typescript
interface UpgradeSkillResponse {
  skill: Skill;
  previous_version: string;
}
```

---

# 4. MCP Servers

MCP server lifecycle and tool discovery.

## Capability: List MCP Servers

~~~meta
id: mcp.list
transport: HTTP GET /harnesses/{harnessId}/mcp-servers
auth: required
~~~

### Intention
Lists all MCP servers connected to the harness.

### Input
```typescript
interface ListMcpServersRequest extends PaginationParams {
  harnessId: HarnessId;                // path parameter
  status?: "connected" | "disconnected" | "error";
}
```

### Output
```typescript
interface ListMcpServersResponse extends PaginatedResponse<McpServer> {}
```

---

## Capability: Connect MCP Server

~~~meta
id: mcp.connect
transport: HTTP POST /harnesses/{harnessId}/mcp-servers
auth: required
~~~

### Intention
Connects a new MCP server to the harness.

### Input
```typescript
interface ConnectMcpServerRequest {
  harnessId: HarnessId;                // path parameter
  name: string;                        // 1-100 chars
  transport: McpTransport;
  auto_reconnect?: boolean;            // default: true
}
```

### Output
```typescript
interface ConnectMcpServerResponse {
  server: McpServer;
}
```

---

## Capability: Get MCP Server

~~~meta
id: mcp.get
transport: HTTP GET /harnesses/{harnessId}/mcp-servers/{serverId}
auth: required
~~~

### Intention
Retrieves details about a connected MCP server.

### Input
```typescript
interface GetMcpServerRequest {
  harnessId: HarnessId;                // path parameter
  serverId: string;                    // path parameter
}
```

### Output
```typescript
interface GetMcpServerResponse {
  server: McpServer;
}
```

---

## Capability: Update MCP Server

~~~meta
id: mcp.update
transport: HTTP PATCH /harnesses/{harnessId}/mcp-servers/{serverId}
auth: required
~~~

### Intention
Updates MCP server configuration.

### Input
```typescript
interface UpdateMcpServerRequest {
  harnessId: HarnessId;                // path parameter
  serverId: string;                    // path parameter
  name?: string;
  transport?: McpTransport;
  auto_reconnect?: boolean;
}
```

### Output
```typescript
interface UpdateMcpServerResponse {
  server: McpServer;
}
```

---

## Capability: Disconnect MCP Server

~~~meta
id: mcp.disconnect
transport: HTTP DELETE /harnesses/{harnessId}/mcp-servers/{serverId}
auth: required
~~~

### Intention
Disconnects an MCP server from the harness.

### Input
```typescript
interface DisconnectMcpServerRequest {
  harnessId: HarnessId;                // path parameter
  serverId: string;                    // path parameter
}
```

### Output
Returns 204 No Content on success.

---

## Capability: List MCP Tools

~~~meta
id: mcp.listTools
transport: HTTP GET /harnesses/{harnessId}/mcp-servers/{serverId}/tools
auth: required
~~~

### Intention
Lists all tools provided by an MCP server.

### Input
```typescript
interface ListMcpToolsRequest {
  harnessId: HarnessId;                // path parameter
  serverId: string;                    // path parameter
}
```

### Output
```typescript
interface ListMcpToolsResponse {
  tools: McpTool[];
}
```

---

## Capability: List MCP Resources

~~~meta
id: mcp.listResources
transport: HTTP GET /harnesses/{harnessId}/mcp-servers/{serverId}/resources
auth: required
~~~

### Intention
Lists all resources provided by an MCP server.

### Input
```typescript
interface ListMcpResourcesRequest {
  harnessId: HarnessId;                // path parameter
  serverId: string;                    // path parameter
}
```

### Output
```typescript
interface ListMcpResourcesResponse {
  resources: McpResource[];
}
```

---

## Capability: List MCP Prompts

~~~meta
id: mcp.listPrompts
transport: HTTP GET /harnesses/{harnessId}/mcp-servers/{serverId}/prompts
auth: required
~~~

### Intention
Lists all prompts provided by an MCP server.

### Input
```typescript
interface ListMcpPromptsRequest {
  harnessId: HarnessId;                // path parameter
  serverId: string;                    // path parameter
}
```

### Output
```typescript
interface ListMcpPromptsResponse {
  prompts: McpPrompt[];
}
```

---

## Capability: MCP Server Health

~~~meta
id: mcp.health
transport: HTTP POST /harnesses/{harnessId}/mcp-servers/{serverId}/health
auth: required
~~~

### Intention
Checks the health and connectivity of an MCP server.

### Input
```typescript
interface McpHealthRequest {
  harnessId: HarnessId;                // path parameter
  serverId: string;                    // path parameter
}
```

### Output
```typescript
interface McpHealthResponse {
  status: "healthy" | "degraded" | "unhealthy";
  latency_ms: number;
  last_error?: string;
}
```

---

# 5. Tools

Unified tool management across skills, MCP, and built-ins.

## Capability: List Tools

~~~meta
id: tools.list
transport: HTTP GET /harnesses/{harnessId}/tools
auth: required
~~~

### Intention
Lists all available tools on the harness, including built-in tools, MCP tools, and skill-provided tools.

### Input
```typescript
interface ListToolsRequest extends PaginationParams {
  harnessId: HarnessId;                // path parameter
  source?: "builtin" | "mcp" | "skill" | "custom";
}
```

### Output
```typescript
interface ListToolsResponse extends PaginatedResponse<Tool> {}

interface Tool {
  id: string;
  name: string;
  description: string;
  source: "builtin" | "mcp" | "skill" | "custom";
  source_id?: string;                  // MCP server ID or skill ID
  input_schema: object;
}
```

---

## Capability: Get Tool

~~~meta
id: tools.get
transport: HTTP GET /harnesses/{harnessId}/tools/{toolId}
auth: required
~~~

### Intention
Retrieves the schema and details for a specific tool.

### Input
```typescript
interface GetToolRequest {
  harnessId: HarnessId;                // path parameter
  toolId: string;                      // path parameter
}
```

### Output
```typescript
interface GetToolResponse {
  tool: Tool;
}
```

---

## Capability: Register Custom Tool

~~~meta
id: tools.register
transport: HTTP POST /harnesses/{harnessId}/tools
auth: required
~~~

### Intention
Registers a custom tool with the harness.

### Input
```typescript
interface RegisterToolRequest {
  harnessId: HarnessId;                // path parameter
  name: string;                        // 1-100 chars
  description: string;                 // 1-1000 chars
  input_schema: object;                // JSON Schema
  handler: ToolHandler;
}

type ToolHandler =
  | { type: "webhook"; url: string }
  | { type: "command"; command: string; args?: string[] };
```

### Output
```typescript
interface RegisterToolResponse {
  tool: Tool;
}
```

---

## Capability: Unregister Tool

~~~meta
id: tools.unregister
transport: HTTP DELETE /harnesses/{harnessId}/tools/{toolId}
auth: required
~~~

### Intention
Unregisters a custom tool from the harness.

### Logic Constraints
- Can only unregister custom tools, not built-in or MCP tools

### Input
```typescript
interface UnregisterToolRequest {
  harnessId: HarnessId;                // path parameter
  toolId: string;                      // path parameter
}
```

### Output
Returns 204 No Content on success.

---

## Capability: Invoke Tool

~~~meta
id: tools.invoke
transport: HTTP POST /harnesses/{harnessId}/tools/{toolId}/invoke
auth: required
~~~

### Intention
Directly invokes a tool outside of an execution context.

### Input
```typescript
interface InvokeToolRequest {
  harnessId: HarnessId;                // path parameter
  toolId: string;                      // path parameter
  input: object;                       // Tool-specific input
}
```

### Output
```typescript
interface InvokeToolResponse {
  success: boolean;
  output: object;
  duration_ms: number;
  error?: string;
}
```

---

## Capability: Invoke Tool (Streaming)

~~~meta
id: tools.invokeStream
transport: HTTP POST /harnesses/{harnessId}/tools/{toolId}/invoke/stream (SSE)
auth: required
~~~

### Intention
Invokes a tool with streaming output. Useful for tools that produce incremental results.

### Input
```typescript
interface InvokeToolStreamRequest {
  harnessId: HarnessId;                // path parameter
  toolId: string;                      // path parameter
  input: object;                       // Tool-specific input
}
```

### Output
```typescript
type ToolStreamEvent =
  | { type: "output"; data: object }
  | { type: "progress"; percentage: number; message: string }
  | { type: "error"; code: string; message: string }
  | { type: "done"; success: boolean; duration_ms: number };
```

---

# 6. Execution

Run tasks, stream responses, manage execution lifecycle.

## Capability: Execute Task

~~~meta
id: execution.run
transport: HTTP POST /harnesses/{harnessId}/execute
auth: required
~~~

### Intention
Executes a task on the harness. Returns immediately with an execution ID; use the stream endpoint to follow progress.

### Input
```typescript
interface ExecuteRequest {
  harnessId: HarnessId;                // path parameter
  message: string;                     // 1-100000 chars
  agent_id?: AgentId;                  // Use specific agent
  skills?: SkillId[];                  // Skills to enable
  model?: string;                      // Override default model
  max_tokens?: number;                 // 1-200000
  temperature?: number;                // 0.0-1.0
  system_prompt?: string;              // Additional system context
  session_id?: SessionId;              // Continue existing session
}
```

### Output
```typescript
interface ExecuteResponse {
  execution_id: ExecutionId;
  status: ExecutionStatus;
  stream_url: string;                  // URL to attach to stream
}
```

### Errors
- `context_length_exceeded` (400): Combined input exceeds model's context window
- `model_not_available` (400): Requested model not available on this harness

---

## Capability: Execute Task (Streaming)

~~~meta
id: execution.stream
transport: HTTP POST /harnesses/{harnessId}/execute/stream (SSE)
auth: required
~~~

### Intention
Executes a task with streaming response. Use this for real-time feedback during execution.

### Logic Constraints
- Client should handle reconnection using `Last-Event-ID` header
- Stream may include multiple tool calls before completion
- `done` event signals stream completion

### Input
```typescript
interface ExecuteStreamRequest {
  harnessId: HarnessId;                // path parameter
  message: string;                     // 1-100000 chars
  agent_id?: AgentId;
  skills?: SkillId[];
  model?: string;
  max_tokens?: number;
  temperature?: number;
  system_prompt?: string;
  session_id?: SessionId;
}
```

### Output
```typescript
// Stream of ExecutionEvent (see Global Types)
type ExecutionEvent =
  | { type: "text"; content: string }
  | { type: "thinking"; content: string }
  | { type: "tool_call_start"; id: string; name: string; input: object }
  | { type: "tool_call_delta"; id: string; input_delta: object }
  | { type: "tool_call_end"; id: string }
  | { type: "tool_result"; id: string; success: boolean; output?: object }
  | { type: "artifact"; id: string; name: string; mime_type: string; size_bytes: number }
  | { type: "progress"; percentage: number; step: string; step_number: number; total_steps: number }
  | { type: "error"; code: string; message: string; recoverable: boolean }
  | { type: "done"; usage: UsageStats };
```

---

## Capability: List Executions

~~~meta
id: execution.list
transport: HTTP GET /harnesses/{harnessId}/executions
auth: required
~~~

### Intention
Lists recent executions on the harness.

### Input
```typescript
interface ListExecutionsRequest extends PaginationParams {
  harnessId: HarnessId;                // path parameter
  status?: ExecutionStatus;
  agent_id?: AgentId;
  since?: ISO8601;                     // Filter by start time
}
```

### Output
```typescript
interface ListExecutionsResponse extends PaginatedResponse<Execution> {}
```

---

## Capability: Get Execution

~~~meta
id: execution.get
transport: HTTP GET /harnesses/{harnessId}/executions/{executionId}
auth: required
~~~

### Intention
Retrieves the current status and progress of an execution.

### Input
```typescript
interface GetExecutionRequest {
  harnessId: HarnessId;                // path parameter
  executionId: ExecutionId;            // path parameter
}
```

### Output
```typescript
interface GetExecutionResponse {
  execution: Execution;
}
```

---

## Capability: Attach to Execution Stream

~~~meta
id: execution.attachStream
transport: HTTP GET /harnesses/{harnessId}/executions/{executionId}/stream (SSE)
auth: required
~~~

### Intention
Attaches to an existing execution's event stream. Use `Last-Event-ID` header to resume from a specific point.

### Logic Constraints
- Returns 410 Gone if execution has completed and stream is no longer available
- Streams are retained for 1 hour after completion

### Input
```typescript
interface AttachStreamRequest {
  harnessId: HarnessId;                // path parameter
  executionId: ExecutionId;            // path parameter
}
```

### Output
Stream of `ExecutionEvent` (see Global Types).

---

## Capability: Cancel Execution

~~~meta
id: execution.cancel
transport: HTTP POST /harnesses/{harnessId}/executions/{executionId}/cancel
auth: required
~~~

### Intention
Cancels a running execution.

### Logic Constraints
- Cancellation is best-effort; currently running tool may complete
- Returns 409 if execution is already completed

### Input
```typescript
interface CancelExecutionRequest {
  harnessId: HarnessId;                // path parameter
  executionId: ExecutionId;            // path parameter
}
```

### Output
```typescript
interface CancelExecutionResponse {
  execution: Execution;
  cancelled: boolean;
}
```

---

## Capability: Get Execution Result

~~~meta
id: execution.result
transport: HTTP GET /harnesses/{harnessId}/executions/{executionId}/result
auth: required
~~~

### Intention
Retrieves the final result of a completed execution.

### Logic Constraints
- Returns 409 if execution is still running

### Input
```typescript
interface GetExecutionResultRequest {
  harnessId: HarnessId;                // path parameter
  executionId: ExecutionId;            // path parameter
}
```

### Output
```typescript
interface GetExecutionResultResponse {
  result: ExecutionResult;
}
```

---

## Capability: List Artifacts

~~~meta
id: execution.listArtifacts
transport: HTTP GET /harnesses/{harnessId}/executions/{executionId}/artifacts
auth: required
~~~

### Intention
Lists all artifacts generated by an execution.

### Input
```typescript
interface ListArtifactsRequest {
  harnessId: HarnessId;                // path parameter
  executionId: ExecutionId;            // path parameter
}
```

### Output
```typescript
interface ListArtifactsResponse {
  artifacts: ArtifactSummary[];
}
```

---

## Capability: Download Artifact

~~~meta
id: execution.downloadArtifact
transport: HTTP GET /harnesses/{harnessId}/executions/{executionId}/artifacts/{artifactId}
auth: required
~~~

### Intention
Downloads a specific artifact generated by an execution.

### Logic Constraints
- Content-Type header matches the artifact's MIME type
- Content-Disposition header contains original filename
- Large files use chunked transfer encoding

### Input
```typescript
interface DownloadArtifactRequest {
  harnessId: HarnessId;                // path parameter
  executionId: ExecutionId;            // path parameter
  artifactId: string;                  // path parameter
}
```

### Output
Returns raw file bytes with appropriate `Content-Type` header.

---

## Capability: List Tool Calls

~~~meta
id: execution.listToolCalls
transport: HTTP GET /harnesses/{harnessId}/executions/{executionId}/tool-calls
auth: required
~~~

### Intention
Lists all tool calls made during an execution with their inputs and outputs.

### Input
```typescript
interface ListToolCallsRequest {
  harnessId: HarnessId;                // path parameter
  executionId: ExecutionId;            // path parameter
}
```

### Output
```typescript
interface ListToolCallsResponse {
  tool_calls: DetailedToolCall[];
}

interface DetailedToolCall {
  id: string;
  name: string;
  input: object;
  output?: object;
  status: "pending" | "running" | "completed" | "failed";
  error?: string;
  started_at: ISO8601;
  completed_at?: ISO8601;
  duration_ms?: number;
}
```

---

## Capability: Send Input

~~~meta
id: execution.sendInput
transport: HTTP POST /harnesses/{harnessId}/executions/{executionId}/input
auth: required
~~~

### Intention
Sends input (stdin) to a running execution that is waiting for user input.

### Logic Constraints
- Returns 409 if execution is not waiting for input
- Returns 410 if execution has completed

### Input
```typescript
interface SendInputRequest {
  harnessId: HarnessId;                // path parameter
  executionId: ExecutionId;            // path parameter
  data: string;                        // Input data (e.g., "yes\n")
}
```

### Output
```typescript
interface SendInputResponse {
  accepted: boolean;
}
```

---

# 7. Sessions

Session persistence, resumption, and interactive communication.

## Capability: List Sessions

~~~meta
id: sessions.list
transport: HTTP GET /harnesses/{harnessId}/sessions
auth: required
~~~

### Intention
Lists all sessions on the harness.

### Input
```typescript
interface ListSessionsRequest extends PaginationParams {
  harnessId: HarnessId;                // path parameter
  status?: "active" | "paused" | "ended";
  agent_id?: AgentId;
}
```

### Output
```typescript
interface ListSessionsResponse extends PaginatedResponse<Session> {}
```

---

## Capability: Create Session

~~~meta
id: sessions.create
transport: HTTP POST /harnesses/{harnessId}/sessions
auth: required
~~~

### Intention
Creates a new interactive session.

### Input
```typescript
interface CreateSessionRequest {
  harnessId: HarnessId;                // path parameter
  name?: string;                       // 1-100 chars
  agent_id?: AgentId;                  // Associate with agent
  skills?: SkillId[];                  // Skills to enable
  system_prompt?: string;              // Initial system context
}
```

### Output
```typescript
interface CreateSessionResponse {
  session: Session;
  connect_url: string;                 // WebSocket URL
}
```

---

## Capability: Get Session

~~~meta
id: sessions.get
transport: HTTP GET /harnesses/{harnessId}/sessions/{sessionId}
auth: required
~~~

### Intention
Retrieves session state and metadata.

### Input
```typescript
interface GetSessionRequest {
  harnessId: HarnessId;                // path parameter
  sessionId: SessionId;                // path parameter
}
```

### Output
```typescript
interface GetSessionResponse {
  session: Session;
}
```

---

## Capability: Update Session

~~~meta
id: sessions.update
transport: HTTP PATCH /harnesses/{harnessId}/sessions/{sessionId}
auth: required
~~~

### Intention
Updates session metadata.

### Input
```typescript
interface UpdateSessionRequest {
  harnessId: HarnessId;                // path parameter
  sessionId: SessionId;                // path parameter
  name?: string;
  status?: "active" | "paused";
}
```

### Output
```typescript
interface UpdateSessionResponse {
  session: Session;
}
```

---

## Capability: End Session

~~~meta
id: sessions.end
transport: HTTP DELETE /harnesses/{harnessId}/sessions/{sessionId}
auth: required
~~~

### Intention
Ends and optionally deletes a session.

### Input
```typescript
interface EndSessionRequest {
  harnessId: HarnessId;                // path parameter
  sessionId: SessionId;                // path parameter
  delete_history?: boolean;            // default: false
}
```

### Output
Returns 204 No Content on success.

---

## Capability: Resume Session

~~~meta
id: sessions.resume
transport: HTTP POST /harnesses/{harnessId}/sessions/{sessionId}/resume
auth: required
~~~

### Intention
Resumes a paused session.

### Input
```typescript
interface ResumeSessionRequest {
  harnessId: HarnessId;                // path parameter
  sessionId: SessionId;                // path parameter
}
```

### Output
```typescript
interface ResumeSessionResponse {
  session: Session;
  connect_url: string;
}
```

---

## Capability: Get Session History

~~~meta
id: sessions.history
transport: HTTP GET /harnesses/{harnessId}/sessions/{sessionId}/history
auth: required
~~~

### Intention
Retrieves the message history for a session.

### Input
```typescript
interface GetSessionHistoryRequest extends PaginationParams {
  harnessId: HarnessId;                // path parameter
  sessionId: SessionId;                // path parameter
  since?: ISO8601;                     // Messages after this time
}
```

### Output
```typescript
interface GetSessionHistoryResponse extends PaginatedResponse<Message> {}
```

---

## Capability: Fork Session

~~~meta
id: sessions.fork
transport: HTTP POST /harnesses/{harnessId}/sessions/{sessionId}/fork
auth: required
~~~

### Intention
Creates a copy of a session with its history, allowing experimentation from a specific point.

### Input
```typescript
interface ForkSessionRequest {
  harnessId: HarnessId;                // path parameter
  sessionId: SessionId;                // path parameter
  new_name?: string;                   // 1-100 chars
  from_message_id?: string;            // Fork from specific message
}
```

### Output
```typescript
interface ForkSessionResponse {
  session: Session;
  forked_from: SessionId;
  message_count: number;
}
```

---

## Channel: Interactive Session

~~~meta
id: sessions.connect
transport: WS /harnesses/{harnessId}/sessions/{sessionId}/connect
auth: required
~~~

### Intention
Establishes a WebSocket connection for real-time interactive communication with a session.

### Logic Constraints
- Connection closes if session is ended or paused
- Client should handle reconnection on disconnect
- Ping/pong frames maintain connection health

### Client Messages
```typescript
type ClientMessage =
  | { type: "message"; id: string; content: string }
  | { type: "stdin"; id: string; data: string }
  | { type: "cancel"; execution_id: string };
```

### Server Messages
```typescript
type ServerMessage =
  | { type: "text"; id: string; content: string }
  | { type: "thinking"; id: string; content: string }
  | { type: "tool_call"; id: string; tool: string; input: object }
  | { type: "stdout"; id: string; data: string }
  | { type: "stderr"; id: string; data: string }
  | { type: "prompt"; id: string; prompt: string }
  | { type: "artifact"; id: string; name: string; mime_type: string }
  | { type: "error"; id: string; code: string; message: string }
  | { type: "done"; id: string; usage: UsageStats };
```

---

## Capability: Send Message

~~~meta
id: sessions.sendMessage
transport: HTTP POST /harnesses/{harnessId}/sessions/{sessionId}/message
auth: required
~~~

### Intention
Sends a message to a session and waits for the complete response. Use this for non-streaming interactions.

### Input
```typescript
interface SendMessageRequest {
  harnessId: HarnessId;                // path parameter
  sessionId: SessionId;                // path parameter
  content: string;                     // 1-100000 chars
}
```

### Output
```typescript
interface SendMessageResponse {
  message: Message;
  response: Message;
}
```

---

## Capability: Send Message (Streaming)

~~~meta
id: sessions.sendMessageStream
transport: HTTP POST /harnesses/{harnessId}/sessions/{sessionId}/message/stream (SSE)
auth: required
~~~

### Intention
Sends a message to a session with streaming response.

### Input
```typescript
interface SendMessageStreamRequest {
  harnessId: HarnessId;                // path parameter
  sessionId: SessionId;                // path parameter
  content: string;                     // 1-100000 chars
}
```

### Output
Stream of `ExecutionEvent` (see Global Types).

---

# 8. Memory

Persistent memory operations across sessions.

## Capability: Get Memory State

~~~meta
id: memory.get
transport: HTTP GET /harnesses/{harnessId}/agents/{agentId}/memory
auth: required
~~~

### Intention
Retrieves the complete memory state for an agent.

### Input
```typescript
interface GetMemoryRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter
}
```

### Output
```typescript
interface GetMemoryResponse {
  memory: MemoryState;
}
```

---

## Capability: List Memory Blocks

~~~meta
id: memory.listBlocks
transport: HTTP GET /harnesses/{harnessId}/agents/{agentId}/memory/blocks
auth: required
~~~

### Intention
Lists all memory blocks for an agent.

### Input
```typescript
interface ListMemoryBlocksRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter
}
```

### Output
```typescript
interface ListMemoryBlocksResponse {
  blocks: MemoryBlock[];
}
```

---

## Capability: Get Memory Block

~~~meta
id: memory.getBlock
transport: HTTP GET /harnesses/{harnessId}/agents/{agentId}/memory/blocks/{label}
auth: required
~~~

### Intention
Retrieves a specific memory block by label.

### Input
```typescript
interface GetMemoryBlockRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter
  label: string;                       // path parameter
}
```

### Output
```typescript
interface GetMemoryBlockResponse {
  block: MemoryBlock;
}
```

---

## Capability: Update Memory Block

~~~meta
id: memory.updateBlock
transport: HTTP PUT /harnesses/{harnessId}/agents/{agentId}/memory/blocks/{label}
auth: required
~~~

### Intention
Updates the value of a memory block.

### Logic Constraints
- Cannot update read-only blocks
- Returns 404 if block doesn't exist (use create instead)

### Input
```typescript
interface UpdateMemoryBlockRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter
  label: string;                       // path parameter
  value: string;                       // 1-100000 chars
}
```

### Output
```typescript
interface UpdateMemoryBlockResponse {
  block: MemoryBlock;
}
```

---

## Capability: Create Memory Block

~~~meta
id: memory.createBlock
transport: HTTP POST /harnesses/{harnessId}/agents/{agentId}/memory/blocks
auth: required
~~~

### Intention
Creates a new memory block for an agent.

### Logic Constraints
- Label must be unique for this agent
- Labels should be descriptive (e.g., "persona", "user_preferences")

### Input
```typescript
interface CreateMemoryBlockRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter
  label: string;                       // 1-100 chars, format: kebab-case
  value: string;                       // 1-100000 chars
  read_only?: boolean;                 // default: false
}
```

### Output
```typescript
interface CreateMemoryBlockResponse {
  block: MemoryBlock;
}
```

---

## Capability: Delete Memory Block

~~~meta
id: memory.deleteBlock
transport: HTTP DELETE /harnesses/{harnessId}/agents/{agentId}/memory/blocks/{label}
auth: required
~~~

### Intention
Deletes a memory block.

### Logic Constraints
- Cannot delete read-only blocks

### Input
```typescript
interface DeleteMemoryBlockRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter
  label: string;                       // path parameter
}
```

### Output
Returns 204 No Content on success.

---

## Capability: Search Memory

~~~meta
id: memory.search
transport: HTTP POST /harnesses/{harnessId}/agents/{agentId}/memory/search
auth: required
~~~

### Intention
Searches across memory blocks and archive for relevant content.

### Input
```typescript
interface SearchMemoryRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter
  query: string;                       // 1-1000 chars
  include_archive?: boolean;           // default: true
  limit?: number;                      // 1-100, default: 10
}
```

### Output
```typescript
interface SearchMemoryResponse {
  results: MemorySearchResult[];
}

interface MemorySearchResult {
  source: "block" | "archive";
  label?: string;                      // For block results
  content: string;
  relevance_score: number;             // 0.0-1.0
}
```

---

## Capability: Get Archive

~~~meta
id: memory.getArchive
transport: HTTP GET /harnesses/{harnessId}/agents/{agentId}/memory/archive
auth: required
~~~

### Intention
Retrieves the archival/long-term memory for an agent.

### Input
```typescript
interface GetArchiveRequest extends PaginationParams {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter
}
```

### Output
```typescript
interface GetArchiveResponse extends PaginatedResponse<ArchiveEntry> {}

interface ArchiveEntry {
  id: string;
  content: string;
  created_at: ISO8601;
  metadata?: Record<string, unknown>;
}
```

---

## Capability: Add to Archive

~~~meta
id: memory.addToArchive
transport: HTTP POST /harnesses/{harnessId}/agents/{agentId}/memory/archive
auth: required
~~~

### Intention
Adds an entry to the agent's archival memory.

### Input
```typescript
interface AddToArchiveRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter
  content: string;                     // 1-100000 chars
  metadata?: Record<string, unknown>;
}
```

### Output
```typescript
interface AddToArchiveResponse {
  entry: ArchiveEntry;
}
```

---

## Capability: Export Memory

~~~meta
id: memory.export
transport: HTTP POST /harnesses/{harnessId}/agents/{agentId}/memory/export
auth: required
~~~

### Intention
Exports the agent's complete memory state as a downloadable snapshot. This snapshot can be included in an OAF package when exporting an agent with `include_memory=true`.

### Logic Constraints
- Content-Disposition header contains `{agentKey}-memory-{timestamp}.zip`
- ZIP structure:
  - `blocks.json` - All memory blocks with labels and content
  - `archive.json` - Archival memory entries with embeddings (if include_archive=true)
  - `metadata.json` - Export metadata (timestamp, agent version, block count)

### Input
```typescript
interface ExportMemoryRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter
  include_archive?: boolean;           // default: true
}
```

### Output
Returns raw ZIP bytes with `Content-Type: application/zip`.

---

## Capability: Import Memory

~~~meta
id: memory.import
transport: HTTP POST /harnesses/{harnessId}/agents/{agentId}/memory/import
content_type: multipart/form-data
auth: required
~~~

### Intention
Imports a previously exported memory snapshot into an agent. Used for restoring memory state or transferring memory between agents.

### Logic Constraints
- ZIP must contain valid `blocks.json` at minimum
- Block labels are used as unique identifiers for merge operations
- Archive entries are identified by content hash to prevent duplicates

### Merge Strategies
- `overwrite` (default): Replace existing blocks with same labels
- `skip`: Keep existing blocks, only import new ones
- `merge`: Attempt to merge content (concatenate for compatible blocks)

### Input
```typescript
interface ImportMemoryRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter
  snapshot: File;                      // ZIP file from export
  merge_strategy?: "overwrite" | "skip" | "merge";  // default: overwrite
}
```

### Output
```typescript
interface ImportMemoryResponse {
  blocks_imported: number;
  archive_entries_imported: number;
  conflicts: number;                   // Number of conflicts encountered
  warnings: string[];                  // Non-fatal import warnings
}
```

---

# 9. Subagents

Spawn, manage, and communicate with subagents.

## Capability: List Subagents

~~~meta
id: subagents.list
transport: HTTP GET /harnesses/{harnessId}/agents/{agentId}/subagents
auth: required
~~~

### Intention
Lists all subagents spawned by a parent agent.

### Input
```typescript
interface ListSubagentsRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter (parent)
}
```

### Output
```typescript
interface ListSubagentsResponse {
  subagents: Subagent[];
}

interface Subagent {
  id: string;
  name: string;
  description: string;
  status: "idle" | "running" | "completed" | "failed";
  parent_agent_id: AgentId;
  created_at: ISO8601;
}
```

---

## Capability: Spawn Subagent

~~~meta
id: subagents.spawn
transport: HTTP POST /harnesses/{harnessId}/agents/{agentId}/subagents
auth: required
~~~

### Intention
Spawns a new subagent to handle a specific task in isolation.

### Input
```typescript
interface SpawnSubagentRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter (parent)
  name: string;                        // 1-100 chars
  description: string;                 // 1-1000 chars
  system_prompt?: string;              // Subagent-specific instructions
  skills?: SkillId[];                  // Skills to enable
  model?: string;                      // Override model
}
```

### Output
```typescript
interface SpawnSubagentResponse {
  subagent: Subagent;
}
```

---

## Capability: Get Subagent

~~~meta
id: subagents.get
transport: HTTP GET /harnesses/{harnessId}/agents/{agentId}/subagents/{subagentId}
auth: required
~~~

### Intention
Retrieves the current state of a subagent.

### Input
```typescript
interface GetSubagentRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter (parent)
  subagentId: string;                  // path parameter
}
```

### Output
```typescript
interface GetSubagentResponse {
  subagent: Subagent;
}
```

---

## Capability: Terminate Subagent

~~~meta
id: subagents.terminate
transport: HTTP DELETE /harnesses/{harnessId}/agents/{agentId}/subagents/{subagentId}
auth: required
~~~

### Intention
Terminates a running subagent.

### Input
```typescript
interface TerminateSubagentRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter (parent)
  subagentId: string;                  // path parameter
}
```

### Output
Returns 204 No Content on success.

---

## Capability: Delegate Task

~~~meta
id: subagents.delegate
transport: HTTP POST /harnesses/{harnessId}/agents/{agentId}/subagents/{subagentId}/delegate
auth: required
~~~

### Intention
Delegates a task to a subagent and waits for completion.

### Input
```typescript
interface DelegateTaskRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter (parent)
  subagentId: string;                  // path parameter
  task: string;                        // 1-100000 chars
  context?: Record<string, unknown>;   // Additional context
}
```

### Output
```typescript
interface DelegateTaskResponse {
  execution_id: ExecutionId;
  status: ExecutionStatus;
}
```

---

## Capability: Delegate Task (Streaming)

~~~meta
id: subagents.delegateStream
transport: HTTP POST /harnesses/{harnessId}/agents/{agentId}/subagents/{subagentId}/delegate/stream (SSE)
auth: required
~~~

### Intention
Delegates a task to a subagent with streaming progress.

### Input
```typescript
interface DelegateTaskStreamRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter (parent)
  subagentId: string;                  // path parameter
  task: string;                        // 1-100000 chars
  context?: Record<string, unknown>;
}
```

### Output
Stream of `ExecutionEvent` (see Global Types).

---

## Capability: Get Subagent Result

~~~meta
id: subagents.result
transport: HTTP GET /harnesses/{harnessId}/agents/{agentId}/subagents/{subagentId}/result
auth: required
~~~

### Intention
Retrieves the result of a completed subagent task.

### Logic Constraints
- Returns 409 if subagent task is still running

### Input
```typescript
interface GetSubagentResultRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter (parent)
  subagentId: string;                  // path parameter
}
```

### Output
```typescript
interface GetSubagentResultResponse {
  result: ExecutionResult;
}
```

---

## Capability: Attach to Subagent Stream

~~~meta
id: subagents.attachStream
transport: HTTP GET /harnesses/{harnessId}/agents/{agentId}/subagents/{subagentId}/stream (SSE)
auth: required
~~~

### Intention
Attaches to a running subagent's execution stream.

### Input
```typescript
interface AttachSubagentStreamRequest {
  harnessId: HarnessId;                // path parameter
  agentId: AgentId;                    // path parameter (parent)
  subagentId: string;                  // path parameter
}
```

### Output
Stream of `ExecutionEvent` (see Global Types).

---

# 10. Files & Artifacts

File system operations and artifact management.

## Capability: List Files

~~~meta
id: files.list
transport: HTTP GET /harnesses/{harnessId}/files
auth: required
~~~

### Intention
Lists files in the harness workspace.

### Input
```typescript
interface ListFilesRequest {
  harnessId: HarnessId;                // path parameter
  path?: string;                       // Directory path, default: "/"
  recursive?: boolean;                 // default: false
}
```

### Output
```typescript
interface ListFilesResponse {
  files: FileInfo[];
  path: string;
}
```

---

## Capability: Read File

~~~meta
id: files.read
transport: HTTP GET /harnesses/{harnessId}/files/{path}
auth: required
~~~

### Intention
Reads the contents of a file.

### Logic Constraints
- Returns 404 for non-existent files
- Content-Type header matches file MIME type
- Text files returned as text; binary files as application/octet-stream

### Input
```typescript
interface ReadFileRequest {
  harnessId: HarnessId;                // path parameter
  path: string;                        // path parameter (URL-encoded)
}
```

### Output
Returns file contents with appropriate `Content-Type` header.

---

## Capability: Write File

~~~meta
id: files.write
transport: HTTP PUT /harnesses/{harnessId}/files/{path}
auth: required
~~~

### Intention
Writes content to a file, creating it if it doesn't exist.

### Logic Constraints
- Creates parent directories if they don't exist
- Overwrites existing files

### Input
```typescript
interface WriteFileRequest {
  harnessId: HarnessId;                // path parameter
  path: string;                        // path parameter (URL-encoded)
  // Body is the file content
}
```

### Output
```typescript
interface WriteFileResponse {
  file: FileInfo;
  created: boolean;
}
```

---

## Capability: Delete File

~~~meta
id: files.delete
transport: HTTP DELETE /harnesses/{harnessId}/files/{path}
auth: required
~~~

### Intention
Deletes a file or empty directory.

### Logic Constraints
- Cannot delete non-empty directories (use recursive flag)

### Input
```typescript
interface DeleteFileRequest {
  harnessId: HarnessId;                // path parameter
  path: string;                        // path parameter (URL-encoded)
  recursive?: boolean;                 // For directories, default: false
}
```

### Output
Returns 204 No Content on success.

---

## Capability: Search Files

~~~meta
id: files.search
transport: HTTP POST /harnesses/{harnessId}/files/search
auth: required
~~~

### Intention
Searches for files using glob patterns or content grep.

### Input
```typescript
interface SearchFilesRequest {
  harnessId: HarnessId;                // path parameter
  glob?: string;                       // Glob pattern (e.g., "**/*.ts")
  grep?: string;                       // Content search (regex)
  path?: string;                       // Starting directory
  max_results?: number;                // 1-1000, default: 100
}
```

### Output
```typescript
interface SearchFilesResponse {
  matches: FileMatch[];
}

interface FileMatch {
  file: FileInfo;
  line_matches?: LineMatch[];          // For grep searches
}

interface LineMatch {
  line_number: number;
  content: string;
}
```

---

## Capability: Upload File

~~~meta
id: files.upload
transport: HTTP POST /harnesses/{harnessId}/files/upload
content_type: multipart/form-data
auth: required
~~~

### Intention
Uploads a single file to the workspace.

### Input
```typescript
interface UploadFileRequest {
  harnessId: HarnessId;                // path parameter
  path: string;                        // Target path
  file: File;                          // File content
  overwrite?: boolean;                 // default: false
}
```

### Output
```typescript
interface UploadFileResponse {
  file: FileInfo;
  created: boolean;
}
```

---

## Capability: Upload Files (Batch)

~~~meta
id: files.uploadBatch
transport: HTTP POST /harnesses/{harnessId}/files/upload-batch
content_type: multipart/form-data
auth: required
~~~

### Intention
Uploads multiple files preserving directory structure.

### Logic Constraints
- Filenames in multipart include relative paths
- Maximum total size: 100MB
- Maximum 500 files per batch

### Input
```typescript
interface UploadFilesBatchRequest {
  harnessId: HarnessId;                // path parameter
  base_path?: string;                  // Base directory, default: "/"
  files: File[];                       // Files with path-preserving names
  overwrite?: boolean;                 // default: false
}
```

### Output
```typescript
interface UploadFilesBatchResponse {
  uploaded: FileInfo[];
  skipped: string[];                   // Paths skipped (already exist)
  errors: FileError[];
}

interface FileError {
  path: string;
  error: string;
}
```

---

## Capability: Download File

~~~meta
id: files.download
transport: HTTP GET /harnesses/{harnessId}/files/{path}/download
auth: required
~~~

### Intention
Downloads a file with Content-Disposition header for saving.

### Logic Constraints
- Content-Disposition: attachment; filename="name"

### Input
```typescript
interface DownloadFileRequest {
  harnessId: HarnessId;                // path parameter
  path: string;                        // path parameter (URL-encoded)
}
```

### Output
Returns file bytes with `Content-Disposition: attachment`.

---

## Capability: Download Files (Batch)

~~~meta
id: files.downloadBatch
transport: HTTP POST /harnesses/{harnessId}/files/download-batch
auth: required
~~~

### Intention
Downloads multiple files as a ZIP archive.

### Logic Constraints
- ZIP preserves directory structure
- Maximum 1000 files per request

### Input
```typescript
interface DownloadFilesBatchRequest {
  harnessId: HarnessId;                // path parameter
  paths: string[];                     // 1-1000 items
}
```

### Output
Returns ZIP bytes with `Content-Type: application/zip`.

---

## Capability: Create Directory

~~~meta
id: files.mkdir
transport: HTTP POST /harnesses/{harnessId}/files/mkdir
auth: required
~~~

### Intention
Creates a directory and any necessary parent directories.

### Input
```typescript
interface CreateDirectoryRequest {
  harnessId: HarnessId;                // path parameter
  path: string;                        // Directory path to create
}
```

### Output
```typescript
interface CreateDirectoryResponse {
  file: FileInfo;
  created: boolean;
}
```

---

# 11. Hooks & Events

Lifecycle hooks and event subscriptions.

## Capability: List Hooks

~~~meta
id: hooks.list
transport: HTTP GET /harnesses/{harnessId}/hooks
auth: required
~~~

### Intention
Lists all registered hooks for a harness.

### Input
```typescript
interface ListHooksRequest {
  harnessId: HarnessId;                // path parameter
  event?: HookEvent;                   // Filter by event type
}
```

### Output
```typescript
interface ListHooksResponse {
  hooks: Hook[];
}
```

---

## Capability: Register Hook

~~~meta
id: hooks.register
transport: HTTP POST /harnesses/{harnessId}/hooks
auth: required
~~~

### Intention
Registers a new lifecycle hook.

### Input
```typescript
interface RegisterHookRequest {
  harnessId: HarnessId;                // path parameter
  event: HookEvent;
  handler: HookHandler;
  enabled?: boolean;                   // default: true
}
```

### Output
```typescript
interface RegisterHookResponse {
  hook: Hook;
}
```

---

## Capability: Get Hook

~~~meta
id: hooks.get
transport: HTTP GET /harnesses/{harnessId}/hooks/{hookId}
auth: required
~~~

### Intention
Retrieves details about a specific hook.

### Input
```typescript
interface GetHookRequest {
  harnessId: HarnessId;                // path parameter
  hookId: string;                      // path parameter
}
```

### Output
```typescript
interface GetHookResponse {
  hook: Hook;
}
```

---

## Capability: Update Hook

~~~meta
id: hooks.update
transport: HTTP PATCH /harnesses/{harnessId}/hooks/{hookId}
auth: required
~~~

### Intention
Updates hook configuration.

### Input
```typescript
interface UpdateHookRequest {
  harnessId: HarnessId;                // path parameter
  hookId: string;                      // path parameter
  handler?: HookHandler;
  enabled?: boolean;
}
```

### Output
```typescript
interface UpdateHookResponse {
  hook: Hook;
}
```

---

## Capability: Unregister Hook

~~~meta
id: hooks.unregister
transport: HTTP DELETE /harnesses/{harnessId}/hooks/{hookId}
auth: required
~~~

### Intention
Removes a hook registration.

### Input
```typescript
interface UnregisterHookRequest {
  harnessId: HarnessId;                // path parameter
  hookId: string;                      // path parameter
}
```

### Output
Returns 204 No Content on success.

---

## Capability: Stream Events

~~~meta
id: hooks.streamEvents
transport: HTTP GET /harnesses/{harnessId}/events/stream (SSE)
auth: required
~~~

### Intention
Subscribes to real-time events from the harness.

### Logic Constraints
- Events include all hook triggers, execution updates, and system events
- Use `Last-Event-ID` for reconnection

### Input
```typescript
interface StreamEventsRequest {
  harnessId: HarnessId;                // path parameter
  events?: string[];                   // Filter to specific event types
}
```

### Output
```typescript
type HarnessEvent =
  | { type: "hook.triggered"; hook_id: string; event: HookEvent; data: object }
  | { type: "execution.started"; execution_id: ExecutionId }
  | { type: "execution.completed"; execution_id: ExecutionId; status: ExecutionStatus }
  | { type: "session.created"; session_id: SessionId }
  | { type: "session.ended"; session_id: SessionId }
  | { type: "skill.installed"; skill_id: SkillId }
  | { type: "skill.uninstalled"; skill_id: SkillId }
  | { type: "error"; code: string; message: string };
```

---

## Capability: List Events

~~~meta
id: hooks.listEvents
transport: HTTP GET /harnesses/{harnessId}/events
auth: required
~~~

### Intention
Lists recent events from the harness.

### Input
```typescript
interface ListEventsRequest extends PaginationParams {
  harnessId: HarnessId;                // path parameter
  type?: string;                       // Filter by event type
  since?: ISO8601;                     // Events after this time
}
```

### Output
```typescript
interface ListEventsResponse extends PaginatedResponse<StoredEvent> {}

interface StoredEvent {
  id: string;
  type: string;
  data: object;
  timestamp: ISO8601;
}
```

---

## Capability: Register Webhook

~~~meta
id: webhooks.register
transport: HTTP POST /harnesses/{harnessId}/webhooks
auth: required
~~~

### Intention
Registers a webhook endpoint to receive async notifications.

### Logic Constraints
- URL must be HTTPS
- Webhook secret is generated if not provided

### Input
```typescript
interface RegisterWebhookRequest {
  harnessId: HarnessId;                // path parameter
  url: string;                         // format: uri, HTTPS required
  events: string[];                    // Event types to subscribe
  secret?: string;                     // Signing secret
}
```

### Output
```typescript
interface RegisterWebhookResponse {
  webhook: Webhook;
}
```

---

## Capability: List Webhooks

~~~meta
id: webhooks.list
transport: HTTP GET /harnesses/{harnessId}/webhooks
auth: required
~~~

### Intention
Lists all registered webhooks.

### Input
```typescript
interface ListWebhooksRequest {
  harnessId: HarnessId;                // path parameter
}
```

### Output
```typescript
interface ListWebhooksResponse {
  webhooks: Webhook[];
}
```

---

## Capability: Delete Webhook

~~~meta
id: webhooks.delete
transport: HTTP DELETE /harnesses/{harnessId}/webhooks/{webhookId}
auth: required
~~~

### Intention
Removes a webhook registration.

### Input
```typescript
interface DeleteWebhookRequest {
  harnessId: HarnessId;                // path parameter
  webhookId: string;                   // path parameter
}
```

### Output
Returns 204 No Content on success.

---

## Webhook: Execution Completed

~~~meta
id: webhooks.executionCompleted
transport: WEBHOOK POST {callback_url}
~~~

### Intention
Notifies when an execution completes.

### Payload
```typescript
interface ExecutionCompletedWebhook {
  event: "execution.completed";
  execution_id: ExecutionId;
  harness_id: HarnessId;
  status: ExecutionStatus;
  artifacts: ArtifactSummary[];
  usage: UsageStats;
  completed_at: ISO8601;
  signature: string;                   // HMAC-SHA256
}
```

### Logic Constraints
- Signature: HMAC-SHA256 of raw body using webhook secret
- Header: `X-OpenHarness-Signature: sha256=<signature>`
- Timeout: 30 seconds
- Retry: exponential backoff (1min, 5min, 30min, 2hr)

---

# 12. Planning & Tasks

Built-in planning and task management.

## Capability: Get Plan

~~~meta
id: planning.get
transport: HTTP GET /harnesses/{harnessId}/executions/{executionId}/plan
auth: required
~~~

### Intention
Retrieves the current execution plan (todo list).

### Input
```typescript
interface GetPlanRequest {
  harnessId: HarnessId;                // path parameter
  executionId: ExecutionId;            // path parameter
}
```

### Output
```typescript
interface GetPlanResponse {
  plan: Plan;
}
```

---

## Capability: Update Plan

~~~meta
id: planning.update
transport: HTTP PATCH /harnesses/{harnessId}/executions/{executionId}/plan
auth: required
~~~

### Intention
Updates the execution plan, typically to add or reorder tasks.

### Input
```typescript
interface UpdatePlanRequest {
  harnessId: HarnessId;                // path parameter
  executionId: ExecutionId;            // path parameter
  tasks?: PlanTask[];                  // Replace task list
}
```

### Output
```typescript
interface UpdatePlanResponse {
  plan: Plan;
}
```

---

## Capability: List Tasks

~~~meta
id: planning.listTasks
transport: HTTP GET /harnesses/{harnessId}/executions/{executionId}/plan/tasks
auth: required
~~~

### Intention
Lists all tasks in the execution plan.

### Input
```typescript
interface ListTasksRequest {
  harnessId: HarnessId;                // path parameter
  executionId: ExecutionId;            // path parameter
  status?: "pending" | "in_progress" | "completed";
}
```

### Output
```typescript
interface ListTasksResponse {
  tasks: PlanTask[];
}
```

---

## Capability: Update Task

~~~meta
id: planning.updateTask
transport: HTTP PATCH /harnesses/{harnessId}/executions/{executionId}/plan/tasks/{taskId}
auth: required
~~~

### Intention
Updates a specific task's status or content.

### Input
```typescript
interface UpdateTaskRequest {
  harnessId: HarnessId;                // path parameter
  executionId: ExecutionId;            // path parameter
  taskId: string;                      // path parameter
  content?: string;
  status?: "pending" | "in_progress" | "completed";
}
```

### Output
```typescript
interface UpdateTaskResponse {
  task: PlanTask;
}
```

---

## Capability: Stream Plan Updates

~~~meta
id: planning.stream
transport: HTTP GET /harnesses/{harnessId}/executions/{executionId}/plan/stream (SSE)
auth: required
~~~

### Intention
Subscribes to real-time plan updates during execution.

### Input
```typescript
interface StreamPlanRequest {
  harnessId: HarnessId;                // path parameter
  executionId: ExecutionId;            // path parameter
}
```

### Output
```typescript
type PlanEvent =
  | { type: "task.added"; task: PlanTask }
  | { type: "task.updated"; task: PlanTask }
  | { type: "task.removed"; task_id: string }
  | { type: "plan.reordered"; task_ids: string[] };
```

---

# 13. Conformance & Diagnostics

Test harness conformance and diagnose issues.

## Capability: Run Conformance Tests

~~~meta
id: conformance.run
transport: HTTP POST /harnesses/{harnessId}/conformance/run
auth: required
~~~

### Intention
Initiates a conformance test run against a harness.

### Input
```typescript
interface RunConformanceRequest {
  harnessId: HarnessId;                // path parameter
  categories?: string[];               // Test categories to run
  quick?: boolean;                     // Skip slow tests, default: false
}
```

### Output
```typescript
interface RunConformanceResponse {
  run_id: string;
  status: "running" | "completed";
  stream_url: string;
}
```

---

## Capability: Stream Conformance Progress

~~~meta
id: conformance.stream
transport: HTTP GET /harnesses/{harnessId}/conformance/run/stream (SSE)
auth: required
~~~

### Intention
Streams real-time progress of conformance tests.

### Input
```typescript
interface StreamConformanceRequest {
  harnessId: HarnessId;                // path parameter
  run_id?: string;                     // Specific run, default: latest
}
```

### Output
```typescript
type ConformanceEvent =
  | { type: "test.started"; test_id: string; test_name: string }
  | { type: "test.passed"; test_id: string }
  | { type: "test.failed"; test_id: string; error: string }
  | { type: "test.skipped"; test_id: string; reason: string }
  | { type: "progress"; completed: number; total: number }
  | { type: "done"; result: ConformanceResult };

interface ConformanceResult {
  passed: number;
  failed: number;
  skipped: number;
  duration_ms: number;
}
```

---

## Capability: Get Conformance Results

~~~meta
id: conformance.results
transport: HTTP GET /harnesses/{harnessId}/conformance/results
auth: required
~~~

### Intention
Retrieves results from conformance test runs.

### Input
```typescript
interface GetConformanceResultsRequest extends PaginationParams {
  harnessId: HarnessId;                // path parameter
}
```

### Output
```typescript
interface GetConformanceResultsResponse extends PaginatedResponse<ConformanceRun> {}

interface ConformanceRun {
  id: string;
  harness_version: string;
  result: "pass" | "fail" | "partial";
  passed: number;
  failed: number;
  skipped: number;
  golden_rule_violations: number;
  run_at: ISO8601;
}
```

---

## Capability: Get Conformance Status

~~~meta
id: conformance.status
transport: HTTP GET /harnesses/{harnessId}/conformance/status
auth: required
~~~

### Intention
Retrieves the current conformance certification status.

### Input
```typescript
interface GetConformanceStatusRequest {
  harnessId: HarnessId;                // path parameter
}
```

### Output
```typescript
interface GetConformanceStatusResponse {
  status: "certified" | "partial" | "failing" | "not_tested";
  certified_version?: string;
  pass_rate: number;                   // 0.0-1.0
  last_run_at?: ISO8601;
  skill_loading_method?: "api" | "file-based";
  supports_file_gen: boolean;
  golden_rule_compliant: boolean;
}
```

---

## Capability: Get Diagnostics

~~~meta
id: diagnostics.get
transport: HTTP GET /harnesses/{harnessId}/diagnostics
auth: required
~~~

### Intention
Retrieves diagnostic information about the harness.

### Input
```typescript
interface GetDiagnosticsRequest {
  harnessId: HarnessId;                // path parameter
}
```

### Output
```typescript
interface GetDiagnosticsResponse {
  harness_id: HarnessId;
  version: string;
  uptime_seconds: number;
  memory_usage_mb: number;
  active_sessions: number;
  active_executions: number;
  connected_mcp_servers: number;
  installed_skills: number;
  config: Record<string, unknown>;
}
```

---

## Capability: Get Logs

~~~meta
id: diagnostics.logs
transport: HTTP GET /harnesses/{harnessId}/logs
auth: required
~~~

### Intention
Retrieves recent logs from the harness.

### Input
```typescript
interface GetLogsRequest extends PaginationParams {
  harnessId: HarnessId;                // path parameter
  level?: "debug" | "info" | "warn" | "error";
  since?: ISO8601;
}
```

### Output
```typescript
interface GetLogsResponse extends PaginatedResponse<LogEntry> {}

interface LogEntry {
  timestamp: ISO8601;
  level: "debug" | "info" | "warn" | "error";
  message: string;
  context?: Record<string, unknown>;
}
```

---

## Capability: Stream Logs

~~~meta
id: diagnostics.streamLogs
transport: HTTP GET /harnesses/{harnessId}/logs/stream (SSE)
auth: required
~~~

### Intention
Streams logs in real-time. Useful for debugging and monitoring.

### Input
```typescript
interface StreamLogsRequest {
  harnessId: HarnessId;                // path parameter
  level?: "debug" | "info" | "warn" | "error";
}
```

### Output
Stream of `LogEntry` objects.
