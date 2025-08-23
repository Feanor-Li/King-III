/**
 * Arguments for [tool_name] tool
 */
export interface ParseImgArgs {
    // Define tool-specific arguments
    prompt: string;
    imagePath: string;
}

/**
 * External API response structure
 */
export interface CamProResponse {
    // Define API response structure
    data: unknown;
    metadata?: Record<string, unknown>;
}

export interface ParseImgResponse {
    text: string;
}