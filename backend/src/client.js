var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
export class CamProClient {
    constructor(apiKey) {
        this.baseUrl = 'https://api.campro.com';
        this.apiKey = apiKey;
    }
    /**
     * Performs API request with proper error handling
     */
    performRequest(params) {
        return __awaiter(this, void 0, void 0, function* () {
            const response = yield fetch(`${this.baseUrl}/endpoint`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`,
                },
                body: JSON.stringify(params),
            });
            if (!response.ok) {
                let errorText;
                try {
                    errorText = yield response.text();
                }
                catch (_a) {
                    errorText = "Unable to parse error response";
                }
                throw new Error(`CamPro API error: ${response.status} ${response.statusText}\n${errorText}`);
            }
            const data = yield response.json();
            return this.formatResponse(data);
        });
    }
    formatResponse(data) {
        // Format response according to service requirements
        return JSON.stringify(data, null, 2);
    }
}
