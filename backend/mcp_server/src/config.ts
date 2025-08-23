import dotenv from 'dotenv';
import path from 'path';

dotenv.config({
  path: path.resolve(__dirname, '../.env')
});

export interface Config {
    apiKey: string;
    port: number;
    isProduction: boolean;
}

export function loadConfig(): Config {
    const apiKey = process.env['CAMPRO_API_KEY'];
    if (!apiKey) {
        throw new Error('CAMPRO_API_KEY environment variable is required');
    }

    const port = parseInt(process.env.PORT || '8080', 10);
    const isProduction = process.env.NODE_ENV === 'production';

    return { apiKey, port, isProduction };
}
