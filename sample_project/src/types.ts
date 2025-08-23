/**
 * Arguments for [tool_name] tool
 */
export interface ParseImgArgs {
    // Define tool-specific arguments
    query: string;
    options?: Record<string, unknown>;
}

/**
 * External API response structure
 */
export interface CamProResponse {
    // Define API response structure
    data: unknown;
    metadata?: Record<string, unknown>;
}